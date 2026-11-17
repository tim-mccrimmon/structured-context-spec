"""Bundle tree resolution: find a bundle's imports and SCDs on disk.

Any bundle type can be the root. Bundles and SCDs are found by their `id`, not their file
name, by indexing every YAML file under the bundle's project root. The project root is the
bundle's directory, walking up past `bundles/`, `domains/` and `concepts/` directories.

The meta bundle published with the spec ships inside this package and is searched before
the project root, so `bundle:meta:<version>` resolves to the published copy wherever the
tools are installed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from .names import RESERVED_DIRS, is_snapshot

PACKAGED_META = Path(__file__).resolve().parent / "meta"
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
    index: Optional["Index"] = None

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
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        # Reserved directories at the root of a workspace are not read (RFC 0002 §9).
        if len(parts) > 1 and parts[0] in RESERVED_DIRS:
            continue
        yield path


def unreadable_reason(error: Exception) -> str:
    """A one-line reason a YAML file could not be read, with the line for a parse error."""
    if isinstance(error, yaml.MarkedYAMLError):
        mark = error.problem_mark or error.context_mark
        problem = error.problem or error.context or "invalid YAML"
        return f"line {mark.line + 1}: {problem}" if mark else problem
    if isinstance(error, UnicodeDecodeError):
        return "not UTF-8 text"
    return getattr(error, "strerror", None) or str(error)


class Index:
    """Bundles and SCDs under one or more directories, keyed by `id`."""

    def __init__(self, roots: Iterable[Path]):
        self.bundles: Dict[str, List[ResolvedBundle]] = {}
        self.scds: Dict[str, List[Tuple[Path, Dict[str, Any]]]] = {}
        self.unreadable: List[Tuple[Path, str]] = []  # YAML files skipped, with the reason
        for root in roots:
            if root.is_dir():
                self._scan(root)

    def _scan(self, root: Path) -> None:
        for path in _yaml_files(root):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
                self.unreadable.append((path, unreadable_reason(e)))
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
        """Return (bundle, version_mismatch) for an import reference.

        An unpinned reference resolves to the working bundle file, not a versioned snapshot; a
        pinned one to the snapshot of that version (D-17). A bundle with no working file (0.6
        layouts that keep only snapshots) resolves an unpinned reference to its first file.
        """
        parsed = parse_bundle_ref(ref)
        if not parsed:
            return None, False
        bundle_id, version = parsed
        candidates = self.bundles.get(bundle_id, [])
        if not candidates:
            return None, False
        working = [c for c in candidates if not is_snapshot(c.path)]
        if version is None:
            return (working or candidates)[0], False
        matching = [c for c in candidates if c.version == version]
        if matching:
            snapshots = [c for c in matching if is_snapshot(c.path)]
            return (snapshots or matching)[0], False
        return (working or candidates)[0], True


def resolve(
    bundle_path: Path,
    extra_search_dirs: Optional[Iterable[Path]] = None,
    index: Optional[Index] = None,
) -> BundleTree:
    """Resolve the import tree and SCDs of the bundle at `bundle_path`.

    `extra_search_dirs` are searched before the project root; by default, the packaged meta
    bundle. Pass `()` to search the project root only.
    Bundles appear in depth-first import order with the root first; SCDs in the order their
    bundles list them, imports before the importing bundle's own SCDs.
    """
    bundle_path = Path(bundle_path)
    project_root = find_project_root(bundle_path)
    if index is None:
        if extra_search_dirs is None:
            extra_search_dirs = (PACKAGED_META,)
        index = Index([*extra_search_dirs, project_root])

    data = yaml.safe_load(bundle_path.read_text(encoding="utf-8")) or {}
    root = ResolvedBundle(
        id=data.get("id", "unknown"),
        type=data.get("type"),
        version=str(data["version"]) if "version" in data else None,
        data=data,
        path=bundle_path,
    )
    tree = BundleTree(root=root, project_root=project_root, index=index)
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
