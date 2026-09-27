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

PROJECT_TYPES = ["healthcare", "fintech", "saas", "government", "standard", "minimal"]
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


def scaffold(tmp_path: Path, project_type: str) -> Path:
    result = CliRunner().invoke(
        cli,
        [
            "new",
            "project",
            "demo",
            "--type",
            project_type,
            "--dir",
            str(tmp_path),
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
            "--no-interactive",
        ],
    )
    assert result.exit_code == 0, result.output
    return tmp_path / "demo"


def validate_with_validator(*args: str):
    return CliRunner().invoke(
        validator_cmd, list(args) + ["--no-color", "--schema-dir", str(SCHEMA)]
    )


@pytest.fixture(scope="module")
def healthcare_project(tmp_path_factory) -> Path:
    return scaffold(tmp_path_factory.mktemp("proj"), "healthcare")


# ---------------------------------------------------------------------------- scaffold


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_scaffold_creates_the_expected_structure(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
    for rel in [
        "bundles/project-bundle.yaml",
        "bundles/meta-bundle.yaml",
        "bundles/standards-bundle.yaml",
        "bundles/domains/software-development.yaml",
        ".scs/config",
        "VERSION",
        "README.md",
        "docs/GETTING_STARTED.md",
    ]:
        assert (root / rel).is_file(), rel
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    if project_type == "minimal":
        assert {"architecture", "security", "deployment-operations"} <= generated <= CONCEPTS
    else:
        assert generated == CONCEPTS
    assert len(list((root / "context" / "project").glob("*.yaml"))) >= 11


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_scaffold_uses_concept_terminology_and_starts_as_draft(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
    for path in (root / "bundles").rglob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        assert data["type"] != "concern", path
        assert data["version"] == "DRAFT", path
    concept = yaml.safe_load((root / "bundles" / "concepts" / "security.yaml").read_text())
    assert concept["type"] == "concept"


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_every_scaffolded_bundle_validates(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
    for path in sorted((root / "bundles").rglob("*.yaml")):
        result = validate_with_validator("--bundle", str(path))
        assert result.exit_code == 0, f"{path.relative_to(root)}\n{result.output}"


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_every_scaffolded_scd_validates(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
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
    project = scaffold(tmp_path, "healthcare")
    result = _version_security_bundle(project, monkeypatch)
    assert result.exit_code == 0, result.output
    assert (project / "bundles/concepts/security-v0.1.0.yaml").is_file()


def test_versioned_snapshot_carries_the_version_and_approval(tmp_path: Path, monkeypatch):
    """ISS-027: the snapshot must say 0.1.0 inside, not DRAFT, and record the approval."""
    project = scaffold(tmp_path, "healthcare")
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


def test_versioned_snapshot_validates(tmp_path: Path, monkeypatch):
    project = scaffold(tmp_path, "healthcare")
    assert _version_security_bundle(project, monkeypatch).exit_code == 0
    snapshot = project / "bundles/concepts/security-v0.1.0.yaml"
    result = validate_with_validator("--bundle", str(snapshot))
    assert result.exit_code == 0, result.output
    assert yaml.safe_load(snapshot.read_text())["version"] == "0.1.0"


def test_a_versioned_snapshot_without_approval_fields_is_rejected(tmp_path: Path, monkeypatch):
    """The DRAFT exemption must not apply once the snapshot carries a real version."""
    project = scaffold(tmp_path, "healthcare")
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

    project = scaffold(tmp_path, "healthcare")
    assert _version_security_bundle(project, monkeypatch, "--no-validate").exit_code == 0
    snapshot = project / "bundles/concepts/security-v0.1.0.yaml"
    manifest = yaml.safe_load(
        (project / "bundles/concepts/VERSION-0.1.0-MANIFEST.yaml").read_text()
    )
    assert manifest["bundle"]["sha256"] == hashlib.sha256(snapshot.read_bytes()).hexdigest()
    assert manifest["approval"]["approved_by"] == "sam@example.com"


def test_versioning_refuses_to_overwrite_without_force(tmp_path: Path, monkeypatch):
    project = scaffold(tmp_path, "healthcare")
    assert _version_security_bundle(project, monkeypatch, "--no-validate").exit_code == 0
    again = _version_security_bundle(project, monkeypatch, "--no-validate")
    assert again.exit_code != 0
    assert "already exists" in again.output


# ------------------------------------------------------ domain bundle imports (ISS-033)


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_domain_bundle_imports_exactly_the_concept_bundles_generated(
    tmp_path: Path, project_type: str
):
    root = scaffold(tmp_path, project_type)
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    domain = yaml.safe_load((root / "bundles/domains/software-development.yaml").read_text())
    imported = {ref.split(":")[1] for ref in domain["imports"]}
    assert imported == generated


def test_add_domain_bundle_imports_the_projects_concept_bundles(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path, "minimal")
    (root / "bundles/domains/software-development.yaml").unlink()
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["add", "bundle", "software-development"])
    assert result.exit_code == 0, result.output
    domain = yaml.safe_load((root / "bundles/domains/software-development.yaml").read_text())
    assert {ref.split(":")[1] for ref in domain["imports"]} == {
        "architecture",
        "security",
        "deployment-operations",
    }
    assert (
        validate_with_validator(
            "--bundle", str(root / "bundles/domains/software-development.yaml")
        ).exit_code
        == 0
    )


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


def test_add_bundle_still_adds_a_domain_bundle(tmp_path: Path, monkeypatch):
    root = _init_bare_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(cli, ["add", "bundle", "software-development"])
    assert result.exit_code == 0, result.output
    assert (root / "bundles" / "domains" / "software-development.yaml").is_file()


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
    assert "Available domain bundles" in result.output


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
MANIFEST = "domain/domain-manifest.yaml"


def _manifest_concepts(root: Path) -> list[dict]:
    return yaml.safe_load((root / MANIFEST).read_text())["domain"]["ontology"]["concepts"]


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_scaffold_generates_a_valid_domain_ontology_manifest(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
    assert (root / MANIFEST).is_file()
    result = validate_with_validator("--domain", str(root / MANIFEST))
    assert result.exit_code == 0, result.output
    assert "0 errors" in result.output and "0 warnings" in result.output


@pytest.mark.parametrize("project_type", PROJECT_TYPES)
def test_manifest_ontology_lists_exactly_the_generated_concepts(tmp_path: Path, project_type: str):
    root = scaffold(tmp_path, project_type)
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
    root = scaffold(tmp_path, "healthcare")
    scaffolded = {c["id"]: (c["name"], c.get("description")) for c in _manifest_concepts(root)}
    assert scaffolded == reference


def test_manifest_declares_the_software_development_domain(tmp_path: Path):
    root = scaffold(tmp_path, "standard")
    domain = yaml.safe_load((root / MANIFEST).read_text())["domain"]
    assert domain["id"] == "domain:software-development"
    assert domain["version"] == "0.1.0"
    assert "concerns" not in domain


def test_getting_started_points_at_the_ontology_manifest(tmp_path: Path):
    root = scaffold(tmp_path, "standard")
    assert MANIFEST in (root / "docs" / "GETTING_STARTED.md").read_text()


def test_add_bundle_reminds_you_to_add_the_concept_to_the_manifest(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path, "minimal")
    monkeypatch.chdir(root)
    result = CliRunner().invoke(cli, ["add", "bundle", "compliance-governance"])
    assert result.exit_code == 0, result.output
    assert MANIFEST in result.output
    assert "concept:compliance-governance" in result.output


def test_add_bundle_is_quiet_when_the_manifest_already_has_the_concept(tmp_path: Path, monkeypatch):
    root = scaffold(tmp_path, "healthcare")
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


def test_add_bundle_honours_the_project_types_compliance_settings(tmp_path: Path, monkeypatch):
    """A healthcare project's compliance bundle lists the HIPAA SCDs; a standard one does not."""
    for project_type, expect_hipaa in (("healthcare", True), ("standard", False)):
        root = scaffold(tmp_path / project_type, project_type)
        (root / "bundles" / "concepts" / "compliance-governance.yaml").unlink()
        monkeypatch.chdir(root)
        assert CliRunner().invoke(cli, ["add", "bundle", "compliance-governance"]).exit_code == 0
        text = (root / "bundles" / "concepts" / "compliance-governance.yaml").read_text()
        assert ("hipaa-compliance" in text) is expect_hipaa


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
    result = CliRunner().invoke(
        cli,
        [
            "new",
            "project",
            "demo",
            "--ontology",
            "mca",
            "--dir",
            str(tmp_path),
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
            "--no-interactive",
        ],
    )
    assert result.exit_code == 0, result.output
    return tmp_path / "demo"


def test_mca_scaffold_generates_exactly_the_16_mca_concepts(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    generated = {p.stem for p in (root / "bundles" / "concepts").glob("*.yaml")}
    assert generated == MCA_CONCEPTS


def test_mca_scaffold_ignores_type(tmp_path: Path):
    """--type is sdlc-only; passing it alongside --ontology mca changes nothing about the
    scaffold (still the full 16-concept set, not a --type variant)."""
    result = CliRunner().invoke(
        cli,
        [
            "new",
            "project",
            "demo",
            "--ontology",
            "mca",
            "--type",
            "minimal",
            "--dir",
            str(tmp_path),
            "--author",
            "A",
            "--email",
            "a@example.com",
            "--no-interactive",
        ],
    )
    assert result.exit_code == 0, result.output
    generated = {p.stem for p in (tmp_path / "demo" / "bundles" / "concepts").glob("*.yaml")}
    assert generated == MCA_CONCEPTS


def test_mca_domain_bundle_imports_exactly_the_16_concepts(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    domain = yaml.safe_load((root / "bundles/domains/merchant-cash-advance.yaml").read_text())
    imported = {ref.split(":")[1] for ref in domain["imports"]}
    assert imported == MCA_CONCEPTS


def test_mca_every_scaffolded_bundle_validates(tmp_path: Path):
    root = scaffold_mca(tmp_path)
    for path in (
        [
            root / "bundles" / f
            for f in ("project-bundle.yaml", "meta-bundle.yaml", "standards-bundle.yaml")
        ]
        + list((root / "bundles" / "concepts").glob("*.yaml"))
        + list((root / "bundles" / "domains").glob("*.yaml"))
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
    assert "ontology_model: mca" in config
    assert "scs_version: 0.1.0" not in config  # was hardcoded stale; now the real package version


def test_sdlc_scaffold_still_records_sdlc_as_the_ontology_model(tmp_path: Path):
    root = scaffold(tmp_path, "standard")
    assert "ontology_model: sdlc" in (root / ".scs" / "config").read_text()


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
    assert "merchant-cash-advance" in result.output


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
