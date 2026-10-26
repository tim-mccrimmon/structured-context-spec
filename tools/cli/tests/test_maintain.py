"""Machine mode for `new` and `bundle version`, and the engine's maintenance commands (WP-06):
D-08, D-13, D-68, D-69, D-71, D-74, D-75, D-76."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import jsonschema
import pytest
import yaml
from click.testing import CliRunner, Result
from scs_validator.commands.validate import validate as validator_cmd

from scs_tools import git as engine_git
from scs_tools import versioning
from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
ENVELOPE_SCHEMA = json.loads((SCHEMA / "cli" / "envelope-schema.json").read_text())
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
APPROVER = "Sam Lee <sam@structuredcontext.dev>"
GIT_USER = "[user]\n\tname = Git User\n\temail = git@structuredcontext.dev\n"


def run(*args: str, input: Optional[str] = None) -> Result:
    return CliRunner().invoke(cli, list(args), input=input)


def envelope(result: Result) -> Dict:
    data = json.loads(result.stdout)
    jsonschema.validate(data, ENVELOPE_SCHEMA)
    assert data["exit_code"] == result.exit_code
    return data


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


def files(root: Path) -> Dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(root).parts
    }


def git_state(repo: Path) -> Dict[str, object]:
    def out(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True
        ).stdout

    return {
        "refs": out("for-each-ref", "--format=%(refname) %(objectname)"),
        "head": out("rev-parse", "HEAD"),
        "index": (repo / ".git" / "index").read_bytes(),
        "status": out("status", "--porcelain", "--untracked-files=all"),
    }


def conforms(root: Path, *args: str, prefix: str = "") -> Dict:
    """Machine-mode conformance (plan section 4): one valid envelope, the dry run changes nothing
    and reports exactly the real run's changes, and the real run changes exactly those files."""
    before = files(root)
    dry = envelope(run(*args, "--json", "--dry-run"))
    assert dry["ok"], dry
    assert files(root) == before
    real = envelope(run(*args, "--json"))
    assert real["ok"], real
    assert dry["changes"] == real["changes"]
    after = files(root)
    changed = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    reported = {prefix + c["path"] for c in real["changes"] if "path" in c}
    assert changed == reported != set()
    for change in real["changes"]:
        if change["action"] == "delete":
            assert prefix + change["path"] not in after
    return real


