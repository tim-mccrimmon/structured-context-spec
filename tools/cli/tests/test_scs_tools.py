"""Regression suite for the ``scs`` (scs-tools) CLI.

Baseline captured 2026-09-24 against the 0.5-dev branch. Covers scaffolding (ISS-005b), the
validate pass-through (ISS-026) and bundle versioning (ISS-005b, ISS-027).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from scs_validator.commands.validate import validate as validator_cmd

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"

ONTOLOGIES = ["sdlc", "cdmo", "mca", "personal"]
CONCEPTS = {
    "architecture",
    "business-context",
    "compliance-governance",
    "data-provenance",
    "deployment-operations",
    "ethics-ai-accountability",
    "performance-reliability",
    "safety-risk",
    "security",
    "testing-validation",
    "usability-accessibility",
}


NEW_OPTIONS = ["--author", "Test Author", "--email", "test@example.com", "--no-interactive"]


def new_workspace(tmp_path: Path, kind: str = "project", name: str = "demo", *options: str) -> Path:
    """A workspace made by `scs new`, in a Domain repository (0.7). `new domain NAME` creates
    `NAME-context/` and returns its `domain/`; `new project NAME` adds `projects/NAME/` to the
    repository `acme-context/`, creating that first if need be."""
    if kind == "domain":
        args = ["new", "domain", name, "--dir", str(tmp_path), *options, *NEW_OPTIONS]
        result = CliRunner().invoke(cli, args)
        assert result.exit_code == 0, result.output
        return tmp_path / f"{name}-context" / "domain"
    repo = tmp_path / "acme-context"
    if not repo.exists():
        new_workspace(tmp_path, "domain", "acme")
    args = ["new", "project", name, "--dir", str(repo), *options, *NEW_OPTIONS]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    return repo / "projects" / name


def scaffold(tmp_path: Path, kind: str = "project", ontology: str = "sdlc") -> Path:
    return new_workspace(tmp_path, kind, "demo", "--ontology", ontology)


def validate_with_validator(*args: str):
    return CliRunner().invoke(
        validator_cmd, list(args) + ["--no-color", "--schema-dir", str(SCHEMA)]
    )


@pytest.fixture(scope="module")
def healthcare_project(tmp_path_factory) -> Path:
    return scaffold(tmp_path_factory.mktemp("proj"))


# ---------------------------------------------------------------------------- scaffold


def test_scaffold_creates_the_expected_structure(tmp_path: Path):
    root = scaffold(tmp_path)
    for rel in [
        "bundles/project-bundle.yaml",
        ".scs/config",
        "README.md",
        "docs/GETTING_STARTED.md",
    ]:
        assert (root / rel).is_file(), rel
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert generated == CONCEPTS
    # The full template set (D-64): nothing is left out by project type
    scds = {p.stem for p in (root / "context" / "project").glob("*.yaml")}
    assert {"hipaa-compliance", "chai-adherence", "tefca-participation"} <= scds
    # 0.6.0: no meta, standards, or domain bundles in a Project workspace
    assert sorted(p.name for p in (root / "bundles").iterdir()) == [
        "concepts",
        "project-bundle.yaml",
    ]


@pytest.mark.parametrize("kind", ["domain", "project"])
def test_scaffold_uses_concept_terminology_and_starts_as_draft(tmp_path: Path, kind: str):
    root = scaffold(tmp_path, kind)
    for path in (root / "bundles").rglob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        assert data["type"] != "concern", path
        assert data["version"] == "DRAFT", path
    concept = yaml.safe_load((root / "bundles" / "concepts" / "security.yaml").read_text())
    assert concept["type"] == "concept"


@pytest.mark.parametrize("kind", ["domain", "project"])
@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_every_scaffolded_bundle_validates(tmp_path: Path, ontology: str, kind: str):
    root = scaffold(tmp_path, kind, ontology)
    for path in sorted((root / "bundles").rglob("*.yaml")):
        result = validate_with_validator("--bundle", str(path))
        assert result.exit_code == 0, f"{path.relative_to(root)}\n{result.output}"


@pytest.mark.parametrize("kind", ["domain", "project"])
@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_every_scaffolded_scd_validates(tmp_path: Path, ontology: str, kind: str):
    root = scaffold(tmp_path, kind, ontology)
    for path in sorted((root / "context" / "project").glob("*.yaml")):
        result = validate_with_validator(str(path))
        assert result.exit_code == 0, f"{path.name}\n{result.output}"


# ------------------------------------------------------------ validate pass-through (ISS-026)


def test_scs_validate_reports_a_valid_bundle(healthcare_project: Path, monkeypatch):
    monkeypatch.chdir(healthcare_project)
    result = CliRunner().invoke(
        cli, ["validate", "--bundle", "bundles/project-bundle.yaml", "--schema-dir", str(SCHEMA)]
    )
    assert "not installed" not in result.output
    assert result.exit_code == 0, result.output
    assert "VALID" in result.output


def test_scs_validate_fails_an_invalid_scd(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("id: not-an-scd\n")
    result = CliRunner().invoke(cli, ["validate", str(bad), "--schema-dir", str(SCHEMA)])
    assert "not installed" not in result.output
    assert result.exit_code == 1, result.output


def test_scs_validate_supports_the_0_5_0_domain_and_checkpoint_modes(tmp_path: Path):
    domain = REPO / "schema" / "domain" / "examples" / "software-development-domain.yaml"
    result = CliRunner().invoke(
        cli, ["validate", "--domain", str(domain), "--schema-dir", str(SCHEMA)]
    )
    assert result.exit_code == 0, result.output


def test_scs_bundle_validate_shortcut(healthcare_project: Path, monkeypatch):
    monkeypatch.chdir(healthcare_project)
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = CliRunner().invoke(cli, ["bundle", "validate"])
    assert "not installed" not in result.output
    assert result.exit_code == 0, result.output


# ------------------------------------------------------------------- versioning (ISS-027)


def _version_security_bundle(project: Path, monkeypatch, *extra: str):
    monkeypatch.chdir(project)
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    return CliRunner().invoke(
        cli,
        [
            "bundle",
            "version",
            "--bundle",
            "bundles/concepts/security.yaml",
            "--version",
            "0.1.0",
            "--approved-by",
            "sam@example.com",
            "--notes",
            "First approved cut",
            "--no-git",
            *extra,
        ],
    )


def test_bundle_version_runs_with_validation_enabled(tmp_path: Path, monkeypatch):
    """ISS-026: versioning must not depend on the (previously broken) `scs validate` command."""
    project = scaffold(tmp_path)
    result = _version_security_bundle(project, monkeypatch)
    assert result.exit_code == 0, result.output
    assert (project / "bundles/concepts/security-v0.1.0.yaml").is_file()


def test_versioned_snapshot_carries_the_version_and_approval(tmp_path: Path, monkeypatch):
    """ISS-027: the snapshot must say 0.1.0 inside, not DRAFT, and record the approval."""
    project = scaffold(tmp_path)
    result = _version_security_bundle(project, monkeypatch, "--no-validate")
    assert result.exit_code == 0, result.output
    snap = yaml.safe_load((project / "bundles/concepts/security-v0.1.0.yaml").read_text())
    assert snap["version"] == "0.1.0"
    prov = snap["provenance"]
    assert prov["version_approved_by"] == "sam@example.com"
    assert prov["version_approved_at"]
    # original working bundle is left untouched
    original = yaml.safe_load((project / "bundles/concepts/security.yaml").read_text())
    assert original["version"] == "DRAFT"
    assert "version_approved_by" not in original["provenance"]


@pytest.mark.parametrize(
    "extra, passed, status", [((), True, "validated"), (("--no-validate",), False, "approved")]
)
def test_versioning_records_what_validation_actually_did(
    tmp_path: Path, monkeypatch, extra, passed, status
):
    """ISS-045: `validation_passed` and `approval_status` record the run, not a default."""
    project = scaffold(tmp_path)
    assert _version_security_bundle(project, monkeypatch, *extra).exit_code == 0
    prov = yaml.safe_load((project / "bundles/concepts/security-v0.1.0.yaml").read_text())[
        "provenance"
    ]
    assert prov["validation_passed"] is passed
    assert prov["approval_status"] == status
    manifest = yaml.safe_load(
        (project / "bundles/concepts/security-v0.1.0-MANIFEST.yaml").read_text()
    )
    assert manifest["status"] == status
    assert ("validation" in manifest) is passed


def test_versioned_snapshot_validates(tmp_path: Path, monkeypatch):
    project = scaffold(tmp_path)
    assert _version_security_bundle(project, monkeypatch).exit_code == 0
    snapshot = project / "bundles/concepts/security-v0.1.0.yaml"
    result = validate_with_validator("--bundle", str(snapshot))
    assert result.exit_code == 0, result.output
    assert yaml.safe_load(snapshot.read_text())["version"] == "0.1.0"


def test_a_versioned_snapshot_without_approval_fields_is_rejected(tmp_path: Path, monkeypatch):
    """The DRAFT exemption must not apply once the snapshot carries a real version."""
    project = scaffold(tmp_path)
    assert _version_security_bundle(project, monkeypatch).exit_code == 0
    snapshot = project / "bundles/concepts/security-v0.1.0.yaml"
    data = yaml.safe_load(snapshot.read_text())
    del data["provenance"]["version_approved_by"]
    del data["provenance"]["version_approved_at"]
    stripped = project / "bundles/concepts/stripped.yaml"
    stripped.write_text(yaml.safe_dump(data, sort_keys=False))
    assert validate_with_validator("--bundle", str(stripped)).exit_code == 1


def test_manifest_checksum_matches_the_snapshot(tmp_path: Path, monkeypatch):
    import hashlib

    project = scaffold(tmp_path)
    assert _version_security_bundle(project, monkeypatch, "--no-validate").exit_code == 0
    snapshot = project / "bundles/concepts/security-v0.1.0.yaml"
    manifest = yaml.safe_load(
        (project / "bundles/concepts/security-v0.1.0-MANIFEST.yaml").read_text()
    )
    assert manifest["bundle"]["sha256"] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
    assert manifest["approval"]["approved_by"] == "sam@example.com"


def test_versioning_refuses_to_overwrite_without_force(tmp_path: Path, monkeypatch):
    project = scaffold(tmp_path)
    assert _version_security_bundle(project, monkeypatch, "--no-validate").exit_code == 0
    again = _version_security_bundle(project, monkeypatch, "--no-validate")
    assert again.exit_code != 0
    assert "already exists" in again.output


def test_scs_version_matches_the_package_version():
    """ISS-042: `scs --version` must not drift from the package metadata."""
    from importlib.metadata import version as pkg_version

    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == f"scs, version {pkg_version('scs-tools')}"


def _version(project: Path, monkeypatch, bundle: str, *extra: str, input=None):
    monkeypatch.chdir(project)
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    return CliRunner().invoke(
        cli,
        ["bundle", "version", "--bundle", bundle, "--version", "1.0.0", "--notes", "n", *extra],
        input=input,
    )


def test_concept_bundles_at_the_same_version_keep_their_own_manifests(tmp_path: Path, monkeypatch):
    """ISS-043: every concept bundle versioned at 1.0.0 used to write the same manifest."""
    project = scaffold(tmp_path)
    for name in ("security", "architecture"):
        result = _version(
            project,
            monkeypatch,
            f"bundles/concepts/{name}.yaml",
            "--approved-by",
            "sam@example.com",
            "--no-git",
            "--no-validate",
        )
        assert result.exit_code == 0, result.output
    for name in ("security", "architecture"):
        manifest = yaml.safe_load(
            (project / f"bundles/concepts/{name}-v1.0.0-MANIFEST.yaml").read_text()
        )
        assert manifest["bundle"]["id"] == f"bundle:{name}"
        assert manifest["bundle"]["file"] == f"{name}-v1.0.0.yaml"
        assert "tag" not in manifest["distribution"]
        assert "repository" not in manifest["distribution"]
    assert not list((project / "bundles/concepts").glob("VERSION-*"))


def test_concept_bundles_at_the_same_version_get_their_own_tags(tmp_path: Path, monkeypatch):
    """ISS-043: git tags are name-qualified, so the second bundle doesn't collide."""
    import subprocess

    project = scaffold(tmp_path)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for var in ("GIT_AUTHOR", "GIT_COMMITTER"):
        monkeypatch.setenv(f"{var}_NAME", "Test")
        monkeypatch.setenv(f"{var}_EMAIL", "git@example.com")
    subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
    for name in ("security", "architecture"):
        result = _version(
            project,
            monkeypatch,
            f"bundles/concepts/{name}.yaml",
            "--approved-by",
            "sam@example.com",
            "--no-validate",
        )
        assert result.exit_code == 0, result.output
    tags = subprocess.check_output(["git", "tag"], cwd=project, text=True).split()
    assert sorted(tags) == ["architecture-v1.0.0", "security-v1.0.0"]
    manifest = yaml.safe_load(
        (project / "bundles/concepts/security-v1.0.0-MANIFEST.yaml").read_text()
    )
    assert manifest["distribution"]["tag"] == "security-v1.0.0"
    assert manifest["distribution"]["repository"] == project.name
    assert manifest["distribution"]["branch"] == "main"

    again = _version(
        project,
        monkeypatch,
        "bundles/concepts/security.yaml",
        "--approved-by",
        "sam@example.com",
        "--no-validate",
        "--force",
    )
    assert again.exit_code != 0
    assert "tag already exists: security-v1.0.0" in again.output


