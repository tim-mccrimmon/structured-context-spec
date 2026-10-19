"""SCS 0.6.0: independent Domain and Project bundles, deprecated standards, citations.

Each test builds a small bundle tree in a temp directory and validates its root bundle.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from scs_validator.commands.validate import validate
from scs_validator.resolver import resolve

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"

PROVENANCE = """provenance:
  created_by: a@example.com
  created_at: "2026-10-19T00:00:00Z"
"""


def run(*args: str):
    return CliRunner().invoke(validate, list(args) + ["--no-color", "--schema-dir", str(SCHEMA)])


def bundle(
    root: Path,
    rel: str,
    bundle_id: str,
    bundle_type: str,
    imports=(),
    scds=(),
    version="DRAFT",
) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"id: {bundle_id}",
        f"type: {bundle_type}",
        f'version: "{version}"',
        f"title: {bundle_id}",
        f"description: {bundle_id}",
        "imports:" + ("" if imports else " []"),
        *[f"  - {i}" for i in imports],
        "scds:" + ("" if scds else " []"),
        *[f"  - {s}" for s in scds],
    ]
    path.write_text("\n".join(lines) + "\n" + PROVENANCE)
    return path


def scd(root: Path, scd_id: str, extra: str = "") -> Path:
    tier, name = scd_id.split(":")[1:]
    path = root / "context" / tier / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'id: {scd_id}\ntype: {tier}\ntitle: {name}\nversion: "0.1.0"\n'
        f"description: {name}\ncontent:\n  summary: {name}\n{extra}{PROVENANCE}"
        "  rationale: test\n"
    )
    return path


@pytest.fixture
def meta(tmp_path: Path) -> Path:
    scd(tmp_path, "scd:meta:roles")
    return bundle(tmp_path, "bundles/meta.yaml", "bundle:meta", "meta", scds=["scd:meta:roles"])


@pytest.fixture
def concept(tmp_path: Path) -> Path:
    scd(tmp_path, "scd:project:org-rule")
    return bundle(
        tmp_path,
        "bundles/concepts/governance.yaml",
        "bundle:governance",
        "concept",
        scds=["scd:project:org-rule"],
    )


# ------------------------------------------------------------------- project bundles


def test_project_bundle_with_direct_scds_and_no_imports_is_valid(tmp_path: Path):
    scd(tmp_path, "scd:project:release-gates")
    root = bundle(
        tmp_path,
        "bundles/project.yaml",
        "bundle:app",
        "project",
        scds=["scd:project:release-gates"],
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0, result.output
    assert "0 warnings" in result.output


def test_project_bundle_importing_concept_bundles_is_valid(tmp_path: Path, concept: Path):
    root = bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project", ["bundle:governance"])
    assert run("--bundle", str(root)).exit_code == 0


@pytest.mark.parametrize("forbidden", ["meta", "domain"])
def test_project_bundle_must_not_import_meta_or_domain(
    tmp_path: Path, meta: Path, concept: Path, forbidden: str
):
    bundle(tmp_path, "bundles/domain.yaml", "bundle:org", "domain", ["bundle:governance"])
    target = {"meta": "bundle:meta", "domain": "bundle:org"}[forbidden]
    root = bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project", [target])
    result = run("--bundle", str(root))
    assert result.exit_code == 1
    assert f"must not import a {forbidden} bundle" in result.output


def test_project_bundle_with_neither_imports_nor_scds_fails_xor(tmp_path: Path):
    root = bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project")
    result = run("--bundle", str(root))
    assert result.exit_code == 1
    assert "XOR" in result.output


# -------------------------------------------------------------------- domain bundles


def test_domain_bundle_importing_meta_and_concepts_is_clean(
    tmp_path: Path, meta: Path, concept: Path
):
    root = bundle(
        tmp_path,
        "bundles/domain.yaml",
        "bundle:org",
        "domain",
        ["bundle:meta", "bundle:governance"],
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0, result.output
    # The only warning is the unpinned meta import.
    assert "should pin a version" in result.output
    assert "1 warnings" in result.output


def test_domain_bundle_without_meta_warns(tmp_path: Path, concept: Path):
    root = bundle(tmp_path, "bundles/domain.yaml", "bundle:org", "domain", ["bundle:governance"])
    result = run("--bundle", str(root))
    assert result.exit_code == 0
    assert "does not import a meta bundle" in result.output


def test_domain_bundle_must_not_import_a_project_bundle(tmp_path: Path, concept: Path):
    scd(tmp_path, "scd:project:x")
    bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project", scds=["scd:project:x"])
    root = bundle(
        tmp_path, "bundles/domain.yaml", "bundle:org", "domain", ["bundle:governance", "bundle:app"]
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 1
    assert "must not import a project bundle" in result.output


def test_domain_bundle_may_import_only_one_meta_bundle(tmp_path: Path, concept: Path):
    scd(tmp_path, "scd:meta:roles")
    bundle(tmp_path, "bundles/m1.yaml", "bundle:meta", "meta", scds=["scd:meta:roles"])
    bundle(tmp_path, "bundles/m2.yaml", "bundle:meta-extra", "meta", scds=["scd:meta:roles"])
    root = bundle(
        tmp_path,
        "bundles/domain.yaml",
        "bundle:org",
        "domain",
        ["bundle:meta", "bundle:meta-extra", "bundle:governance"],
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 1
    assert "at most 1 allowed" in result.output


# ------------------------------------------------------------------ resolution


def test_unresolved_import_is_a_warning(tmp_path: Path):
    root = bundle(
        tmp_path, "bundles/project.yaml", "bundle:app", "project", ["bundle:missing:1.0.0"]
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0
    assert "could not be resolved" in result.output


def test_import_cycle_is_an_error(tmp_path: Path):
    bundle(tmp_path, "bundles/a.yaml", "bundle:a", "domain", ["bundle:b"])
    bundle(tmp_path, "bundles/b.yaml", "bundle:b", "domain", ["bundle:a"])
    result = run("--bundle", str(tmp_path / "bundles" / "a.yaml"))
    assert result.exit_code == 1
    assert "Circular bundle imports" in result.output


def test_resolver_finds_bundles_by_id_not_file_name(tmp_path: Path, concept: Path):
    root = bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project", ["bundle:governance"])
    tree = resolve(root)
    assert [b.id for b in tree.bundles] == ["bundle:app", "bundle:governance"]
    assert [s.ref for s in tree.scds] == ["scd:project:org-rule"]


def test_resolver_prefers_the_pinned_version(tmp_path: Path):
    scd(tmp_path, "scd:project:x")
    bundle(tmp_path, "old/c.yaml", "bundle:c", "concept", scds=["scd:project:x"], version="1.0.0")
    bundle(tmp_path, "new/c.yaml", "bundle:c", "concept", scds=["scd:project:x"], version="2.0.0")
    root = bundle(tmp_path, "bundles/project.yaml", "bundle:app", "project", ["bundle:c:2.0.0"])
    tree = resolve(root)
    edge = tree.direct_imports()[0]
    assert edge.target.version == "2.0.0" and not edge.version_mismatch


# ------------------------------------------------------- standards and citations


def test_standards_bundle_is_deprecated(tmp_path: Path):
    scd(tmp_path, "scd:standards:hipaa")
    root = bundle(
        tmp_path, "bundles/std.yaml", "bundle:std", "standards", scds=["scd:standards:hipaa"]
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0
    assert "deprecated in SCS 0.6.0" in result.output


def test_scd_cites_must_be_well_formed_citations(tmp_path: Path):
    good = scd(
        tmp_path,
        "scd:project:good",
        "cites:\n  - std:iso-13485:2016#7.3.9\n  - std:hipaa#164.312(d)\n",
    )
    bad = scd(tmp_path, "scd:project:bad", "cites:\n  - ISO 13485 7.3.9\n")
    assert run(str(good)).exit_code == 0
    assert run(str(bad)).exit_code == 1


def test_satisfies_may_target_a_citation(tmp_path: Path):
    scd(
        tmp_path,
        "scd:project:rule",
        "relationships:\n  - type: satisfies\n    target: std:soc2:2017#CC6.6\n",
    )
    root = bundle(
        tmp_path, "bundles/project.yaml", "bundle:app", "project", scds=["scd:project:rule"]
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0, result.output
    assert "0 warnings" in result.output


def test_only_satisfies_may_target_a_citation(tmp_path: Path):
    scd(
        tmp_path,
        "scd:project:rule",
        "relationships:\n  - type: depends-on\n    target: std:soc2:2017#CC6.6\n",
    )
    root = bundle(
        tmp_path, "bundles/project.yaml", "bundle:app", "project", scds=["scd:project:rule"]
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 1
    assert "Only 'satisfies' may target a std: citation" in result.output


ONTOLOGY = """domain:
  id: domain:test
  name: Test
  version: 0.1.0
  description: Test domain.
  ontology:
    concepts:
      - id: concept:risk
        name: Risk
        satisfies:
          - {target}
  schemas:
    meta:
      content_schema: meta.json
    project:
      content_schema: project.json
"""


@pytest.mark.parametrize(
    "target, exit_code, expect",
    [
        ("std:iso-14971:2019#5", 0, "0 warnings"),
        ("scd:standards:iso-14971", 0, "deprecated in SCS 0.6.0"),
    ],
)
def test_ontology_satisfies_targets(tmp_path: Path, target: str, exit_code: int, expect: str):
    manifest = tmp_path / "domain.yaml"
    manifest.write_text(ONTOLOGY.format(target=target))
    result = run("--domain", str(manifest))
    assert result.exit_code == exit_code, result.output
    assert expect in result.output


def test_project_scd_may_satisfy_another_project_scd(tmp_path: Path):
    scd(tmp_path, "scd:project:audit-requirements")
    scd(
        tmp_path,
        "scd:project:audit-trail",
        "relationships:\n  - type: satisfies\n    target: scd:project:audit-requirements\n",
    )
    root = bundle(
        tmp_path,
        "bundles/project.yaml",
        "bundle:app",
        "project",
        scds=["scd:project:audit-requirements", "scd:project:audit-trail"],
    )
    result = run("--bundle", str(root))
    assert result.exit_code == 0, result.output
