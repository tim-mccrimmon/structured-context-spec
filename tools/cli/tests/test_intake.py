"""The intake record, `derived_from`, and review findings (WP-07): D-07, D-20, D-28, D-77, D-78.
Schema cases without the CLI are in tools/scd-validator/tests/test_intake_schema.py."""

# ruff: noqa: F811  (tests take the imported `repo` fixture as an argument)

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from test_maintain import (
    codes,
    conforms,
    envelope,
    fill,
    repo,  # noqa: F401  (the fixture)
    run,
    validate,
)

PERSON = "Jane Doe <jane@acme-health.org>"
ANSWER = (
    "id: q-boundaries-1\n"
    "question: Anything AI tools must never do?\n"
    "answer: Never use a personal AI account for client work.\n"
    "answered_by: role:owner\n"
    "answered_at: 2026-10-20T14:12:00Z\n"
)
FINDING = [
    "intake",
    "record-finding",
    "--kind",
    "technical-risk",
    "--target",
    "scd:project:prohibited#NO-001",
    "--finding",
    "The prohibition has no approved alternative.",
]


def record(workspace: Path) -> dict:
    return yaml.safe_load((workspace / "intake.yaml").read_text())


def derive(scd: Path, *entries: str) -> None:
    """Fill the SCD's prohibition and give it `derived_from` entries (YAML flow mappings)."""
    fill(scd)
    lines = "".join(f"\n        - {e}" for e in entries)
    scd.write_text(
        scd.read_text().replace('"personal AI accounts"', f'"x"\n      derived_from:{lines}')
    )


# ------------------------------------------------------------------ the writers


def test_intake_set_conforms_on_create_and_modify(repo: Path):
    app = repo / "projects" / "app"
    data = conforms(repo, "intake", "set", "audience", "individual")
    assert data["changes"] == [{"action": "create", "path": "projects/app/intake.yaml"}]
    conforms(repo, "intake", "set", "data", "[PHI, PII]")
    assert record(app) == {
        "intake_version": "1.0",
        "scs_version": "0.7.0",
        "audience": "individual",
        "data": ["PHI", "PII"],
    }


def test_intake_set_reads_stdin_and_upserts_by_key(repo: Path):
    app = repo / "projects" / "app"
    assert envelope(run("intake", "set", "answers", "-", "--json", input=ANSWER))["ok"]
    changed = ANSWER.replace("Never use", "Do not use")
    data = envelope(run("intake", "set", "answers", "-", "--json", input=changed))
    assert data["result"]["entry"] == "replaced"
    run("intake", "set", "approvers", f"{{person: {PERSON}, role: Owner}}")
    run("intake", "set", "approvers", "{person: 'role:reviewer'}")
    run("intake", "set", "approvers", f"{{person: {PERSON}, role: Lead}}")
    saved = record(app)
    assert [a["answer"] for a in saved["answers"]] == [
        "Do not use a personal AI account for client work."
    ]
    assert saved["answers"][0]["answered_at"] == "2026-10-20T14:12:00Z"
    assert saved["approvers"] == [
        {"person": PERSON, "role": "Lead"},
        {"person": "role:reviewer"},
    ]
    assert list(saved) == ["intake_version", "scs_version", "approvers", "answers"]


def test_an_answer_without_a_time_gets_the_current_one(repo: Path):
    timeless = "\n".join(ANSWER.splitlines()[:-1])
    assert envelope(run("intake", "set", "answers", "-", "--json", input=timeless))["ok"]
    stamp = record(repo / "projects" / "app")["answers"][0]["answered_at"]
    assert isinstance(stamp, str) and stamp.endswith("Z")


@pytest.mark.parametrize(
    "field, value, code, exit_code",
    [
        ("review_findings", "[]", "INTAKE_FIELD_RESERVED", 3),
        ("scs_version", "0.8.0", "INTAKE_FIELD_RESERVED", 3),
        ("colour", "blue", "INTAKE_SCHEMA_INVALID", 1),
        ("ontology", "hipaa", "INTAKE_SCHEMA_INVALID", 1),
        ("owner", "jane@acme-health.org", "INTAKE_SCHEMA_INVALID", 1),
        ("approvers", "{role: Owner}", "INTAKE_SCHEMA_INVALID", 1),
    ],
)
def test_intake_set_refuses_an_invalid_change(repo: Path, field, value, code, exit_code):
    app = repo / "projects" / "app"
    run("intake", "set", "audience", "individual")
    before = (app / "intake.yaml").read_bytes()
    result = run("intake", "set", field, value, "--json")
    data = envelope(result)
    assert result.exit_code == exit_code and codes(data) == [code]
    assert data["changes"] == []
    assert (app / "intake.yaml").read_bytes() == before


