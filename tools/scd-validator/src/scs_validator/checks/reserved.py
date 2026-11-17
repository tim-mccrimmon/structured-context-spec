"""Reserved bundle names (D-33): plan, test-plan, and qa belong to a later release."""

from __future__ import annotations

from typing import Optional

from ..names import reserved_bundle_name
from ..utils import ValidationError, ValidationResult
from . import CheckContext, register
from ._shared import shown


@register("reserved-bundle-names")
def check(context: CheckContext) -> Optional[ValidationResult]:
    result = ValidationResult("reserved_names")
    for bundles in context.index.bundles.values():
        for bundle in bundles:
            name = reserved_bundle_name(bundle.id, bundle.path)
            if name:
                result.add_error(
                    ValidationError(
                        f"Bundle name '{name}' is reserved for a later release; rename the bundle",
                        scd_id=bundle.id,
                        file_path=shown(bundle.path),
                        code="RESERVED_BUNDLE_NAME",
                    )
                )
    return result
