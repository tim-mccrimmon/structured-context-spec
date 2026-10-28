#!/usr/bin/env python3
"""Behaviour tests for the SCS Agent Skills (D-51).

Each scenario in scenarios.yaml is a conversation between the agent under test, running the
skills through the Claude Agent SDK, and a simulated user. Every run gets a fresh sandbox:
its own fixture repository, HOME, and Claude configuration, with Bash sandboxed (or guarded,
where a scenario sets sandbox: false) and no network.
The assertions in checks.py are scored per scenario: MUST in 5 of 5 runs, SHOULD in 4 of 5.

    export ANTHROPIC_API_KEY=...            # a key for this harness only
    python harness.py run --runs 1 --model claude-haiku-5-5 --scenario compile   # debug
    python harness.py run                    # the full D-51 run (config.yaml)
    python harness.py report runs/<stamp>    # re-score a finished run

Every run spends money; the summary reports what each run cost.
"""

import argparse
import asyncio
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import yaml
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    PermissionResultDeny,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from pydantic import BaseModel

import checks
import fixtures

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SKILLS = ROOT / "skills"
SKIP = {".git", ".claude", ".cc-writes", "__pycache__"}  # .cc-writes: the Bash sandbox
RESULT_LIMIT = 20000
SKILL_NAMES = sorted(p.parent.name for p in SKILLS.glob("scs-*/SKILL.md"))


class Reply(BaseModel):
    message: str
    approves_change: bool
    done: bool


class Verdict(BaseModel):
    verdict: bool
    reason: str


# --- sandbox and snapshots -----------------------------------------------------------------


def repos(work: Path) -> list[Path]:
    return sorted(p for p in work.iterdir() if (p / ".git").exists())


def snapshot(work: Path) -> dict[str, str]:
    state = {}
    for path in work.rglob("*"):
        rel = path.relative_to(work)
        if SKIP.intersection(rel.parts) or not path.is_file():
            continue
        state[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for repo in repos(work):
        refs = subprocess.run(["git", "for-each-ref", "refs/tags", "--format",
                               "%(refname:short) %(objectname)"], cwd=repo,
                              capture_output=True, text=True).stdout
        for line in refs.splitlines():
            tag, obj = line.split()
            state[f"tag:{repo.name}/{tag}"] = obj
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                              capture_output=True, text=True).stdout.strip()
        state[f"head:{repo.name}"] = head
    return state


def changed(before: dict, after: dict) -> list[str]:
    return sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))


def engine_env(sandbox: Path, key: str) -> dict:
    bin_dir = Path(sys.executable).parent
    return {
        "ANTHROPIC_API_KEY": key,
        "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin",
        "HOME": str(sandbox / "home"),
        "CLAUDE_CONFIG_DIR": str(sandbox / "claude-config"),
        "LANG": "en_US.UTF-8",
    }


def prepare(sandbox: Path, fixture: str, key: str) -> tuple[Path, dict, dict]:
    work = sandbox / "work"
    for d in (work, sandbox / "home", sandbox / "claude-config"):
        d.mkdir(parents=True)
    env = engine_env(sandbox, key)
    info = fixtures.BUILDERS[fixture](work, env)
    if "repo" in info:
        fixtures.commit(env, info["repo"])
    skills_dir = work / ".claude" / "skills"
    skills_dir.mkdir(parents=True)
    for skill in sorted(SKILLS.glob("scs-*/SKILL.md")):
        shutil.copytree(skill.parent, skills_dir / skill.parent.name)
    return work, env, {k: str(v) if isinstance(v, Path) else v for k, v in info.items()}


# --- models ---------------------------------------------------------------------------------


class Meter:
    def __init__(self, prices: dict):
        self.prices = prices
        self.usd = 0.0

    def add(self, model: str, usage) -> None:
        p = self.prices[model]
        self.usd += (
            usage.input_tokens * p["input"]
            + usage.output_tokens * p["output"]
            + (usage.cache_creation_input_tokens or 0) * p["cache_write"]
            + (usage.cache_read_input_tokens or 0) * p["cache_read"]
        ) / 1e6


def transcript(turns: list[dict]) -> str:
    lines = []
    for turn in turns:
        lines += [f"YOU: {turn['user']}", f"ASSISTANT: {turn['assistant'] or '(no text)'}"]
    return "\n\n".join(lines)


