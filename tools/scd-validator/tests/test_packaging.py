"""Packaging tests for scs-validator (ISS-035).

The rules and JSON Schemas must ship inside the package, or an installed wheel cannot run. The
repo-root ``schema/`` directory is the source of truth for the schemas; the copy inside the package
is vendored by ``scripts/sync_schemas.py`` and these tests fail if the two drift.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import pytest
from click.testing import CliRunner

from scs_validator import utils
from scs_validator.commands.validate import validate
from scs_validator.rules_loader import RulesLoader

REPO = Path(__file__).resolve().parents[3]
REPO_SCHEMA = REPO / "schema"
PACKAGE = Path(str(resources.files("scs_validator")))
PACKAGED_RULES = PACKAGE / "rules"
PACKAGED_SCHEMAS = PACKAGE / "schemas"

REQUIRED_SCHEMAS = [
    "bundles/scd-bundle-schema.json",
    "checkpoint/checkpoint-record-schema.json",
    "domain/domain-manifest-schema.json",
    "scd/meta-scd-template.json",
    "scd/project-scd-template.json",
    "scd/standards-scd-template.json",
]
REQUIRED_RULE_FILES = [
    "bundle-rules.yaml",
    "completeness-rules.yaml",
    "domain-ontology-rules.yaml",
    "relationship-rules.yaml",
    "scd-rules.yaml",
]


def test_default_rules_ship_inside_the_package():
    for name in REQUIRED_RULE_FILES:
        assert (PACKAGED_RULES / "v0.5.0" / name).is_file(), name
    assert RulesLoader().rules_dir.resolve() == (PACKAGED_RULES / "v0.5.0").resolve()


@pytest.mark.parametrize("rel", REQUIRED_SCHEMAS)
def test_schemas_ship_inside_the_package(rel: str):
    assert (PACKAGED_SCHEMAS / rel).is_file(), rel


def test_packaged_schema_dir_is_recognised_as_a_schema_dir():
    assert utils._looks_like_schema_dir(PACKAGED_SCHEMAS)
    assert utils.packaged_schema_dir().resolve() == PACKAGED_SCHEMAS.resolve()


def test_packaged_schemas_match_the_repo_schema_source_of_truth():
    """Drift check: run `python scripts/sync_schemas.py` from tools/scd-validator to fix a failure."""
    if not REPO_SCHEMA.is_dir():
        pytest.skip("repo-root schema/ not available (running from an sdist or installed copy)")
    source = {p.relative_to(REPO_SCHEMA).as_posix(): p for p in REPO_SCHEMA.rglob("*.json")}
    vendored = {p.relative_to(PACKAGED_SCHEMAS).as_posix(): p for p in PACKAGED_SCHEMAS.rglob("*.json")}
    assert set(vendored) == set(source), (
        f"only in schema/: {sorted(set(source) - set(vendored))}; "
        f"only in package: {sorted(set(vendored) - set(source))}"
    )
    stale = [rel for rel in source if source[rel].read_bytes() != vendored[rel].read_bytes()]
    assert not stale, f"vendored schemas differ from schema/: {stale}"


def test_discovery_falls_back_to_the_packaged_schemas(tmp_path: Path, monkeypatch):
    """An installed wheel has no checkout: with nothing else found, the packaged copy is used."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(utils.SCHEMA_DIR_ENV_VAR, raising=False)
    monkeypatch.setattr(utils, "_checkout_schema_dir", lambda searched: None)
    path, _ = utils.resolve_schema_dir(None)
    assert path is not None and path.resolve() == PACKAGED_SCHEMAS.resolve()


def test_checkout_schema_wins_over_the_packaged_copy(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(utils.SCHEMA_DIR_ENV_VAR, raising=False)
    path, _ = utils.resolve_schema_dir(None)
    assert path is not None and path.resolve() == REPO_SCHEMA.resolve()


def _run(*args: str):
    return CliRunner().invoke(validate, list(args) + ["--no-color"])


def test_validation_works_using_only_the_packaged_schemas():
    fixture = Path(__file__).parent / "fixtures" / "valid" / "test-meta-roles.yaml"
    assert _run(str(fixture), "--schema-dir", str(PACKAGED_SCHEMAS)).exit_code == 0
    domain = REPO / "schema" / "domain" / "examples" / "software-development-domain.yaml"
    if domain.is_file():
        assert _run("--domain", str(domain), "--schema-dir", str(PACKAGED_SCHEMAS)).exit_code == 0
    checkpoint = REPO / "examples" / "med-adherence" / "project-bundle.yaml"
    if checkpoint.is_file():
        assert _run("--bundle", str(checkpoint), "--schema-dir", str(PACKAGED_SCHEMAS)).exit_code == 0


def test_the_sync_script_reports_no_drift():
    script = Path(__file__).resolve().parents[1] / "scripts" / "sync_schemas.py"
    if not (script.is_file() and REPO_SCHEMA.is_dir()):
        pytest.skip("sync script or repo schema/ not available")
    import subprocess
    import sys

    result = subprocess.run([sys.executable, str(script), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
