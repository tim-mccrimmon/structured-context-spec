"""`scs bundle diff`: what changed in a bundle between two versions, or a version and the working
tree (RFC 0002 section 7, D-41).

The diff covers the bundle's resolved tree, the content a compile of it would read: SCDs added
and removed; prohibitions, directives, and facts added, removed, and changed; citations added
and removed; and the imports of every bundle in the tree, added, removed, or re-pinned. Old
content comes from the version's tag. The summary is deterministic: every list is sorted, so the
same two inputs always give the same bytes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scs_validator import integrity
from scs_validator.envelope import diagnostics_from_results
from scs_validator.gitrepo import GitRepo, GitUnavailable, VersionTag, split_version
from scs_validator.names import SNAPSHOT_RE, bundle_name
from scs_validator.resolver import BundleTree, parse_bundle_ref, resolve
from scs_validator.utils import ValidationResult

from scs_tools.machine import CommandError, Envelope
from scs_tools.workspace import find_domain_repository, workspace_name

ITEM_KINDS = ("prohibitions", "directives", "facts")
WORKING = "working"


class DiffFailed(Exception):
    """A side could not be read; its diagnostics are already in the envelope."""


@dataclass
class Content:
    """One side of a diff. `scds` maps each SCD id to its data, or to None when the content is
    not recorded (a pre-0.7 snapshot holds the bundle file only)."""

    scds: Dict[str, Optional[Dict[str, Any]]] = field(default_factory=dict)
    imports: Dict[str, List[str]] = field(default_factory=dict)  # bundle id -> import refs


@dataclass
class Side:
    label: str  # a version, "working", or "empty"
    source: str  # "tag", "working", "empty", or "legacy-snapshot"
    content: Content
    tag: Optional[str] = None
    path: Optional[Path] = None  # the legacy snapshot


def content_of(tree: BundleTree, recorded: bool = True) -> Content:
    content = Content()
    for scd in tree.scds:
        content.scds[scd.ref] = scd.data if recorded else None
    for bundle in tree.bundles:
        content.imports[bundle.id] = [str(ref) for ref in bundle.data.get("imports") or []]
    return content


def _items(scd: Optional[Dict[str, Any]]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    body = (scd or {}).get("content")
    body = body if isinstance(body, dict) else {}
    found: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for kind in ITEM_KINDS:
        for n, entry in enumerate(body.get(kind) or []):
            if not isinstance(entry, dict):
                continue
            item_id = str(entry.get("id") or f"#{n + 1}")
            found[(kind, item_id)] = entry
    return found


def _citations(scd: Optional[Dict[str, Any]]) -> set:
    """(item id or "", citation) for the SCD's own cites and each item's."""
    if not scd:
        return set()
    cites = {("", str(c)) for c in scd.get("cites") or []}
    for (_, item_id), entry in _items(scd).items():
        cites |= {(item_id, str(c)) for c in entry.get("cites") or []}
    return cites


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _unversioned(ref: str) -> str:
    parsed = parse_bundle_ref(ref)
    return parsed[0] if parsed else ref


def _version_of(ref: str) -> Optional[str]:
    parsed = parse_bundle_ref(ref)
    return parsed[1] if parsed else None


def diff(old: Content, new: Content) -> Dict[str, Any]:
    """The structured diff from `old` to `new`; every list sorted."""
    added_scds = sorted(set(new.scds) - set(old.scds))
    removed_scds = sorted(set(old.scds) - set(new.scds))
    items: Dict[str, List[Dict[str, Any]]] = {"added": [], "removed": [], "changed": []}
    citations: Dict[str, List[Dict[str, Any]]] = {"added": [], "removed": []}
    not_compared: List[str] = []

    for scd_id in sorted(set(old.scds) | set(new.scds)):
        before, after = old.scds.get(scd_id), new.scds.get(scd_id)
        in_both = scd_id in old.scds and scd_id in new.scds
        if in_both and (before is None or after is None):
            not_compared.append(scd_id)
            continue
        old_items, new_items = _items(before), _items(after)
        for kind, item_id in sorted(set(new_items) - set(old_items)):
            items["added"].append({"scd": scd_id, "kind": kind, "id": item_id})
        for kind, item_id in sorted(set(old_items) - set(new_items)):
            items["removed"].append({"scd": scd_id, "kind": kind, "id": item_id})
        for key in sorted(set(old_items) & set(new_items)):
            a, b = old_items[key], new_items[key]
            fields = sorted(
                k for k in set(a) | set(b) if _canonical(a.get(k)) != _canonical(b.get(k))
            )
            if fields:
                items["changed"].append(
                    {"scd": scd_id, "kind": key[0], "id": key[1], "fields": fields}
                )
        old_cites, new_cites = _citations(before), _citations(after)
        for item_id, cite in sorted(new_cites - old_cites):
            citations["added"].append(_cite(scd_id, item_id, cite))
        for item_id, cite in sorted(old_cites - new_cites):
            citations["removed"].append(_cite(scd_id, item_id, cite))

    imports: Dict[str, List[Dict[str, Any]]] = {"added": [], "removed": [], "repinned": []}
    for bundle_id in sorted(set(old.imports) | set(new.imports)):
        before_refs = {_unversioned(r): r for r in old.imports.get(bundle_id, [])}
        after_refs = {_unversioned(r): r for r in new.imports.get(bundle_id, [])}
        for name in sorted(set(after_refs) - set(before_refs)):
            imports["added"].append({"bundle": bundle_id, "ref": after_refs[name]})
        for name in sorted(set(before_refs) - set(after_refs)):
            imports["removed"].append({"bundle": bundle_id, "ref": before_refs[name]})
        for name in sorted(set(before_refs) & set(after_refs)):
            if before_refs[name] != after_refs[name]:
                imports["repinned"].append(
                    {
                        "bundle": bundle_id,
                        "import": name,
                        "from": _version_of(before_refs[name]),
                        "to": _version_of(after_refs[name]),
                    }
                )

    result: Dict[str, Any] = {
        "scds": {"added": added_scds, "removed": removed_scds},
        "items": items,
        "citations": citations,
        "imports": imports,
    }
    result["changed"] = bool(
        added_scds or removed_scds or any(items.values()) or any(citations.values())
        or any(imports.values())
    )  # fmt: skip
    if not_compared:
        result["not_compared"] = not_compared
    return result


def _cite(scd_id: str, item_id: str, cite: str) -> Dict[str, Any]:
    entry: Dict[str, Any] = {"scd": scd_id, "cite": cite}
    if item_id:
        entry["item"] = item_id
    return entry


# ------------------------------------------------------------------ choosing the two sides


def _versions(repo: GitRepo, workspace: str, name: str) -> List[VersionTag]:
    tags = [t for t in repo.version_tags() if t.workspace == workspace and t.name == name]
    return sorted(tags, key=lambda t: split_version(t.version))


def _legacy_snapshot(bundle_file: Path) -> Optional[Tuple[str, Path]]:
    """The latest pre-0.7 snapshot beside the bundle, named `<file stem>-v<version>.yaml`."""
    found = []
    for path in bundle_file.parent.glob(f"{bundle_file.stem}-v*.yaml"):
        match = SNAPSHOT_RE.match(path.stem)
        if match and match.group("name") == bundle_file.stem:
            found.append((split_version(match.group("version")), match.group("version"), path))
    if not found:
        return None
    _, version, path = max(found)
    return version, path


def _tagged(envelope: Envelope, repo: GitRepo, tag: VersionTag) -> Content:
    checked = ValidationResult("versions")
    tagged = integrity.verify_tag(repo, tag, checked)
    if tagged is None or tagged.tree is None:
        envelope.diagnostics.extend(diagnostics_from_results([checked]))
        raise DiffFailed(tag.tag)
    return content_of(tagged.tree)


def sides(
    envelope: Envelope,
    bundle_file: Path,
    workspace_root: Path,
    from_version: Optional[str],
    to_version: str,
) -> Tuple[str, Side, Side]:
    """The bundle id and the two sides to compare, per D-41."""
    working_tree = resolve(bundle_file)
    bundle_id = working_tree.root.id
    name = bundle_name(bundle_id, bundle_file)
    workspace = workspace_name(workspace_root)

    repo: Optional[GitRepo] = None
    domain_repo = find_domain_repository(workspace_root)
    if domain_repo is not None:
        try:
            repo = GitRepo.find(domain_repo)
        except GitUnavailable as e:
            raise CommandError("GIT_REQUIRED", f"bundle diff reads version tags: {e}")
    try:
        old, new = _sides(
            envelope, bundle_file, working_tree, repo, workspace, name, from_version, to_version
        )
    finally:
        if repo is not None:
            repo.close()
    return bundle_id, old, new


def _sides(
    envelope: Envelope,
    bundle_file: Path,
    working_tree: BundleTree,
    repo: Optional[GitRepo],
    workspace: str,
    name: str,
    from_version: Optional[str],
    to_version: str,
) -> Tuple[Side, Side]:
    bundle_id = working_tree.root.id
    tags = _versions(repo, workspace, name) if repo is not None else []
    by_version = {t.version: t for t in tags}

    def version_side(version: str) -> Side:
        tag = by_version.get(version)
        if tag is None or repo is None:
            raise CommandError(
                "DIFF_VERSION_NOT_FOUND",
                f"{bundle_id} has no version {version}: no tag " f"{workspace}/{name}-v{version}",
            )
        return Side(version, "tag", _tagged(envelope, repo, tag), tag=tag.tag)

    if to_version == WORKING:
        new = Side(WORKING, "working", content_of(working_tree))
    else:
        new = version_side(to_version)

    if from_version is not None:
        old = version_side(from_version)
    elif tags:
        old = version_side(tags[-1].version)
    else:
        legacy = _legacy_snapshot(bundle_file)
        if legacy is not None:
            version, path = legacy
            old = Side(
                version, "legacy-snapshot", content_of(resolve(path), recorded=False), path=path
            )
            envelope.info(
                "DIFF_LEGACY_BASELINE",
                f"{bundle_id} has no SCS 0.7 version; comparing with its pre-0.7 snapshot "
                f"{path.name}. That snapshot records the bundle file only, so SCDs in both "
                "are listed under not_compared rather than item by item",
            )
        else:
            old = Side("empty", "empty", Content())
    return old, new


def summary_lines(bundle_id: str, old: Side, new: Side, result: Dict[str, Any]) -> List[str]:
    """Human-readable lines for the diff, in the same order as the JSON."""
    lines = [f"{bundle_id}: {old.label} -> {new.label}"]
    if not result["changed"] and not result.get("not_compared"):
        return lines + ["  No changes"]
    for scd_id in result["scds"]["added"]:
        lines.append(f"  + SCD {scd_id}")
    for scd_id in result["scds"]["removed"]:
        lines.append(f"  - SCD {scd_id}")
    for entry in result["items"]["added"]:
        lines.append(f"  + {entry['scd']} {entry['kind'][:-1]} {entry['id']}")
    for entry in result["items"]["removed"]:
        lines.append(f"  - {entry['scd']} {entry['kind'][:-1]} {entry['id']}")
    for entry in result["items"]["changed"]:
        fields = ", ".join(entry["fields"])
        lines.append(f"  ~ {entry['scd']} {entry['kind'][:-1]} {entry['id']} ({fields})")
    for entry in result["citations"]["added"]:
        where = f" {entry['item']}" if "item" in entry else ""
        lines.append(f"  + cite {entry['cite']} in {entry['scd']}{where}")
    for entry in result["citations"]["removed"]:
        where = f" {entry['item']}" if "item" in entry else ""
        lines.append(f"  - cite {entry['cite']} in {entry['scd']}{where}")
    for entry in result["imports"]["added"]:
        lines.append(f"  + import {entry['ref']} in {entry['bundle']}")
    for entry in result["imports"]["removed"]:
        lines.append(f"  - import {entry['ref']} in {entry['bundle']}")
    for entry in result["imports"]["repinned"]:
        before = entry["from"] or "unpinned"
        after = entry["to"] or "unpinned"
        lines.append(f"  ~ import {entry['import']} in {entry['bundle']}: {before} -> {after}")
    for scd_id in result.get("not_compared", []):
        lines.append(f"  ? {scd_id} (content not recorded in the baseline)")
    return lines
