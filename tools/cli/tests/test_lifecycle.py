"""Lifecycle integrity (plan section 5, WP-14): versioning, the D-39 checks, and compile."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest
import yaml
from click.testing import CliRunner, Result
from scs_validator.commands.validate import validate as validator_cmd
from scs_validator.digest import content_digest
from scs_validator.resolver import resolve

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
APPROVER = "Sam Lee <sam@structuredcontext.dev>"
ENGINE = "scs-tools <noreply@scs.invalid>"
CONCEPT = "bundles/concepts/prohibited.yaml"
ROOT = "bundles/project-bundle.yaml"
SCD = "context/project/prohibited.yaml"
ROOT_SCD = "context/project/app-rules.yaml"
# Plain git for test setup, past the hostile global config the engine has to survive.
PLAIN = [
    "-c",
    "user.name=Test",
    "-c",
    "user.email=test@structuredcontext.dev",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "tag.gpgSign=false",
    "-c",
    "tag.forceSignAnnotated=false",
    "-c",
    "core.hooksPath=/dev/null",
    "-c",
    "core.autocrlf=false",
]


def run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *PLAIN, "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new))


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A personal Domain repository with a Project `app` whose `prohibited` concept has one
    prohibition. The root imports the concept unpinned."""
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = run(
        "new", "domain", "acme", "--dir", str(tmp_path), "--ontology", "personal", *AUTHOR,
        "--no-interactive",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    root = tmp_path / "acme-context"
    monkeypatch.chdir(root)
    result = run("new", "project", "app", "--ontology", "personal", *AUTHOR, "--no-interactive")
    assert result.exit_code == 0, result.output
    ws = root / "projects" / "app"
    edit(
        ws / SCD,
        "  prohibitions: []",
        "  prohibitions:\n    - id: NO-001\n      kind: tool\n"
        '      subject: "personal AI accounts"',
    )
    monkeypatch.chdir(ws)
    return root


def ws(repo: Path) -> Path:
    return repo / "projects" / "app"


def own_scd(repo: Path) -> None:
    """Give the root an SCD of its own in place of its import (a bundle has one or the other)."""
    app = ws(repo)
    scd = (app / SCD).read_text()
    scd = scd.replace("scd:project:prohibited", "scd:project:app-rules")
    (app / ROOT_SCD).write_text(scd.replace("personal AI accounts", "shared passwords"))
    edit(app / ROOT, "  - bundle:prohibited\n", "")
    edit(app / ROOT, "imports:\n", "imports: []\n")
    edit(app / ROOT, "scds: []", "scds:\n  - scd:project:app-rules")


def version(bundle: str, number: str, *extra: str) -> Tuple[int, Dict]:
    result = run(
        "bundle", "version", "--bundle", bundle, "--version", number, "--approved-by", APPROVER,
        "--json", *extra,
    )  # fmt: skip
    data = json.loads(result.stdout)
    return result.exit_code, data


def pin(repo: Path, number: str) -> None:
    text = (ws(repo) / ROOT).read_text()
    lines = [
        f"  - bundle:prohibited:{number}" if line.startswith("  - bundle:prohibited") else line
        for line in text.splitlines()
    ]
    (ws(repo) / ROOT).write_text("\n".join(lines) + "\n")


def release(repo: Path, concept: str = "1.0.0", root: str = "1.0.0") -> None:
    """Version the concept, pin it, version the root."""
    code, data = version(CONCEPT, concept)
    assert code == 0, data
    pin(repo, concept)
    code, data = version(ROOT, root)
    assert code == 0, data


def validate(repo: Path, *args: str) -> Tuple[int, List[Dict]]:
    result = CliRunner().invoke(
        validator_cmd, ["--json", "--schema-dir", str(SCHEMA), "--repo", str(repo), *args]
    )
    data = json.loads(result.stdout)
    return result.exit_code, data["diagnostics"]


def found(diagnostics: List[Dict]) -> Set[str]:
    return {d["code"] for d in diagnostics}


def tags(repo: Path) -> List[str]:
    return git(repo, "tag", "--list").split()


def compile_(*args: str) -> Result:
    return run("compile", *args)


def commit_all(repo: Path, message: str = "edit") -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD").strip()


def move_tag(repo: Path, tag: str, commit: str) -> None:
    git(repo, "tag", "-f", "-a", "-m", "moved", tag, commit)


# ------------------------------------------------------------------ versioning guards


@pytest.mark.parametrize("no_validate", [False, True])
@pytest.mark.parametrize("ref", ["bundle:prohibited", "bundle:prohibited:DRAFT"])
def test_an_unpinned_or_draft_import_is_refused(repo: Path, no_validate: bool, ref: str):
    edit(ws(repo) / ROOT, "  - bundle:prohibited\n", f"  - {ref}\n")
    code, data = version(ROOT, "1.0.0", *(["--no-validate"] if no_validate else []))
    assert code == 1
    assert "VERSION_IMPORT_NOT_PINNED" in codes(data)
    assert data["changes"] == [] and tags(repo) == []


def test_no_validate_still_refuses_a_drifted_import(repo: Path):
    version(CONCEPT, "1.0.0")
    pin(repo, "1.0.0")
    edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
    code, data = version(ROOT, "1.0.0", "--no-validate")
    assert code == 1
    assert "CONTENT_DIGEST_MISMATCH" in codes(data)
    assert "app/app-v1.0.0" not in tags(repo)


def test_a_version_is_never_overwritten(repo: Path):
    assert version(CONCEPT, "1.0.0")[0] == 0
    code, data = version(CONCEPT, "1.0.0")
    assert code == 1 and codes(data) == ["VERSION_EXISTS"]


@pytest.mark.parametrize("option", ["--force", "--no-git"])
def test_force_and_no_git_are_gone(repo: Path, option: str):
    result = run(
        "bundle", "version", "--bundle", CONCEPT, "--version", "1.0.0", "--approved-by", APPROVER,
        option,
    )  # fmt: skip
    assert result.exit_code == 3
    assert "No such option" in result.output


# ------------------------------------------------------------------ the version commit


def test_the_version_commit_holds_the_whole_workspace_and_nothing_else(repo: Path):
    commit_all(repo, "scaffold")
    app = ws(repo)
    (app / "docs" / "GETTING_STARTED.md").unlink()
    (app / "intake.yaml").write_text('intake_version: "1.0"\nscs_version: 0.7.0\n')
    (app / "README.md").write_text("# app\n")
    (app / "dist").mkdir()
    (app / "dist" / "old.yaml").write_text("x: 1\n")
    (repo / "domain" / "README.md").write_text("unstaged\n")
    (repo / "domain" / "docs" / "GETTING_STARTED.md").write_text("staged\n")
    git(repo, "add", "domain/docs/GETTING_STARTED.md")

    code, data = version(CONCEPT, "1.0.0")
    assert code == 0, data
    commit = data["result"]["commit"]
    committed = {
        line.split("\t")[1]: line.split("\t")[0]
        for line in git(repo, "show", "--name-status", "--format=", commit).splitlines()
    }
    assert committed == {
        "projects/app/docs/GETTING_STARTED.md": "D",
        "projects/app/intake.yaml": "A",
        "projects/app/README.md": "M",
        "projects/app/bundles/concepts/prohibited-v1.0.0.yaml": "A",
        "projects/app/bundles/concepts/prohibited-v1.0.0-MANIFEST.yaml": "A",
    }
    entry = next(c for c in data["changes"] if c["action"] == "git-commit")
    assert {p["path"]: p["status"] for p in entry["paths"]} == committed
    assert git(repo, "diff", "--cached", "--name-only").split() == [
        "domain/docs/GETTING_STARTED.md"
    ]
    assert "domain/README.md" in git(repo, "diff", "--name-only")
    assert (app / "dist" / "old.yaml").is_file()


def test_an_ignored_digest_input_is_refused_and_sources_are_not_committed(repo: Path):
    gitignore = repo / ".gitignore"
    kept = gitignore.read_text()
    gitignore.write_text(kept + "projects/app/context/project/prohibited.yaml\n")
    code, data = version(CONCEPT, "1.0.0")
    assert code == 1
    assert codes(data) == ["VERSION_INPUT_UNTRACKED"]
    assert data["diagnostics"][0]["path"] == "projects/app/" + SCD

    gitignore.write_text(kept)
    (ws(repo) / "sources").mkdir()
    (ws(repo) / "sources" / "policy.txt").write_text("source document\n")
    code, data = version(CONCEPT, "1.0.0")
    assert code == 0, data
    assert "sources/" not in git(repo, "ls-tree", "-r", "--name-only", "HEAD")


def test_author_committer_and_annotated_tag_under_a_hostile_git_config(repo: Path):
    """conftest sets no identity, signing on, and failing hooks (D-55, D-58)."""
    code, data = version(CONCEPT, "1.0.0")
    assert code == 0, data
    fmt = "%an <%ae>|%cn <%ce>"
    assert git(repo, "log", "-1", f"--format={fmt}").strip() == f"{APPROVER}|{ENGINE}"
    assert git(repo, "cat-file", "-t", "app/prohibited-v1.0.0").strip() == "tag"
    tag = git(repo, "cat-file", "-p", "app/prohibited-v1.0.0")
    assert f"tagger {ENGINE}" in tag
    assert data["result"]["tag"] == "app/prohibited-v1.0.0"


def test_a_dry_run_writes_nothing_and_lists_the_commit(repo: Path):
    code, data = version(CONCEPT, "1.0.0", "--dry-run")
    assert code == 0, data
    assert tags(repo) == [] and not (ws(repo) / "bundles/concepts/prohibited-v1.0.0.yaml").exists()
    kinds = [c["action"] for c in data["changes"]]
    assert kinds == ["create", "create", "git-commit", "git-tag"]


# ------------------------------------------------------------------ rebuild and compile


def test_a_worktree_at_the_tag_rebuilds_the_same_artifact(repo: Path, tmp_path: Path, monkeypatch):
    release(repo)
    original = compile_(ROOT, "--version", "1.0.0", "--stdout")
    assert original.exit_code == 0, original.output
    tree = tmp_path / "rebuild"
    git(repo, "worktree", "add", "-q", "--detach", str(tree), "app/app-v1.0.0")
    monkeypatch.chdir(tree / "projects" / "app")
    rebuilt = compile_(ROOT, "--version", "1.0.0", "--stdout")
    assert rebuilt.exit_code == 0, rebuilt.output
    assert rebuilt.stdout == original.stdout
    artifact = yaml.safe_load(rebuilt.stdout)
    manifest = yaml.safe_load((ws(repo) / "bundles/app-v1.0.0-MANIFEST.yaml").read_text())
    assert artifact["source_digest"] == manifest["content_digest"]


def test_an_edit_after_versioning_does_not_enter_the_version(repo: Path):
    own_scd(repo)
    assert version(ROOT, "1.0.0")[0] == 0
    edit(ws(repo) / ROOT_SCD, "shared passwords", "shared passwords and sticky notes")
    assert validate(repo)[0] == 0
    assert validate(repo, "--verify-version", "app/app-v1.0.0")[0] == 0
    compiled = compile_(ROOT, "--version", "1.0.0", "--stdout")
    assert compiled.exit_code == 0, compiled.output
    assert "shared passwords." in compiled.stdout and "sticky notes" not in compiled.stdout


def test_a_draft_root_with_a_drifted_import_never_compiles(repo: Path):
    version(CONCEPT, "1.0.0")
    pin(repo, "1.0.0")
    edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
    for flags in (
        ["--allow-draft"],
        ["--allow-draft", "--no-validate"],
        ["--allow-draft", "--no-cites"],
    ):
        result = compile_(ROOT, *flags, "--json")
        assert result.exit_code == 1, (flags, result.output)
        assert "CONTENT_DIGEST_MISMATCH" in codes(json.loads(result.stdout))
    assert not (ws(repo) / "dist").exists()


def test_an_unpinned_import_resolves_to_the_working_file(repo: Path):
    version(CONCEPT, "1.0.0")
    edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
    result = compile_(ROOT, "--allow-draft", "--stdout")
    assert result.exit_code == 0, result.output
    assert "Prohibited: personal AI accounts and USB drives." in result.stdout
    assert "source_digest" not in result.stdout


# ------------------------------------------------------------------ the D-39 checks


def test_a_moved_tag_fails_check_1(repo: Path):
    own_scd(repo)
    assert version(ROOT, "1.0.0")[0] == 0
    edit(ws(repo) / ROOT_SCD, "shared passwords", "shared passwords and sticky notes")
    move_tag(repo, "app/app-v1.0.0", commit_all(repo))
    code, diagnostics = validate(repo, "--verify-version", "app/app-v1.0.0")
    assert code == 1 and "CONTENT_DIGEST_MISMATCH" in found(diagnostics)
    assert "CONTENT_DIGEST_MISMATCH" in found(validate(repo)[1])


def test_a_forged_import_manifest_fails_check_1(repo: Path):
    release(repo)
    manifest = ws(repo) / "bundles/concepts/prohibited-v1.0.0-MANIFEST.yaml"
    manifest.write_text(manifest.read_text() + "# forged\n")
    move_tag(repo, "app/app-v1.0.0", commit_all(repo))
    code, diagnostics = validate(repo, "--verify-version", "app/app-v1.0.0")
    assert code == 1
    assert any("differs from the one at app/prohibited-v1.0.0" in d["message"] for d in diagnostics)


def test_a_shallow_clone_cannot_be_checked(repo: Path, tmp_path: Path):
    release(repo)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", *PLAIN, "clone", "-q", "--depth", "1", f"file://{repo}", str(clone)], check=True
    )
    code, diagnostics = validate(clone)
    assert code == 1 and "GIT_HISTORY_INCOMPLETE" in found(diagnostics)


