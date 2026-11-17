"""Machine mode (RFC 0002 section 3, WP-05): the --json envelope, exit codes, and dry runs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import jsonschema
import pytest
from click.testing import CliRunner, Result

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
ENVELOPE_SCHEMA = json.loads((REPO / "schema" / "cli" / "envelope-schema.json").read_text())
SCS_TOOLS = REPO / "tools" / "cli" / "scs_tools"

VALID_SCD = """\
id: scd:project:release-gates
type: project
title: Release Gates
version: "1.0.0"
description: The gates a release passes before it ships.
content:
  gates:
    - name: tests
      required: true
provenance:
  created_by: Test Author <test@structuredcontext.dev>
  created_at: "2026-10-25T00:00:00Z"
"""


AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]


def run(*args: str, input: str = "") -> Result:
    return CliRunner().invoke(cli, list(args), input=input)


def envelope(result: Result) -> Dict:
    """The one JSON object on stdout, checked against the envelope schema and the exit code."""
    data = json.loads(result.stdout)
    jsonschema.validate(data, ENVELOPE_SCHEMA)
    assert data["exit_code"] == result.exit_code
    assert data["ok"] is (result.exit_code == 0)
    return data


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


def snapshot(root: Path) -> Dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


NEW_OPTIONS = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]


def new(tmp_path: Path, kind: str = "project", name: str = "demo") -> Path:
    """A workspace made by `scs new` in a Domain repository: `new domain NAME` returns
    `NAME-context/domain`; `new project NAME` is added to `acme-context/`, created if need be."""
    if kind == "domain":
        result = run(
            "new", "domain", name, "--dir", str(tmp_path), *NEW_OPTIONS, "--no-interactive"
        )
        assert result.exit_code == 0, result.output
        return tmp_path / f"{name}-context" / "domain"
    repo = tmp_path / "acme-context"
    if not repo.exists():
        new(tmp_path, "domain", "acme")
    result = run("new", "project", name, "--dir", str(repo), *NEW_OPTIONS, "--no-interactive")
    assert result.exit_code == 0, result.output
    return repo / "projects" / name


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = new(tmp_path)
    monkeypatch.chdir(path)
    return path


@pytest.fixture
def domain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = new(tmp_path, "domain")
    monkeypatch.chdir(path)
    return path


@pytest.fixture
def domain_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A Domain repository: domain/ plus one Project workspace, with the cwd at its root."""
    repo = new(tmp_path, "domain", "acme").parent
    new(tmp_path, "project", "pump")
    monkeypatch.chdir(repo)
    return repo


def assert_dry_run_matches(workspace: Path, *args: str, input: str = "") -> Dict:
    """`--dry-run` reports the same changes as the real run and writes nothing. Envelope paths
    are relative to the Domain repository root (D-42)."""
    root = workspace.parents[1] if workspace.parent.name == "projects" else workspace.parent
    before = snapshot(root)
    dry = envelope(run(*args, "--json", "--dry-run", input=input))
    assert snapshot(root) == before
    real = envelope(run(*args, "--json", input=input))
    assert dry["changes"] == real["changes"]
    after = snapshot(root)
    changed = {p for p in after if before.get(p) != after[p]}
    reported = {c["path"] for c in real["changes"]}
    assert {str(Path(p)) for p in changed} == {str(Path(p)) for p in reported} != set()
    return real


# ---------------------------------------------------------------- one test per exit code


def test_exit_0_version_envelope():
    data = envelope(run("--version", "--json"))
    assert data["command"] == "--version"
    assert data["result"]["scs_version"] == data["scs_version"] == "0.7.0"
    assert data["result"]["tools_version"] == data["tools_version"]


def test_exit_1_invalid_scd(project: Path):
    bad = project / "context" / "project" / "tech-stack.yaml"
    bad.write_text("id: not-an-id\ntype: project\n")
    result = run("validate", str(bad), "--json")
    assert result.exit_code == 1, result.output
    data = envelope(result)
    assert data["diagnostics"] and {d["severity"] for d in data["diagnostics"]} >= {"error"}


