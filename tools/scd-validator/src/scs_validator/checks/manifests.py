"""Version manifests against schema/manifest/version-manifest-schema.json, in repository
mode (D-28, D-36). Manifests named VERSION-<version>-MANIFEST.yaml predate 0.7 and are
history (D-54); they are not checked.
"""

from __future__ import annotations

import json
from typing import Optional

import yaml
from jsonschema import Draft202012Validator

from ..utils import ValidationError, ValidationResult
from . import CheckContext, register
from ._shared import shown

SCHEMA = ("manifest", "version-manifest-schema.json")


@register("version-manifests")
def check(context: CheckContext) -> Optional[ValidationResult]:
    if context.workspace is None or context.schema_dir is None:
        return None
    manifests = [
        p
        for p in sorted((context.workspace_root / "bundles").rglob("*-MANIFEST.yaml"))
        if not p.name.startswith("VERSION-")
    ]
    if not manifests:
        return None
    schema_path = context.schema_dir.joinpath(*SCHEMA)
    validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    result = ValidationResult("version_manifests")
    for path in manifests:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
            result.add_error(
                ValidationError(
                    f"Cannot read version manifest: {e}",
                    file_path=shown(path),
                    code="MANIFEST_SCHEMA_INVALID",
                )
            )
            continue
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
            where = ".".join(str(p) for p in error.absolute_path) or "(root)"
            result.add_error(
                ValidationError(
                    f"{where}: {error.message}",
                    file_path=shown(path),
                    code="MANIFEST_SCHEMA_INVALID",
                )
            )
    return result