def test_the_approver_is_never_taken_from_git_config(tmp_path: Path, monkeypatch):
    """ISS-047: without --approved-by the user is asked; git config user.email is not used."""
    project = scaffold(tmp_path)
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text("[user]\n\temail = git@example.com\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(gitconfig))
    result = _version(
        project,
        monkeypatch,
        "bundles/concepts/security.yaml",
        "--no-git",
        "--no-validate",
        input="jane@example.com\n",
    )
    assert result.exit_code == 0, result.output
    assert "Approver email" in result.output
    manifest = yaml.safe_load(
        (project / "bundles/concepts/security-v1.0.0-MANIFEST.yaml").read_text()
    )
    assert manifest["approval"]["approved_by"] == "jane@example.com"


@pytest.mark.parametrize("approver", [None, "", "   "])
def test_versioning_without_an_approver_fails(tmp_path: Path, monkeypatch, approver):
    """ISS-047: no approver (no input, or a blank one) means no version."""
    project = scaffold(tmp_path)
    extra = () if approver is None else ("--approved-by", approver)
    result = _version(
        project,
        monkeypatch,
        "bundles/concepts/security.yaml",
        "--no-git",
        "--no-validate",
        *extra,
    )
    assert result.exit_code != 0
    assert not (project / "bundles/concepts/security-v1.0.0.yaml").exists()


# ------------------------------------- root bundle imports (ISS-033, SCS 0.6.0 layout)


@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_project_bundle_imports_exactly_the_concept_bundles_generated(
    tmp_path: Path, ontology: str
):
    root = scaffold(tmp_path, "project", ontology)
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    project = yaml.safe_load((root / "bundles/project-bundle.yaml").read_text())
    assert project["type"] == "project" and project["id"] == "bundle:demo"
    imported = {ref.split(":")[1] for ref in project["imports"]}
    assert imported == generated


@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_new_domain_scaffolds_a_domain_bundle_importing_meta_and_concepts(
    tmp_path: Path, ontology: str
):
    root = scaffold(tmp_path, "domain", ontology)
    assert sorted(p.name for p in (root / "bundles").iterdir()) == [
        "concepts",
        "domain-bundle.yaml",
    ]
    domain = yaml.safe_load((root / "bundles/domain-bundle.yaml").read_text())
    assert domain["type"] == "domain" and domain["id"] == "bundle:demo"
    assert domain["scds"] == []
    assert domain["imports"][0] == "bundle:meta:0.6.0"
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert {ref.split(":")[1] for ref in domain["imports"][1:]} == generated
    assert "bundle_type: domain" in (root / ".scs" / "config").read_text()


def test_new_domain_workspace_validates(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    result = validate_with_validator("--bundle", str(root / "bundles/domain-bundle.yaml"))
    assert result.exit_code == 0, result.output


def test_bundle_validate_shortcut_finds_the_domain_bundle(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path, "domain")
    monkeypatch.chdir(root)
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    # No project-bundle.yaml here: before 0.6.0 the shortcut aborted
    result = CliRunner().invoke(cli, ["bundle", "validate"])
    assert result.exit_code == 0, result.output
    assert "VALID" in result.output


def test_scaffolded_skeletons_do_not_compile_until_directives_are_written(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    result = CliRunner().invoke(
        cli,
        [
            "compile",
            str(root / "bundles/domain-bundle.yaml"),
            "--allow-draft",
            "--no-validate",
            "--stdout",
        ],
    )
    # The packaged meta bundle contributes directives; the skeleton SCDs do not.
    assert result.exit_code == 0, result.output
    assert "demo/governance-context/M-001" in result.stdout
    assert "has no directives" in result.output


def test_add_bundle_rejects_a_domain_name_with_a_hint(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path)
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["add", "bundle", "software-development"])
    assert result.exit_code != 0
    assert "scs new domain" in result.output
    assert not (root / "bundles" / "domains").exists()


# ------------------------------------ concept bundles in add / list / info (ISS-034)


def _init_bare_project(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "existing"
    root.mkdir()
    monkeypatch.chdir(root)
    result = CliRunner().invoke(
        cli, ["init", "--type", "minimal", "--author", "T", "--email", "t@e.com"]
    )
    assert result.exit_code == 0, result.output
    return root


def test_add_bundle_adds_a_concept_bundle(tmp_path: Path, monkeypatch):
    root = _init_bare_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli, ["add", "bundle", "security"])
    assert result.exit_code == 0, result.output
    target = root / "bundles" / "concepts" / "security.yaml"
    assert target.is_file()
    data = yaml.safe_load(target.read_text())
    assert data["type"] == "concept" and data["id"] == "bundle:security"
    assert validate_with_validator("--bundle", str(target)).exit_code == 0


def test_add_bundle_rejects_an_unknown_name_cleanly(tmp_path: Path, monkeypatch):
    _init_bare_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli, ["add", "bundle", "no-such-bundle"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_bundle_list_shows_the_projects_concept_bundles(healthcare_project: Path, monkeypatch):
    monkeypatch.chdir(healthcare_project)
    result = CliRunner().invoke(cli, ["bundle", "list"])
    assert result.exit_code == 0, result.output
    assert "Concept bundles" in result.output
    for concept in CONCEPTS:
        assert f"{concept}.yaml" in result.output
    assert "Domain: unknown" not in result.output


def test_bundle_list_available_names_concepts_as_concept_bundles(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["bundle", "list", "--available"])
    assert result.exit_code == 0, result.output
    assert "Available concept bundles" in result.output
    assert "scs new domain" in result.output


def test_bundle_info_finds_a_project_concept_bundle(healthcare_project: Path, monkeypatch):
    monkeypatch.chdir(healthcare_project)
    result = CliRunner().invoke(cli, ["bundle", "info", "security"])
    assert result.exit_code == 0, result.output
    assert "ID: bundle:security" in result.output
    assert "Type: concept" in result.output


def test_bundle_info_falls_back_to_the_template_outside_a_project(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["bundle", "info", "security"])
    assert result.exit_code == 0, result.output
    assert "template bundle" in result.output.lower()


def test_add_scd_adds_a_template_scd_that_validates(tmp_path: Path, monkeypatch):
    root = _init_bare_project(tmp_path, monkeypatch)
    for name in ["system-context", "risk-assessment", "threat-model"]:
        result = CliRunner().invoke(cli, ["add", "scd", name, "--author", "Tim"])
        assert result.exit_code == 0, result.output
        assert (
            validate_with_validator(str(root / "context" / "project" / f"{name}.yaml")).exit_code
            == 0
        )


# ------------------------------------------- Domain Ontology manifest in the scaffold (ISS-029)

SDLC_ONTOLOGY_EXAMPLE = REPO / "schema" / "domain" / "examples" / "software-development-domain.yaml"
MANIFEST = "ontology/domain-manifest.yaml"


def _manifest_concepts(root: Path) -> list[dict]:
    return yaml.safe_load((root / MANIFEST).read_text())["domain"]["ontology"]["concepts"]


@pytest.mark.parametrize("kind", ["domain", "project"])
@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_scaffold_generates_a_valid_domain_ontology_manifest(
    tmp_path: Path, ontology: str, kind: str
):
    root = scaffold(tmp_path, kind, ontology)
    assert (root / MANIFEST).is_file()
    result = validate_with_validator("--domain", str(root / MANIFEST))
    assert result.exit_code == 0, result.output
    assert "0 errors" in result.output and "0 warnings" in result.output


@pytest.mark.parametrize("kind", ["domain", "project"])
@pytest.mark.parametrize("ontology", ONTOLOGIES)
def test_manifest_ontology_lists_exactly_the_generated_concepts(
    tmp_path: Path, ontology: str, kind: str
):
    root = scaffold(tmp_path, kind, ontology)
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert {c["id"] for c in _manifest_concepts(root)} == {f"concept:{g}" for g in generated}


def test_manifest_uses_the_reference_sdlc_ontology_wording(tmp_path: Path):
    """Drift guard: names and descriptions come from the shipped SDLC reference ontology."""
    if not SDLC_ONTOLOGY_EXAMPLE.is_file():
        pytest.skip("reference ontology example not available")
    reference = {
        c["id"]: (c["name"], c.get("description"))
        for c in yaml.safe_load(SDLC_ONTOLOGY_EXAMPLE.read_text())["domain"]["ontology"]["concepts"]
    }
    root = scaffold(tmp_path)
    scaffolded = {c["id"]: (c["name"], c.get("description")) for c in _manifest_concepts(root)}
    assert scaffolded == reference


def test_manifest_declares_the_software_development_domain(tmp_path: Path):
    root = scaffold(tmp_path)
    domain = yaml.safe_load((root / MANIFEST).read_text())["domain"]
    assert domain["id"] == "domain:software-development"
    assert domain["version"] == "0.1.0"
    assert "concerns" not in domain


def test_getting_started_points_at_the_ontology_manifest(tmp_path: Path):
    root = scaffold(tmp_path)
    assert MANIFEST in (root / "docs" / "GETTING_STARTED.md").read_text()


def test_add_bundle_reminds_you_to_add_the_concept_to_the_manifest(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path)
    # Remove the concept the way a user pruning the scaffold would: bundle and manifest entry
    (root / "bundles" / "concepts" / "compliance-governance.yaml").unlink()
    manifest = yaml.safe_load((root / MANIFEST).read_text())
    concepts = manifest["domain"]["ontology"]["concepts"]
    concepts[:] = [c for c in concepts if c["id"] != "concept:compliance-governance"]
    (root / MANIFEST).write_text(yaml.safe_dump(manifest))
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["add", "bundle", "compliance-governance"])
    assert result.exit_code == 0, result.output
    assert MANIFEST in result.output
    assert "concept:compliance-governance" in result.output


def test_add_bundle_is_quiet_when_the_manifest_already_has_the_concept(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path)
    (root / "bundles" / "concepts" / "security.yaml").unlink()
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["add", "bundle", "security"])
    assert result.exit_code == 0, result.output
    assert MANIFEST not in result.output


def test_add_bundle_without_a_manifest_says_nothing_about_it(tmp_path: Path, monkeypatch):
    _init_bare_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli, ["add", "bundle", "security"])
    assert result.exit_code == 0, result.output
    assert "domain-manifest" not in result.output