def test_exit_2_strict_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from scs_validator import api, utils

    def warned(*args: object, **kwargs: object) -> api.Report:
        result = utils.ValidationResult("semantic")
        result.add_warning(
            utils.ValidationWarning(
                "Provenance section is empty", level="semantic", code="SCD_PROVENANCE_EMPTY"
            )
        )
        return api.Report([result])

    monkeypatch.setattr(api, "validate_files", warned)
    scd = tmp_path / "x.yaml"
    scd.write_text(VALID_SCD)
    result = run("validate", str(scd), "--json", "--strict")
    assert result.exit_code == 2, result.output
    assert envelope(result)["diagnostics"][0]["severity"] == "warning"


@pytest.mark.parametrize(
    "args",
    [
        ["compile", "--json"],
        ["compile", "x.yaml", "--json", "--no-such-option"],
        ["add", "bundle", "--json"],
        ["scd", "write", "x.yaml", "--json"],
    ],
)
def test_exit_3_usage_errors(args: List[str]):
    result = run(*args)
    assert result.exit_code == 3, result.output
    assert codes(envelope(result)) == ["USAGE_ERROR"]


def test_exit_3_usage_error_without_json_is_human():
    result = run("compile")
    assert result.exit_code == 3
    assert not result.stdout.lstrip().startswith("{")


def test_exit_4_missing_file(tmp_path: Path):
    result = run("compile", str(tmp_path / "missing.yaml"), "--json")
    assert result.exit_code == 4, result.output
    assert codes(envelope(result)) == ["FILE_NOT_FOUND"]


def test_exit_5_internal_error(project: Path, monkeypatch: pytest.MonkeyPatch):
    import scs_tools.commands.compile as compile_module

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(compile_module, "compile_tree", boom)
    result = run("compile", "bundles/project-bundle.yaml", "--json", "--no-validate")
    assert result.exit_code == 5, result.output
    data = envelope(result)
    assert codes(data) == ["INTERNAL_ERROR"]
    assert "boom" in data["diagnostics"][0]["message"]


# ---------------------------------------------------------------- per-command conformance


def test_validate_envelope_carries_the_report(project: Path):
    result = run("validate", "--bundle", "bundles/project-bundle.yaml", "--json")
    data = envelope(result)
    assert data["command"] == "validate"
    assert isinstance(data["result"], dict)


def test_compile_writes_dist_bundle_name_version(domain: Path):
    data = assert_dry_run_matches(domain, "compile", "bundles/domain-bundle.yaml", "--allow-draft")
    path = data["result"]["path"]
    assert re.fullmatch(r"domain/dist/demo-DRAFT\+[0-9a-f]{8}\.yaml", path)
    assert data["changes"] == [{"action": "create", "path": path}]
    assert (domain.parent / path).is_file()

    again = envelope(run("compile", "bundles/domain-bundle.yaml", "--allow-draft", "--json"))
    assert again["changes"] == [] and again["result"]["sha256"] == data["result"]["sha256"]


def test_compile_refuses_output_outside_the_repository(domain: Path, tmp_path: Path):
    outside = tmp_path / "elsewhere" / "artifact.yaml"
    result = run(
        "compile", "bundles/domain-bundle.yaml", "--allow-draft", "-o", str(outside), "--json"
    )
    assert result.exit_code == 1, result.output
    assert codes(envelope(result))[-1] == "OUTPUT_OUTSIDE_REPO"
    assert not outside.exists()


def test_compile_stdout_conflicts_with_json(project: Path):
    result = run("compile", "bundles/project-bundle.yaml", "--stdout", "--json")
    assert result.exit_code == 3
    assert codes(envelope(result)) == ["USAGE_ERROR"]