async def simulate(client, model: str, meter: Meter, persona: str, facts: str,
                   turns: list[dict]) -> Reply:
    response = await client.messages.parse(
        model=model,
        max_tokens=2000,
        system=f"{persona}\nFacts:\n{facts}",
        messages=[{"role": "user", "content": (
            "The conversation so far:\n\n" + transcript(turns) + "\n\nWrite your next reply. "
            "Set approves_change to true only if your reply approves a change the assistant "
            "showed you and asked about. Set done to true if your goal is reached or the "
            "assistant cannot do it; then message may be empty."
        )}],
        output_format=Reply,
    )
    meter.add(model, response.usage)
    return response.parsed_output


async def judge(client, model: str, meter: Meter, question: str, evidence: str) -> Verdict:
    response = await client.messages.parse(
        model=model,
        max_tokens=2000,
        system="You grade an AI assistant's message strictly and literally. Answer the question "
               "about the message with verdict true or false, and a one-sentence reason.",
        messages=[{"role": "user", "content": f"{evidence}\n\nQuestion: {question}"}],
        output_format=Verdict,
    )
    meter.add(model, response.usage)
    return response.parsed_output


# --- one run --------------------------------------------------------------------------------


async def converse(work: Path, env: dict, scenario: dict, config: dict, persona: str,
                   api, meter: Meter, log) -> dict:
    turns: list[dict] = []
    record = {"agent_cost_usd": 0.0, "skills_loaded": None, "stopped": None}
    limits = config["limits"]

    async def guard(input_data, tool_use_id, context):
        path = input_data["tool_input"].get("file_path") or ""
        if path and not Path(path).resolve().is_relative_to(work.resolve()):
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                           "permissionDecision": "deny",
                                           "permissionDecisionReason": "outside the sandbox"}}
        return {}

    async def bash_guard(input_data, tool_use_id, context):
        # Used when a scenario runs unsandboxed: the same tests as check b, applied before the
        # command runs.
        command = input_data["tool_input"].get("command", "")
        bad = (checks.outside(checks.write_targets(command), [work])
               + checks.outside(checks.engine_dirs(command) + checks.cd_targets(command),
                                [work]))
        if bad or checks.NETWORK_RE.search(command):
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                           "permissionDecision": "deny",
                                           "permissionDecisionReason": "outside the work folder"}}
        return {}

    async def refuse(tool_name, tool_input, context):
        return PermissionResultDeny(message=f"{tool_name} is not available in this session")

    sandboxed = scenario.get("sandbox", True)
    hooks = [HookMatcher(matcher="Write|Edit|NotebookEdit", hooks=[guard])]
    if not sandboxed:
        hooks.append(HookMatcher(matcher="Bash", hooks=[bash_guard]))
    options = ClaudeAgentOptions(
        model=config["models"]["agent"],
        cwd=str(work),
        setting_sources=["project"],
        skills=SKILL_NAMES,
        allowed_tools=["Bash", "Read", "Glob", "Grep", "Skill", "Write", "Edit"],
        disallowed_tools=["WebFetch", "WebSearch"],
        max_turns=limits["agent_turns"],
        max_budget_usd=limits["budget_usd"],
        env=env,
        sandbox={"enabled": sandboxed, "autoAllowBashIfSandboxed": True,
                 "allowUnsandboxedCommands": False, "failIfUnavailable": True},
        hooks={"PreToolUse": hooks},
        can_use_tool=refuse,
    )
    message, affirmative = scenario["opening"].strip(), False
    max_user = scenario.get("max_user_turns", limits["user_turns"])
    async with ClaudeSDKClient(options=options) as agent:
        for _ in range(max_user):
            before = snapshot(work)
            await agent.query(message)
            texts, tools = [], {}
            async for msg in agent.receive_response():
                if isinstance(msg, SystemMessage) and msg.subtype == "init":
                    record["skills_loaded"] = msg.data.get("skills")
                elif isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            texts.append(block.text)
                        elif isinstance(block, ToolUseBlock):
                            tools[block.id] = {"name": block.name, "input": block.input}
                elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
                    for block in msg.content:
                        if isinstance(block, ToolResultBlock) and block.tool_use_id in tools:
                            content = block.content
                            if isinstance(content, list):
                                content = "\n".join(c.get("text", "") for c in content)
                            tools[block.tool_use_id]["result"] = (content or "")[:RESULT_LIMIT]
                            tools[block.tool_use_id]["is_error"] = block.is_error
                elif isinstance(msg, ResultMessage):
                    record["agent_cost_usd"] = max(record["agent_cost_usd"],
                                                   msg.total_cost_usd or 0.0)
                    record.setdefault("result_costs", []).append(msg.total_cost_usd)
                    if msg.subtype != "success":
                        record["stopped"] = msg.subtype
            after = snapshot(work)
            new_repos = [r.name for r in repos(work) if f"head:{r.name}" not in before]
            for tool in tools.values():
                path = tool["input"].get("file_path")
                if path:
                    tool["outside"] = bool(checks.outside([path], repos(work)))
                elif tool["name"] == "Bash":
                    command = tool["input"].get("command", "")
                    tool["outside"] = (checks.outside(checks.write_targets(command), repos(work))
                                       + checks.outside(checks.engine_dirs(command), [work]))
            turns.append({"user": message, "affirmative": affirmative,
                          "assistant": "\n\n".join(texts), "tools": list(tools.values()),
                          "changes": changed(before, after), "new_repos": new_repos})
            log(f"turn {len(turns) - 1}: {len(tools)} tool call(s), "
                f"{len(turns[-1]['changes'])} change(s)")
            if record["stopped"]:
                break
            reply = await simulate(api, config["models"]["user"], meter, persona,
                                   scenario["facts"], turns)
            if reply.done or not reply.message.strip():
                break
            message, affirmative = reply.message, reply.approves_change
    record["turns"] = turns
    return record


