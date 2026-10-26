"""Domain repositories and workspace checks (WP-04, RFC 0002 §9).

Repository mode, reserved directories and bundle names (D-33), duplicate ids (D-43), workspace
configuration (D-03, D-04), and version manifests (D-28, D-36).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import pytest
import yaml
from click.testing import CliRunner
from jsonschema import Draft202012Validator

from scs_validator import checks
from scs_validator.checks import CheckContext
from scs_validator.commands.validate import validate
from scs_validator.utils import ValidationInfo, ValidationResult

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
REPORT_SCHEMA = json.loads((SCHEMA / "validator" / "report-schema.json").read_text())
MANIFEST_SCHEMA = json.loads((SCHEMA / "manifest" / "version-manifest-schema.json").read_text())
ONTOLOGY = SCHEMA / "domain" / "examples" / "software-development-domain.yaml"

PROVENANCE = """provenance:
  created_by: Jane Doe <jane@structuredcontext.dev>
  created_at: "2026-10-25T00:00:00Z"
  rationale: test
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def scd(root: Path, name: str, scd_id: Optional[str] = None) -> Path:
    return write(
        root / "context" / "project" / f"{name}.yaml",
        f"""id: {scd_id or f"scd:project:{name}"}
type: project
title: {name}
version: "1.0.0"
description: {name}
content:
  summary: {name}
  facts:
    - id: F-001
      fact: A fact about {name}.
{PROVENANCE}""",
    )


def concept(root: Path, name: str, version: str = "DRAFT", stem: Optional[str] = None) -> Path:
    approval = (
        ""
        if version == "DRAFT"
        else "  version_approved_by: Jane Doe <jane@structuredcontext.dev>\n"
        '  version_approved_at: "2026-10-25T00:00:00Z"\n'
    )
    return write(
        root / "bundles" / "concepts" / f"{stem or name}.yaml",
        f"""id: bundle:{name}
type: concept
version: "{version}"
title: {name}
description: {name}
imports: []
scds:
  - scd:project:{name}
{PROVENANCE}{approval}""",
    )


def workspace(root: Path, name: str, bundle_type: str, concept_name: str) -> Path:
    write(root / ".scs" / "config", f"bundle_type: {bundle_type}\nname: {name}\n")
    scd(root, concept_name)
    concept(root, concept_name)
    imports = f"  - bundle:{concept_name}\n"
    if bundle_type == "domain":
        imports = "  - bundle:meta:0.6.0\n" + imports
    write(
        root / "bundles" / f"{bundle_type}-bundle.yaml",
        f"""id: bundle:{name}
type: {bundle_type}
version: DRAFT
title: {name}
description: {name}
imports:
{imports}scds: []
{PROVENANCE}""",
    )
    return root


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "acme-context"
    workspace(root / "domain", "domain", "domain", "company")
    workspace(root / "projects" / "app", "app", "project", "release")
    return root


def run(*args: str, cwd: Optional[Path] = None, monkeypatch=None):
    if cwd is not None and monkeypatch is not None:
        monkeypatch.chdir(cwd)
    return CliRunner().invoke(validate, list(args) + ["--no-color", "--schema-dir", str(SCHEMA)])


def report(*args: str) -> dict:
    result = run(*args, "--output", "json")
    data = json.loads(result.output)
    Draft202012Validator(REPORT_SCHEMA).validate(data)
    return data


def codes(data: dict) -> list:
    sections = [data] + data.get("workspaces", [])
    return [
        f["code"] for s in sections for kind in ("errors", "warnings", "infos") for f in s[kind]
    ]


# ------------------------------------------------------------------ repository mode


def test_a_clean_repository_passes_strict(repo: Path):
    result = run("--repo", str(repo), "--strict")
    assert result.exit_code == 0, result.output
    data = report("--repo", str(repo))
    assert [w["name"] for w in data["workspaces"]] == ["domain", "app"]
    assert data["summary"]["status"] == "valid"


def test_repository_mode_is_the_default_at_a_repository_root(repo: Path, monkeypatch):
    result = run("--strict", cwd=repo, monkeypatch=monkeypatch)
    assert result.exit_code == 0, result.output
    assert "Workspace domain" in result.output and "Workspace app" in result.output