def validate(repo: Path, *args: str) -> tuple:
    result = CliRunner().invoke(
        validator_cmd, ["--json", "--schema-dir", str(SCHEMA), "--repo", str(repo), *args]
    )
    data = json.loads(result.stdout)
    return result.exit_code, data["diagnostics"]


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A personal Domain repository with a Project `app`, cwd in the Project."""
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    monkeypatch.chdir(tmp_path)
    result = run("new", "domain", "acme", "--ontology", "personal", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    root = tmp_path / "acme-context"
    monkeypatch.chdir(root)
    result = run("new", "project", "app", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    monkeypatch.chdir(root / "projects" / "app")
    return root


def app(repo: Path) -> Path:
    return repo / "projects" / "app"


def fill(path: Path, subject: str = "personal AI accounts") -> None:
    text = path.read_text()
    assert "  prohibitions: []" in text
    path.write_text(
        text.replace(
            "  prohibitions: []",
            f'  prohibitions:\n    - id: NO-001\n      kind: tool\n      subject: "{subject}"',
        )
    )


# ------------------------------------------------------------------ conformance


def test_new_domain_conforms(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    real = conforms(
        tmp_path, "new", "domain", "acme", *AUTHOR, "--no-interactive", prefix="acme-context/"
    )
    actions = [c["action"] for c in real["changes"]]
    assert actions[-2:] == ["git-init", "git-commit"]


def test_new_project_conforms(repo: Path, monkeypatch):
    monkeypatch.chdir(repo)
    real = conforms(repo, "new", "project", "web", *AUTHOR, "--no-interactive")
    assert all(c["path"].startswith("projects/web/") for c in real["changes"])


def test_bundle_version_conforms(repo: Path):
    fill(app(repo) / "context/project/prohibited.yaml")
    before = git_state(repo)
    dry = envelope(
        run(
            "bundle", "version", "-b", "bundles/concepts/prohibited.yaml", "-v", "1.0.0",
            "--approved-by", APPROVER, "--json", "--dry-run",
        )
    )  # fmt: skip
    assert git_state(repo) == before
    real = envelope(
        run(
            "bundle", "version", "-b", "bundles/concepts/prohibited.yaml", "-v", "1.0.0",
            "--approved-by", APPROVER, "--json",
        )
    )  # fmt: skip
    strip = [{k: v for k, v in c.items() if k != "ref"} for c in dry["changes"]]
    assert strip == [{k: v for k, v in c.items() if k != "ref"} for c in real["changes"]]
    assert [c.get("ref") for c in real["changes"]][-1] == "app/prohibited-v1.0.0"


# ------------------------------------------------------------------ authors and approvers


@pytest.mark.parametrize("machine", [False, True])
@pytest.mark.parametrize("missing", ["--author", "--email"])
def test_new_never_invents_an_author(tmp_path: Path, monkeypatch, machine: bool, missing: str):
    """D-71: without --author and --email, non-interactive and machine mode give NO_INPUT;
    git's identity appears only as the suggestion."""
    (tmp_path / "gitconfig").write_text(GIT_USER)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    monkeypatch.chdir(tmp_path)
    given = {"--author": "Test Author", "--email": "test@structuredcontext.dev"}
    del given[missing]
    args = ["new", "domain", "acme", *[x for kv in given.items() for x in kv], "--no-interactive"]
    result = run(*args, *(["--json"] if machine else []))
    assert result.exit_code == 3
    assert not (tmp_path / "acme-context").exists()
    if machine:
        data = envelope(result)
        assert codes(data) == ["NO_INPUT"] and data["changes"] == []
        expected = (
            {"author": "Git User"}
            if missing == "--author"
            else {"email": "git@structuredcontext.dev"}
        )
        assert data["diagnostics"][0]["suggestion"] == expected


def test_interactive_new_offers_git_identity_as_defaults(tmp_path: Path, monkeypatch):
    (tmp_path / "gitconfig").write_text(GIT_USER)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    monkeypatch.chdir(tmp_path)
    result = run("new", "domain", "acme", "--ontology", "personal", input="\n\n")
    assert result.exit_code == 0, result.output
    assert "[Git User]" in result.output and "[git@structuredcontext.dev]" in result.output
    config = (tmp_path / "acme-context/domain/bundles/domain-bundle.yaml").read_text()
    assert 'created_by: "Git User <git@structuredcontext.dev>"' in config


def test_add_needs_an_author_in_machine_mode(repo: Path, tmp_path: Path, monkeypatch):
    (tmp_path / "gitconfig").write_text(GIT_USER)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    data = envelope(run("add", "bundle", "groceries", "--new", "--json"))
    assert codes(data) == ["NO_INPUT"] and data["changes"] == []
    assert data["diagnostics"][0]["suggestion"] == {
        "author": "Git User",
        "email": "git@structuredcontext.dev",
    }


# ------------------------------------------------------------------ D-74