@pytest.mark.parametrize("concept", sorted(CONCEPTS))
def test_add_bundle_works_for_every_concept(tmp_path: Path, monkeypatch, concept: str):
    """ISS-037: compliance-governance crashed ('config' is undefined) under `add bundle`."""
    root = _init_bare_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli, ["add", "bundle", concept])
    assert result.exit_code == 0, result.output
    target = root / "bundles" / "concepts" / f"{concept}.yaml"
    assert validate_with_validator("--bundle", str(target)).exit_code == 0


def test_add_bundle_lists_the_full_set_unless_a_0_6_project_type_applies(
    tmp_path: Path, monkeypatch
):
    """A 0.7 workspace gets the full compliance bundle (D-64); a 0.6 workspace made with
    `scs init --type standard` still leaves the HIPAA SCDs out."""
    root = scaffold(tmp_path)
    (root / "bundles" / "concepts" / "compliance-governance.yaml").unlink()
    monkeypatch.chdir(root)
    assert CliRunner().invoke(cli, ["add", "bundle", "compliance-governance"]).exit_code == 0
    text = (root / "bundles" / "concepts" / "compliance-governance.yaml").read_text()
    assert "hipaa-compliance" in text

    legacy = tmp_path / "legacy"
    legacy.mkdir()
    monkeypatch.chdir(legacy)
    args = ["init", "--type", "standard", "--author", "T", "--email", "t@e.com"]
    assert CliRunner().invoke(cli, args).exit_code == 0
    assert CliRunner().invoke(cli, ["add", "bundle", "compliance-governance"]).exit_code == 0
    text = (legacy / "bundles" / "concepts" / "compliance-governance.yaml").read_text()
    assert "hipaa-compliance" not in text


