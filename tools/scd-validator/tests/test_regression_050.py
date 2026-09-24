"""Regression suite for SCS 0.5.0 validator behaviour.

Baseline captured 2026-09-24 against the 0.5-dev branch. These tests pin the behaviour delivered by
ISS-002 to ISS-006 (Domain Ontology schema + validator, examples, checkpoint records) so later fixes
cannot silently regress it. Known pre-existing failures are marked ``xfail(strict=True)`` with the
ISS that tracks them, so the marker has to be removed when the underlying issue is fixed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from scs_validator.commands.validate import validate

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
EXAMPLES = REPO / "examples"
DOMAIN_EXAMPLES = SCHEMA / "domain" / "examples"
FIXTURES = Path(__file__).parent / "fixtures"

BUNDLE_TYPES = {"project", "meta", "standards", "concept", "domain"}

# third-party model output kept as evidence of cross-model testing; not a validity target
EXCLUDED_DIRS = {"llm-portability"}


def run(*args: str, schema: bool = True):
    argv = list(args) + ["--no-color"]
    if schema:
        argv += ["--schema-dir", str(SCHEMA)]
    return CliRunner().invoke(validate, argv)


def _rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def _bundle_type(path: Path) -> str | None:
    m = re.search(r"^type:\s*(\S+)", path.read_text(), re.M)
    return m.group(1).strip("\"'") if m else None


def _example_bundles() -> list[Path]:
    found = []
    for p in sorted(EXAMPLES.rglob("*.yaml")):
        if EXCLUDED_DIRS & set(p.relative_to(EXAMPLES).parts) or "scds" in p.parts:
            continue
        if _bundle_type(p) in BUNDLE_TYPES:
            found.append(p)
    return found


def _example_scds() -> list[Path]:
    return [
        p
        for p in sorted(EXAMPLES.rglob("*.yaml"))
        if "scds" in p.parts and not (EXCLUDED_DIRS & set(p.relative_to(EXAMPLES).parts))
    ]


KNOWN_INVALID_BUNDLES = {
    "examples/med-adherence/standards-bundle.yaml": "ISS-022",
}
KNOWN_INVALID_DOMAINS: dict[str, str] = {}


def _param(path: Path, known: dict[str, str]):
    rel = _rel(path)
    marks = []
    if rel in known:
        marks.append(
            pytest.mark.xfail(strict=True, reason=f"{known[rel]}: known pre-existing failure")
        )
    return pytest.param(path, id=rel, marks=marks)


# ---------------------------------------------------------------- bundles and SCDs


@pytest.mark.parametrize("bundle", [_param(p, KNOWN_INVALID_BUNDLES) for p in _example_bundles()])
def test_example_bundle_validates(bundle: Path):
    result = run("--bundle", str(bundle))
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize("scd", [pytest.param(p, id=_rel(p)) for p in _example_scds()])
def test_example_scd_validates(scd: Path):
    result = run(str(scd))
    assert result.exit_code == 0, result.output


def test_valid_fixture_passes():
    assert run(str(FIXTURES / "valid" / "test-meta-roles.yaml")).exit_code == 0


def test_invalid_fixture_fails():
    result = run(str(FIXTURES / "invalid" / "test-invalid.yaml"))
    assert result.exit_code == 1, result.output


def test_at_least_one_of_each_shipped_bundle_kind_is_covered():
    kinds = {_bundle_type(p) for p in _example_bundles()}
    assert BUNDLE_TYPES <= kinds


# ------------------------------------------------------------------ domain manifests


@pytest.mark.parametrize(
    "manifest", [_param(p, KNOWN_INVALID_DOMAINS) for p in sorted(DOMAIN_EXAMPLES.glob("*.yaml"))]
)
def test_domain_manifest_examples_validate(manifest: Path):
    result = run("--domain", str(manifest))
    assert result.exit_code == 0, result.output


def test_software_development_ontology_is_clean():
    result = run("--domain", str(DOMAIN_EXAMPLES / "software-development-domain.yaml"))
    assert result.exit_code == 0
    assert "0 errors" in result.output and "0 warnings" in result.output


def test_cdmo_ontology_only_warns_about_unresolved_satisfies_targets():
    result = run("--domain", str(DOMAIN_EXAMPLES / "medical-device-cdmo-domain.yaml"))
    assert result.exit_code == 0
    assert "0 errors" in result.output
    warnings = [ln for ln in result.output.splitlines() if "⚠" in ln]
    assert warnings, "expected the documented unresolved-satisfies warnings"
    assert all("satisfies" in ln for ln in warnings)


def test_strict_mode_turns_warnings_into_exit_code_2():
    result = run("--domain", str(DOMAIN_EXAMPLES / "medical-device-cdmo-domain.yaml"), "--strict")
    assert result.exit_code == 2


def test_legacy_concerns_manifest_is_an_error_with_a_migration_hint(tmp_path: Path):
    manifest = tmp_path / "old-domain.yaml"
    manifest.write_text(
        "domain:\n"
        "  id: domain:legacy\n"
        "  name: Legacy\n"
        "  version: 0.1.0\n"
        "  description: A 0.3-style manifest\n"
        "  concerns:\n"
        "    - bundle:security:1.0.0\n"
        "  schemas:\n"
        "    meta:\n"
        '      content_schema: "../../scd/meta-scd-content-schema.json"\n'
    )
    result = run("--domain", str(manifest))
    assert result.exit_code == 1
    assert "legacy 'concerns' field" in result.output
    assert "ontology" in result.output


def _manifest_with(concept_block: str) -> str:
    return (
        "domain:\n"
        "  id: domain:t\n"
        "  name: T\n"
        "  version: 0.1.0\n"
        "  description: test\n"
        "  ontology:\n"
        "    concepts:\n"
        f"{concept_block}"
        "  schemas:\n"
        "    meta:\n"
        '      content_schema: "x.json"\n'
        "    standards:\n"
        '      content_schema: "x.json"\n'
        "    project:\n"
        '      content_schema: "x.json"\n'
    )


@pytest.mark.parametrize(
    "block, expect",
    [
        (
            "      - id: concept:a\n        name: A\n        parent: concept:b\n"
            "      - id: concept:b\n        name: B\n        parent: concept:a\n",
            "cycl",
        ),
        (
            "      - id: concept:a\n        name: A\n"
            "        relationships:\n          - type: depends-on\n"
            "            target: concept:missing\n",
            "missing",
        ),
        (
            "      - id: concept:a\n        name: A\n      - id: concept:a\n        name: A2\n",
            "unique",
        ),
    ],
    ids=["parent-cycle", "dangling-target", "duplicate-id"],
)
def test_ontology_rules_reject_bad_manifests(tmp_path: Path, block: str, expect: str):
    manifest = tmp_path / "bad.yaml"
    manifest.write_text(_manifest_with(block))
    result = run("--domain", str(manifest))
    assert result.exit_code == 1, result.output
    assert expect in result.output.lower()


# --------------------------------------------------------------- checkpoint records

GOOD_CHECKPOINT = """\
checkpoint:
  bundle: bundle:risk-management:1.2.0
  concept: concept:risk-management
  agent: role:quality-engineer
  intent: hazard-analysis-review
  timestamp: "2026-09-23T10:00:00Z"
  workflow_ref: "workflow:release-review/run-4821/step-3"