def test_a_deleted_tag_is_reported(repo: Path):
    release(repo)
    git(repo, "tag", "-d", "app/prohibited-v1.0.0")
    code, diagnostics = validate(repo)
    assert code == 1 and "VERSION_TAG_MISSING" in found(diagnostics)


def test_a_deleted_unpinned_concept_leaves_valid_history(repo: Path):
    version(CONCEPT, "1.0.0")
    own_scd(repo)
    for path in (CONCEPT, SCD, "bundles/concepts/prohibited-v1.0.0.yaml",
                 "bundles/concepts/prohibited-v1.0.0-MANIFEST.yaml"):  # fmt: skip
        (ws(repo) / path).unlink()
    commit_all(repo)
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics
    assert validate(repo, "--verify-version", "app/prohibited-v1.0.0")[0] == 0


@pytest.mark.parametrize("key", ["content_digest", "tools_version"])
def test_a_tagged_manifest_without_a_required_key_is_an_error(repo: Path, key: str):
    version(CONCEPT, "1.0.0")
    path = ws(repo) / "bundles/concepts/prohibited-v1.0.0-MANIFEST.yaml"
    manifest = yaml.safe_load(path.read_text())
    del manifest[key]
    path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    move_tag(repo, "app/prohibited-v1.0.0", commit_all(repo))
    code, diagnostics = validate(repo, "--verify-version", "app/prohibited-v1.0.0")
    assert code == 1 and "VERSION_MANIFEST_INCOMPLETE" in found(diagnostics)