def finish(work: Path, env: dict) -> dict:
    found = repos(work)
    if not found:
        return {"repo": None, "intake": False, "missing_intake": [], "validate_exit": None}
    repo = found[0]
    workspaces = [repo / "domain"] + sorted((repo / "projects").glob("*/"))
    workspaces = [w for w in workspaces if (w / ".scs" / "config").exists()]
    missing = [w.name for w in workspaces if not (w / "intake.yaml").exists()]
    exit_code = subprocess.run(["scs-validate", "--strict"], cwd=repo, env=env,
                               capture_output=True).returncode
    return {"repo": repo.name, "intake": bool(workspaces) and not missing,
            "missing_intake": missing, "validate_exit": exit_code}


async def score(run: dict, scenario: dict, api, config: dict, meter: Meter) -> dict:
    names = sorted(set(scenario["targets"]) | set(checks.CROSS_CUTTING))
    results = {}
    for name in names:
        if name == "e":
            results[name] = await score_e(run, api, config, meter)
        elif name == "l":
            results[name] = await score_l(run, api, config, meter)
        elif name == "i":
            results[name] = checks.check_i(run, scenario, ROOT)
        else:
            results[name] = checks.CHECKS[name](run, scenario)
    return results


async def score_e(run: dict, api, config: dict, meter: Meter) -> dict:
    exercised = False
    for t, turn in enumerate(run["turns"]):
        failures = checks.failed_envelopes(turn)
        if not failures:
            continue
        exercised = True
        summary = json.dumps([{"command": f.get("command"), "ok": False,
                               "errors": [d for d in f.get("diagnostics", [])
                                          if d.get("severity") == "error"][:5]}
                              for f in failures], indent=1)[:4000]
        succeeded = [e.get("command") for e in checks.operations(turn) if e.get("ok")]
        verdict = await judge(
            api, config["models"]["judge"], meter,
            "Does the assistant's message state or imply that any of the failed operations "
            "succeeded? Saying a later, different attempt succeeded is fine only if the message "
            "also makes clear the failed one did not.",
            f"Failed operations in this turn:\n{summary}\n\nOperations that succeeded in this "
            f"turn: {succeeded or 'none'}\n\nThe assistant's message:\n"
            f"{turn['assistant']}",
        )
        if verdict.verdict:
            return checks.fail(f"turn {t}: {verdict.reason}")
    return checks.ok() if exercised else checks.na("no ok:false envelope")


