"""scs compile: runtime artifacts from Domain and Project bundles (spec/0.6/runtime-artifact.md)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
EXAMPLE = REPO / "examples" / "two-tier-governance"
DOMAIN = EXAMPLE / "org" / "bundles" / "domain-bundle.yaml"
PROJECT = EXAMPLE / "infusion-pump-fw" / "bundles" / "project-bundle.yaml"
SCHEMA = json.loads((REPO / "schema" / "runtime" / "runtime-artifact-schema.json").read_text())


def compile_(*args: str):
    return CliRunner().invoke(cli, ["compile", *args])


@pytest.fixture
def org(tmp_path: Path) -> Path:
    """A writable copy of the example organization."""
    shutil.copytree(EXAMPLE / "org", tmp_path / "org")
    return tmp_path / "org"


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text
    path.write_text(text.replace(old, new))


# -------------------------------------------------------------------- golden output


@pytest.mark.parametrize(
    "bundle, golden",
    [
        (DOMAIN, EXAMPLE / "compiled" / "global.yaml"),
        (PROJECT, EXAMPLE / "compiled" / "projects" / "infusion-pump-fw.yaml"),
    ],
)
def test_compiled_examples_match_the_committed_artifacts(
    tmp_path: Path, bundle: Path, golden: Path
):
    out = tmp_path / "out.yaml"
    result = compile_(str(bundle), "-o", str(out))
    assert result.exit_code == 0, result.output
    assert out.read_bytes() == golden.read_bytes()


@pytest.mark.parametrize("bundle", [DOMAIN, PROJECT])
def test_artifacts_conform_to_the_runtime_schema(bundle: Path):
    jsonschema = pytest.importorskip("jsonschema")
    result = compile_(str(bundle), "--no-validate")
    jsonschema.validate(yaml.safe_load(result.stdout), SCHEMA)


def test_compiling_twice_gives_identical_bytes(tmp_path: Path):
    a, b = tmp_path / "a.yaml", tmp_path / "b.yaml"
    compile_(str(DOMAIN), "-o", str(a))
    compile_(str(DOMAIN), "-o", str(b))
    assert a.read_bytes() == b.read_bytes()


def test_artifact_has_no_volatile_content():
    text = compile_(str(DOMAIN), "--no-validate").stdout
    for volatile in (
        "created_at",
        "version_approved",
        "2026-",
        "@medtech-cdmo.example",
        str(REPO),
    ):
        assert volatile not in text


def test_provenance_changes_do_not_change_the_artifact(org: Path, tmp_path: Path):
    before = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate").stdout
    scd = org / "context" / "project" / "ai-review.yaml"
    edit(scd, "rationale: Initial approved version", "rationale: Reworded rationale")
    after = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate").stdout
    assert before == after


def test_rule_ids_order_and_self_identification():
    artifact = yaml.safe_load(compile_(str(DOMAIN), "--no-validate").stdout)
    ids = [r["id"] for r in artifact["rules"]]
    assert ids == [
        "medtech-cdmo/identity",
        "medtech-cdmo/prohibited/NO-001",
        "medtech-cdmo/prohibited/NO-002",
        "medtech-cdmo/prohibited/NO-003",
        "medtech-cdmo/governance-context/M-001",
        "medtech-cdmo/governance-context/M-002",
        "medtech-cdmo/governance-context/M-003",
        "medtech-cdmo/ai-review/AI-001",
        "medtech-cdmo/ai-review/AI-002",
        "medtech-cdmo/confidential-data/CD-001",
        "medtech-cdmo/confidential-data/CD-002",
        "medtech-cdmo/design-review/DR-001",
        "medtech-cdmo/design-change-control/DCC-001",
        "medtech-cdmo/design-change-control/DCC-002",
    ]
    assert "Domain bundle bundle:medtech-cdmo version 1.0.0" in artifact["rules"][0]["rule"]
    assert artifact["sources"] == [
        "bundle:meta:0.6.0",
        "bundle:company:1.0.0",
        "bundle:prohibited:1.0.0",
        "bundle:ai-use:1.0.0",
        "bundle:design-controls:1.0.0",
    ]


def test_json_format_carries_the_same_artifact():
    as_yaml = yaml.safe_load(compile_(str(PROJECT), "--no-validate").stdout)
    as_json = json.loads(compile_(str(PROJECT), "--no-validate", "--format", "json").stdout)
    assert as_yaml == as_json


def test_no_cites_drops_citations():
    artifact = yaml.safe_load(compile_(str(PROJECT), "--no-validate", "--no-cites").stdout)
    assert all("cites" not in r for r in artifact["rules"])


# ------------------------------------------------------------------------- drafts


def test_draft_bundles_are_refused_without_allow_draft(org: Path):
    edit(
        org / "bundles" / "concepts" / "ai-use.yaml",
        'version: "1.0.0"',
        'version: "DRAFT"',
    )
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate")
    assert result.exit_code != 0
    assert "DRAFT bundles cannot be compiled" in result.output


def test_allowed_draft_versions_track_content(org: Path):
    edit(org / "bundles" / "domain-bundle.yaml", 'version: "1.0.0"', 'version: "DRAFT"')
    root = str(org / "bundles" / "domain-bundle.yaml")
    first = yaml.safe_load(compile_(root, "--no-validate", "--allow-draft").stdout)
    assert first["version"].startswith("DRAFT+") and len(first["version"]) == len("DRAFT+") + 8
    assert first["version"] in first["rules"][0]["rule"]

    again = yaml.safe_load(compile_(root, "--no-validate", "--allow-draft").stdout)
    assert again["version"] == first["version"]

    edit(
        org / "context" / "project" / "ai-review.yaml",
        "say so and name",
        "say so, and name",
    )
    changed = yaml.safe_load(compile_(root, "--no-validate", "--allow-draft").stdout)
    assert changed["version"] != first["version"]


# ------------------------------------------------------------------------- errors


def test_todo_in_a_directive_is_an_error(org: Path):
    edit(
        org / "context" / "project" / "ai-review.yaml",
        "say so and name",
        "TODO say so and name",
    )
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate")
    assert result.exit_code != 0
    assert "still contains TODO" in result.output


def test_duplicate_rule_ids_are_an_error(org: Path):
    edit(org / "context" / "project" / "ai-review.yaml", "id: AI-002", "id: AI-001")
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate")
    assert result.exit_code != 0
    assert "Duplicate rule id medtech-cdmo/ai-review/AI-001" in result.output


def test_duplicate_directive_ids_fail_validation(org: Path):
    edit(org / "context" / "project" / "ai-review.yaml", "id: AI-002", "id: AI-001")
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"))
    assert result.exit_code != 0
    assert "Validation failed" in result.output


def test_scds_without_directives_warn_and_an_empty_tree_is_an_error(tmp_path: Path):
    ctx = tmp_path / "context" / "project"
    ctx.mkdir(parents=True)
    (ctx / "notes.yaml").write_text(
        'id: scd:project:notes\ntype: project\ntitle: Notes\nversion: "1.0.0"\n'
        "description: Notes.\ncontent:\n  summary: Background only.\n"
        'provenance:\n  created_by: a@example.com\n  created_at: "2026-10-19T00:00:00Z"\n'
    )
    bundles = tmp_path / "bundles"
    bundles.mkdir()
    (bundles / "project-bundle.yaml").write_text(
        'id: bundle:p\ntype: project\nversion: "1.0.0"\ntitle: P\ndescription: P.\n'
        "imports: []\nscds:\n  - scd:project:notes\n"
        'provenance:\n  created_by: a@example.com\n  created_at: "2026-10-19T00:00:00Z"\n'
        '  version_approved_by: a@example.com\n  version_approved_at: "2026-10-19T00:00:00Z"\n'
    )
    result = compile_(str(bundles / "project-bundle.yaml"), "--no-validate")
    assert result.exit_code != 0
    assert "has no directives" in result.output
    assert "nothing to compile" in result.output


def test_only_domain_and_project_bundles_compile():
    concept = EXAMPLE / "org" / "bundles" / "concepts" / "ai-use.yaml"
    result = compile_(str(concept), "--no-validate")
    assert result.exit_code != 0
    assert "Only domain and project bundles can be compiled" in result.output


def test_unresolved_import_is_an_error(org: Path):
    edit(
        org / "bundles" / "domain-bundle.yaml",
        "  - bundle:design-controls:1.0.0",
        "  - bundle:design-controls:1.0.0\n  - bundle:missing:1.0.0",
    )
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate")
    assert result.exit_code != 0
    assert "bundle:missing:1.0.0' in bundle:medtech-cdmo could not be resolved" in result.output


def test_validation_errors_stop_compilation(org: Path, tmp_path: Path):
    # A project bundle that imports the Domain bundle is invalid in 0.6.0.
    project = org / "bundles" / "bad-project.yaml"
    project.write_text(
        'id: bundle:bad\ntype: project\nversion: "1.0.0"\ntitle: Bad\ndescription: Bad.\n'
        "imports:\n  - bundle:medtech-cdmo:1.0.0\nscds: []\n"
        'provenance:\n  created_by: a@example.com\n  created_at: "2026-10-19T00:00:00Z"\n'
        '  version_approved_by: a@example.com\n  version_approved_at: "2026-10-19T00:00:00Z"\n'
    )
    out = tmp_path / "out.yaml"
    result = compile_(str(project), "-o", str(out))
    assert result.exit_code != 0
    assert "must not import a domain bundle" in result.output
    assert not out.exists()


# ------------------------------------------------------------ prohibitions and facts


def test_prohibitions_compile_to_binary_rules_ahead_of_directives():
    artifact = yaml.safe_load(compile_(str(DOMAIN), "--no-validate").stdout)
    rules = {r["id"]: r["rule"] for r in artifact["rules"]}
    assert rules["medtech-cdmo/prohibited/NO-001"] == (
        "Prohibited: consumer generative AI services and personal AI accounts. "
        "Use instead: the company's private AI service."
    )
    assert rules["medtech-cdmo/prohibited/NO-002"] == (
        "Prohibited: committing credentials, keys, or tokens to any repository."
    )
    assert "reason" not in str(artifact) and "Client contracts" not in str(artifact)


def test_facts_compile_into_their_own_list():
    artifact = yaml.safe_load(compile_(str(DOMAIN), "--no-validate").stdout)
    assert list(artifact)[-1] == "facts"
    assert [f["id"] for f in artifact["facts"]] == [
        "medtech-cdmo/company-profile/CO-001",
        "medtech-cdmo/company-profile/CO-002",
        "medtech-cdmo/company-profile/CO-003",
    ]
    assert artifact["facts"][1]["cites"] == ["std:iso-13485:2016"]


def test_artifacts_without_facts_have_no_facts_key():
    artifact = yaml.safe_load(compile_(str(PROJECT), "--no-validate").stdout)
    assert "facts" not in artifact


def test_a_qualified_prohibition_fails_validation(org: Path):
    edit(
        org / "context" / "project" / "prohibited.yaml",
        "to any repository",
        "to any repository unless encrypted",
    )
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"))
    assert result.exit_code != 0
    assert "is not binary" in result.output


def test_duplicate_fact_ids_are_an_error(org: Path):
    edit(org / "context" / "project" / "company-profile.yaml", "id: CO-003", "id: CO-002")
    result = compile_(str(org / "bundles" / "domain-bundle.yaml"), "--no-validate")
    assert "Duplicate rule id medtech-cdmo/company-profile/CO-002" in result.output


def test_facts_change_the_draft_digest(org: Path):
    edit(org / "bundles" / "domain-bundle.yaml", 'version: "1.0.0"', 'version: "DRAFT"')
    root = str(org / "bundles" / "domain-bundle.yaml")
    first = yaml.safe_load(compile_(root, "--no-validate", "--allow-draft").stdout)["version"]
    edit(org / "context" / "project" / "company-profile.yaml", "ISO 13485:2016.", "ISO 13485.")
    second = yaml.safe_load(compile_(root, "--no-validate", "--allow-draft").stdout)["version"]
    assert first != second


def test_rule_ids_are_unique_across_domain_and_project_artifacts(tmp_path: Path):
    """An SCD of the same name in both bundles must not yield the same rule id."""
    shutil.copytree(EXAMPLE, tmp_path / "ex")
    project = tmp_path / "ex" / "infusion-pump-fw"
    shutil.copy(
        tmp_path / "ex" / "org" / "context" / "project" / "ai-review.yaml",
        project / "context" / "project" / "ai-review.yaml",
    )
    edit(
        project / "bundles" / "project-bundle.yaml",
        "  - scd:project:release-gates",
        "  - scd:project:release-gates\n  - scd:project:ai-review",
    )
    domain = yaml.safe_load(
        compile_(str(tmp_path / "ex/org/bundles/domain-bundle.yaml"), "--no-validate").stdout
    )
    proj = yaml.safe_load(
        compile_(str(project / "bundles/project-bundle.yaml"), "--no-validate").stdout
    )
    domain_ids = {r["id"] for r in domain["rules"]}
    project_ids = {r["id"] for r in proj["rules"]}
    assert "medtech-cdmo/ai-review/AI-001" in domain_ids
    assert "infusion-pump-fw/ai-review/AI-001" in project_ids
    assert not domain_ids & project_ids
