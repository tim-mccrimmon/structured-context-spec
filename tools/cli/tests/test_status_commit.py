"""WP-10b: `scs commit` (D-84) and `scs status` (D-83)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List

import jsonschema
import pytest
from click.testing import CliRunner, Result

from scs_tools import git as engine_git
from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
ENVELOPE_SCHEMA = json.loads((REPO / "schema" / "cli" / "envelope-schema.json").read_text())
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
PERSON = "Jane Doe <jane@acme-health.org>"


def run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def envelope(result: Result) -> Dict:
    data = json.loads(result.stdout)
    jsonschema.validate(data, ENVELOPE_SCHEMA)
    assert data["exit_code"] == result.exit_code
    return data


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A Domain repository (cdmo) with one Project, `app`; the current directory is its root."""
    result = run("new", "domain", "acme", "--dir", str(tmp_path), "--ontology", "cdmo", *AUTHOR)
    assert result.exit_code == 0, result.output
    root = tmp_path / "acme-context"
    monkeypatch.chdir(root)
    result = run("new", "project", "app", "--ontology", "sdlc", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    return root


# ------------------------------------------------------------------ scs commit (D-84)


def test_commit_needs_a_named_person_as_author(repo: Path):
    (repo / "domain" / "context" / "project" / "prohibited.yaml").write_text("changed\n")
    data = envelope(run("commit", "--workspace", "domain", "-m", "x", "--json"))
    assert data["exit_code"] == 3 and codes(data) == ["COMMIT_AUTHOR_REQUIRED"]
    data = envelope(
        run("commit", "--workspace", "domain", "-m", "x", "--author", "role:qa", "--json")
    )
    assert codes(data) == ["COMMIT_AUTHOR_INVALID"]


def test_commit_dry_run_lists_the_files_and_commits_nothing(repo: Path):
    (repo / "domain" / "context" / "project" / "prohibited.yaml").write_text("changed\n")
    before = git(repo, "rev-parse", "HEAD")
    data = envelope(
        run("commit", "--workspace", "domain", "-m", "x", "--author", PERSON, "--dry-run", "--json")
    )
    assert data["ok"]
    assert data["changes"] == [
        {
            "action": "git-commit",
            "ref": "HEAD",
            "paths": [{"path": "domain/context/project/prohibited.yaml", "status": "M"}],
        }
    ]
    assert git(repo, "rev-parse", "HEAD") == before


def test_commit_takes_only_the_workspace_and_never_sources(repo: Path):
    domain = repo / "domain"
    (domain / "context" / "project" / "prohibited.yaml").write_text("changed\n")
    (domain / "sources" / "policy.md").write_text("source document\n")
    project_scd = repo / "projects" / "app" / "context" / "project" / "stakeholders.yaml"
    project_scd.write_text("changed\n")
    (repo / "notes.txt").write_text("staged elsewhere\n")
    git(repo, "add", "notes.txt")

    data = envelope(
        run("commit", "--workspace", "domain", "-m", "Draft rules", "--author", PERSON, "--json")
    )
    assert data["ok"], data
    assert git(repo, "log", "-1", "--format=%an <%ae>|%cn|%s").strip() == (
        f"{PERSON}|scs-tools|Draft rules"
    )
    committed = git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert committed == ["domain/context/project/prohibited.yaml"]
    status = git(repo, "status", "--porcelain")
    assert "A  notes.txt" in status  # still staged, not committed
    assert "projects/app/context/project/stakeholders.yaml" in status
    assert "policy.md" not in status  # ignored (D-59)


def test_commit_with_nothing_to_commit_changes_nothing(repo: Path):
    before = git(repo, "rev-parse", "HEAD")
    data = envelope(run("commit", "--workspace", "app", "-m", "x", "--author", PERSON, "--json"))
    assert data["ok"] and data["changes"] == [] and data["result"]["files"] == 0
    assert git(repo, "rev-parse", "HEAD") == before


# ------------------------------------------------------------------ scs status (D-83)


def status(*args: str) -> Dict:
    data = envelope(run("status", *args, "--json"))
    assert data["ok"], data
    return data["result"]


def test_status_at_the_root_reports_every_workspace(repo: Path):
    result = status()
    assert [w["workspace"] for w in result["workspaces"]] == ["domain", "app"]
    domain, app = result["workspaces"]
    assert domain["bundle"] == "bundle:acme" and domain["ontology"] == "cdmo"
    assert domain["latest_version"] is None and domain["working_version"] == "DRAFT"
    assert domain["intake"] == {"present": False}
    assert domain["scds"]["count"] > 0 and domain["scds"]["placeholders"]
    assert app["scds"]["placeholders"]  # sdlc templates carry "[...]" hints
    assert "domain_latest_version" not in domain
    assert app["domain_latest_version"] is None
    assert domain["uncommitted"] == [] and app["uncommitted"] == []


def test_status_reports_sources_findings_and_uncommitted_files(repo: Path):
    domain = repo / "domain"
    (domain / "sources" / "policy.md").write_text("source document\n")
    (domain / "sources" / "sop.md").write_text("source document\n")
    record = {"id": "doc-policy", "title": "AI policy", "path": "sources/policy.md"}
    missing = {"id": "doc-qm", "title": "Quality manual", "path": "sources/qm.pdf"}
    for doc in (record, missing):
        assert (
            run(
                "intake", "set", "source_documents", json.dumps(doc), "--workspace", "domain"
            ).exit_code
            == 0
        )
    for decision, rationale in (("deferred", None), ("kept", "policy says so")):
        args = [
            "intake",
            "record-finding",
            "--kind",
            "technical-risk",
            "--target",
            "scd:project:prohibited#NO-001",
            "--finding",
            "f",
            "--decision",
            decision,
            "--decided-by",
            PERSON,
            "--workspace",
            "domain",
        ]
        assert run(*args, *(["--rationale", rationale] if rationale else [])).exit_code == 0

    ws = status("--workspace", "domain")["workspaces"][0]
    assert ws["sources"] == {
        "files": ["domain/sources/policy.md", "domain/sources/sop.md"],
        "unrecorded": ["domain/sources/sop.md"],
        "missing": ["doc-qm"],
    }
    assert ws["intake"]["source_documents"] == ["doc-policy", "doc-qm"]
    assert ws["intake"]["findings"] == {"changed": 0, "kept": 1, "deferred": 1}
    assert ws["intake"]["deferred"] == ["rf-1"]
    assert ws["uncommitted"] == [{"path": "domain/intake.yaml", "status": "A"}]


def test_status_reports_versions_and_the_domain_version_to_a_project(repo: Path):
    # A version tag made directly, with the engine's git settings (conftest's config signs tags)
    engine_git.run(repo, "tag", "-a", "domain/acme-v1.0.0", "-m", "v1")
    (repo / "domain" / "context" / "project" / "prohibited.yaml").write_text("changed\n")
    result = status()
    domain, app = result["workspaces"]
    assert domain["versions"] == ["1.0.0"] and domain["latest_version"] == "1.0.0"
    assert domain["changed_since_version"] == 1
    assert domain["compiled"] == {"artifacts": [], "latest_version_compiled": False}
    assert app["domain_latest_version"] == "1.0.0"


def test_status_in_a_project_reports_only_that_project(repo: Path, monkeypatch):
    monkeypatch.chdir(repo / "projects" / "app")
    assert [w["workspace"] for w in status()["workspaces"]] == ["app"]


def test_status_outside_a_repository_fails(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = envelope(run("status", "--json"))
    assert codes(data) == ["WORKSPACE_NOT_FOUND"]
