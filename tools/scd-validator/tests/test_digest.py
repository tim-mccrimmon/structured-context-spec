"""Content digests of versioned bundles (ISS-045, spec/0.7/bundle-format.md §7.6)."""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml
from click.testing import CliRunner

from scs_validator.commands.validate import validate
from scs_validator.digest import (
    DIGEST_RE,
    canonical_json,
    content_digest,
    digest_of,
    verify_tree,
)
from scs_validator.resolver import resolve

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


PROVENANCE = """provenance:
  created_by: a@example.com
  created_at: "2026-10-19T00:00:00Z"
"""
APPROVAL = """  version_approved_by: a@example.com
  version_approved_at: "2026-10-25T00:00:00Z"
"""


def concept(root: Path) -> Path:
    """A versioned concept bundle with one SCD."""
    write(
        root / "context" / "project" / "site.yaml",
        f"""id: scd:project:site
type: project
title: Site
version: "1.0.0"
description: Site
content:
  summary: Site
  facts:
    - id: S-001
      fact: The plant is in Minnesota.
{PROVENANCE}  rationale: test
""",
    )
    return write(
        root / "bundles" / "concepts" / "site.yaml",
        f"""id: bundle:site
type: concept
version: "1.0.0"
title: Site
description: Site
imports: []
scds:
  - scd:project:site
{PROVENANCE}{APPROVAL}""",
    )


def record(bundle_path: Path, name: str = "site", legacy: bool = False) -> Path:
    """Write a version manifest for the bundle as `scs bundle version` would."""
    tree = resolve(bundle_path)
    digest = content_digest(tree.root, tree.index)
    inputs, _ = digest.inputs()
    manifest = {"version": "1.0.0", "bundle": {"id": tree.root.id}}
    if not legacy:
        manifest.update(content_digest=digest.digest, content_inputs=inputs)
    filename = "VERSION-1.0.0-MANIFEST.yaml" if legacy else f"{name}-v1.0.0-MANIFEST.yaml"
    return write(bundle_path.parent / filename, yaml.safe_dump(manifest))


def digest(bundle_path: Path) -> str:
    tree = resolve(bundle_path)
    return content_digest(tree.root, tree.index).digest


def run(*args: str):
    return CliRunner().invoke(validate, list(args) + ["--no-color", "--schema-dir", str(SCHEMA)])


def test_canonical_json_ignores_key_order_and_keeps_non_ascii():
    assert canonical_json({"b": 1, "a": "é"}) == '{"a":"é","b":1}'
    assert canonical_json(yaml.safe_load("a: 1\nb: [x, y]")) == canonical_json(
        yaml.safe_load("# note\nb:\n  - 'x'\n  - \"y\"\na: 1\n")
    )


def test_yaml_dates_and_keys_canonicalize():
    when = yaml.safe_load("d: 2026-10-25\nt: 2026-10-25T08:00:00Z\n1: x")
    assert isinstance(when["d"], datetime.date)
    assert canonical_json(when) == ('{"1":"x","d":"2026-10-25","t":"2026-10-25T08:00:00+00:00"}')


def test_digest_format():
    assert DIGEST_RE.match(digest_of({"a": 1}))


def test_formatting_edits_keep_the_digest_and_content_edits_change_it(tmp_path: Path):
    path = concept(tmp_path)
    before = digest(path)
    scd = tmp_path / "context" / "project" / "site.yaml"
    scd.write_text("# reviewed 2026-10-25\n" + scd.read_text().replace('"1.0.0"', "'1.0.0'"))
    assert digest(path) == before
    scd.write_text(scd.read_text().replace("Minnesota", "Wisconsin"))
    assert digest(path) != before


def test_a_missing_scd_is_recorded_and_adding_it_changes_the_digest(tmp_path: Path):
    path = concept(tmp_path)
    scd = tmp_path / "context" / "project" / "site.yaml"
    text = scd.read_text()
    scd.unlink()
    tree = resolve(path)
    missing = content_digest(tree.root, tree.index)
    assert missing.scds == {"scd:project:site": None}
    scd.write_text(text)
    assert digest(path) != missing.digest


def test_an_import_change_changes_the_importer_digest(tmp_path: Path):
    concept(tmp_path)
    domain = write(
        tmp_path / "bundles" / "domain-bundle.yaml",
        """id: bundle:org
type: domain
version: "1.0.0"
title: Org
imports:
  - bundle:meta:0.6.0
  - bundle:site:1.0.0
""",
    )
    tree = resolve(domain)
    before = content_digest(tree.root, tree.index)
    inputs, _ = before.inputs()
    assert {"bundle:org:1.0.0", "bundle:site:1.0.0", "bundle:meta:0.6.0"} <= set(inputs["bundles"])
    assert "scd:project:site" in inputs["scds"]
    scd = tmp_path / "context" / "project" / "site.yaml"
    scd.write_text(scd.read_text().replace("Minnesota", "Wisconsin"))
    assert digest(domain) != before.digest


def test_verification_statuses(tmp_path: Path):
    path = concept(tmp_path)
    assert verify_tree(resolve(path)) == []  # no version manifest: nothing to verify against
    record(path)
    (check,) = verify_tree(resolve(path))
    assert check.status == "verified"
    scd = tmp_path / "context" / "project" / "site.yaml"
    scd.write_text(scd.read_text().replace("Minnesota", "Wisconsin"))
    (check,) = verify_tree(resolve(path))
    assert check.status == "mismatch"
    assert any("site.yaml (scd:project:site)" in c for c in check.changes)


def test_a_draft_bundle_is_not_verified(tmp_path: Path):
    path = concept(tmp_path)
    record(path)
    path.write_text(path.read_text().replace('version: "1.0.0"', 'version: "DRAFT"'))
    assert verify_tree(resolve(path)) == []


def test_validator_reports_a_mismatch_as_an_error_without_strict(tmp_path: Path):
    path = concept(tmp_path)
    record(path)
    assert run("--bundle", str(path)).exit_code == 0
    scd = tmp_path / "context" / "project" / "site.yaml"
    scd.write_text(scd.read_text().replace("Minnesota", "Wisconsin"))
    result = run("--bundle", str(path))
    assert result.exit_code == 1, result.output
    assert "has changed since it was versioned" in result.output
    assert "scd:project:site" in result.output


def test_validator_warns_on_a_manifest_without_a_content_digest(tmp_path: Path):
    path = concept(tmp_path)
    record(path, legacy=True)
    result = run("--bundle", str(path))
    assert result.exit_code == 0, result.output
    assert "cannot be verified" in result.output
    assert run("--bundle", str(path), "--strict").exit_code == 2