def test_add_scd_and_bundle(project: Path):
    # The scaffold supplies the full set (D-64); remove what is added back below
    (project / "context" / "project" / "audit-trail.yaml").unlink()
    (project / "bundles" / "concepts" / "compliance-governance.yaml").unlink()
    data = assert_dry_run_matches(project, "add", "scd", "audit-trail", *AUTHOR)
    assert data["command"] == "add scd"
    assert data["changes"][0]["action"] == "create"

    data = assert_dry_run_matches(project, "add", "bundle", "compliance-governance", *AUTHOR)
    assert data["command"] == "add bundle"


def test_add_refuses_to_overwrite_without_force(project: Path):
    run("add", "scd", "audit-trail", *AUTHOR)
    result = run("add", "scd", "audit-trail", *AUTHOR, "--json")
    assert result.exit_code == 1
    assert codes(envelope(result)) == ["FILE_EXISTS"]


def test_add_bundle_plan_is_reserved(project: Path):
    before = snapshot(project)
    result = run("add", "bundle", "plan", *AUTHOR, "--json")
    assert result.exit_code == 1
    assert codes(envelope(result)) == ["RESERVED_BUNDLE_NAME"]
    assert snapshot(project) == before


def test_workspace_required_at_a_domain_repository_root(domain_repo: Path):
    result = run("add", "scd", "audit-trail", *AUTHOR, "--json")
    assert result.exit_code == 3, result.output
    assert codes(envelope(result)) == ["WORKSPACE_REQUIRED"]


def test_workspace_option_selects_the_workspace(domain_repo: Path):
    (domain_repo / "projects" / "pump" / "context" / "project" / "audit-trail.yaml").unlink()
    data = envelope(run("add", "scd", "audit-trail", *AUTHOR, "--workspace", "pump", "--json"))
    assert data["changes"] == [
        {"action": "create", "path": "projects/pump/context/project/audit-trail.yaml"}
    ]
    result = run("add", "scd", "audit-trail", *AUTHOR, "--workspace", "nope", "--json")
    assert codes(envelope(result)) == ["WORKSPACE_NOT_FOUND"]


def test_scd_write_from_stdin(project: Path):
    target = "context/project/release-gates.yaml"
    data = assert_dry_run_matches(
        project, "scd", "write", target, "--from-file", "-", input=VALID_SCD
    )
    shown = f"projects/demo/{target}"  # relative to the repository root (D-42)
    assert data["result"] == {"path": shown, "id": "scd:project:release-gates", "written": True}
    assert (project / target).read_text() == VALID_SCD


def test_scd_write_refuses_an_invalid_scd(project: Path):
    target = project / "context" / "project" / "broken.yaml"
    result = run("scd", "write", str(target), "--from-file", "-", "--json", input="id: nope\n")
    assert result.exit_code == 1
    assert envelope(result)["result"]["written"] is False
    assert not target.exists()


def test_scd_write_refuses_paths_outside_the_repository(project: Path, tmp_path: Path):
    outside = tmp_path / "outside.yaml"
    result = run("scd", "write", str(outside), "--from-file", "-", "--json", input=VALID_SCD)
    assert result.exit_code == 1
    assert codes(envelope(result)) == ["OUTPUT_OUTSIDE_REPO"]
    assert not outside.exists()


def test_scd_write_rejects_empty_input(project: Path):
    result = run("scd", "write", "context/project/x.yaml", "--from-file", "-", "--json")
    assert result.exit_code == 3
    assert codes(envelope(result)) == ["INPUT_EMPTY"]


# ---------------------------------------------------------------- engine boundary


def test_no_command_shells_out_to_the_validator():
    """scs-tools calls scs_validator in-process (D-08); no subprocess runs the validator."""
    pattern = re.compile(r"scs[-_]validat|\"-m\",\s*\"scs")
    offenders = []
    for path in SCS_TOOLS.rglob("*.py"):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if "subprocess" in line or "Popen" in line or "check_output" in line:
                window = "\n".join(path.read_text().splitlines()[number - 1 : number + 4])
                if pattern.search(window):
                    offenders.append(f"{path.relative_to(REPO)}:{number}")
    assert offenders == []