def test_no_domain_workspace_is_an_error(repo: Path):
    shutil.rmtree(repo / "domain")
    result = run("--repo", str(repo))
    assert result.exit_code == 1, result.output
    assert codes(report("--repo", str(repo))) == ["DOMAIN_WORKSPACE_MISSING"]


def test_two_domain_workspaces_is_an_error(repo: Path):
    write(repo / "projects" / "app" / ".scs" / "config", "bundle_type: domain\nname: app\n")
    assert run("--repo", str(repo)).exit_code == 1
    assert "DOMAIN_WORKSPACE_MULTIPLE" in codes(report("--repo", str(repo)))


def test_the_worst_workspace_sets_the_exit_code(repo: Path):
    path = repo / "projects" / "app" / "bundles" / "project-bundle.yaml"
    path.write_text(path.read_text().replace("description: app\n", ""))
    data = report("--repo", str(repo))
    assert data["workspaces"][0]["summary"]["status"] == "valid"
    assert data["workspaces"][1]["summary"]["status"] == "failed"
    assert run("--repo", str(repo)).exit_code == 1


# ------------------------------------------------------------- reserved names (D-33)


def test_reserved_directories_are_not_read_under_strict(repo: Path):
    for name in ("plan", "test-plan", "qa"):
        write(repo / "domain" / name / "notes.yaml", "id: [not valid yaml")
        scd(repo / "domain" / name, "company")  # would be a duplicate id if read
        concept(repo / "domain" / name, "qa")  # would be a reserved bundle name if read
    result = run("--repo", str(repo), "--strict")
    assert result.exit_code == 0, result.output
    assert codes(report("--repo", str(repo))) == []


def test_reserved_directory_names_below_the_workspace_root_are_read(repo: Path):
    scd(repo / "domain" / "context" / "plan", "company")
    assert "DUPLICATE_ID" in codes(report("--repo", str(repo)))


@pytest.mark.parametrize("bundle_id, stem", [("qa", "qa"), ("test-plan", "rules"), ("x", "plan")])
def test_reserved_bundle_names_are_errors(repo: Path, bundle_id: str, stem: str):
    ws = repo / "projects" / "app"
    scd(ws, bundle_id)
    concept(ws, bundle_id, stem=stem)
    assert run("--repo", str(repo)).exit_code == 1
    assert "RESERVED_BUNDLE_NAME" in codes(report("--repo", str(repo)))


def test_reserved_bundle_name_is_reported_in_bundle_mode(tmp_path: Path):
    scd(tmp_path, "qa")
    path = concept(tmp_path, "qa")
    assert "RESERVED_BUNDLE_NAME" in codes(report("--bundle", str(path)))


# ---------------------------------------------------------------- duplicate ids (D-43)


def test_two_scds_with_one_id_are_duplicates(repo: Path):
    scd(repo / "domain", "copy", scd_id="scd:project:company")
    assert run("--repo", str(repo)).exit_code == 1
    assert "DUPLICATE_ID" in codes(report("--repo", str(repo)))


def test_two_bundle_files_at_one_version_are_duplicates(repo: Path):
    concept(repo / "domain", "company", stem="company-copy")
    assert "DUPLICATE_ID" in codes(report("--repo", str(repo)))


def test_snapshots_of_two_versions_are_not_duplicates(repo: Path):
    ws = repo / "domain"
    for version in ("1.0.0", "1.1.0"):
        concept(ws, "company", version=version, stem=f"company-v{version}")
        write(
            ws / "bundles" / "concepts" / f"company-v{version}-MANIFEST.yaml",
            yaml.safe_dump(
                {
                    "version": version,
                    "bundle": {"id": "bundle:company"},
                    "approval": {"approved_by": "Jane Doe <jane@structuredcontext.dev>"},
                }
            ),
        )
    found = codes(report("--repo", str(repo)))
    assert "DUPLICATE_ID" not in found
    assert "MANIFEST_SCHEMA_INVALID" not in found


# --------------------------------------------------------- workspace config (D-03, D-04)


