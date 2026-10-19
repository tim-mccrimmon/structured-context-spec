"""Bundle tree resolution: find a bundle's imports and SCDs on disk.

Any bundle type can be the root. Bundles and SCDs are found by their `id`, not their file
name, by indexing every YAML file under the bundle's project root. The project root is the
bundle's directory, walking up past `bundles/`, `domains/` and `concepts/` directories.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

BUNDLE_REF = re.compile(r"^bundle:(?P<name>[a-zA-Z0-9._-]+)(?::(?P<version>\d+\.\d+\.\d+))?$")
LAYOUT_DIRS = {"bundles", "domains", "concepts"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}


@dataclass
class ResolvedBundle:
    id: str
    type: Optional[str]
    version: Optional[str]
    data: Dict[str, Any]
    path: Path


@dataclass
class ResolvedSCD:
    ref: str
    data: Dict[str, Any]
    path: Path
    bundle_id: str


@dataclass
class ImportEdge:
    importer: ResolvedBundle
    ref: str
    target: Optional[ResolvedBundle]
    version_mismatch: bool = False


@dataclass
class BundleTree:
    root: ResolvedBundle
    project_root: Path
    bundles: List[ResolvedBundle] = field(default_factory=list)
    edges: List[ImportEdge] = field(default_factory=list)
    scds: List[ResolvedSCD] = field(default_factory=list)
    unresolved_scds: List[Tuple[str, str]] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)

    @property
    def unresolved_imports(self) -> List[ImportEdge]:
        return [e for e in self.edges if e.target is None]

    def direct_imports(self) -> List[ImportEdge]:
        return [e for e in self.edges if e.importer is self.root]


def parse_bundle_ref(ref: str) -> Optional[Tuple[str, Optional[str]]]:
    """Split `bundle:<name>[:<version>]` into (`bundle:<name>`, version)."""
    m = BUNDLE_REF.match(ref)
    if not m:
        return None
    return f"bundle:{m.group('name')}", m.group("version")


def find_project_root(bundle_path: Path) -> Path:
    root = bundle_path.resolve().parent
    while root.name in LAYOUT_DIRS and root.parent != root:
        root = root.parent
    return root


def _yaml_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.suffix not in (".yaml", ".yml") or not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


class Index:
    """Bundles and SCDs under one or more directories, keyed by `id`."""

    def __init__(self, roots: Iterable[Path]):
        self.bundles: Dict[str, List[ResolvedBundle]] = {}
        self.scds: Dict[str, List[Tuple[Path, Dict[str, Any]]]] = {}
        for root in roots:
            if root.is_dir():
                self._scan(root)

    def _scan(self, root: Path) -> None:
        for path in _yaml_files(root):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError, UnicodeDecodeError):
                continue
            if not isinstance(data, dict) or not isinstance(data.get("id"), str):
                continue
            doc_id = data["id"]
            if doc_id.startswith("bundle:"):
                self.bundles.setdefault(doc_id, []).append(
                    ResolvedBundle(
                        id=doc_id,
                        type=data.get("type"),
                        version=str(data["version"]) if "version" in data else None,
                        data=data,
                        path=path,
                    )
                )
            elif doc_id.startswith("scd:"):
                self.scds.setdefault(doc_id, []).append((path, data))

    def find_bundle(self, ref: str) -> Tuple[Optional[ResolvedBundle], bool]:
        """Return (bundle, version_mismatch) for an import reference."""
        parsed = parse_bundle_ref(ref)
        if not parsed:
            return None, False
        bundle_id, version = parsed
        candidates = self.bundles.get(bundle_id, [])
        if not candidates:
            return None, False
        if version is None:
            return candidates[0], False
        for c in candidates:
            if c.version == version:
                return c, False
        return candidates[0], True


def resolve(
    bundle_path: Path,
    extra_search_dirs: Iterable[Path] = (),
    index: Optional[Index] = None,
) -> BundleTree:
    """Resolve the import tree and SCDs of the bundle at `bundle_path`.

    `extra_search_dirs` are searched after the project root (e.g. a packaged meta bundle).
    Bundles appear in depth-first import order with the root first; SCDs in the order their
    bundles list them, imports before the importing bundle's own SCDs.
    """
    bundle_path = Path(bundle_path)
    project_root = find_project_root(bundle_path)
    if index is None:
        index = Index([project_root, *extra_search_dirs])

    data = yaml.safe_load(bundle_path.read_text(encoding="utf-8")) or {}
    root = ResolvedBundle(
        id=data.get("id", "unknown"),
        type=data.get("type"),
        version=str(data["version"]) if "version" in data else None,
        data=data,
        path=bundle_path,
    )
    tree = BundleTree(root=root, project_root=project_root)
    seen_scds: Dict[str, bool] = {}

    def visit(bundle: ResolvedBundle, stack: List[str]) -> None:
        tree.bundles.append(bundle)
        for ref in bundle.data.get("imports") or []:
            target, mismatch = index.find_bundle(str(ref))
            tree.edges.append(ImportEdge(bundle, str(ref), target, mismatch))
            if target is None:
                continue
            if target.id in stack:
                tree.cycles.append(stack[stack.index(target.id) :] + [target.id])
                continue
            if any(b.path == target.path for b in tree.bundles):
                continue
            visit(target, stack + [target.id])
        for ref in bundle.data.get("scds") or []:
            ref = str(ref)
            if ref in seen_scds:
                continue
            seen_scds[ref] = True
            found = index.scds.get(ref)
            if not found:
                tree.unresolved_scds.append((bundle.id, ref))
                continue
            path, scd = found[0]
            tree.scds.append(ResolvedSCD(ref=ref, data=scd, path=path, bundle_id=bundle.id))

    visit(root, [root.id])
    return tree