def _digest_of_snapshot(path: Path) -> str:
    tree = resolve(path)
    assert tree.index is not None
    return content_digest(tree.root, tree.index).digest


@pytest.mark.parametrize("change", ["matching-digest", "deleted", "approver"])
def test_an_altered_working_manifest_is_reported(repo: Path, change: str):
    version(CONCEPT, "1.0.0")
    path = ws(repo) / "bundles/concepts/prohibited-v1.0.0-MANIFEST.yaml"
    manifest = yaml.safe_load(path.read_text())
    if change == "matching-digest":
        edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
        manifest["content_digest"] = _digest_of_snapshot(path.with_name("prohibited-v1.0.0.yaml"))
        path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    elif change == "deleted":
        path.unlink()
    else:
        manifest["approval"]["approved_by"] = "Someone Else <else@structuredcontext.dev>"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    code, diagnostics = validate(repo)
    assert code == 1 and "MANIFEST_ALTERED" in found(diagnostics)


def test_a_tag_without_its_manifest_is_reported(repo: Path):
    first = git(repo, "rev-list", "--max-parents=0", "HEAD").strip()
    git(repo, "tag", "-a", "-m", "stray", "app/prohibited-v2.0.0", first)
    code, diagnostics = validate(repo, "--verify-version", "app/prohibited-v2.0.0")
    assert code == 1 and "VERSION_MANIFEST_MISSING" in found(diagnostics)
    assert "VERSION_MANIFEST_MISSING" in found(validate(repo)[1])


