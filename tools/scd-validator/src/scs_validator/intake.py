"""The intake record, `intake.yaml` at a workspace's root (RFC 0002 section 4, D-07, D-35).

YAML reads an unquoted `2026-10-20T14:12:00Z` as a timestamp, so values are normalized to ISO
8601 strings before schema validation; the schema then sees the same text the file holds.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from jsonschema import Draft202012Validator

INTAKE_FILE = "intake.yaml"
INTAKE_VERSION = "1.0"
SCHEMA = ("intake", "intake-schema.json")


def normalize(data: Any) -> Any:
    """`data` with every YAML timestamp as an ISO 8601 string; UTC written as `Z`."""
    if isinstance(data, dict):
        return {k: normalize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [normalize(v) for v in data]
    if isinstance(data, datetime.datetime):
        if data.tzinfo is None:
            return data.isoformat()
        text = data.isoformat()
        return text[:-6] + "Z" if text.endswith("+00:00") else text
    if isinstance(data, datetime.date):
        return data.isoformat()
    return data


def load(path: Path) -> Any:
    """The record at `path`, normalized. Raises OSError, UnicodeDecodeError, or yaml.YAMLError."""
    return normalize(yaml.safe_load(path.read_text(encoding="utf-8")))


def schema_errors(data: Any, schema_dir: Path) -> List[str]:
    """Schema violations as `<where>: <message>`, in document order."""
    schema = json.loads(schema_dir.joinpath(*SCHEMA).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(data), key=lambda e: list(map(str, e.path))
    )
    return [
        f"{'.'.join(str(p) for p in error.absolute_path) or '(root)'}: {error.message}"
        for error in errors
    ]


def ids(data: Any, key: str) -> Set[str]:
    """The `id`s of the entries in list `key` (`answers`, `source_documents`)."""
    entries = data.get(key) if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return set()
    return {str(e["id"]) for e in entries if isinstance(e, dict) and e.get("id") is not None}


def derived_from(scd: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every `derived_from` entry in an SCD, with the item it is on:
    `{"item": <item id>, "intake"|"source": <id>}`."""
    content = scd.get("content")
    if not isinstance(content, dict):
        return []
    found = []
    for key in ("prohibitions", "directives", "facts"):
        items = content.get(key)
        for item in items if isinstance(items, list) else []:
            entries = item.get("derived_from") if isinstance(item, dict) else None
            for entry in entries if isinstance(entries, list) else []:
                if isinstance(entry, dict):
                    found.append({"item": item.get("id"), **entry})
    return found


def workspace_record(workspace_root: Path) -> Optional[Path]:
    path = workspace_root / INTAKE_FILE
    return path if path.is_file() else None
