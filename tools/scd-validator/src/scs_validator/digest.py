"""Content digests of versioned bundles (spec/0.7/bundle-format.md §7.6, RFC 0002 §11).

A bundle's content digest covers its manifest, every SCD it lists, and the content digest of
every bundle it imports. Each document is parsed and serialized canonically before hashing,
so edits to comments or formatting don't change the digest and edits to content do.

`scs bundle version` records the digest in the bundle's version manifest; the validator and
the compiler recompute it and report a mismatch.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import yaml

from .names import bundle_name
from .resolver import PACKAGED_META, BundleTree, Index, ResolvedBundle

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class DigestError(Exception):
    """The digest can't be computed (an import cycle)."""


def _plain(data: Any) -> Any:
    """Parsed YAML as JSON values: keys as strings, dates and timestamps as ISO 8601."""
    if isinstance(data, dict):
        return {str(k): _plain(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_plain(v) for v in data]
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    return data


def canonical_json(data: Any) -> str:
    """Sorted keys, no insignificant whitespace, non-ASCII characters unescaped."""
    return json.dumps(_plain(data), sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest_of(data: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


@dataclass
class ContentDigest:
    digest: str
    bundle: ResolvedBundle
    manifest: str
    scds: Dict[str, Optional[str]]
    imports: Dict[str, Optional["ContentDigest"]]
    scd_paths: Dict[str, Path] = field(default_factory=dict)

    def walk(self) -> List["ContentDigest"]:
        """This bundle and every bundle it imports, transitively, each once."""
        seen: Dict[Path, ContentDigest] = {}

        def visit(d: ContentDigest) -> None:
            if d.bundle.path in seen:
                return
            seen[d.bundle.path] = d
            for child in d.imports.values():
                if child:
                    visit(child)

        visit(self)
        return list(seen.values())

    def inputs(self) -> Tuple[Dict[str, Any], Dict[str, Path]]:
        """Every bundle manifest and SCD in the tree with its digest, as recorded in a version
        manifest's `content_inputs`, and the file each came from. A bundle or SCD that could
        not be found is recorded as null. The record is for naming what changed; the content
        digest alone is what is verified."""
        bundles: Dict[str, Optional[str]] = {}
        scds: Dict[str, Optional[str]] = {}
        paths: Dict[str, Path] = {}
        for d in self.walk():
            key = f"{d.bundle.id}:{d.bundle.version}" if d.bundle.version else d.bundle.id
            bundles[key] = d.manifest
            paths[key] = d.bundle.path
            scds.update(d.scds)
            paths.update(d.scd_paths)
            bundles.update({ref: None for ref, child in d.imports.items() if child is None})
        record = {"bundles": dict(sorted(bundles.items())), "scds": dict(sorted(scds.items()))}
        return record, paths


def content_digest(
    bundle: ResolvedBundle,
    index: Index,
    _stack: Tuple[str, ...] = (),
    _memo: Optional[Dict[Path, ContentDigest]] = None,
) -> ContentDigest:
    """Compute the content digest of `bundle`, resolving its SCDs and imports in `index`.

    SCDs are taken in id order, imports in reference order. An SCD or import that can't be
    found contributes null, so adding it later changes the digest.
    """
    if bundle.id in _stack:
        raise DigestError(f"Circular bundle imports: {' -> '.join(_stack + (bundle.id,))}")
    memo: Dict[Path, ContentDigest] = {} if _memo is None else _memo

    scds: Dict[str, Optional[str]] = {}
    scd_paths: Dict[str, Path] = {}
    for ref in sorted({str(r) for r in bundle.data.get("scds") or []}):
        found = index.scds.get(ref)
        scds[ref] = digest_of(found[0][1]) if found else None
        if found:
            scd_paths[ref] = found[0][0]

    imports: Dict[str, Optional[ContentDigest]] = {}
    for ref in sorted({str(r) for r in bundle.data.get("imports") or []}):
        target, mismatch = index.find_bundle(ref)
        if target is None or mismatch:
            imports[ref] = None
            continue
        if target.path not in memo:
            memo[target.path] = content_digest(target, index, _stack + (bundle.id,), memo)
        imports[ref] = memo[target.path]

    manifest = digest_of(bundle.data)
    digest = digest_of(
        [
            manifest,
            [[k, v] for k, v in scds.items()],
            [[k, v.digest if v else None] for k, v in imports.items()],
        ]
    )
    return ContentDigest(digest, bundle, manifest, scds, imports, scd_paths)


def version_manifest_names(bundle_id: str, version: str) -> List[str]:
    """File names a bundle's version manifest may have, newest convention first."""
    name = bundle_name(bundle_id)
    return [f"{name}-v{version}-MANIFEST.yaml", f"VERSION-{version}-MANIFEST.yaml"]


def find_version_manifest(bundle: ResolvedBundle) -> Optional[Tuple[Path, Dict[str, Any]]]:
    """The version manifest written for this bundle's id and version, next to the bundle."""
    if not bundle.version or bundle.version == "DRAFT":
        return None
    for name in version_manifest_names(bundle.id, bundle.version):
        path = bundle.path.parent / name
        if not path.is_file():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and (data.get("bundle") or {}).get("id") == bundle.id:
            if str(data.get("version", bundle.version)) == bundle.version:
                return path, data
    return None


@dataclass
class Verification:
    bundle: ResolvedBundle
    manifest: Path
    status: str  # "verified", "mismatch", or "unrecorded" (no content_digest in the manifest)
    changes: List[str] = field(default_factory=list)


def _shown(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def changes(
    actual: ContentDigest, recorded: Any, display: Optional[Callable[[Path], str]] = None
) -> List[str]:
    """The bundles and SCDs whose content differs from the recorded `content_inputs`, each
    named by its file (shown with `display`) and id."""
    if not isinstance(recorded, dict):
        return []
    _shown_path = display or _shown
    current, paths = actual.inputs()
    out: List[str] = []
    for kind in ("bundles", "scds"):
        before, after = recorded.get(kind) or {}, current[kind]
        for key in sorted(set(before) | set(after)):
            if key not in before:
                out.append(f"{key} (added)")
            elif key not in after:
                out.append(f"{key} (removed)")
            elif before[key] != after[key]:
                out.append(
                    f"{key} (not found)"
                    if after[key] is None
                    else f"{_shown_path(paths[key])} ({key})"
                )
    return out


def verify(bundle: ResolvedBundle, index: Index) -> Optional[Verification]:
    """Check a versioned bundle against its version manifest. None when it has none."""
    found = find_version_manifest(bundle)
    if not found:
        return None
    path, manifest = found
    recorded = manifest.get("content_digest")
    if not recorded:
        return Verification(bundle, path, "unrecorded")
    actual = content_digest(bundle, index)
    if actual.digest == recorded:
        return Verification(bundle, path, "verified")
    return Verification(bundle, path, "mismatch", changes(actual, manifest.get("content_inputs")))


def tree_index(tree: BundleTree) -> Index:
    """The index the tree was resolved with, or a fresh one with the resolver's defaults."""
    return tree.index or Index([PACKAGED_META, tree.project_root])


def verify_tree(tree: BundleTree) -> List[Verification]:
    """Verify every versioned bundle in the tree that has a version manifest. Bundles in an
    import cycle are skipped; the cycle is reported elsewhere."""
    index = tree_index(tree)
    results = []
    for bundle in tree.bundles:
        try:
            result = verify(bundle, index)
        except DigestError:
            continue
        if result:
            results.append(result)
    return results
