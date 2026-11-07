"""Section owners (D-92): every working concept bundle, and every Project bundle that lists SCDs
directly, names an owner role that the workspace's intake record maps to a person. Released
snapshots are not reported; they cannot change. Versioning makes these errors."""

from __future__ import annotations

from typing import Optional

from ..names import is_snapshot
from ..owners import problem
from ..utils import ValidationResult, ValidationWarning
from . import CheckContext, register
from ._shared import shown
from .intake import _record


@register("owners")
def check(context: CheckContext) -> Optional[ValidationResult]:
    intake, unreadable = _record(context)
    if unreadable:
        return None  # the intake-record check reports it; every role would read as unmapped
    if context.workspace is None and intake is None:
        return None  # a bundle outside a 0.7 workspace (an example, a 0.6 layout)
    result = ValidationResult("owners")
    bundles = [b for found in context.index.bundles.values() for b in found]
    for bundle in sorted(bundles, key=lambda b: str(b.path)):
        if is_snapshot(bundle.path):
            continue
        found = problem(bundle.data, intake)
        if found:
            kind, message = found
            result.add_warning(
                ValidationWarning(
                    message,
                    level="owners",
                    scd_id=bundle.id,
                    file_path=shown(bundle.path),
                    code=f"BUNDLE_OWNER_{kind}",
                )
            )
    return result
