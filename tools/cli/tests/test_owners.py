"""Section owners (D-92): an owner role on each section's bundle, mapped to a person in the
intake record; a warning in validation, an error at versioning."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pytest
import yaml
from click.testing import CliRunner, Result
from scs_validator.commands.validate import validate as validator_cmd

from scs_tools.cli import cli

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schema"
AUTHOR = ["--author", "Test Author", "--email", "test@structuredcontext.dev"]
APPROVER = "Sam Lee <sam@structuredcontext.dev>"
QUALITY = "{role: quality, person: Pat Kim <pat@acme.example>, title: VP Quality}"
CONCEPT = "bundles/concepts/prohibited.yaml"


def run(*args: str, input: str = "") -> Result:
    return CliRunner().invoke(cli, list(args), input=input)


def run_json(*args: str) -> Tuple[int, Dict]:
    result = run(*args, "--json")
    return result.exit_code, json.loads(result.stdout)


def codes(data: Dict) -> List[str]:
    return [d["code"] for d in data["diagnostics"]]


def validate(repo: Path) -> List[Dict]:
    result = CliRunner().invoke(
        validator_cmd, ["--json", "--schema-dir", str(SCHEMA), "--repo", str(repo)]
    )
    return json.loads(result.stdout)["diagnostics"]


def strict_exit(repo: Path) -> int:
    result = CliRunner().invoke(
        validator_cmd, ["--strict", "--json", "--schema-dir", str(SCHEMA), "--repo", str(repo)]
    )
    return result.exit_code


def new_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ontology: str) -> Path:
    monkeypatch.setenv("SCS_SCHEMA_DIR", str(SCHEMA))
    result = run(
        "new", "domain", "acme", "--dir", str(tmp_path), "--ontology", ontology, *AUTHOR,
        "--no-interactive",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    repo = tmp_path / "acme-context"
    monkeypatch.chdir(repo / "domain")
    return repo


def owners_of(workspace: Path) -> Dict[str, str]:
    found = {}
    for path in sorted((workspace / "bundles" / "concepts").glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        found[path.stem] = data.get("owner")
    return found


@pytest.mark.parametrize("ontology", ["cdmo", "sdlc", "mca"])
def test_every_scaffolded_concept_has_a_default_owner_role(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ontology: str
):
    repo = new_repo(tmp_path, monkeypatch, ontology)
    owners = owners_of(repo / "domain")
    assert owners and all(owners.values()), owners
    assert owners["prohibited"] == "ai-governance"
    assert owners["company"] == "executive"


def test_a_personal_domain_has_one_owner_role(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = new_repo(tmp_path, monkeypatch, "personal")
    assert set(owners_of(repo / "domain").values()) == {"owner"}


def test_unmapped_and_missing_owners_are_info_until_mapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = new_repo(tmp_path, monkeypatch, "cdmo")
    diagnostics = validate(repo)
    unmapped = [d for d in diagnostics if d["code"] == "BUNDLE_OWNER_UNMAPPED"]
    assert unmapped and all(d["severity"] == "info" for d in unmapped)
    assert strict_exit(repo) == 0  # a fresh scaffold still passes --strict

    code, data = run_json("status")
    roles = data["result"]["workspaces"][0]["owners"]["unmapped_roles"]
    assert "quality" in roles and "ai-governance" in roles
    for role in roles:
        code, data = run_json(
            "intake",
            "set",
            "owners",
            f"{{role: {role}, person: P <p-{role}@acme.example>}}",
        )
        assert code == 0, data
    assert "BUNDLE_OWNER_UNMAPPED" not in [d["code"] for d in validate(repo)]
    code, data = run_json("status")
    owners = data["result"]["workspaces"][0]["owners"]
    assert owners["unmapped_roles"] == [] and owners["missing"] == []
    qms = next(s for s in owners["sections"] if s["bundle"] == "bundle:qms-records")
    assert qms["owner"] == "quality" and qms["person"] == "P <p-quality@acme.example>"

    concept = repo / "domain" / "bundles" / "concepts" / "qms-records.yaml"
    concept.write_text(concept.read_text().replace("owner: quality\n", ""))
    missing = [d for d in validate(repo) if d["code"] == "BUNDLE_OWNER_MISSING"]
    assert [d["path"] for d in missing] == ["domain/bundles/concepts/qms-records.yaml"]


def test_owners_upsert_by_role(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = new_repo(tmp_path, monkeypatch, "cdmo")
    run("intake", "set", "owners", QUALITY)
    run("intake", "set", "owners", "{role: quality, person: Lee Wu <lee@acme.example>}")
    intake = yaml.safe_load((repo / "domain" / "intake.yaml").read_text())
    assert intake["owners"] == [{"role": "quality", "person": "Lee Wu <lee@acme.example>"}]
    code, data = run_json("intake", "set", "owners", "{role: quality, person: role:qa}")
    assert code != 0 and "INTAKE_SCHEMA_INVALID" in codes(data)


def test_versioning_needs_an_owner_mapped_to_a_person(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = new_repo(tmp_path, monkeypatch, "personal")
    scd = repo / "domain" / "context" / "project" / "prohibited.yaml"
    scd.write_text(
        scd.read_text().replace(
            "  prohibitions: []",
            '  prohibitions:\n    - id: NO-001\n      kind: tool\n      subject: "pastebins"',
        )
    )
    args = (
        "bundle",
        "version",
        "-b",
        CONCEPT,
        "-v",
        "1.0.0",
        "--approved-by",
        APPROVER,
    )
    code, data = run_json(*args)
    assert code == 1 and "VERSION_OWNER_UNMAPPED" in codes(data)

    concept = repo / "domain" / CONCEPT
    concept.write_text(concept.read_text().replace("owner: owner\n", ""))
    code, data = run_json(*args)
    assert code == 1 and "VERSION_OWNER_MISSING" in codes(data)

    code, data = run_json("bundle", "set-owner", "owner", "-b", CONCEPT)
    assert code == 0, data
    run("intake", "set", "owners", "{role: owner, person: Jo Doe <jo@acme.example>}")
    code, data = run_json(*args)
    assert code == 0, data

    # A change of person needs no new version: the intake is outside the content digest.
    run("intake", "set", "owners", "{role: owner, person: Al Roe <al@acme.example>}")
    diagnostics = validate(repo)
    assert "CONTENT_DIGEST_MISMATCH" not in [d["code"] for d in diagnostics]
    assert not [d for d in diagnostics if d["code"].startswith("RELEASED_OWNER")]

    # A released section whose role no one holds now fails --strict.
    intake_path = repo / "domain" / "intake.yaml"
    intake = yaml.safe_load(intake_path.read_text())
    intake["owners"] = []
    intake_path.write_text(yaml.safe_dump(intake, sort_keys=False))
    released = [d for d in validate(repo) if d["code"] == "RELEASED_OWNER_UNMAPPED"]
    assert [(d["severity"], d["path"]) for d in released] == [
        ("warning", "domain/bundles/concepts/prohibited-v1.0.0.yaml")
    ]
    assert strict_exit(repo) == 2


def test_set_owner_replaces_or_inserts_and_refuses_what_does_not_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    repo = new_repo(tmp_path, monkeypatch, "cdmo")
    path = repo / "domain" / "bundles" / "concepts" / "security.yaml"
    before = path.read_text()
    code, data = run_json("bundle", "set-owner", "ciso", "-b", str(path), "--dry-run")
    assert code == 0 and data["changes"][0]["action"] == "modify"
    assert path.read_text() == before

    code, data = run_json("bundle", "set-owner", "ciso", "-b", str(path))
    assert code == 0 and data["result"] == {
        "bundle": "bundle:security",
        "owner": "ciso",
        "was": "security",
    }
    text = path.read_text()
    assert text.count("owner:") == 1 and "owner: ciso\n" in text
    assert text.replace("owner: ciso", "owner: security") == before

    path.write_text(text.replace("owner: ciso\n", ""))
    run("bundle", "set-owner", "quality", "-b", str(path))
    lines = path.read_text().splitlines()
    assert lines[lines.index("owner: quality") - 1].startswith("description:")

    code, data = run_json("bundle", "set-owner", "Quality Lead", "-b", str(path))
    assert code == 3 and codes(data) == ["OWNER_ROLE_INVALID"]
    code, data = run_json("bundle", "set-owner", "quality")  # the Domain bundle
    assert code != 0 and codes(data) == ["OWNER_NOT_APPLICABLE"]


def test_add_bundle_owner_goes_with_new(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    new_repo(tmp_path, monkeypatch, "cdmo")
    code, data = run_json("add", "bundle", "security", "--owner", "ciso", *AUTHOR)
    assert code == 3 and codes(data) == ["USAGE_ERROR"]
    code, data = run_json("add", "bundle", "grants", "--new", "--owner", "Bad Role", *AUTHOR)
    assert code == 3 and codes(data) == ["OWNER_ROLE_INVALID"]
