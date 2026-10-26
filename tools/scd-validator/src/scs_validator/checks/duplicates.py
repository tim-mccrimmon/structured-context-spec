"""Duplicate ids within a workspace (D-43).

SCDs are keyed by id. Bundles are keyed by id and version, so a working bundle and the
snapshots of its released versions are separate documents, not duplicates.
"""

from __future__ import annotations

from typing import Optional

from ..utils import ValidationError, ValidationResult
from . import CheckContext, register
from ._shared import shown


@register("duplicate-ids")
def check(context: CheckContext) -> Optional[ValidationResult]:
    result = ValidationResult("duplicate_ids")
    for bundle_id, bundles in context.index.bundles.items():
        by_version: dict = {}
        for bundle in bundles:
            by_version.setdefault(bundle.version, []).append(bundle.path)
        for version, paths in by_version.items():
            if len(paths) > 1:
                label = f"{bundle_id} version {version}" if version else bundle_id
                result.add_error(
                    ValidationError(
                        f"{label} is defined in {len(paths)} files: "
                        + ", ".join(shown(p) for p in paths),
                        scd_id=bundle_id,
                        code="DUPLICATE_ID",
                    )
                )
    for scd_id, found in context.index.scds.items():
        if len(found) > 1:
            result.add_error(
                ValidationError(
                    f"{scd_id} is defined in {len(found)} files: "
                    + ", ".join(shown(p) for p, _ in found),
                    scd_id=scd_id,
                    code="DUPLICATE_ID",
                )
            )
    return result