"""

BAD_CHECKPOINT = """\
checkpoint:
  bundle: risk-management
  agent: role:quality-engineer
"""


def test_valid_checkpoint_record_passes(tmp_path: Path):
    f = tmp_path / "cp.yaml"
    f.write_text(GOOD_CHECKPOINT)
    assert run("--checkpoint", str(f)).exit_code == 0


def test_invalid_checkpoint_record_reports_each_problem(tmp_path: Path):
    f = tmp_path / "cp.yaml"
    f.write_text(BAD_CHECKPOINT)
    result = run("--checkpoint", str(f))
    assert result.exit_code == 1
    assert "3 errors" in result.output
    assert "'intent'" in result.output and "'timestamp'" in result.output
    assert "does not match required pattern" in result.output


# ------------------------------------------------------------ policy SCD (ISS-006)

POLICY_SCD = """\
id: scd:project:policy-risk-management-readonly
type: project
title: "Risk Management - Read-Only Access Policy"
version: "DRAFT"
concept: concept:risk-management
description: >
  Defines which roles may access risk-management data, and under what constraints.

content:
  applies_to_roles:
    - role:quality-engineer
  permitted_operations:
    - capability: fetch-data
      resource: risk-register
    - capability: write-data
      resource: risk-register
      requires_approval: true

provenance:
  created_by: jane@example.com
  created_at: "2026-09-22T00:00:00Z"
