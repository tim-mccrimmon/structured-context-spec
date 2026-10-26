"""Workspace configuration in repository mode: `.scs/config` name (D-03) and the ontology
manifest's location (D-04)."""

from __future__ import annotations

from typing import Optional

from ..utils import ValidationError, ValidationInfo, ValidationResult
from ..workspace import CONFIG, LEGACY_ONTOLOGY_MANIFEST, ONTOLOGY_MANIFEST
from . import CheckContext, register
from ._shared import shown


@register("workspace-config")
def check(context: CheckContext) -> Optional[ValidationResult]:
    workspace = context.workspace
    if workspace is None:
        return None
    result = ValidationResult("workspace")
    config = shown(workspace.root / CONFIG)
    if workspace.config_error:
        result.add_error(
            ValidationError(
                f"Cannot read the workspace configuration: {workspace.config_error}",
                file_path=config,
                code="WORKSPACE_CONFIG_INVALID",
            )
        )
    elif workspace.config_name != workspace.name:
        found = f"'{workspace.config_name}'" if workspace.config_name else "no name"
        result.add_error(
            ValidationError(
                f"Workspace '{workspace.name}' has {found} in its configuration; "
                f"set name: {workspace.name}",
                file_path=config,
                code="CONFIG_NAME_MISMATCH",
            )
        )
    legacy = workspace.root / LEGACY_ONTOLOGY_MANIFEST
    if legacy.is_file() and not (workspace.root / ONTOLOGY_MANIFEST).is_file():
        result.add_info(
            ValidationInfo(
                f"The ontology manifest is at the 0.6 location; move it to {ONTOLOGY_MANIFEST}",
                level="workspace",
                file_path=shown(legacy),
                code="ONTOLOGY_LEGACY_LOCATION",
            )
        )
    return result
