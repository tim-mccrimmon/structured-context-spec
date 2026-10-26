"""Empty SCDs (D-70): an SCD with no prohibitions, directives, or facts contributes nothing to a
compiled artifact. Reported as info, so a fresh scaffold still passes --strict; the agent reads
it and removes the SCD or fills it in."""

from __future__ import annotations

from typing import Optional

from ..utils import ValidationInfo, ValidationResult
from . import CheckContext, register
from ._shared import shown

COMPILED = ("prohibitions", "directives", "facts")


def is_empty(scd: dict) -> bool:
    content = scd.get("content")
    content = content if isinstance(content, dict) else {}
    return not any(content.get(key) for key in COMPILED)


@register("empty-scds")
def check(context: CheckContext) -> Optional[ValidationResult]:
    result = ValidationResult("empty_scds")
    for scd_id, found in sorted(context.index.scds.items()):
        path, data = found[0]
        if is_empty(data):
            result.add_info(
                ValidationInfo(
                    f"{scd_id} has no prohibitions, directives, or facts, so it contributes "
                    "nothing to a compiled artifact; fill it in or remove it",
                    level="scd",
                    scd_id=scd_id,
                    file_path=shown(path),
                    code="SCD_EMPTY",
                )
            )
    return result
