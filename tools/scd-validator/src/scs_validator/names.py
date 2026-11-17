"""Bundle names and the names a workspace reserves (RFC 0002 §9, D-33).

`bundle_name` is the one place a bundle's name is derived from its id; version manifests,
snapshots, and tags are all named from it (`<workspace>/<bundle-name>-v<version>`).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

# Directories a workspace reserves at its root for a later release. 0.7 neither creates nor
# reads them.
RESERVED_DIRS = frozenset({"plan", "test-plan", "qa"})
# Bundle names reserved for the same release, so its tags cannot collide with a bundle's.
RESERVED_BUNDLE_NAMES = frozenset({"plan", "test-plan", "qa"})

SNAPSHOT_RE = re.compile(r"^(?P<name>.+)-v(?P<version>\d+\.\d+\.\d+)$")
# A version tag made by SCS 0.7: `<workspace>/<bundle-name>-v<version>` (D-02, D-39). Tags without
# the workspace qualifier predate 0.7 and are history (D-54).
VERSION_TAG_RE = re.compile(
    r"^(?P<workspace>[A-Za-z0-9._-]+)/(?P<name>[A-Za-z0-9._-]+)-v(?P<version>\d+\.\d+\.\d+)$"
)


def version_tag(workspace: str, name: str, version: str) -> str:
    return f"{workspace}/{name}-v{version}"


def snapshot_name(name: str, version: str) -> str:
    """The snapshot file of a version, beside its manifest (D-43)."""
    return f"{name}-v{version}.yaml"


def manifest_name(name: str, version: str) -> str:
    """The version manifest file (D-02)."""
    return f"{name}-v{version}-MANIFEST.yaml"


def is_snapshot(path: Path) -> bool:
    """A versioned snapshot, by its file name (D-43), rather than a working document."""
    return SNAPSHOT_RE.match(path.stem) is not None


def bundle_name(bundle_id: str, path: Optional[Path] = None) -> str:
    """The name part of `bundle:<name>`, falling back to the file stem when the id has none."""
    parts = bundle_id.split(":")
    if len(parts) >= 2 and parts[0] == "bundle" and parts[1]:
        return parts[1]
    return path.stem if path is not None else bundle_id


def reserved_bundle_name(bundle_id: str, path: Optional[Path] = None) -> Optional[str]:
    """The reserved name a bundle uses, by its id's name part or its file stem, if any."""
    candidates = [bundle_name(bundle_id)]
    if path is not None:
        stem = path.stem
        match = SNAPSHOT_RE.match(stem)
        candidates.append(match.group("name") if match else stem)
    for name in candidates:
        if name in RESERVED_BUNDLE_NAMES:
            return name
    return None
