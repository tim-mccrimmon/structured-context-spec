"""Section owners (D-92). A working section bundle (a concept bundle, or a Project bundle that
lists SCDs directly) with no owner role, or whose role the workspace's intake record does not
map to a person, is info, so a fresh scaffold still passes --strict; versioning makes it an
error. The latest released version of each section is a warning when its role is not held by
anyone now, so --strict catches a released section that has lost its accountable person."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from ..gitrepo import split_version
from ..names import is_snapshot
from ..owners import problem
from ..resolver import ResolvedBundle
from ..utils import ValidationInfo, ValidationResult, ValidationWarning
from . import CheckContext, register
from ._shared import shown
from .intake import _record

RELEASED_MESSAGE = {
    "MISSING": "{id} version {version} names no owner, so no one is accountable for this "
    "released section; set an owner and release a new version",
    "UNMAPPED": "{id} version {version} is owned by role '{role}', which no one in the "
    "workspace's intake.yaml holds now; add it with 'scs intake set owners'",
}


def _latest_released(context: CheckContext) -> Dict[str, ResolvedBundle]:
    latest: Dict[str, Tuple[Tuple[int, ...], ResolvedBundle]] = {}
    for bundle_id, found in context.index.bundles.items():
        for bundle in found:
            if not is_snapshot(bundle.path) or not bundle.version:
                continue
            try:
                key = split_version(bundle.version)
            except ValueError:
                continue
            if bundle_id not in latest or key > latest[bundle_id][0]:
                latest[bundle_id] = (key, bundle)
    return {bundle_id: bundle for bundle_id, (_, bundle) in latest.items()}


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
            result.add_info(
                ValidationInfo(
                    message,
                    level="owners",
                    scd_id=bundle.id,
                    file_path=shown(bundle.path),
                    code=f"BUNDLE_OWNER_{kind}",
                )
            )
    released = _latest_released(context)
    for bundle_id in sorted(released):
        bundle = released[bundle_id]
        found = problem(bundle.data, intake)
        if found:
            kind, _ = found
            result.add_warning(
                ValidationWarning(
                    RELEASED_MESSAGE[kind].format(
                        id=bundle_id, version=bundle.version, role=bundle.data.get("owner")
                    ),
                    level="owners",
                    scd_id=bundle_id,
                    file_path=shown(bundle.path),
                    code=f"RELEASED_OWNER_{kind}",
                )
            )
    return result