def test_config_name_must_match_the_workspace(repo: Path):
    write(repo / "projects" / "app" / ".scs" / "config", "bundle_type: project\nname: other\n")
    assert run("--repo", str(repo)).exit_code == 1
    assert codes(report("--repo", str(repo))) == ["CONFIG_NAME_MISMATCH"]


def test_a_0_6_project_name_key_is_still_read(repo: Path):
    write(
        repo / "projects" / "app" / ".scs" / "config",
        "bundle_type: project\nproject_name: app\n",
    )
    assert run("--repo", str(repo), "--strict").exit_code == 0


def test_an_unreadable_config_is_an_error(repo: Path):
    write(repo / "projects" / "app" / ".scs" / "config", "- not\n- a mapping\n")
    assert "WORKSPACE_CONFIG_INVALID" in codes(report("--repo", str(repo)))


def test_the_legacy_ontology_location_is_info_and_passes_strict(repo: Path):
    shutil.copy(ONTOLOGY, write(repo / "domain" / "domain" / "domain-manifest.yaml", ""))
    result = run("--repo", str(repo), "--strict")
    assert result.exit_code == 0, result.output
    assert codes(report("--repo", str(repo))) == ["ONTOLOGY_LEGACY_LOCATION"]


def test_the_ontology_location_carries_no_info(repo: Path):
    shutil.copy(ONTOLOGY, write(repo / "domain" / "ontology" / "domain-manifest.yaml", ""))
    assert codes(report("--repo", str(repo))) == []


# ------------------------------------------------------ version manifests (D-28, D-36)


def manifest(approved_by=None, **extra) -> dict:
    data = {"version": "1.0.0", "bundle": {"id": "bundle:company"}, "approval": {}}
    if approved_by is not None:
        data["approval"]["approved_by"] = approved_by
    data.update(extra)
    return data


@pytest.mark.parametrize(
    "approved_by", [None, "", "role:quality-manager", "role:qm <qm@example.com>", "jane@x.com"]
)
def test_the_manifest_schema_requires_a_person_approver(approved_by):
    errors = list(Draft202012Validator(MANIFEST_SCHEMA).iter_errors(manifest(approved_by)))
    assert errors


def test_the_manifest_schema_accepts_a_person_without_digest_or_tools_version():
    data = manifest("Jane Doe <jane@structuredcontext.dev>")
    assert list(Draft202012Validator(MANIFEST_SCHEMA).iter_errors(data)) == []
    data.update(content_digest="sha256:" + "0" * 64, tools_version="0.7.0")
    assert list(Draft202012Validator(MANIFEST_SCHEMA).iter_errors(data)) == []


def test_repository_mode_checks_version_manifests(repo: Path):
    path = repo / "domain" / "bundles" / "concepts" / "company-v1.0.0-MANIFEST.yaml"
    write(path, yaml.safe_dump(manifest("role:quality-manager")))
    assert run("--repo", str(repo)).exit_code == 1
    assert set(codes(report("--repo", str(repo)))) == {"MANIFEST_SCHEMA_INVALID"}


def test_pre_0_7_manifests_are_history(repo: Path):
    path = repo / "domain" / "bundles" / "concepts" / "VERSION-1.0.0-MANIFEST.yaml"
    write(path, yaml.safe_dump(manifest("jane@example.com")))
    assert run("--repo", str(repo), "--strict").exit_code == 0


# -------------------------------------------------------------------- check registry


def test_a_check_registered_elsewhere_runs_and_info_keeps_exit_0(repo: Path):
    seen = []

    @checks.register("test-only")
    def check(context: CheckContext):
        seen.append(context.workspace.name if context.workspace else None)
        result = ValidationResult("test")
        result.add_info(ValidationInfo("note", level="test", code="ONTOLOGY_LEGACY_LOCATION"))
        return result

    try:
        result = run("--repo", str(repo), "--strict")
        assert result.exit_code == 0, result.output
        assert seen == ["domain", "app"]
        data = report("--repo", str(repo), "--strict")
        assert data["summary"]["total_infos"] == 2
        assert data["summary"]["status"] == "valid"
    finally:
        checks.unregister("test-only")