"""


def test_policy_scd_validates_as_an_ordinary_project_scd(tmp_path: Path):
    f = tmp_path / "policy.yaml"
    f.write_text(POLICY_SCD)
    result = run(str(f))
    assert result.exit_code == 0, result.output


# ----------------------------------------------------------------- schema location


def test_nonexistent_explicit_schema_dir_is_rejected(tmp_path: Path):
    result = run(
        str(FIXTURES / "valid" / "test-meta-roles.yaml"),
        "--schema-dir",
        str(tmp_path / "nope"),
        schema=False,
    )
    assert result.exit_code != 0


def test_schema_dir_is_found_without_the_flag(tmp_path: Path, monkeypatch):
    """ISS-028: a source-checkout install must find the repo-root schema/ from any directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SCS_SCHEMA_DIR", raising=False)
    result = run(str(FIXTURES / "valid" / "test-meta-roles.yaml"), schema=False)
    assert result.exit_code == 0, result.output


def test_schema_dir_env_var_is_honoured(tmp_path: Path, monkeypatch):
    """ISS-028: SCS_SCHEMA_DIR overrides discovery."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = run(str(FIXTURES / "valid" / "test-meta-roles.yaml"), schema=False)
    assert result.exit_code == 0, result.output


# ----------------------------------------------------- MCA ontology (ships with 0.5.0)

MCA_MANIFEST = DOMAIN_EXAMPLES / "merchant-cash-advance-domain.yaml"
MCA_NATIVE = {
    "origination",
    "underwriting-decisioning",
    "contract-characterization",
    "disclosure-compliance",
    "security-interest-management",
    "servicing-collections",
    "capital-funding",
    "portfolio-risk-management",
    "broker-partner-management",
}
MCA_INFRASTRUCTURE = {"data-provenance", "data-security", "systems-integration"}
MCA_AI_GOVERNANCE = {"governance", "ai-accountability", "training-competency", "adoption-rollout"}
MCA_EDGES = {
    ("adoption-rollout", "relates-to", "governance"),
    ("broker-partner-management", "relates-to", "origination"),
    ("broker-partner-management", "relates-to", "disclosure-compliance"),
    ("capital-funding", "relates-to", "portfolio-risk-management"),
    ("contract-characterization", "relates-to", "disclosure-compliance"),
    ("data-provenance", "depends-on", "systems-integration"),
    ("data-security", "depends-on", "systems-integration"),
    ("origination", "depends-on", "data-provenance"),
    ("origination", "relates-to", "underwriting-decisioning"),
    ("security-interest-management", "relates-to", "portfolio-risk-management"),
    ("servicing-collections", "depends-on", "security-interest-management"),
    ("servicing-collections", "relates-to", "contract-characterization"),
    ("underwriting-decisioning", "depends-on", "data-provenance"),
    ("underwriting-decisioning", "relates-to", "contract-characterization"),
    ("underwriting-decisioning", "relates-to", "portfolio-risk-management"),
}


def _mca_ontology() -> dict:
    import yaml

    return yaml.safe_load(MCA_MANIFEST.read_text())["domain"]["ontology"]


def test_mca_ontology_validates_clean():
    result = run("--domain", str(MCA_MANIFEST))
    assert result.exit_code == 0, result.output
    assert "0 errors" in result.output and "0 warnings" in result.output


def test_mca_ontology_has_the_sixteen_concepts():
    ids = {c["id"].split(":", 1)[1] for c in _mca_ontology()["concepts"]}
    assert ids == MCA_NATIVE | MCA_INFRASTRUCTURE | MCA_AI_GOVERNANCE
    assert len(ids) == 16


def test_mca_names_its_access_control_concept_data_security_not_security():
    """In this business "security" natively means the lien on receivables."""
    ids = {c["id"] for c in _mca_ontology()["concepts"]}
    assert "concept:data-security" in ids and "concept:security-interest-management" in ids
    assert "concept:security" not in ids


def test_mca_concept_relationships_are_the_documented_set():
    edges = {
        (c["id"].split(":", 1)[1], r["type"], r["target"].split(":", 1)[1])
        for c in _mca_ontology()["concepts"]
        for r in c.get("relationships", [])
    }
    assert edges == MCA_EDGES


def test_every_mca_concept_is_described():
    for concept in _mca_ontology()["concepts"]:
        assert concept.get("description", "").strip(), concept["id"]


def test_mca_manifest_is_client_neutral():
    text = MCA_MANIFEST.read_text().lower()
    for term in ("everest", "whetstone", "alpine", "nextern"):
        assert term not in text, term
