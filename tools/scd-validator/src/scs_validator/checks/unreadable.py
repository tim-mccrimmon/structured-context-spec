"""Unreadable files: a YAML file in the workspace that does not parse is skipped by the index,
so an SCD in it is never seen. Reported as a warning naming the file and the parse error, so
the author can fix it or delete it. A bundle listing an SCD that lives in such a file also gets
BUNDLE_SCD_UNRESOLVED. Files other checks already read and report are left to them."""

from __future__ import annotations

from typing import Optional

from ..intake import workspace_record
from ..utils import ValidationResult, ValidationWarning
from ..workspace import LEGACY_ONTOLOGY_MANIFEST, ONTOLOGY_MANIFEST
from . import CheckContext, register
from ._shared import shown


@register("unreadable-files")
def check(context: CheckContext) -> Optional[ValidationResult]:
    reported = {tree.root.path.resolve() for tree in context.trees}
    if context.workspace is not None:
        reported |= {path.resolve() for path in context.workspace.root_bundles()}
    reported |= {
        (context.workspace_root / p).resolve()
        for p in (ONTOLOGY_MANIFEST, LEGACY_ONTOLOGY_MANIFEST)
    }
    record = workspace_record(context.workspace_root)
    if record is not None:
        reported.add(record.resolve())
    result = ValidationResult("unreadable_files")
    for path, reason in context.index.unreadable:
        if path.resolve() in reported:
            continue
        result.add_warning(
            ValidationWarning(
                f"{shown(path)} could not be read as YAML ({reason}) and was skipped; "
                "fix it or delete it",
                level="file",
                file_path=shown(path),
                code="WORKSPACE_FILE_UNREADABLE",
            )
        )
    return result
