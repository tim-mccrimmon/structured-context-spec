"""The Agent Skills under `skills/` (WP-10): format, shared rules, and the engine calls they name.

These are structural checks. The behaviour tests (scripted conversations, D-51) need a model
and run separately.
"""

import importlib.util
import json
import re
import shlex
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from scs_tools.cli import cli

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
NAMES = [
    "scs-compile",
    "scs-draft",
    "scs-explain",
    "scs-intake",
    "scs-review",
    "scs-validate",
    "scs-version",
]
RULES_RE = re.compile(r"## Rules for every SCS skill\n(.*?)\n## ", re.DOTALL)


def frontmatter(skill: str):
    text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    _, head, body = text.split("---", 2)
    return yaml.safe_load(head), body


def engine():
    spec = importlib.util.spec_from_file_location(
        "scs_engine", SKILLS / "scs-intake" / "scripts" / "scs_engine.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_seven_skills_exist():
    assert sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md")) == NAMES


def test_copies_match_their_sources():
    result = subprocess.run(
        [sys.executable, str(SKILLS / "sync.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("skill", NAMES)
def test_frontmatter_follows_the_agent_skills_format(skill: str):
    meta, body = frontmatter(skill)
    assert meta["name"] == skill
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"])
    assert 0 < len(meta["description"]) <= 1024
    assert len(meta.get("compatibility", "")) <= 500
    assert all(isinstance(v, str) for v in meta["metadata"].values())
    assert meta["metadata"]["scs-minimum-tools-version"] == engine().MINIMUM_TOOLS_VERSION
    assert len(body.splitlines()) < 500


@pytest.mark.parametrize("skill", NAMES)
def test_skills_ref_validates(skill: str):
    validator = pytest.importorskip("skills_ref.validator")
    assert validator.validate(SKILLS / skill) == []


def test_every_skill_carries_the_same_rules():
    blocks = {s: RULES_RE.search(frontmatter(s)[1]) for s in NAMES}
    assert all(blocks.values()), [s for s, b in blocks.items() if not b]
    assert len({b.group(1) for b in blocks.values()}) == 1


@pytest.mark.parametrize("skill", NAMES)
def test_relative_links_resolve(skill: str):
    for page in (SKILLS / skill).rglob("*.md"):
        for target in re.findall(r"\]\(([^)#:]+)(?:#[^)]*)?\)", page.read_text(encoding="utf-8")):
            assert (page.parent / target).exists(), f"{page}: {target}"


def _engine_calls():
    """Every `scs ...` command line in the skills' code blocks, as (skill, words)."""
    calls = []
    for skill in NAMES:
        for page in (SKILLS / skill).rglob("*.md"):
            text = page.read_text(encoding="utf-8")
            for span in re.findall(r"(?<!`)`(scs(?:-validate)? [^`]+)`(?!`)", text):
                calls.append((skill, shlex.split(span.replace("...", "x"))))
            for block in re.findall(r"```\n(.*?)```", text, re.DOTALL):
                joined = block.replace("\\\n", " ")
                for line in joined.splitlines():
                    match = re.search(r"run (scs(?:-validate)? .*)", line)
                    if match:
                        command = re.split(r"\s<<?\s|\s<<'", match.group(1))[0]
                        calls.append((skill, shlex.split(command)))
    return calls


@pytest.mark.parametrize("skill,words", _engine_calls())
def test_named_engine_commands_and_flags_exist(skill: str, words):
    if words[0] == "scs-validate":
        from scs_validator.commands.validate import validate

        command, rest = validate, words[1:]
        help_text = CliRunner().invoke(command, ["--help"]).output
    else:
        path = [w for w in words[1:3] if not w.startswith("-") and not w.startswith("<")]
        # Only group words, never a positional argument: stop once --help succeeds as a leaf.
        prefix = []
        for word in path:
            trial = CliRunner().invoke(cli, [*prefix, word, "--help"])
            if trial.exit_code != 0:
                break
            prefix.append(word)
        assert prefix, f"{skill}: unknown command {words}"
        help_text = CliRunner().invoke(cli, [*prefix, "--help"]).output
        rest = words[1 + len(prefix) :]
    for flag in (w.split("=")[0] for w in rest if w.startswith("--")):
        assert flag in help_text, f"{skill}: {' '.join(words[:3])} has no {flag}"


@pytest.mark.parametrize(
    "version,minimum,ok",
    [
        ("0.7.0", "0.7.0", True),
        ("0.7.0rc1", "0.7.0", True),  # D-56: a pre-release meets its base version
        ("0.7.1", "0.7.0", True),
        ("0.6.9", "0.7.0", False),
        ("0.10.0", "0.7.0", True),
        ("unknown", "0.7.0", False),
    ],
)
def test_engine_version_comparison(version: str, minimum: str, ok: bool):
    assert engine().meets(version, minimum) is ok


def test_stage_wheels_restores_standard_names(tmp_path: Path, monkeypatch, capsys):
    module = engine()
    monkeypatch.setattr(module.tempfile, "gettempdir", lambda: str(tmp_path))
    upload = tmp_path / "a6975716-scs_tools-0.7.0rc0-py3-none-any.whl"
    upload.write_bytes(b"wheel")
    assert module.stage_wheels([str(upload), str(tmp_path / "notes.txt")]) == 1
    out = json.loads(capsys.readouterr().out)
    staged = Path(out["staged"][0])
    assert staged.name == "scs_tools-0.7.0rc0-py3-none-any.whl"
    assert staged.read_bytes() == b"wheel"
    assert out["rejected"] == [str(tmp_path / "notes.txt")]


def test_install_plan_installs_nothing_and_pins_the_version(capsys):
    module = engine()
    assert module.install_plan([]) == 0
    plans = json.loads(capsys.readouterr().out)["plans"]
    assert "scs-tools==" in plans[0]["command"] or "scs-tools==" in plans[1]["command"]


def test_install_plan_recommends_bundled_wheels(tmp_path: Path, monkeypatch, capsys):
    module = engine()
    wheel = tmp_path / "scs_tools-0.7.0rc1-py3-none-any.whl"
    monkeypatch.setattr(module, "bundled_wheels", lambda: [wheel])
    assert module.install_plan([]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["recommended"] == "bundled or uploaded wheels"
    assert [p["recommended"] for p in out["plans"]] == [True, False, False]
    assert str(wheel) in out["plans"][0]["command"]
    assert all("may be a pre-release" in p["note"] for p in out["plans"][1:])


def test_install_plan_recommends_pypi_without_wheels(monkeypatch, capsys):
    module = engine()
    monkeypatch.setattr(module, "bundled_wheels", lambda: [])
    assert module.install_plan([]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["recommended"] == "PyPI"
    assert out["plans"][0]["recommended"] is True


def test_run_refuses_anything_but_the_engine(capsys):
    assert engine().run(["rm", "-rf", "/"]) == 3
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_package_builds_one_zip_per_skill_with_bundled_wheels(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    for name in ("scs_tools-0.7.0rc1-py3-none-any.whl", "scs_validator-0.7.0rc1-py3-none-any.whl"):
        (wheels / name).write_bytes(b"wheel")
    out = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, str(SKILLS / "package.py"), "--out", str(out), "--wheels", str(wheels)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert sorted(p.stem for p in out.glob("*.zip")) == NAMES
    with zipfile.ZipFile(out / "scs-intake.zip") as archive:
        names = set(archive.namelist())
    assert "scs-intake/SKILL.md" in names
    assert "scs-intake/assets/wheels/scs_tools-0.7.0rc1-py3-none-any.whl" in names
    assert all(n.startswith("scs-intake/") for n in names)


def test_package_refuses_an_incomplete_wheel_set(tmp_path: Path):
    (tmp_path / "scs_tools-0.7.0rc1-py3-none-any.whl").write_bytes(b"wheel")
    result = subprocess.run(
        [sys.executable, str(SKILLS / "package.py"), "--out", str(tmp_path / "o")]
        + ["--wheels", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
