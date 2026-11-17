"""Placeholder provenance (D-71): a `created_by` that names no one, in a working SCD or bundle.
Released snapshots are not reported; they cannot change."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple

from ..names import is_snapshot
from ..provenance import is_placeholder
from ..utils import ValidationResult, ValidationWarning
from . import CheckContext, register
from ._shared import shown


def _documents(context: CheckContext) -> Iterable[Tuple[str, Any, Dict[str, Any]]]:
    for bundles in context.index.bundles.values():
        for bundle in bundles:
            if not is_snapshot(bundle.path):
                yield bundle.id, bundle.path, bundle.data
    for scd_id, found in context.index.scds.items():
        for path, data in found:
            yield scd_id, path, data


@register("placeholder-provenance")
def check(context: CheckContext) -> Optional[ValidationResult]:
    result = ValidationResult("provenance")
    for doc_id, path, data in sorted(_documents(context), key=lambda d: str(d[1])):
        provenance = data.get("provenance")
        created_by = provenance.get("created_by") if isinstance(provenance, dict) else None
        if is_placeholder(created_by):
            result.add_warning(
                ValidationWarning(
                    f"provenance.created_by '{created_by}' is a placeholder, not a person, team, "
                    "or organization; set it to who created this document (Name <email>)",
                    level="provenance",
                    scd_id=doc_id,
                    file_path=shown(path),
                    code="PROVENANCE_PLACEHOLDER",
                )
            )
    return result