async def score_l(run: dict, api, config: dict, meter: Meter) -> dict:
    # Only the reply to the out-of-scope request is scored: a later step the user asks for on
    # its own, such as a compile, is in scope.
    calls = checks.engine_calls(run["turns"][0])
    if calls:
        return checks.fail(f"engine called: {calls[0]['program']} "
                           f"{' '.join(calls[0]['args'][:3])}")
    text = run["turns"][0]["assistant"]
    verdict = await judge(
        api, config["models"]["judge"], meter,
        "Does the assistant say that deploying to an AI service, multi-reviewer approval "
        "workflows, and hosting a shared registry are outside what SCS (or these skills) do, "
        "rather than attempting them?",
        f"The user asked to deploy an artifact to Claude Enterprise, set up a two-reviewer "
        f"approval workflow, and host bundles in a shared registry.\n\nThe assistant:\n{text}",
    )
    return checks.ok(verdict.reason) if verdict.verdict else checks.fail(verdict.reason)


async def one_run(name: str, n: int, scenario: dict, config: dict, persona: str, out: Path,
                  key: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        sandbox = out / "sandboxes" / f"{name}-{n}"
        started = time.monotonic()
        log = lambda m: print(f"[{name} #{n}] {m}", flush=True)  # noqa: E731
        api = anthropic.AsyncAnthropic(api_key=key)
        meter = Meter(config["prices"])
        work, env, info = prepare(sandbox, scenario["fixture"], key)
        start = snapshot(work)
        try:
            record = await converse(work, env, scenario, config, persona, api, meter, log)
        except Exception as error:  # a crashed run is a failed run, recorded as such
            record = {"turns": [], "error": repr(error), "agent_cost_usd": 0.0}
            log(f"error: {error!r}")
        run = {"scenario": name, "run": n, "fixture": info, "start": start,
               "end": snapshot(work), "final": finish(work, env), **record}
        run["outside_changes"] = [
            k for k in changed(start, run["end"])
            if not k.startswith(("tag:", "head:"))
            and not any(k.startswith(r.name + "/") for r in repos(work))
        ]
        run["results"] = await score(run, scenario, api, config, meter) if run["turns"] else {
            a: checks.fail(record.get("error", "no turns")) for a in scenario["targets"]}
        run["harness_cost_usd"] = meter.usd
        run["seconds"] = round(time.monotonic() - started)
        (out / "runs").mkdir(exist_ok=True)
        (out / "runs" / f"{name}-{n}.json").write_text(json.dumps(run, indent=1, default=str))
        log(f"done in {run['seconds']}s, agent ${run['agent_cost_usd']:.2f}, "
            f"harness ${meter.usd:.3f}: "
            + " ".join(f"{a}={r['status']}" for a, r in run["results"].items()))
        return run


# --- report ---------------------------------------------------------------------------------


def report(out: Path, config: dict, scenarios: dict) -> str:
    runs = [json.loads(p.read_text()) for p in sorted((out / "runs").glob("*.json"))]
    total = config["runs"]
    cells: dict[tuple[str, str], list[str]] = {}
    for run in runs:
        for name, result in run["results"].items():
            cells.setdefault((name, run["scenario"]), []).append(result["status"])
    lines = [f"# Skill behaviour run, {out.name}", "",
             f"Agent model `{runs[0].get('model', config['models']['agent'])}`; "
             f"{len(runs)} run(s). MUST passes in {config['pass']['MUST']} of 5 runs, SHOULD "
             f"in {config['pass']['SHOULD']} of 5 (scaled to {total} run(s) here).", "",
             "| Assertion | Level | Scenario | Pass | Fail | Not exercised | Verdict |",
             "|---|---|---|---|---|---|---|"]
    verdicts = {}
    for (name, scen), statuses in sorted(cells.items()):
        targeted = name in scenarios[scen]["targets"]
        passes, fails = statuses.count("pass"), statuses.count("fail")
        nas = statuses.count("na")
        if not targeted and passes + fails == 0:
            continue
        level = checks.LEVELS[name]
        need = math.ceil(len(statuses) * config["pass"][level] / 5)
        good = passes >= need if targeted else fails <= len(statuses) - need
        verdicts.setdefault(name, []).append(good)
        lines.append(f"| {name} | {level} | {scen} | {passes} | {fails} | {nas} | "
                     f"{'pass' if good else 'FAIL'} |")
    agent = sum(r.get("agent_cost_usd", 0) for r in runs)
    harness = sum(r.get("harness_cost_usd", 0) for r in runs)
    lines += ["", "| Assertion | Level | Verdict |", "|---|---|---|"]
    lines += [f"| {n} | {checks.LEVELS[n]} | {'pass' if all(v) else 'FAIL'} |"
              for n, v in sorted(verdicts.items())]
    lines += ["", f"Cost: agent ${agent:.2f}, simulated user and judge ${harness:.2f}, "
              f"total ${agent + harness:.2f} (${(agent + harness) / max(len(runs), 1):.2f} "
              "per run).", "", "## Failures", ""]
    for run in runs:
        for name, result in run["results"].items():
            if result["status"] == "fail":
                lines.append(f"- {run['scenario']} #{run['run']}, {name}: {result['detail']}")
    lines += ["", "## Notes (passing, but worth reading)", ""]
    for run in runs:
        result = run["results"].get("b", {})
        if result.get("status") == "pass" and result.get("detail"):
            lines.append(f"- {run['scenario']} #{run['run']}, b: {result['detail']}")
    text = "\n".join(lines) + "\n"
    (out / "report.md").write_text(text)
    return text


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


async def main_run(args) -> int:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Set ANTHROPIC_API_KEY to the harness key.", file=sys.stderr)
        return 3
    config = load(HERE / "config.yaml")
    spec = load(HERE / "scenarios.yaml")
    if args.model:
        config["models"]["agent"] = args.model
    if args.runs:
        config["runs"] = args.runs
    names = args.scenario or list(spec["scenarios"])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out) / stamp
    out.mkdir(parents=True)
    (out / "config.json").write_text(json.dumps(
        {**config, "scenarios": names, "model": config["models"]["agent"]}, indent=1))
    sem = asyncio.Semaphore(args.parallel)
    await asyncio.gather(*(
        one_run(name, n, spec["scenarios"][name], config, spec["persona"], out, key, sem)
        for name in names for n in range(1, config["runs"] + 1)))
    print(report(out, config, spec["scenarios"]))
    print(f"Details: {out}")
    return 0