def test_reversioning_bottom_up_restores_a_valid_repository(repo: Path):
    release(repo)
    edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
    assert validate(repo)[0] == 1
    release(repo, "1.0.1", "1.1.0")
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics
    assert validate(repo, "--verify-version", "app/app-v1.0.0")[0] == 0


def test_the_drift_diagnostic_names_the_files_and_the_order(repo: Path):
    release(repo)
    edit(ws(repo) / SCD, "personal AI accounts", "personal AI accounts and USB drives")
    code, diagnostics = validate(repo)
    assert code == 1
    message = next(d["message"] for d in diagnostics if d["code"] == "CONTENT_DIGEST_MISMATCH")
    assert "context/project/prohibited.yaml" in message
    assert "bottom-up, re-pinning each in the next: bundle:prohibited, then bundle:app" in message


# ------------------------------------------------------------------ D-70, D-71, reserved, D-54


def test_empty_scds_are_info_and_listed_by_a_dry_run(repo: Path):
    edit(ws(repo) / SCD, "personal AI accounts", "")
    path = ws(repo) / SCD
    text = path.read_text()
    start = text.index("  prohibitions:\n")
    end = text.index('subject: ""\n') + len('subject: ""\n')
    path.write_text(text[:start] + "  prohibitions: []\n" + text[end:])
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics
    empty = {d.get("path") for d in diagnostics if d["code"] == "SCD_EMPTY"}
    assert empty == {"domain/context/project/prohibited.yaml", "projects/app/" + SCD}
    assert all(d["severity"] == "info" for d in diagnostics if d["code"] == "SCD_EMPTY")
    code, data = version(CONCEPT, "1.0.0", "--dry-run")
    assert code == 0, data
    assert data["result"]["empty_scds"] == ["scd:project:prohibited"]
    registry = yaml.safe_load((SCHEMA / "diagnostics" / "codes.yaml").read_text())["codes"]
    assert "COMPLETENESS_STUB_SCD" not in registry


