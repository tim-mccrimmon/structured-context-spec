"""The workspace's intake record against schema/intake/intake-schema.json, and `derived_from`
resolution against it (RFC 0002 sections 4 and 5, D-20). Each workspace is checked against its
own `intake.yaml`."""

from __future__ import annotations

from typing import Any, Optional, Tuple

import yaml

from ..intake import derived_from, ids, load, schema_errors, workspace_record
from ..utils import ValidationError, ValidationResult, ValidationWarning
from . import CheckContext, register
from ._shared import shown


def _record(context: CheckContext) -> Tuple[Any, Optional[str]]:
    """The workspace's record (None when absent) and why it could not be read, if it could not."""
    path = workspace_record(context.workspace_root)
    if path is None:
        return None, None
    try:
        return load(path), None
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        return None, str(e)


@register("intake-record")
def check_record(context: CheckContext) -> Optional[ValidationResult]:
    path = workspace_record(context.workspace_root)
    if path is None or context.schema_dir is None:
        return None
    result = ValidationResult("intake")
    data, problem = _record(context)
    messages = [f"Cannot read the intake record: {problem}"] if problem else []
    messages += [] if problem else schema_errors(data, context.schema_dir)
    for message in messages:
        result.add_error(
            ValidationError(message, file_path=shown(path), code="INTAKE_SCHEMA_INVALID")
        )
    return result


@register("derived-from")
def check_derived_from(context: CheckContext) -> Optional[ValidationResult]:
    data, problem = _record(context)
    if problem:
        return None  # the intake-record check reports it; every id would read as unresolved
    known = {"intake": ids(data, "answers"), "source": ids(data, "source_documents")}
    where = {"intake": "answers", "source": "source_documents"}
    result = ValidationResult("derived_from")
    for scd_id, found in sorted(context.index.scds.items()):
        path, scd = found[0]
        for entry in derived_from(scd):
            for key in ("intake", "source"):
                value = entry.get(key)
                if value is None or str(value) in known[key]:
                    continue
                reason = (
                    f"is not among the {where[key]} in the workspace's intake.yaml"
                    if data is not None
                    else "cannot resolve: the workspace has no intake.yaml"
                )
                result.add_warning(
                    ValidationWarning(
                        f"{entry['item']}: derived_from {key} '{value}' {reason}",
                        level="provenance",
                        scd_id=scd_id,
                        file_path=shown(path),
                        code="DERIVED_FROM_UNRESOLVED",
                    )
                )
    return result
