"""Domain repositories (RFC 0002 section 9, WP-03): `scs new domain` and `scs new project`."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List

import jsonschema
import pytest
import yaml
from click.testing import CliRunner, Result
from scs_validator.commands.validate import validate as validator_cmd

from scs_tools import git
from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
ENVELOPE_SCHEMA = json.loads((SCHEMA / "cli" / "envelope-schema.json").read_text())
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
OPERATIONS = ["Create", "Maintain", "Validate", "Version", "Compile"]


def run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def envelope(result: Result) -> Dict:
    data = json.loads(result.stdout)
    jsonschema.validate(data, ENVELOPE_SCHEMA)
    assert data["exit_code"] == result.exit_code
    return data


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


def new_domain(parent: Path, name: str = "x", *options: str) -> Path:
    result = run("new", "domain", name, "--dir", str(parent), *AUTHOR, "--no-interactive", *options)
    assert result.exit_code == 0, result.output
    return parent / f"{name}-context"


def new_project(cwd: Path, name: str, monkeypatch: pytest.MonkeyPatch, *options: str) -> Result:
    monkeypatch.chdir(cwd)
    return run("new", "project", name, *AUTHOR, "--no-interactive", *options)


def git_out(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


# ------------------------------------------------------------------ acceptance (WP-03)


def test_new_domain_then_project_validates_strictly_at_the_repository_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = new_domain(tmp_path, "x")
    assert (repo / "domain" / ".scs" / "config").is_file()
    result = new_project(repo, "a", monkeypatch)
    assert result.exit_code == 0, result.output
    assert (repo / "projects" / "a" / "bundles" / "project-bundle.yaml").is_file()

    monkeypatch.chdir(repo)
    result = CliRunner().invoke(
        validator_cmd, ["--strict", "--no-color", "--schema-dir", str(SCHEMA)]
    )
    assert result.exit_code == 0, result.output
    assert "Workspace domain" in result.output and "Workspace a" in result.output

    workflow = yaml.safe_load((repo / ".github" / "workflows" / "scs-validate.yml").read_text())
    steps = workflow["jobs"]["validate"]["steps"]
    checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout"))
    assert checkout["with"]["fetch-depth"] == 0
    assert checkout["with"]["fetch-tags"] is True
    assert steps[-1]["run"] == "scs-validate --strict"


def test_new_project_works_from_inside_a_workspace(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path)
    result = new_project(repo / "domain" / "bundles", "a", monkeypatch)
    assert result.exit_code == 0, result.output
    assert (repo / "projects" / "a" / ".scs" / "config").is_file()


def test_agents_md_states_the_domain_operations_and_exclusion(tmp_path: Path):
    repo = new_domain(tmp_path, "acme-health")
    agents = (repo / "AGENTS.md").read_text()
    assert "**acme-health**" in agents
    for operation in OPERATIONS:
        assert f"**{operation}**" in agents, operation
    assert "Application work does not belong here" in agents
    assert "confine your changes to that workspace" in agents
    claude = (repo / "CLAUDE.md").read_text()
    assert "@AGENTS.md" in claude and "[AGENTS.md](AGENTS.md)" in claude


def test_reserved_directories_are_not_created(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path)
    assert new_project(repo, "a", monkeypatch).exit_code == 0
    reserved = {"plan", "test-plan", "qa"}
    assert not [p for p in repo.rglob("*") if p.is_dir() and p.name in reserved]


def test_a_domain_named_plan_is_reserved(tmp_path: Path):
    data = envelope(run("new", "domain", "plan", "--dir", str(tmp_path), "--json", *AUTHOR))
    assert data["exit_code"] == 1 and codes(data) == ["RESERVED_BUNDLE_NAME"]
    assert data["changes"] == []
    assert not (tmp_path / "plan-context").exists()


def test_a_project_named_qa_is_reserved(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path)
    data = envelope(new_project(repo, "qa", monkeypatch, "--json"))
    assert data["exit_code"] == 1 and codes(data) == ["RESERVED_BUNDLE_NAME"]
    assert not (repo / "projects" / "qa").exists()


def test_new_project_outside_a_domain_repository_fails(tmp_path: Path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    data = envelope(new_project(elsewhere, "a", monkeypatch, "--json"))
    assert data["exit_code"] == 1 and codes(data) == ["DOMAIN_WORKSPACE_MISSING"]
    assert list(elsewhere.iterdir()) == []


def test_organization_domain_scaffold(tmp_path: Path):
    repo = new_domain(tmp_path, "acme")
    domain = repo / "domain"
    concepts = {p.stem for p in (domain / "bundles" / "concepts").glob("*.yaml")}
    assert {"company", "prohibited", "security", "compliance-governance"} <= concepts
    bundle = yaml.safe_load((domain / "bundles" / "domain-bundle.yaml").read_text())
    assert bundle["id"] == "bundle:acme" and bundle["type"] == "domain"
    config = yaml.safe_load((domain / ".scs" / "config").read_text())
    assert config["ontology"] == "sdlc" and "project_type" not in config
    assert (domain / "ontology" / "domain-manifest.yaml").is_file()
    assert not (domain / "domain").exists()  # 0.6 location (D-04)


def _concepts_and_scds(workspace: Path):
    concepts = {p.stem for p in (workspace / "bundles" / "concepts").glob("*.yaml")}
    scds = {p.stem for p in (workspace / "context" / "project").glob("*.yaml")}
    return concepts, scds


def test_personal_ontology_scaffold(tmp_path: Path, monkeypatch):
    """Personal is an ontology whose only fixed concept is boundaries (D-61, D-62, D-72);
    identity is provenance, not a concept (D-63)."""
    repo = new_domain(tmp_path, "jdoe", "--ontology", "personal")
    assert new_project(repo, "reminders", monkeypatch, "--ontology", "personal").exit_code == 0
    domain, project = repo / "domain", repo / "projects" / "reminders"
    for workspace in (domain, project):
        assert _concepts_and_scds(workspace) == ({"prohibited"}, {"prohibited"})
        config = yaml.safe_load((workspace / ".scs" / "config").read_text())
        assert config["ontology"] == "personal"
        manifest = yaml.safe_load((workspace / "ontology" / "domain-manifest.yaml").read_text())
        assert manifest["domain"]["id"] == "domain:personal"
        ids = [c["id"] for c in manifest["domain"]["ontology"]["concepts"]]
        assert ids == ["concept:prohibited"]
    bundle = yaml.safe_load((domain / "bundles" / "domain-bundle.yaml").read_text())
    assert bundle["imports"] == ["bundle:meta:0.6.0", "bundle:prohibited"]
    bundle = yaml.safe_load((project / "bundles" / "project-bundle.yaml").read_text())
    assert bundle["imports"] == ["bundle:prohibited"]
    prohibited = (project / "context" / "project" / "prohibited.yaml").read_text()
    assert "Projects cannot override" not in prohibited  # Domain wording only
    monkeypatch.chdir(repo)
    result = CliRunner().invoke(
        validator_cmd, ["--strict", "--no-color", "--schema-dir", str(SCHEMA)]
    )
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("ontology", ["sdlc", "cdmo", "mca", "personal"])
def test_every_ontology_scaffolds_a_domain_and_a_project(tmp_path: Path, monkeypatch, ontology):
    repo = new_domain(tmp_path, "acme", "--ontology", ontology)
    assert new_project(repo, "app", monkeypatch, "--ontology", ontology).exit_code == 0
    domain, _ = _concepts_and_scds(repo / "domain")
    project, _ = _concepts_and_scds(repo / "projects" / "app")
    assert "prohibited" in domain
    assert ("company" in domain) is (ontology != "personal")
    monkeypatch.chdir(repo)
    result = CliRunner().invoke(
        validator_cmd, ["--strict", "--no-color", "--schema-dir", str(SCHEMA)]
    )
    assert result.exit_code == 0, result.output


def test_provenance_names_a_person(tmp_path: Path):
    """Provenance identifies a person as `Name <email>` (D-28, D-63)."""
    repo = new_domain(tmp_path, "acme")
    for path in [*(repo / "domain").rglob("*.yaml")]:
        data = yaml.safe_load(path.read_text()) or {}
        if isinstance(data, dict) and "provenance" in data:
            assert (
                data["provenance"]["created_by"] == "Test Author <test@structuredcontext.dev>"
            ), path


def test_the_new_repository_has_one_commit_by_scs_tools(tmp_path: Path):
    repo = new_domain(tmp_path)
    log = git_out(repo, "log", "--format=%an <%ae>|%cn <%ce>").splitlines()
    assert log == [f"{git.ENGINE_IDENTITY}|{git.ENGINE_IDENTITY}"]
    assert git_out(repo, "status", "--porcelain") == ""
    assert git_out(repo, "branch", "--show-current").strip() == "main"
    tracked = set(git_out(repo, "ls-files").split())
    assert {"AGENTS.md", "CLAUDE.md", ".gitignore", ".gitattributes"} <= tracked
    assert "projects/.gitkeep" in tracked and "domain/.scs/config" in tracked


def test_sources_are_ignored_and_dist_is_not(tmp_path: Path):
    repo = new_domain(tmp_path)
    assert git_out(repo, "check-ignore", "domain/sources/manual.pdf").strip()
    assert git_out(repo, "check-ignore", "projects/a/sources/sop.docx").strip()
    ignored = subprocess.run(["git", "-C", str(repo), "check-ignore", "domain/dist/x.yaml"])
    assert ignored.returncode == 1  # dist/ is left to the user


def test_gitattributes_forces_lf(tmp_path: Path):
    repo = new_domain(tmp_path)
    lines = (repo / ".gitattributes").read_text().splitlines()
    assert "* text eol=lf" in lines


def test_workspace_config_keys(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path, "acme", "--ontology", "mca")
    assert new_project(repo, "pump", monkeypatch, "--ontology", "cdmo").exit_code == 0
    domain = yaml.safe_load((repo / "domain" / ".scs" / "config").read_text())
    project = yaml.safe_load((repo / "projects" / "pump" / ".scs" / "config").read_text())
    assert domain["name"] == "domain" and domain["bundle_type"] == "domain"
    assert project["name"] == "pump" and project["bundle_type"] == "project"
    assert domain["ontology"] == "mca" and project["ontology"] == "cdmo"
    for config in (domain, project):
        assert config["scs_version"] == "0.7.0"
        assert config["tools_version"]


# ---------------------------------------------------------------- refusals and envelope


def test_new_domain_json_lists_files_init_and_commit(tmp_path: Path):
    data = envelope(run("new", "domain", "x", "--dir", str(tmp_path), "--json", *AUTHOR))
    assert data["ok"] is True
    created = [c["path"] for c in data["changes"] if c["action"] == "create"]
    assert data["changes"][-2] == {"action": "git-init", "ref": "main"}
    commit = data["changes"][-1]
    assert commit["action"] == "git-commit" and commit["ref"] == "HEAD"
    assert sorted(p["path"] for p in commit["paths"]) == sorted(created)
    assert {p["status"] for p in commit["paths"]} == {"A"}
    assert "AGENTS.md" in created and "domain/bundles/domain-bundle.yaml" in created
    assert data["result"]["bundle"] == "bundle:x"


def test_new_project_json_lists_files_relative_to_the_repository(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path)
    data = envelope(new_project(repo, "a", monkeypatch, "--json"))
    paths = [c["path"] for c in data["changes"]]
    assert all(c["action"] == "create" for c in data["changes"])
    assert "projects/a/bundles/project-bundle.yaml" in paths
    assert all(p.startswith("projects/a/") for p in paths)


def test_an_existing_repository_or_project_is_not_overwritten(tmp_path: Path, monkeypatch):
    repo = new_domain(tmp_path)
    data = envelope(run("new", "domain", "x", "--dir", str(tmp_path), "--json", *AUTHOR))
    assert codes(data) == ["WORKSPACE_EXISTS"]
    assert new_project(repo, "a", monkeypatch).exit_code == 0
    data = envelope(new_project(repo, "a", monkeypatch, "--json"))
    assert codes(data) == ["WORKSPACE_EXISTS"]


@pytest.mark.parametrize("name", ["domain", "security", "company", ".x", "a/b"])
def test_invalid_project_names_are_refused(tmp_path: Path, monkeypatch, name: str):
    repo = new_domain(tmp_path)
    data = envelope(new_project(repo, name, monkeypatch, "--json"))
    assert data["exit_code"] == 3 and codes(data) == ["WORKSPACE_NAME_INVALID"]
    assert sorted(p.name for p in (repo / "projects").iterdir()) == [".gitkeep"]


@pytest.mark.parametrize("option", [["--ontology", "none"], ["--type", "minimal"]])
def test_removed_options_are_usage_errors(tmp_path: Path, monkeypatch, option: list):
    repo = new_domain(tmp_path)
    data = envelope(new_project(repo, "a", monkeypatch, *option, "--json"))
    assert data["exit_code"] == 3 and codes(data) == ["USAGE_ERROR"]


def test_new_domain_needs_git(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(git, "available", lambda: False)
    data = envelope(run("new", "domain", "x", "--dir", str(tmp_path), "--json", *AUTHOR))
    assert codes(data) == ["GIT_REQUIRED"]
    assert not (tmp_path / "x-context").exists()


def test_a_failed_commit_leaves_nothing_behind(tmp_path: Path, monkeypatch):
    real = git.run

    def failing(repo: Path, *args: str, **kwargs: str) -> str:
        if args[0] == "commit":
            raise git.GitError("git commit: simulated failure")
        return real(repo, *args, **kwargs)

    monkeypatch.setattr(git, "run", failing)
    data = envelope(run("new", "domain", "x", "--dir", str(tmp_path), "--json", *AUTHOR))
    assert codes(data) == ["GIT_COMMAND_FAILED"] and data["changes"] == []
    assert not (tmp_path / "x-context").exists()