@pytest.mark.parametrize(
    "created_by, placeholder",
    [
        ("CI <ci@example.com>", True),
        ("scs-maintainers", False),
        ("Tim McCrimmon", False),
        ("security-team@medtech.com", False),
    ],
)
def test_placeholder_provenance(repo: Path, created_by: str, placeholder: bool):
    path = ws(repo) / SCD
    edit(
        path,
        'created_by: "Test Author <test@structuredcontext.dev>"',
        f'created_by: "{created_by}"',
    )
    diagnostics = validate(repo)[1]
    assert ("PROVENANCE_PLACEHOLDER" in found(diagnostics)) is placeholder
    head = git(repo, "rev-parse", "HEAD")
    code, data = version(CONCEPT, "1.0.0")
    if placeholder:
        assert code == 1 and "VERSION_PROVENANCE_PLACEHOLDER" in codes(data)
        assert git(repo, "rev-parse", "HEAD") == head and tags(repo) == []
        assert not (ws(repo) / "bundles/concepts/prohibited-v1.0.0.yaml").exists()
    else:
        assert "VERSION_PROVENANCE_PLACEHOLDER" not in codes(data)


@pytest.mark.parametrize("reserved", ["plan", "test-plan", "qa"])
def test_reserved_directories_are_ignored(repo: Path, reserved: str):
    directory = ws(repo) / reserved
    directory.mkdir()
    (directory / "broken.yaml").write_text("id: scd:project:prohibited\ntype: [not valid\n")
    (directory / "bundle.yaml").write_text("id: bundle:prohibited\ntype: concept\nversion: 9.9.9\n")
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics
    assert not any(reserved + "/" in (d.get("path") or "") for d in diagnostics)
    result = compile_(ROOT, "--allow-draft", "--stdout")
    assert result.exit_code == 0, result.output


def test_a_06_repository_passes_after_versioning_once_under_07(repo: Path):
    """D-54: unqualified tags and VERSION-* manifests without a content digest are history."""
    app = ws(repo)
    edit(app / CONCEPT, 'version: "DRAFT"', 'version: "1.0.0"')
    pin(repo, "1.0.0")
    root = yaml.safe_load((app / ROOT).read_text())
    root["version"] = "1.0.0"
    (app / "bundles/project-bundle-v1.0.0.yaml").write_text(yaml.safe_dump(root, sort_keys=False))
    (app / "bundles/VERSION-1.0.0-MANIFEST.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1.0.0",
                "status": "validated",
                "bundle": {"id": "bundle:app", "file": "project-bundle-v1.0.0.yaml"},
                "approval": {"approved_by": APPROVER},
            }
        )
    )
    git(repo, "tag", "-a", "-m", "0.6", "v1.0.0", commit_all(repo, "0.6 release"))

    code, data = version(ROOT, "1.1.0")
    assert code == 1 and "VERSION_TAG_MISSING" in codes(data)
    edit(app / CONCEPT, 'version: "1.0.0"', 'version: "DRAFT"')
    release(repo, "1.0.1", "1.1.0")
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics
