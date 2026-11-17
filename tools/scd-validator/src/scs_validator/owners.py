"""Section owners (D-92): the role accountable for a section, mapped to a person in the
workspace's intake record.

A concept bundle, or a Project bundle that lists SCDs directly, names an owner role in its
`owner` field. The workspace's `intake.yaml` `owners` list maps each role to a person.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def needs_owner(bundle: Dict[str, Any]) -> bool:
    """A bundle that holds a section of content: a concept bundle, or a Project bundle that
    lists SCDs directly."""
    kind = bundle.get("type")
    return kind == "concept" or (kind == "project" and bool(bundle.get("scds")))


def owner_map(intake: Any) -> Dict[str, Dict[str, Any]]:
    """The intake record's owners by role."""
    entries = intake.get("owners") if isinstance(intake, dict) else None
    if not isinstance(entries, list):
        return {}
    return {str(e["role"]): e for e in entries if isinstance(e, dict) and e.get("role") is not None}


def problem(bundle: Dict[str, Any], intake: Any) -> Optional[Tuple[str, str]]:
    """(`MISSING` or `UNMAPPED`, message) when the bundle needs an owner it does not have, or
    names a role the intake does not map; else None."""
    if not needs_owner(bundle):
        return None
    bundle_id = bundle.get("id", "the bundle")
    role = bundle.get("owner")
    if not role:
        return (
            "MISSING",
            f"{bundle_id} names no owner, the role accountable for this section; set one with "
            "'scs bundle set-owner <role>'",
        )
    if str(role) not in owner_map(intake):
        return (
            "UNMAPPED",
            f"{bundle_id} is owned by role '{role}', which the workspace's intake.yaml does not "
            f"map to a person; add it with 'scs intake set owners'",
        )
    return None
