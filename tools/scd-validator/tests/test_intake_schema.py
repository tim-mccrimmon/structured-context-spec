"""The intake schema and `derived_from` in SCD items (WP-07, RFC 0002 sections 4, 5, 12). The
writers and repository checks are tested end to end in tools/cli/tests/test_intake.py."""

from __future__ import annotations

import copy
import datetime
import re
from pathlib import Path

import pytest
import yaml

from scs_validator.intake import derived_from, normalize, schema_errors
from scs_validator.schema_validator import SchemaValidator

REPO = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO / "schema"
RFC = REPO / "rfcs" / "RFC-0002-agent-mediated-scs.md"

PERSONAL = {
    "intake_version": "1.0",
    "scs_version": "0.7.0",
    "audience": "individual",
    "domain": "new",
    "workspace": "domain",
    "regulated": False,
    "ontology": "personal",
    "owner": "Jane Doe <jane@acme-health.org>",
    "boundaries": ["Never commit secrets or API keys"],
    "practices": ["Python with type hints", "Conventional commits"],
}

PROJECT = {
    "intake_version": "1.0",
    "scs_version": "0.7.0",
    "audience": "organization",
    "workspace": "infusion-pump-fw",
    "regulated": True,
    "ontology": "cdmo",
    "project": {
        "name": "infusion-pump-fw",
        "purpose": "Firmware for a volumetric infusion pump",
        "technology": ["C", "FreeRTOS"],
    },
    "risk": {
        "classification": "IEC 62304 software safety class C",
        "cites": ["std:iec-62304:2006-a1#4.3"],
    },
    "data": ["PHI"],
    "boundaries": ["No AI-generated code in the dose calculation module without review"],
    "approvers": [{"person": "role:software-quality-lead"}],
    "answers": [
        {
            "id": "q-risk-1",
            "question": "What is the software safety class?",
            "answer": "Class C",
            "answered_by": "role:software-quality-lead",
            "answered_at": "2026-10-21T09:00:00-05:00",
        }
    ],
}

FINDING = {
    "id": "rf-1",
    "kind": "missing-protection",
    "target": "scd:project:release-gates#RG-002",
    "finding": "No directive covers PHI in test fixtures.",
    "decision": "changed",
    "decided_by": "Jane Doe <jane@acme-health.org>",
    "decided_at": "2026-10-20T14:40:00Z",
}


def errors(data) -> list:
    return schema_errors(normalize(data), SCHEMA_DIR)


def rfc_example() -> dict:
    text = RFC.read_text(encoding="utf-8")
    block = re.search(r"```yaml\n(intake_version:.*?)```", text, re.S)
    assert block, "RFC 0002 section 4 example not found"
    return yaml.safe_load(block.group(1))


def test_the_rfc_example_validates():
    example = rfc_example()
    assert isinstance(example["answers"][0]["answered_at"], datetime.datetime)
    assert errors(example) == []


@pytest.mark.parametrize("record", [PERSONAL, PROJECT], ids=["personal", "project"])
def test_profile_fixtures_validate(record):
    assert errors(record) == []


def test_only_the_versions_are_required():
    assert errors({"intake_version": "1.0", "scs_version": "0.7.0"}) == []
    assert len(errors({})) == 2


@pytest.mark.parametrize("who", ["role:quality-manager", "Jane Doe <jane@acme-health.org>"])
def test_role_or_person_attribution(who):
    record = {**PROJECT, "review_findings": [{**FINDING, "decided_by": who}]}
    record["approvers"] = [{"person": who, "role": "Quality Manager"}]
    assert errors(record) == []


@pytest.mark.parametrize(
    "who", ["jane@acme-health.org", "Jane Doe", "role:", "role:Quality Manager", ""]
)
def test_other_attribution_fails(who):
    assert errors({**PROJECT, "approvers": [{"person": who}]})


def test_the_owner_is_a_person_not_a_role():
    """D-63: owner is a person identifier."""
    assert errors({**PERSONAL, "owner": "role:owner"})


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "style"},
        {"kind": "framework_conflict"},
        {"decision": "rejected"},
        {"decision": "kept"},  # kept without a rationale
        {"decided_by": None},
        {"decided_at": None},
        {"decided_at": "2026-10-20"},
        {"target": None},
    ],
)
def test_review_finding_rules(change):
    finding = copy.deepcopy(FINDING)
    for key, value in change.items():
        if value is None:
            del finding[key]
        else:
            finding[key] = value
    assert errors({**PROJECT, "review_findings": [finding]})


@pytest.mark.parametrize(
    "kind",
    [
        "framework-conflict",
        "missing-protection",
        "technical-risk",
        "ethical-risk",
        "layer-conflict",
    ],
)
def test_every_rfc_finding_kind_is_accepted(kind):
    kept = {**FINDING, "kind": kind, "decision": "kept", "rationale": "Accepted risk"}
    assert errors({**PROJECT, "review_findings": [kept]}) == []


def test_normalize_writes_timestamps_as_iso_strings():
    utc = datetime.datetime(2026, 10, 20, 14, 12, tzinfo=datetime.timezone.utc)
    offset = datetime.datetime(
        2026, 10, 20, 9, 12, tzinfo=datetime.timezone(datetime.timedelta(hours=-5))
    )
    assert normalize({"a": [utc, offset, datetime.date(2026, 10, 20)]}) == {
        "a": ["2026-10-20T14:12:00Z", "2026-10-20T09:12:00-05:00", "2026-10-20"]
    }


# ------------------------------------------------------------------ derived_from


def scd(derived) -> dict:
    return {
        "id": "scd:project:boundaries",
        "type": "project",
        "title": "Boundaries",
        "version": "0.1.0",
        "description": "Boundaries",
        "content": {
            "prohibitions": [
                {"id": "PU-003", "kind": "practice", "subject": "editing", "derived_from": derived}
            ],
            "directives": [{"id": "DC-007", "directive": "Redline.", "derived_from": derived}],
            "facts": [{"id": "F-1", "fact": "A fact.", "derived_from": derived}],
        },
        "provenance": {
            "created_by": "Jane Doe <jane@acme-health.org>",
            "created_at": "2026-10-20T14:12:00Z",
        },
    }


def scd_errors(derived) -> list:
    return SchemaValidator(SCHEMA_DIR).validate_scd(scd(derived)).errors


@pytest.mark.parametrize(
    "derived",
    [
        [{"intake": "q-boundaries-1"}],
        [{"source": "doc-qm", "locator": "section 4.2.5"}],
        [{"intake": "q-1"}, {"source": "doc-qm"}],
    ],
)
def test_derived_from_is_accepted_on_every_compiled_item(derived):
    assert scd_errors(derived) == []


@pytest.mark.parametrize(
    "derived",
    [
        [{"intake": "q-1", "source": "doc-qm"}],
        [{"locator": "section 1"}],
        [{"intake": "q-1", "note": "x"}],
        [{"intake": ""}],
        {"intake": "q-1"},
    ],
)
def test_malformed_derived_from_fails(derived):
    assert len(scd_errors(derived)) == 3  # one per item kind


def test_items_stay_closed():
    data = scd([{"intake": "q-1"}])
    data["content"]["directives"][0]["provenance"] = "x"
    assert SchemaValidator(SCHEMA_DIR).validate_scd(data).errors


def test_derived_from_entries_are_found_with_their_items():
    assert derived_from(scd([{"intake": "q-1"}])) == [
        {"item": "PU-003", "intake": "q-1"},
        {"item": "DC-007", "intake": "q-1"},
        {"item": "F-1", "intake": "q-1"},
    ]