# ------------------------------------------------------ --ontology mca (ISS-029)

MCA_ONTOLOGY_EXAMPLE = REPO / "schema" / "domain" / "examples" / "merchant-cash-advance-domain.yaml"
MCA_CONCEPTS = {
    "origination",
    "underwriting-decisioning",
    "contract-characterization",
    "disclosure-compliance",
    "security-interest-management",
    "servicing-collections",
    "capital-funding",
    "portfolio-risk-management",
    "broker-partner-management",
    "data-provenance",
    "data-security",
    "systems-integration",
    "governance",
    "ai-accountability",
    "training-competency",
    "adoption-rollout",
}


def scaffold_mca(tmp_path: Path) -> Path:
    return new_workspace(tmp_path, "project", "demo", "--ontology", "mca")


def test_mca_scaffold_generates_exactly_the_16_mca_concepts(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert generated == MCA_CONCEPTS


@pytest.mark.parametrize("option", [["--type", "minimal"], ["--profile", "personal"]])
def test_new_has_no_type_or_profile(tmp_path: Path, option: list):
    """Templates depend on the ontology and the workspace kind only (D-61, D-64)."""
    result = CliRunner().invoke(cli, ["new", "domain", "x", "--dir", str(tmp_path), *option])
    assert result.exit_code == 3
    assert not (tmp_path / "x-context").exists()


def test_mca_project_bundle_imports_exactly_the_16_concepts(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    project = yaml.safe_load((root / "bundles/project-bundle.yaml").read_text())
    imported = {ref.split(":")[1] for ref in project["imports"]}
    assert imported == MCA_CONCEPTS


def test_mca_every_scaffolded_bundle_validates(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    for path in [root / "bundles" / "project-bundle.yaml"] + list(
        (root / "bundles" / "concepts").glob("*.yaml")
    ):
        result = validate_with_validator("--bundle", str(path))
        assert result.exit_code == 0, f"{path}: {result.output}"


def test_mca_every_scaffolded_scd_validates(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    for path in (root / "context" / "project").glob("*.yaml"):
        result = validate_with_validator(str(path))
        assert result.exit_code == 0, f"{path}: {result.output}"


def test_mca_manifest_is_valid_and_has_relationships(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    result = validate_with_validator("--domain", str(root / MANIFEST))
    assert result.exit_code == 0, result.output
    assert "0 errors" in result.output and "0 warnings" in result.output
    concepts = _manifest_concepts(root)
    with_rels = [c for c in concepts if c.get("relationships")]
    assert len(with_rels) > 0, "expected at least one mca concept to carry relationships"


def test_mca_manifest_declares_the_mca_domain(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    domain = yaml.safe_load((root / MANIFEST).read_text())["domain"]
    assert domain["id"] == "domain:merchant-cash-advance"
    assert "concerns" not in domain


def test_mca_reference_data_matches_the_shipped_ontology_example():
    """Drift guard: MCA_CONCEPTS/MCA_CONCEPT_INFO/MCA_CONCEPT_RELATIONSHIPS in
    project_types.py must match schema/domain/examples/merchant-cash-advance-domain.yaml
    exactly - see the note in that module."""
    if not MCA_ONTOLOGY_EXAMPLE.is_file():
        pytest.skip("reference ontology example not available")
    from scs_tools.utils.project_types import (
        MCA_CONCEPT_INFO,
        MCA_CONCEPT_RELATIONSHIPS,
    )
    from scs_tools.utils.project_types import (
        MCA_CONCEPTS as MODULE_MCA_CONCEPTS,
    )

    reference = yaml.safe_load(MCA_ONTOLOGY_EXAMPLE.read_text())["domain"]["ontology"]["concepts"]
    reference_ids = [c["id"].split(":", 1)[1] for c in reference]

    assert MODULE_MCA_CONCEPTS == reference_ids, "concept id list/order drifted from the example"

    for c in reference:
        cid = c["id"].split(":", 1)[1]
        assert MCA_CONCEPT_INFO[cid] == (c["name"], c["description"].strip())
        assert MCA_CONCEPT_RELATIONSHIPS.get(cid, []) == c.get("relationships", [])


def test_mca_scd_config_records_the_ontology_model(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    config = (root / ".scs" / "config").read_text()
    assert "ontology: mca" in config
    assert "scs_version: 0.7.0" in config  # the spec version (D-06)
    assert "tools_version: " in config


def test_sdlc_scaffold_still_records_sdlc_as_the_ontology_model(tmp_path: Path):
    root = scaffold(tmp_path)
    assert "ontology: sdlc" in (root / ".scs" / "config").read_text()


def test_add_bundle_and_add_scd_work_inside_an_mca_project(tmp_path: Path, monkeypatch):
    root = scaffold_mca(tmp_path)
    (root / "bundles" / "concepts" / "governance.yaml").unlink()
    (root / "context" / "project" / "governance.yaml").unlink()
    monkeypatch.chdir(root)

    result = CliRunner().invoke(cli, ["add", "bundle", "governance"])
    assert result.exit_code == 0, result.output
    target = root / "bundles" / "concepts" / "governance.yaml"
    assert validate_with_validator("--bundle", str(target)).exit_code == 0

    result = CliRunner().invoke(cli, ["add", "scd", "governance"])
    assert result.exit_code == 0, result.output
    scd_target = root / "context" / "project" / "governance.yaml"
    assert validate_with_validator(str(scd_target)).exit_code == 0


def test_add_bundle_without_ontology_model_in_config_defaults_to_sdlc(tmp_path: Path, monkeypatch):
    """A project scaffolded before --ontology existed has no ontology_model line at all -
    add/bundle commands must still default correctly to sdlc, not error."""
    root = _init_bare_project(tmp_path, monkeypatch)
    config_file = root / ".scs" / "config"
    lines = [
        line
        for line in config_file.read_text().splitlines()
        if not line.startswith("ontology_model")
    ]
    config_file.write_text("\n".join(lines) + "\n")

    result = CliRunner().invoke(cli, ["add", "bundle", "security"])
    assert result.exit_code == 0, result.output
    assert (root / "bundles" / "concepts" / "security.yaml").is_file()


def test_bundle_list_available_shows_both_ontology_models(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["bundle", "list", "--available"])
    assert result.exit_code == 0, result.output
    assert "ontology model 'sdlc'" in result.output
    assert "ontology model 'mca'" in result.output
    assert "governance" in result.output  # an mca-only concept name


def test_bundle_info_finds_an_mca_concept_in_project(tmp_path: Path, monkeypatch):
    root = scaffold_mca(tmp_path)
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["bundle", "info", "governance"])
    assert result.exit_code == 0, result.output
    assert "ID: bundle:governance" in result.output


def test_bundle_info_falls_back_to_the_mca_template_outside_a_project(tmp_path: Path, monkeypatch):
    """governance only exists as an mca concept - the template fallback must search across
    ontology models, not just sdlc's."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["bundle", "info", "governance"])
    assert result.exit_code == 0, result.output
    assert "template bundle" in result.output.lower()
    assert "ID: bundle:governance" in result.output


# --------------------------------------------- company facts and prohibitions (Domain only)


def test_new_domain_adds_company_and_prohibited_concepts(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    domain = yaml.safe_load((root / "bundles/domain-bundle.yaml").read_text())
    assert domain["imports"][1:3] == ["bundle:company", "bundle:prohibited"]
    for rel in ["context/project/company-profile.yaml", "context/project/prohibited.yaml"]:
        assert (root / rel).is_file(), rel
        assert validate_with_validator(str(root / rel)).exit_code == 0
    manifest = yaml.safe_load((root / MANIFEST).read_text())
    ids = [c["id"] for c in manifest["domain"]["ontology"]["concepts"]]
    assert ids[:2] == ["concept:company", "concept:prohibited"]
    assert validate_with_validator("--domain", str(root / MANIFEST)).exit_code == 0


def test_new_project_does_not_add_the_domain_wide_concepts(tmp_path: Path):
    root = scaffold(tmp_path)
    assert not (root / "bundles/concepts/prohibited.yaml").exists()
    assert not (root / "context/project/company-profile.yaml").exists()


def test_new_mca_domain_validates(tmp_path: Path):
    root = new_workspace(tmp_path, "domain", "funder", "--ontology", "mca")
    assert (root / "bundles/concepts/prohibited.yaml").is_file()
    result = validate_with_validator("--bundle", str(root / "bundles/domain-bundle.yaml"))
    assert result.exit_code == 0, result.output


def test_filled_in_prohibitions_and_facts_compile(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    prohibited = root / "context/project/prohibited.yaml"
    prohibited.write_text(
        prohibited.read_text().replace(
            "  prohibitions: []\n",
            "  prohibitions:\n    - id: NO-001\n      kind: practice\n"
            "      subject: committing credentials to any repository\n",
        )
    )
    profile = root / "context/project/company-profile.yaml"
    profile.write_text(
        profile.read_text().replace(
            "  facts: []\n", "  facts:\n    - id: CO-001\n      fact: Demo builds software.\n"
        )
    )
    result = CliRunner().invoke(
        cli, ["compile", str(root / "bundles/domain-bundle.yaml"), "--allow-draft", "--stdout"]
    )
    assert result.exit_code == 0, result.output
    artifact = yaml.safe_load(result.stdout)
    assert artifact["rules"][1] == {
        "id": "demo/prohibited/NO-001",
        "rule": "Prohibited: committing credentials to any repository.",
    }
    assert artifact["facts"] == [
        {"id": "demo/company-profile/CO-001", "fact": "Demo builds software."}
    ]


def test_add_bundle_and_scd_find_the_common_templates(tmp_path: Path, monkeypatch):
    root = _init_bare_project(tmp_path, monkeypatch)
    assert CliRunner().invoke(cli, ["add", "bundle", "prohibited"]).exit_code == 0
    assert CliRunner().invoke(cli, ["add", "scd", "prohibited"]).exit_code == 0
    assert (root / "bundles/concepts/prohibited.yaml").is_file()
    assert (root / "context/project/prohibited.yaml").is_file()


# ------------------------------------------------------------------ sdlc Global profile

PROJECT_ONLY_SCDS = {
    "problem-definition",
    "stakeholders",
    "business-objectives",
    "opportunity-analysis",
    "constraints-and-assumptions",
    "success-criteria",
    "system-context",
    "component-model",
    "threat-model",
    "response-time",
    "availability",
    "fault-tolerance",
    "scalability",
    "error-handling-ux",
    "data-model",
    "validation-plan",
    "risk-assessment",
    "safety-checklist",
}


def test_sdlc_domain_uses_the_global_profile(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    scds = {p.stem for p in (root / "context" / "project").glob("*.yaml")}
    assert not scds & PROJECT_ONLY_SCDS
    assert {"engineering-practices", "audit-requirements", "policy-enforcement"} <= scds
    concepts = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert not concepts & {"business-context", "performance-reliability", "safety-risk"}
    assert not (root / "docs" / "business-context").exists()


def test_sdlc_domain_concept_bundles_list_only_generated_scds(tmp_path: Path):
    root = scaffold(tmp_path, "domain")
    generated = {f"scd:project:{p.stem}" for p in (root / "context" / "project").glob("*.yaml")}
    listed = set()
    for path in (root / "bundles" / "concepts").glob("*.yaml"):
        listed |= set(yaml.safe_load(path.read_text())["scds"])
    assert listed == generated
    security = yaml.safe_load((root / "bundles/concepts/security.yaml").read_text())
    assert security["scds"] == [
        "scd:project:authn-authz",
        "scd:project:data-protection",
        "scd:project:data-handling",
    ]


def test_sdlc_project_keeps_the_full_profile(tmp_path: Path):
    root = scaffold(tmp_path)
    scds = {p.stem for p in (root / "context" / "project").glob("*.yaml")}
    assert PROJECT_ONLY_SCDS <= scds
    assert "engineering-practices" not in scds


# ---------------------------------------------------------------------- cdmo ontology

CDMO_ONTOLOGY_EXAMPLE = REPO / "schema" / "domain" / "examples" / "medical-device-cdmo-domain.yaml"
CDMO_EXAMPLE = REPO / "examples" / "medical-device-cdmo"


def scaffold_cdmo(tmp_path: Path, kind: str = "project") -> Path:
    return new_workspace(tmp_path, kind, "demo", "--ontology", "cdmo")


def test_cdmo_reference_data_matches_the_shipped_ontology_and_example():
    """Drift guard: the CDMO_* data in project_types.py must match the ontology manifest and
    the example concept bundles exactly."""
    if not CDMO_ONTOLOGY_EXAMPLE.is_file():
        pytest.skip("reference ontology example not available")
    from scs_tools.utils import project_types as pt

    concepts = yaml.safe_load(CDMO_ONTOLOGY_EXAMPLE.read_text())["domain"]["ontology"]["concepts"]
    assert pt.CDMO_CONCEPTS == [c["id"].split(":")[1] for c in concepts]
    for c in concepts:
        cid = c["id"].split(":")[1]
        assert pt.CDMO_CONCEPT_INFO[cid] == (c["name"], " ".join(c["description"].split()))
        assert pt.CDMO_CONCEPT_RELATIONSHIPS.get(cid, []) == c.get("relationships", [])
        assert pt.CDMO_CONCEPT_SATISFIES.get(cid, []) == c.get("satisfies", [])
        bundle = yaml.safe_load((CDMO_EXAMPLE / "concepts" / f"{cid}.yaml").read_text())
        assert [s.split(":")[2] for s in bundle["scds"]] == pt.CDMO_CONCEPT_SCDS[cid]


def test_cdmo_domain_profile_is_a_subset_of_the_ontology():
    from scs_tools.utils import project_types as pt

    for concept, scds in pt.CDMO_DOMAIN_CONCEPT_SCDS.items():
        assert set(scds) <= set(pt.CDMO_CONCEPT_SCDS[concept]), concept
    assert "prohibited-uses" not in pt.CDMO_DOMAIN_CONCEPT_SCDS["compliance-governance"]


def test_every_cdmo_slot_has_a_template():
    from scs_tools.utils.project_types import CDMO_CONCEPT_SCDS

    templates = REPO / "tools" / "cli" / "scs_tools" / "templates" / "scds" / "cdmo"
    assert {p.stem for p in templates.glob("*.yaml")} == {
        s for scds in CDMO_CONCEPT_SCDS.values() for s in scds
    }


def test_cdmo_domain_scds_carry_no_profile_note(tmp_path: Path):
    """ISS-044: "Profile: Project only" contradicted the Domain workspace that held the SCD."""
    root = scaffold_cdmo(tmp_path, "domain")
    scds = list((root / "context" / "project").glob("*.yaml"))
    assert scds
    assert not [p.name for p in scds if "Profile:" in p.read_text()]


def test_cdmo_project_scaffolds_every_slot_and_validates(tmp_path: Path):
    root = scaffold_cdmo(tmp_path)
    scds = {p.stem for p in (root / "context" / "project").glob("*.yaml")}
    assert len(scds) == 48 and "prohibited-uses" in scds and "risk-register" in scds
    result = validate_with_validator("--bundle", str(root / "bundles/project-bundle.yaml"))
    assert result.exit_code == 0, result.output
    for path in sorted((root / "context" / "project").glob("*.yaml")):
        assert validate_with_validator(str(path)).exit_code == 0, path.name


def test_cdmo_domain_uses_the_global_profile(tmp_path: Path):
    root = scaffold_cdmo(tmp_path, kind="domain")
    scds = {p.stem for p in (root / "context" / "project").glob("*.yaml")}
    assert len(scds) == 30
    assert {"prohibited", "company-profile", "agent-autonomy-rules"} <= scds
    assert not scds & {"prohibited-uses", "risk-register", "cutover-plan", "program-objectives"}
    concepts = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert not concepts & {"business-context", "system-architecture", "implementation-cutover"}
    manifest = root / MANIFEST
    assert validate_with_validator("--domain", str(manifest)).exit_code == 0
    entries = yaml.safe_load(manifest.read_text())["domain"]["ontology"]["concepts"]
    risk = next(c for c in entries if c["id"] == "concept:risk-management")
    assert risk["satisfies"] == ["std:iso-14971:2019"]
    result = validate_with_validator("--bundle", str(root / "bundles/domain-bundle.yaml"))
    assert result.exit_code == 0, result.output


def test_cdmo_example_directive_compiles_once_uncommented(tmp_path: Path):
    root = scaffold_cdmo(tmp_path, kind="domain")
    scd = root / "context" / "project" / "agent-autonomy-rules.yaml"
    scd.write_text(
        scd.read_text().replace(
            "  directives: []\n  # Examples:\n  # - id: AAR-001\n  #   directive:",
            "  directives:\n  - id: AAR-001\n    directive:",
        )
    )
    result = CliRunner().invoke(
        cli, ["compile", str(root / "bundles/domain-bundle.yaml"), "--allow-draft", "--stdout"]
    )
    assert result.exit_code == 0, result.output
    ids = [r["id"] for r in yaml.safe_load(result.stdout)["rules"]]
    assert "demo/agent-autonomy-rules/AAR-001" in ids