async def main_rescore(out: Path) -> int:
    """Score the saved records again with the current checks (the judge is called again)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Set ANTHROPIC_API_KEY to the harness key.", file=sys.stderr)
        return 3
    config = {**load(HERE / "config.yaml"), **json.loads((out / "config.json").read_text())}
    scenarios = load(HERE / "scenarios.yaml")["scenarios"]
    api = anthropic.AsyncAnthropic(api_key=key)
    meter = Meter(config["prices"])
    for path in sorted((out / "runs").glob("*.json")):
        run = json.loads(path.read_text())
        if run["turns"]:
            run["results"] = await score(run, scenarios[run["scenario"]], api, config, meter)
            path.write_text(json.dumps(run, indent=1, default=str))
    print(report(out, config, scenarios))
    print(f"Rescoring cost ${meter.usd:.2f} (judge only).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run scenarios")
    run.add_argument("--scenario", action="append", help="run only this scenario (repeatable)")
    run.add_argument("--runs", type=int, help="runs per scenario (default: config.yaml)")
    run.add_argument("--model", help="agent model, for debugging (default: config.yaml)")
    run.add_argument("--parallel", type=int, default=2, help="runs at a time (default 2)")
    run.add_argument("--out", default=str(HERE / "runs"), help="output directory")
    again = sub.add_parser("report", help="report a finished run from its saved results")
    again.add_argument("dir")
    rescore = sub.add_parser("rescore", help="score a finished run again with the current checks")
    rescore.add_argument("dir")
    args = parser.parse_args()
    if args.command == "run":
        return asyncio.run(main_run(args))
    out = Path(args.dir)
    if args.command == "rescore":
        return asyncio.run(main_rescore(out))
    config = {**load(HERE / "config.yaml"), **json.loads((out / "config.json").read_text())}
    print(report(out, config, load(HERE / "scenarios.yaml")["scenarios"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