def test_a_project_inherits_its_domains_ontology(repo: Path, monkeypatch):
    config = yaml.safe_load((app(repo) / ".scs/config").read_text())
    assert config["ontology"] == "personal"
    assert sorted(p.stem for p in (app(repo) / "bundles/concepts").glob("*.yaml")) == ["prohibited"]
    monkeypatch.chdir(repo)
    result = run("new", "project", "web", "--ontology", "sdlc", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    assert "ontology: sdlc" in (repo / "projects/web/.scs/config").read_text()


# ------------------------------------------------------------------ add bundle --new (D-68, D-76)


def test_add_bundle_new_creates_a_concept_with_its_scd_ontology_entry_and_import(repo: Path):
    real = conforms(repo, "add", "bundle", "groceries", "--new", "--title", "Groceries", *AUTHOR)
    assert {(c["action"], c["path"]) for c in real["changes"]} == {
        ("create", "projects/app/bundles/concepts/groceries.yaml"),
        ("create", "projects/app/context/project/groceries.yaml"),
        ("modify", "projects/app/bundles/project-bundle.yaml"),
        ("modify", "projects/app/ontology/domain-manifest.yaml"),
    }
    root = yaml.safe_load((app(repo) / "bundles/project-bundle.yaml").read_text())
    assert root["imports"] == ["bundle:prohibited", "bundle:groceries"]
    manifest = yaml.safe_load((app(repo) / "ontology/domain-manifest.yaml").read_text())
    ids = [c["id"] for c in manifest["domain"]["ontology"]["concepts"]]
    assert ids[-1] == "concept:groceries"
    assert "# Domain Ontology manifest" in (app(repo) / "ontology/domain-manifest.yaml").read_text()
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics


@pytest.mark.parametrize("name", ["plan", "prohibited", "Bad_Name"])
def test_add_bundle_new_refuses_bad_or_existing_names(repo: Path, name: str):
    before = files(repo)
    data = envelope(run("add", "bundle", name, "--new", *AUTHOR, "--json"))
    assert not data["ok"] and data["changes"] == []
    assert files(repo) == before


# ------------------------------------------------------------------ pin, add-import, add-scd


def _release_concept(repo: Path, version: str = "1.0.0") -> None:
    fill(app(repo) / "context/project/prohibited.yaml")
    result = run(
        "bundle", "version", "-b", "bundles/concepts/prohibited.yaml", "-v", version,
        "--approved-by", APPROVER,
    )  # fmt: skip
    assert result.exit_code == 0, result.output


def test_pin_changes_exactly_one_import(repo: Path):
    _release_concept(repo)
    root = app(repo) / "bundles/project-bundle.yaml"
    before = root.read_text().splitlines()
    real = conforms(repo, "bundle", "pin", "prohibited", "--version", "1.0.0")
    assert real["changes"] == [
        {"action": "modify", "path": "projects/app/bundles/project-bundle.yaml"}
    ]
    after = root.read_text().splitlines()
    differ = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(before) == len(after)
    assert differ == [("  - bundle:prohibited", "  - bundle:prohibited:1.0.0")]


def test_pin_to_an_unreleased_version_or_a_missing_import_fails(repo: Path):
    _release_concept(repo)
    data = envelope(run("bundle", "pin", "prohibited", "--version", "2.0.0", "--json"))
    assert codes(data) == ["VERSION_NOT_FOUND"]
    data = envelope(run("bundle", "pin", "security", "--version", "1.0.0", "--json"))
    assert codes(data) == ["IMPORT_NOT_FOUND"]


def test_add_import_and_add_scd(repo: Path):
    assert run("add", "bundle", "groceries", "--new", *AUTHOR).exit_code == 0
    data = envelope(run("bundle", "add-import", "groceries", "--json"))
    assert codes(data) == ["IMPORT_EXISTS"]
    data = envelope(run("bundle", "add-import", "nothing-here", "--json"))
    assert codes(data) == ["IMPORT_UNRESOLVED"]

    scd = app(repo) / "context/project/pantry.yaml"
    scd.write_text(
        (app(repo) / "context/project/groceries.yaml")
        .read_text()
        .replace("scd:project:groceries", "scd:project:pantry")
    )
    real = conforms(
        repo, "bundle", "add-scd", "scd:project:pantry", "--bundle",
        "bundles/concepts/groceries.yaml",
    )  # fmt: skip
    assert real["changes"] == [
        {"action": "modify", "path": "projects/app/bundles/concepts/groceries.yaml"}
    ]
    concept = yaml.safe_load((app(repo) / "bundles/concepts/groceries.yaml").read_text())
    assert concept["scds"] == ["scd:project:groceries", "scd:project:pantry"]
    data = envelope(run("bundle", "add-scd", "scd:project:pantry", "--json"))
    assert codes(data) == ["BUNDLE_XOR_VIOLATION"]
    data = envelope(run("bundle", "add-scd", "scd:project:nope", "--json", "--bundle",
                        "bundles/concepts/groceries.yaml"))  # fmt: skip
    assert codes(data) == ["SCD_NOT_FOUND"]


# ------------------------------------------------------------------ remove-scd (D-69, D-75)


def test_removing_the_last_scd_removes_the_concept_its_import_and_ontology_entry(repo: Path):
    real = conforms(repo, "bundle", "remove-scd", "scd:project:prohibited")
    assert {(c["action"], c["path"]) for c in real["changes"]} == {
        ("delete", "projects/app/bundles/concepts/prohibited.yaml"),
        ("delete", "projects/app/context/project/prohibited.yaml"),
        ("modify", "projects/app/bundles/project-bundle.yaml"),
        ("modify", "projects/app/ontology/domain-manifest.yaml"),
    }
    root = yaml.safe_load((app(repo) / "bundles/project-bundle.yaml").read_text())
    assert root["imports"] == []
    manifest = (app(repo) / "ontology/domain-manifest.yaml").read_text()
    assert "concept:prohibited" not in manifest
    assert real["result"]["bundle_removed"] == "bundle:prohibited"


def test_an_scd_another_bundle_lists_is_kept(repo: Path):
    assert run("add", "bundle", "groceries", "--new", *AUTHOR).exit_code == 0
    assert (
        run(
            "bundle", "add-scd", "scd:project:prohibited", "-b", "bundles/concepts/groceries.yaml"
        ).exit_code
        == 0
    )
    data = envelope(run("bundle", "remove-scd", "scd:project:prohibited", "--json"))
    assert codes(data) == ["USAGE_ERROR"] and data["exit_code"] == 3

    real = conforms(
        repo, "bundle", "remove-scd", "scd:project:prohibited", "-b",
        "bundles/concepts/groceries.yaml",
    )  # fmt: skip
    assert real["changes"] == [
        {"action": "modify", "path": "projects/app/bundles/concepts/groceries.yaml"}
    ]
    assert (app(repo) / "context/project/prohibited.yaml").is_file()
    assert real["result"]["scd_file_deleted"] is False


def test_remove_scd_keeps_the_comments_of_the_files_it_edits(repo: Path):
    assert run("add", "bundle", "groceries", "--new", *AUTHOR).exit_code == 0
    assert run("bundle", "remove-scd", "scd:project:groceries").exit_code == 0
    root = (app(repo) / "bundles/project-bundle.yaml").read_text()
    assert "# A Project bundle imports its concept bundles directly." in root
    assert yaml.safe_load(root)["imports"] == ["bundle:prohibited"]


# ------------------------------------------------------------------ rollback (D-09)


def _fail(*args, **kwargs):
    raise engine_git.GitError("injected failure")


@pytest.mark.parametrize("after", ["snapshot", "manifest", "commit", "tag"])
def test_a_failed_version_leaves_everything_as_it_was(repo: Path, monkeypatch, after: str):
    fill(app(repo) / "context/project/prohibited.yaml")
    subprocess.run(["git", "-C", str(repo), "add", "projects/app/README.md"], check=True)
    before_files, before_git = files(repo), git_state(repo)

    if after == "snapshot":
        real_write = Path.write_text

        def write(self, *args, **kwargs):
            if self.name.endswith("-MANIFEST.yaml"):
                raise OSError("injected failure")
            return real_write(self, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", write)
    elif after == "manifest":
        monkeypatch.setattr(versioning.git, "commit_paths", _fail)
    elif after == "commit":
        real_run = engine_git.run

        def run_git(repo_path, *args, **kwargs):
            if args[:1] == ("tag",):
                raise engine_git.GitError("injected failure")
            return real_run(repo_path, *args, **kwargs)

        monkeypatch.setattr(versioning.git, "run", run_git)
    else:
        monkeypatch.setattr(versioning.git, "move_head", _fail)

    result = run(
        "bundle", "version", "-b", "bundles/concepts/prohibited.yaml", "-v", "1.0.0",
        "--approved-by", APPROVER, "--json",
    )  # fmt: skip
    monkeypatch.undo()
    data = envelope(result)
    assert not data["ok"] and data["changes"] == []
    assert files(repo) == before_files
    assert git_state(repo) == before_git
