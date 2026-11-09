# Skill behaviour harness (D-51)

Scripted conversations that test the SCS Agent Skills (`skills/`) against the assertions in
`plan/0.7/06-work-breakdown.md`: a to m (WP-10), n to t (WP-10b, the rc2 skills), u (section owners, D-92), and v (content first, ISS-056). The agent under test runs the skills through the
Claude Agent SDK; a second model plays the user; checks read the transcript, the engine's
JSON envelopes, and the repository before and after.

This is a maintainer tool. It calls the Anthropic API and costs money on every run. It is not
part of CI.

## Files

| File | What it holds |
|---|---|
| `config.yaml` | Pinned models, runs per scenario, pass thresholds, limits, prices |
| `scenarios.yaml` | The simulated user's persona and the thirteen scenarios |
| `fixtures.py` | Builds each scenario's starting Domain repository with the engine |
| `checks.py` | The assertions, a to v, as functions of a recorded run |
| `harness.py` | Runs the conversations, scores them, writes the report |

## Running

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pip install -e ../scd-validator -e ../cli       # the engine under test
export ANTHROPIC_API_KEY=...                     # a key for this harness only

python harness.py run --scenario compile --runs 1 --model claude-haiku-5-5   # debug
python harness.py run                                                         # full D-51 run
python harness.py report runs/<timestamp>                                     # re-render
```

Each run writes `runs/<timestamp>/`: one JSON record per conversation, the sandboxes, and
`report.md` with the per-assertion verdict and the cost.

## Isolation

Each conversation gets its own fixture repository, HOME, and Claude configuration. Bash runs
in the Claude Code sandbox, with WebFetch and WebSearch disabled, and a hook denies Write and
Edit outside the work folder. Check b also flags Bash commands that write outside the
repository (redirections, file commands, engine `--dir` and `--output`).

The sandbox refuses writes to `.git/config` and `.git/hooks`, so `git init`, and with it
`scs new domain`, cannot run inside it. The `domain-init` scenario therefore sets `sandbox: false` and
runs with a Bash guard hook that denies writes outside the work folder, `cd` out of it, and
network commands. The guard is a pattern check, not a sandbox.

## Source documents

The set-up scenarios give the simulated user documents (an AI usage policy, a project brief)
held outside the work folder. When the assistant names a folder for them, the user says they
have put them there and the harness copies them into it, between turns, if it is a `sources/`
folder in the work folder. A path the user cannot use leaves the folder empty, and assertion o
fails on the unrecorded document.

## Scoring

MUST assertions pass in 5 of 5 runs and SHOULD assertions in 4 of 5 (D-51). An assertion that
does not apply to a run (`na`) is not counted, except in a scenario that targets it, where it
counts as a failure. Assertions e, l, n, p, t, and u need judgment and are graded by the judge
model, p t and u after a mechanical part (the Project's `--ontology`; `scs status` first; every owner role held); o is
mechanical (the path, the recorded document, no profile answer recorded first) and then
judged (no profile question asked first); the rest are mechanical. s reads the committer of
every commit made during the run. `python harness.py rescore runs/<timestamp>` scores saved runs again with
the current checks, paying only for the judge.

Choices worth knowing when reading a report:

- b is scored on what is left: a write outside the repository that the guard refused, or that
  left nothing behind, passes and is listed under Notes. A path through a variable (`$TMPDIR`)
  cannot be resolved and fails.
- e ignores a failure that the agent retried in the same turn (the same operation, and for
  `bundle version` the same `--bundle`). A retry whose output went into a pipe counts as
  superseding, so a second failure hidden by the pipe is not caught.
- c, g, and h3 count `scs bundle release` (ISS-058) as a version, as well as
  `scs bundle version`.
- Since rc6 (ISS-056) the skills ask section owners and the releaser at release, not in
  set-up: u is scored on `release-owners`, and v checks that `domain-init` and `project-init`,
  which stop at drafting, record no owners or approvers.
- l scores only the reply to the out-of-scope request; a step the user then asks for on its
  own, such as a compile, is in scope.

## Results

| Date | Runs | Result | Report |
|---|---|---|---|
| 2026-10-28 | 40 on `claude-sonnet-5-5` | All MUST and SHOULD assertions pass; i 4 of 5 | `results/2026-10-28-sonnet-5-5.md` |
| 2026-11-02 | rc2 skills (WP-10b): 60 runs, then targeted reruns | Every MUST passes 5 of 5; p (pacing, now SHOULD) 4 of 5 | `results/2026-11-02-rc2.md` |

## Model changes

The models are pinned in `config.yaml`. Record any change here, with the date and the reason,
and re-run the full set.

| Date | Agent | User | Judge | Note |
|---|---|---|---|---|
| 2026-10-28 | claude-sonnet-5-5 | claude-haiku-5-5 | claude-sonnet-5-5 | First run |