def test_record_finding_conforms_and_numbers_findings(repo: Path):
    decided = ["--decided-by", PERSON, "--decided-at", "2026-10-20T14:40:00Z"]
    data = conforms(repo, *FINDING, "--decision", "deferred", *decided)
    assert data["result"]["id"] == "rf-1"
    data = conforms(
        repo, *FINDING, "--decision", "kept", "--rationale", "Intended", "--decided-by", "role:qa"
    )
    assert data["result"] == {"id": "rf-2", "entry": "added", "path": "projects/app/intake.yaml"}
    conforms(repo, *FINDING, "--id", "rf-1", "--decision", "changed", *decided)
    findings = record(repo / "projects" / "app")["review_findings"]
    assert [(f["id"], f["decision"]) for f in findings] == [("rf-1", "changed"), ("rf-2", "kept")]
    assert findings[1]["decided_at"].endswith("Z")


def test_record_finding_needs_a_rationale_to_keep(repo: Path):
    result = run(*FINDING, "--decision", "kept", "--decided-by", PERSON, "--json")
    data = envelope(result)
    assert result.exit_code == 1 and codes(data) == ["INTAKE_SCHEMA_INVALID"]
    assert "rationale" in data["diagnostics"][0]["message"]
    assert not (repo / "projects" / "app" / "intake.yaml").exists()


def test_record_finding_never_takes_the_decider_from_git(repo: Path, tmp_path: Path, monkeypatch):
    (tmp_path / "gitconfig").write_text(
        "[user]\n\tname = Git User\n\temail = git@acme-health.org\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    result = run(*FINDING, "--decision", "deferred", "--json")
    data = envelope(result)
    assert result.exit_code == 3 and codes(data) == ["NO_INPUT"]
    assert data["diagnostics"][0]["suggestion"] == {"decided_by": "Git User <git@acme-health.org>"}
    assert not (repo / "projects" / "app" / "intake.yaml").exists()


def test_the_writers_act_on_the_named_workspace(repo: Path):
    assert run("intake", "set", "audience", "individual", "--workspace", "domain").exit_code == 0
    assert (repo / "domain" / "intake.yaml").is_file()
    assert not (repo / "projects" / "app" / "intake.yaml").exists()


# ------------------------------------------------------------------ validation


def test_derived_from_resolves_against_the_workspaces_intake(repo: Path):
    app = repo / "projects" / "app"
    derive(
        app / "context" / "project" / "prohibited.yaml",
        "{intake: q-boundaries-1}",
        "{source: doc-sop}",
    )
    code, diagnostics = validate(repo, "--strict")
    unresolved = [d for d in diagnostics if d["code"] == "DERIVED_FROM_UNRESOLVED"]
    assert code == 2 and len(unresolved) == 2
    assert {d["path"] for d in unresolved} == {"projects/app/context/project/prohibited.yaml"}

    run("intake", "set", "answers", "-", input=ANSWER)
    code, diagnostics = validate(repo, "--strict")
    assert code == 2 and [
        d["message"] for d in diagnostics if d["code"] == "DERIVED_FROM_UNRESOLVED"
    ] == [
        "NO-001: derived_from source 'doc-sop' is not among the source_documents in the "
        "workspace's intake.yaml"
    ]

    run("intake", "set", "source_documents", "{id: doc-sop, title: AI use SOP}")
    code, diagnostics = validate(repo, "--strict")
    assert code == 0, diagnostics

    # The Domain's record does not resolve the Project's items.
    (app / "intake.yaml").rename(repo / "domain" / "intake.yaml")
    assert "DERIVED_FROM_UNRESOLVED" in codes({"diagnostics": validate(repo, "--strict")[1]})


def test_derived_from_with_both_intake_and_source_is_an_error(repo: Path):
    app = repo / "projects" / "app"
    derive(app / "context" / "project" / "prohibited.yaml", "{intake: q-1, source: doc-1}")
    code, diagnostics = validate(repo)
    assert code == 1
    assert any(
        d["code"] == "SCHEMA_SCD_INVALID" and "derived_from" in d["message"] for d in diagnostics
    ), diagnostics


def test_an_invalid_intake_record_is_reported_in_each_workspace(repo: Path):
    (repo / "domain" / "intake.yaml").write_text(
        "intake_version: '1.0'\nscs_version: 0.7.0\nprofile: x\n"
    )
    (repo / "projects" / "app" / "intake.yaml").write_text("answers: [\n")
    code, diagnostics = validate(repo)
    invalid = sorted(d["path"] for d in diagnostics if d["code"] == "INTAKE_SCHEMA_INVALID")
    assert code == 1 and invalid == ["domain/intake.yaml", "projects/app/intake.yaml"]


def test_compiled_output_never_contains_derived_from(repo: Path):
    app = repo / "projects" / "app"
    derive(app / "context" / "project" / "prohibited.yaml", "{intake: q-boundaries-1}")
    run("intake", "set", "answers", "-", input=ANSWER)
    result = run("compile", "bundles/project-bundle.yaml", "--allow-draft", "--stdout")
    assert result.exit_code == 0, result.output
    assert "Prohibited: x." in result.stdout
    assert "derived_from" not in result.stdout and "q-boundaries-1" not in result.stdout
