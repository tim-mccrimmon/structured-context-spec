"""Write a workspace's intake record (RFC 0002 section 4). `scs intake set` and
`scs intake record-finding` are its only writers (D-07); the agent does not edit the file.

Every change is validated against the intake schema before anything is written, so the record
on disk is always valid. The file is written whole, keys in the schema's order.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from scs_validator.envelope import SCS_VERSION
from scs_validator.intake import (
    INTAKE_FILE,
    INTAKE_VERSION,
    SCHEMA,
    load,
    normalize,
    schema_errors,
)
from scs_validator.utils import resolve_schema_dir

from scs_tools import identity
from scs_tools.machine import EXIT_USAGE, CommandError, Envelope
from scs_tools.maintain import Edit, _dump
from scs_tools.workspace import repository_root, select_workspace

KEYED = {"answers": "id", "source_documents": "id", "approvers": "person"}  # D-77
ENGINE_FIELDS = ("intake_version", "scs_version")
FINDING_ID_RE = re.compile(r"^rf-(\d+)$")


def _schema_dir() -> Path:
    found, searched = resolve_schema_dir(None)
    if found is None:
        raise CommandError(
            "SCHEMA_DIR_NOT_FOUND", f"No SCS schema directory found (searched {searched})"
        )
    return found


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Record:
    """A workspace's intake record, read but not yet written."""

    def __init__(self, workspace: Optional[str]):
        self.workspace = select_workspace(workspace).resolve()
        self.root = repository_root(self.workspace) or self.workspace
        self.path = self.workspace / INTAKE_FILE
        self.data: Dict[str, Any] = {}
        if self.path.is_file():
            try:
                data = load(self.path)
            except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
                raise CommandError(
                    "INTAKE_SCHEMA_INVALID",
                    f"Cannot read the intake record: {e}",
                    path=self.shown(),
                )
            if data is not None and not isinstance(data, dict):
                raise CommandError(
                    "INTAKE_SCHEMA_INVALID",
                    "The intake record is not a mapping",
                    path=self.shown(),
                )
            self.data = data or {}
        self.data.setdefault("intake_version", INTAKE_VERSION)
        self.data.setdefault("scs_version", SCS_VERSION)

    def shown(self) -> str:
        return self.path.relative_to(self.root).as_posix()

    def upsert(self, field: str, key: str, entry: Dict[str, Any]) -> str:
        """Replace the entry in list `field` whose `key` matches, or append; `replaced` or
        `added`."""
        entries = self.data.get(field)
        entries = list(entries) if isinstance(entries, list) else []
        for i, existing in enumerate(entries):
            if isinstance(existing, dict) and existing.get(key) == entry.get(key):
                entries[i] = entry
                self.data[field] = entries
                return "replaced"
        entries.append(entry)
        self.data[field] = entries
        return "added"

    def write(self, envelope: Envelope, dry_run: bool) -> None:
        schema_dir = _schema_dir()
        errors = schema_errors(self.data, schema_dir)
        if errors:
            raise CommandError(
                "INTAKE_SCHEMA_INVALID",
                "The change would make the intake record invalid: " + "; ".join(errors),
                path=self.shown(),
            )
        schema = json.loads(schema_dir.joinpath(*SCHEMA).read_text(encoding="utf-8"))
        order = list(schema["properties"])
        ordered = {k: self.data[k] for k in sorted(self.data, key=order.index)}
        edit = Edit(self.root)
        edit.writes[self.path] = _dump(ordered)
        edit.apply(envelope, dry_run)


def _parse(value: str, stdin: Optional[str]) -> Any:
    text = stdin if value == "-" else value
    if text is None or not text.strip():
        raise CommandError("INPUT_EMPTY", "No value given", exit_code=EXIT_USAGE)
    try:
        return normalize(yaml.safe_load(text))
    except yaml.YAMLError as e:
        raise CommandError("USAGE_ERROR", f"The value is not YAML: {e}", exit_code=EXIT_USAGE)


def set_field(
    envelope: Envelope,
    workspace: Optional[str],
    field: str,
    value: str,
    stdin: Optional[str],
    dry_run: bool,
) -> None:
    """`scs intake set FIELD VALUE` (D-77)."""
    if field == "review_findings":
        raise CommandError(
            "INTAKE_FIELD_RESERVED",
            "review_findings is written by scs intake record-finding",
            exit_code=EXIT_USAGE,
        )
    if field in ENGINE_FIELDS:
        raise CommandError(
            "INTAKE_FIELD_RESERVED", f"{field} is set by the engine", exit_code=EXIT_USAGE
        )
    parsed = _parse(value, stdin)
    record = Record(workspace)
    if field in KEYED and isinstance(parsed, dict):
        key = KEYED[field]
        if field == "answers":
            parsed.setdefault("answered_at", _now())
        outcome = record.upsert(field, key, parsed)
        envelope.result = {"field": field, key: parsed.get(key), "entry": outcome}
    else:
        record.data[field] = parsed
        envelope.result = {"field": field}
    record.write(envelope, dry_run)
    envelope.result["path"] = record.shown()


def _next_finding_id(findings: List[Any]) -> str:
    numbers = [
        int(m.group(1))
        for f in findings
        if isinstance(f, dict) and (m := FINDING_ID_RE.match(str(f.get("id", ""))))
    ]
    return f"rf-{max(numbers, default=0) + 1}"


def record_finding(
    envelope: Envelope,
    workspace: Optional[str],
    finding_id: Optional[str],
    kind: str,
    target: str,
    finding: str,
    cites: List[str],
    decision: str,
    rationale: Optional[str],
    decided_by: Optional[str],
    decided_at: Optional[str],
    dry_run: bool,
) -> None:
    """`scs intake record-finding`: upsert one review finding and the user's decision."""
    decider = (decided_by or "").strip()
    if not decider:
        suggested = identity.person_suggestion()
        raise CommandError(
            "NO_INPUT",
            "A decision names who made it: pass --decided-by 'Name <email>' or role:<name>. "
            "It is never taken from git configuration",
            exit_code=EXIT_USAGE,
            suggestion={"decided_by": suggested} if suggested else None,
        )
    record = Record(workspace)
    findings = record.data.get("review_findings")
    findings = findings if isinstance(findings, list) else []
    entry: Dict[str, Any] = {
        "id": finding_id or _next_finding_id(findings),
        "kind": kind,
        "target": target,
        "finding": finding,
    }
    if cites:
        entry["cites"] = list(cites)
    entry["decision"] = decision
    if rationale:
        entry["rationale"] = rationale
    entry["decided_by"] = decider
    entry["decided_at"] = decided_at or _now()
    outcome = record.upsert("review_findings", "id", entry)
    envelope.result = {"id": entry["id"], "entry": outcome}
    record.write(envelope, dry_run)
    envelope.result["path"] = record.shown()
