"""Workspaces and Domain repositories (RFC 0002 §9).

A Domain repository holds one Domain workspace under `domain/` and zero or more Project
workspaces under `projects/<name>/`. A workspace is a directory with a `.scs/config` file.
Its name is `domain` or its directory name under `projects/` (D-03).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .names import SNAPSHOT_RE

CONFIG = Path(".scs") / "config"
ONTOLOGY_MANIFEST = Path("ontology") / "domain-manifest.yaml"
LEGACY_ONTOLOGY_MANIFEST = Path("domain") / "domain-manifest.yaml"
ROOT_BUNDLE_TYPES = ("domain", "project")


@dataclass
class Workspace:
    name: str
    root: Path
    config: Dict[str, str] = field(default_factory=dict)
    config_error: Optional[str] = None

    @property
    def bundle_type(self) -> Optional[str]:
        return self.config.get("bundle_type")

    @property
    def config_name(self) -> Optional[str]:
        """`name` (0.7), else `project_name` (0.6 scaffolds) (D-06)."""
        return self.config.get("name") or self.config.get("project_name")

    def ontology_manifest(self) -> Optional[Path]:
        """The ontology manifest, at the 0.7 location or else the 0.6 one (D-04)."""
        for relative in (ONTOLOGY_MANIFEST, LEGACY_ONTOLOGY_MANIFEST):
            if (self.root / relative).is_file():
                return self.root / relative
        return None

    def root_bundles(self) -> List[Path]:
        """Working Domain or Project bundle files in `bundles/`, not version snapshots."""
        found = []
        for path in sorted((self.root / "bundles").glob("*.yaml")):
            if SNAPSHOT_RE.match(path.stem) or path.stem.endswith("-MANIFEST"):
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError, UnicodeDecodeError):
                found.append(path)  # let bundle validation report it
                continue
            if isinstance(data, dict) and data.get("type") in ROOT_BUNDLE_TYPES:
                found.append(path)
        return found


def read_config(path: Path) -> Dict[str, str]:
    """`.scs/config` as a mapping of strings. Raises ValueError if it is not one."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        raise ValueError(str(e)) from e
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("expected key: value lines")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def load_workspace(name: str, root: Path) -> Workspace:
    workspace = Workspace(name=name, root=root)
    try:
        workspace.config = read_config(root / CONFIG)
    except ValueError as e:
        workspace.config_error = str(e)
    return workspace


def is_repository(path: Path) -> bool:
    """A Domain repository has `domain/` or `projects/<name>/` holding a workspace."""
    if (path / "domain" / CONFIG).is_file():
        return True
    projects = path / "projects"
    return projects.is_dir() and any((p / CONFIG).is_file() for p in projects.iterdir())


def discover_workspaces(repo: Path) -> List[Workspace]:
    """The Domain workspace, then each Project workspace by name."""
    found = []
    if (repo / "domain" / CONFIG).is_file():
        found.append(load_workspace("domain", repo / "domain"))
    projects = repo / "projects"
    if projects.is_dir():
        for path in sorted(p for p in projects.iterdir() if (p / CONFIG).is_file()):
            found.append(load_workspace(path.name, path))
    return found
