"""Maintain a workspace through the engine (D-08): pin, add or remove imports and SCDs, and add a
concept that has no shipped template (D-68).

Edits are made to the text, so the comments and layout of scaffolded files survive. Each
command works out every file it will write before writing any of them; `--dry-run` stops there.
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml
from scs_validator.envelope import Change, relative
from scs_validator.names import RESERVED_BUNDLE_NAMES, bundle_name, is_snapshot
from scs_validator.owners import needs_owner
from scs_validator.resolver import Index, parse_bundle_ref
from scs_validator.workspace import ONTOLOGY_MANIFEST, load_workspace

from scs_tools.machine import EXIT_USAGE, CommandError, Envelope
from scs_tools.workspace import find_workspace, repository_root, select_workspace

ROOT_BUNDLE_FILES = ("domain-bundle.yaml", "project-bundle.yaml")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# ------------------------------------------------------------------ YAML list editing


def _block(lines: List[str], key: str) -> Optional[Tuple[int, int, bool]]:
    """(key line, end of block, flow-empty) for a top-level `key:` list, or None."""
    for i, line in enumerate(lines):
        match = re.match(rf"^{re.escape(key)}:\s*(\[\s*\])?\s*(#.*)?$", line.rstrip("\n"))
        if match:
            end = i + 1
            while end < len(lines) and (
                not lines[end].strip() or lines[end][0] in " \t" or lines[end].startswith("- ")
            ):
                end += 1
            return i, end, bool(match.group(1))
    return None


def _item(line: str) -> Optional[str]:
    match = re.match(r"^(\s*)-\s+(.+?)\s*(#.*)?$", line.rstrip("\n"))
    if not match:
        return None
    return match.group(2).strip("\"'")


def list_items(text: str, key: str) -> List[str]:
    data = yaml.safe_load(text) or {}
    return [str(v) for v in (data.get(key) or [])]


def _flow(text: str, key: str) -> bool:
    """True when `key` holds a non-empty flow list (`key: [a, b]`), which is rewritten whole."""
    lines = text.splitlines(keepends=True)
    if _block(lines, key) is not None:
        return False
    return bool(list_items(text, key))


def _rewrite(text: str, key: str, items: List[str]) -> str:
    data = yaml.safe_load(text) or {}
    data[key] = items
    return str(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def add_item(text: str, key: str, item: str) -> str:
    if _flow(text, key):
        return _rewrite(text, key, [*list_items(text, key), item])
    lines = text.splitlines(keepends=True)
    found = _block(lines, key)
    if found is None:
        sep = "" if not text or text.endswith("\n") else "\n"
        return f"{text}{sep}\n{key}:\n  - {item}\n"
    start, end, empty = found
    if empty:
        lines[start] = f"{key}:\n  - {item}\n"
        return "".join(lines)
    items = [i for i in range(start + 1, end) if _item(lines[i]) is not None]
    at = items[-1] + 1 if items else start + 1
    indent = re.match(r"^(\s*)", lines[items[-1]]).group(1) if items else "  "  # type: ignore
    lines.insert(at, f"{indent}- {item}\n")
    return "".join(lines)


def remove_item(text: str, key: str, item: str) -> str:
    if _flow(text, key):
        return _rewrite(text, key, [i for i in list_items(text, key) if i != item])
    lines = text.splitlines(keepends=True)
    found = _block(lines, key)
    assert found is not None
    start, end, _ = found
    items = [i for i in range(start + 1, end) if _item(lines[i]) is not None]
    drop = [i for i in items if _item(lines[i]) == item]
    for i in reversed(drop):
        del lines[i]
    if len(drop) == len(items):
        lines[start] = f"{key}: []\n"
    return "".join(lines)


def replace_item(text: str, key: str, old: str, new: str) -> str:
    if _flow(text, key):
        return _rewrite(text, key, [new if i == old else i for i in list_items(text, key)])
    lines = text.splitlines(keepends=True)
    found = _block(lines, key)
    assert found is not None
    start, end, _ = found
    for i in range(start + 1, end):
        if _item(lines[i]) == old:
            lines[i] = lines[i].replace(old, new, 1)
    return "".join(lines)


def _target_of(entry: List[str]) -> Optional[str]:
    try:
        data = yaml.safe_load(textwrap.dedent("".join(entry)))
    except yaml.YAMLError:
        return None
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return str(data[0].get("target", "")) or None
    return None


def remove_relationships(text: str, targets: Set[str]) -> Tuple[str, List[str]]:
    """Drop the SCD's `relationships` entries whose target is in `targets`, keeping comments and
    layout; returns the new text and the targets dropped."""
    data = yaml.safe_load(text) or {}
    current = data.get("relationships") if isinstance(data, dict) else None
    if not isinstance(current, list) or not any(
        isinstance(r, dict) and str(r.get("target")) in targets for r in current
    ):
        return text, []
    kept = [r for r in current if not (isinstance(r, dict) and str(r.get("target")) in targets)]
    dropped = [str(r.get("target")) for r in current if r not in kept]
    lines = text.splitlines(keepends=True)
    found = _block(lines, "relationships")
    if found is not None and not found[2]:
        start, end, _ = found
        entries: List[Tuple[int, int]] = []
        i = start + 1
        while i < end:
            match = re.match(r"^(\s*)-\s", lines[i])
            if not match:
                i += 1
                continue
            indent = len(match.group(1))
            j = i + 1
            while j < end:
                stripped = lines[j].lstrip()
                depth = len(lines[j]) - len(stripped)
                if stripped.strip() and (depth <= indent or stripped.startswith("#")):
                    break
                j += 1
            entries.append((i, j))
            i = j
        drop = [(a, b) for a, b in entries if _target_of(lines[a:b]) in targets]
        for a, b in reversed(drop):
            del lines[a:b]
        if len(drop) == len(entries):
            lines[start] = "relationships: []\n"
        edited = "".join(lines)
        try:
            if (yaml.safe_load(edited) or {}).get("relationships") == kept:
                return edited, dropped
        except yaml.YAMLError:
            pass
    data["relationships"] = kept
    return str(yaml.safe_dump(data, sort_keys=False, allow_unicode=True)), dropped


# ------------------------------------------------------------------ ontology manifest editing


def _concept_entries(lines: List[str]) -> List[Tuple[str, int, int]]:
    """(concept id, first line, end line) for each `- id: concept:...` entry."""
    starts = []
    for i, line in enumerate(lines):
        match = re.match(r"^(\s+)-\s+id:\s*[\"']?(concept:[^\"'\s#]+)", line)
        if match:
            starts.append((match.group(2), i, len(match.group(1))))
    entries = []
    for n, (concept, i, indent) in enumerate(starts):
        end = starts[n + 1][1] if n + 1 < len(starts) else i + 1
        if n + 1 == len(starts):
            while end < len(lines) and (
                not lines[end].strip() or len(lines[end]) - len(lines[end].lstrip()) > indent
            ):
                end += 1
        entries.append((concept, i, end))
    return entries


def remove_concept(text: str, concept: str) -> str:
    """Drop the concept's entry and any relationship to it."""
    lines = text.splitlines(keepends=True)
    for found, start, end in _concept_entries(lines):
        if found == concept:
            del lines[start:end]
            break
    text = "".join(lines)
    data = yaml.safe_load(text) or {}
    concepts = ((data.get("domain") or {}).get("ontology") or {}).get("concepts") or []
    if any(
        isinstance(rel, dict) and rel.get("target") == concept
        for c in concepts
        if isinstance(c, dict)
        for rel in c.get("relationships") or []
    ):
        for c in concepts:
            if isinstance(c, dict) and c.get("relationships"):
                c["relationships"] = [
                    r
                    for r in c["relationships"]
                    if not (isinstance(r, dict) and r.get("target") == concept)
                ]
        text = str(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return text


def add_concept(text: str, concept: str, name: str, description: str) -> str:
    lines = text.splitlines(keepends=True)
    entries = _concept_entries(lines)
    entry = [f"- id: {concept}\n", f'  name: "{name}"\n', f'  description: "{description}"\n']
    if entries:
        _, first, _ = entries[0]
        indent = lines[first][: len(lines[first]) - len(lines[first].lstrip())]
        _, _, end = entries[-1]
        while end > 0 and not lines[end - 1].strip():
            end -= 1
        lines[end:end] = ["\n"] + [indent + line for line in entry]
        return "".join(lines)
    data = yaml.safe_load(text) or {}
    ontology = data.setdefault("domain", {}).setdefault("ontology", {})
    ontology["concepts"] = [{"id": concept, "name": name, "description": description}]
    return str(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


# ------------------------------------------------------------------ the workspace


@dataclass
class Edit:
    """The files one command writes, worked out before any is written."""

    root: Path
    writes: Dict[Path, Optional[str]] = field(default_factory=dict)  # None deletes

    def text(self, path: Path) -> str:
        if path in self.writes:
            value = self.writes[path]
            assert value is not None
            return value
        return path.read_text(encoding="utf-8")

    def apply(self, envelope: Envelope, dry_run: bool) -> None:
        for path in sorted(self.writes):
            content = self.writes[path]
            shown = relative(path, self.root)
            if content is None:
                envelope.changes.append(Change("delete", path=shown))
            elif not path.exists():
                envelope.changes.append(Change("create", path=shown))
            elif path.read_text(encoding="utf-8") != content:
                envelope.changes.append(Change("modify", path=shown))
            else:
                continue
            if dry_run:
                continue
            if content is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")


@dataclass
class Workspace:
    path: Path
    root: Path
    index: Index

    def shown(self, path: Path) -> str:
        return relative(path, self.root)

    def working_bundles(self) -> List[Tuple[str, Path, dict]]:
        found = []
        for bundle_id, candidates in self.index.bundles.items():
            for b in candidates:
                if not is_snapshot(b.path) and _inside(b.path, self.path):
                    found.append((bundle_id, b.path, b.data))
        return sorted(found, key=lambda b: str(b[1]))

    def root_bundle(self) -> Path:
        found = [self.path / "bundles" / n for n in ROOT_BUNDLE_FILES]
        found = [p for p in found if p.is_file()]
        if len(found) != 1:
            raise CommandError(
                "USAGE_ERROR",
                "Cannot tell the workspace's root bundle; name the bundle with --bundle",
                exit_code=EXIT_USAGE,
            )
        return found[0]


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def open_workspace(name: Optional[str], bundle: Optional[Path]) -> Workspace:
    if bundle is not None:
        if not bundle.is_file():
            raise CommandError("FILE_NOT_FOUND", f"No such bundle file: {bundle}", exit_code=4)
        path = find_workspace(bundle.resolve().parent) or select_workspace(name)
    else:
        path = select_workspace(name)
    path = path.resolve()
    root = repository_root(path) or path
    return Workspace(path, root, Index([path]))


def _target(ws: Workspace, bundle: Optional[Path]) -> Tuple[Path, dict]:
    path = bundle.resolve() if bundle is not None else ws.root_bundle()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if is_snapshot(path):
        raise CommandError(
            "USAGE_ERROR",
            f"{ws.shown(path)} is a released version; edit the working bundle instead",
            exit_code=EXIT_USAGE,
            path=ws.shown(path),
        )
    return path, data


def _bundle_id(ref: str) -> str:
    parsed = parse_bundle_ref(ref if ref.startswith("bundle:") else f"bundle:{ref}")
    if not parsed:
        raise CommandError("USAGE_ERROR", f"Not a bundle reference: {ref}", exit_code=EXIT_USAGE)
    return parsed[0]


# ------------------------------------------------------------------ commands


def pin(
    envelope: Envelope, ws: Workspace, bundle: Optional[Path], ref: str, version: str, dry_run: bool
) -> None:
    path, data = _target(ws, bundle)
    bundle_id = _bundle_id(ref)
    imports = [str(i) for i in data.get("imports") or []]
    current = [i for i in imports if (parse_bundle_ref(i) or ("",))[0] == bundle_id]
    if not current:
        raise CommandError(
            "IMPORT_NOT_FOUND",
            f"{data.get('id')} does not import {bundle_id}; add it with 'scs bundle add-import'",
            path=ws.shown(path),
        )
    target, mismatch = ws.index.find_bundle(f"{bundle_id}:{version}")
    if target is None or mismatch or not is_snapshot(target.path):
        raise CommandError(
            "VERSION_NOT_FOUND",
            f"{bundle_id} has no released version {version}; version it first with "
            "'scs bundle version'",
            path=ws.shown(path),
        )
    pinned = f"{bundle_id}:{version}"
    edit = Edit(ws.root)
    text = path.read_text(encoding="utf-8")
    edit.writes[path] = replace_item(text, "imports", current[0], pinned)
    edit.apply(envelope, dry_run)
    envelope.result = {"bundle": data.get("id"), "import": pinned, "was": current[0]}


OWNER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def set_owner_text(text: str, role: str) -> str:
    """`text` with its top-level `owner:` set to `role`: replaced in place, else inserted after
    the `description:` block, else before `imports:`."""
    lines = text.splitlines(keepends=True)
    line = f"owner: {role}\n"
    for i, current in enumerate(lines):
        if re.match(r"^owner:", current):
            lines[i] = line
            return "".join(lines)
    for i, current in enumerate(lines):
        if re.match(r"^description:", current):
            end = i + 1
            while end < len(lines) and lines[end].startswith((" ", "\t")):
                end += 1
            lines.insert(end, line)
            return "".join(lines)
    for i, current in enumerate(lines):
        if re.match(r"^imports:", current):
            lines.insert(i, line)
            return "".join(lines)
    return text.rstrip("\n") + "\n" + line


def set_owner(
    envelope: Envelope, ws: Workspace, bundle: Optional[Path], role: str, dry_run: bool
) -> None:
    if not OWNER_RE.match(role):
        raise CommandError(
            "OWNER_ROLE_INVALID",
            f"'{role}' is not an owner role: lowercase letters, digits, and hyphens, such as "
            "quality or regulatory",
            exit_code=EXIT_USAGE,
        )
    path, data = _target(ws, bundle)
    if not needs_owner(data):
        raise CommandError(
            "OWNER_NOT_APPLICABLE",
            f"{data.get('id')} holds no SCDs of its own; owners go on concept bundles and on a "
            "Project bundle that lists SCDs directly",
            path=ws.shown(path),
        )
    edit = Edit(ws.root)
    edit.writes[path] = set_owner_text(path.read_text(encoding="utf-8"), role)
    edit.apply(envelope, dry_run)
    envelope.result = {"bundle": data.get("id"), "owner": role, "was": data.get("owner")}


def add_import(
    envelope: Envelope, ws: Workspace, bundle: Optional[Path], ref: str, dry_run: bool
) -> None:
    path, data = _target(ws, bundle)
    ref = ref if ref.startswith("bundle:") else f"bundle:{ref}"
    bundle_id = _bundle_id(ref)
    if data.get("type") == "concept":
        raise CommandError(
            "IMPORT_TYPE_FORBIDDEN",
            f"{data.get('id')} is a concept bundle; concept bundles import nothing",
            path=ws.shown(path),
        )
    if data.get("scds"):
        raise CommandError(
            "BUNDLE_XOR_VIOLATION",
            f"{data.get('id')} lists SCDs; a bundle has imports or SCDs, not both",
            path=ws.shown(path),
        )
    imports = [str(i) for i in data.get("imports") or []]
    if any((parse_bundle_ref(i) or ("",))[0] == bundle_id for i in imports):
        raise CommandError(
            "IMPORT_EXISTS", f"{data.get('id')} already imports {bundle_id}", path=ws.shown(path)
        )
    target, mismatch = ws.index.find_bundle(ref)
    if target is None or mismatch:
        raise CommandError(
            "IMPORT_UNRESOLVED", f"{ref} does not resolve in this workspace", path=ws.shown(path)
        )
    edit = Edit(ws.root)
    edit.writes[path] = add_item(path.read_text(encoding="utf-8"), "imports", ref)
    edit.apply(envelope, dry_run)
    envelope.result = {"bundle": data.get("id"), "import": ref}


def add_scd(
    envelope: Envelope, ws: Workspace, bundle: Optional[Path], scd_id: str, dry_run: bool
) -> None:
    path, data = _target(ws, bundle)
    if data.get("imports"):
        raise CommandError(
            "BUNDLE_XOR_VIOLATION",
            f"{data.get('id')} has imports; a bundle has imports or SCDs, not both. Add the SCD "
            "to a concept bundle with --bundle",
            path=ws.shown(path),
        )
    if scd_id not in ws.index.scds:
        raise CommandError("SCD_NOT_FOUND", f"No SCD {scd_id} in this workspace")
    if scd_id in [str(s) for s in data.get("scds") or []]:
        raise CommandError(
            "SCD_ALREADY_LISTED", f"{data.get('id')} already lists {scd_id}", path=ws.shown(path)
        )
    edit = Edit(ws.root)
    edit.writes[path] = add_item(path.read_text(encoding="utf-8"), "scds", scd_id)
    edit.apply(envelope, dry_run)
    envelope.result = {"bundle": data.get("id"), "scd": scd_id}


def remove_scd(
    envelope: Envelope, ws: Workspace, bundle: Optional[Path], scd_ids: List[str], dry_run: bool
) -> None:
    """Retire one or more SCDs as one change: each later removal sees the earlier ones, so the
    dry run shows every concept bundle that goes."""
    edit = Edit(ws.root)
    initial = [(i, p.resolve(), d) for i, p, d in ws.working_bundles()]

    def working() -> List[Tuple[str, Path, dict]]:
        current = []
        for bundle_id, path, data in initial:
            if path in edit.writes:
                if edit.writes[path] is None:
                    continue
                data = yaml.safe_load(edit.text(path)) or {}
            current.append((bundle_id, path, data))
        return current

    manifest = load_workspace(ws.path.name, ws.path).ontology_manifest()
    removed: List[Dict[str, object]] = []
    for scd_id in scd_ids:
        bundles = working()
        listing = [b for b in bundles if scd_id in [str(s) for s in b[2].get("scds") or []]]
        if bundle is not None:
            path, data = _target(ws, bundle)
            if path not in [b[1] for b in listing]:
                raise CommandError(
                    "SCD_NOT_LISTED",
                    f"{data.get('id')} does not list {scd_id}",
                    path=ws.shown(path),
                )
        elif len(listing) == 1:
            path, data = listing[0][1], listing[0][2]
        elif not listing:
            listed = {str(s) for b in bundles for s in b[2].get("scds") or []}
            matches = sorted(s for s in listed if s.rsplit(":", 1)[-1] == scd_id)
            if not scd_id.startswith("scd:") and len(matches) == 1:
                raise CommandError(
                    "SCD_NOT_LISTED",
                    f"No bundle in this workspace lists {scd_id}; SCDs are named by their "
                    f"full id, {matches[0]}",
                    suggestion={"scd_id": matches[0]},
                )
            raise CommandError("SCD_NOT_LISTED", f"No bundle in this workspace lists {scd_id}")
        else:
            names = ", ".join(b[0] for b in listing)
            raise CommandError(
                "USAGE_ERROR",
                f"{scd_id} is listed by {names}; name the bundle with --bundle",
                exit_code=EXIT_USAGE,
            )

        edit.writes[path] = remove_item(edit.text(path), "scds", scd_id)
        item: Dict[str, object] = {
            "bundle": data.get("id"),
            "scd": scd_id,
            "scd_file_deleted": False,
        }

        # The SCD file goes when nothing else lists it (D-75)
        others = [b for b in listing if b[1] != path]
        if not others:
            for scd_path, _ in ws.index.scds.get(scd_id, []):
                if _inside(scd_path, ws.path):
                    edit.writes[scd_path.resolve()] = None
                    item["scd_file_deleted"] = True

        # A concept bundle left with no SCDs goes, with its imports and ontology entry (D-69)
        remaining = list_items(edit.text(path), "scds")
        if data.get("type") == "concept" and not remaining:
            concept_id = str(data.get("id"))
            edit.writes[path] = None
            for _, other_path, other in working():
                for ref in [str(i) for i in other.get("imports") or []]:
                    if (parse_bundle_ref(ref) or ("",))[0] == concept_id:
                        edit.writes[other_path] = remove_item(edit.text(other_path), "imports", ref)
            if manifest is not None:
                concept = f"concept:{bundle_name(concept_id)}"
                edit.writes[manifest.resolve()] = remove_concept(
                    edit.text(manifest.resolve()), concept
                )
            item["bundle_removed"] = concept_id
        removed.append(item)

    # Relationships in the workspace's other SCDs that point at a retired SCD go too, so no
    # reference is left dangling.
    gone = {str(i["scd"]) for i in removed if i["scd_file_deleted"]}
    relationships: List[Dict[str, str]] = []
    for scd_id, entries in sorted(ws.index.scds.items()):
        for scd_path, _ in entries:
            scd_path = scd_path.resolve()
            if not _inside(scd_path, ws.path) or edit.writes.get(scd_path, "") is None:
                continue
            text, dropped = remove_relationships(edit.text(scd_path), gone)
            if dropped:
                edit.writes[scd_path] = text
                relationships += [{"scd": scd_id, "target": d} for d in dropped]
    edit.apply(envelope, dry_run)
    envelope.result = {"removed": removed, "relationships_removed": relationships}


def new_concept(
    envelope: Envelope,
    ws: Workspace,
    name: str,
    title: Optional[str],
    description: Optional[str],
    created_by: str,
    dry_run: bool,
    owner: Optional[str] = None,
) -> None:
    """A concept with no shipped template: its bundle, its first SCD, its ontology entry, and the
    root bundle's import of it (D-68, D-76). `owner` is its owner role (D-92)."""
    if owner is not None and not OWNER_RE.match(owner):
        raise CommandError(
            "OWNER_ROLE_INVALID",
            f"'{owner}' is not an owner role: lowercase letters, digits, and hyphens",
            exit_code=EXIT_USAGE,
        )
    if name in RESERVED_BUNDLE_NAMES:
        raise CommandError(
            "RESERVED_BUNDLE_NAME",
            f"'{name}' is reserved for a later release; choose another bundle name",
        )
    if not NAME_RE.match(name):
        raise CommandError(
            "USAGE_ERROR",
            f"'{name}' is not a valid concept name: lowercase letters, digits, and '-'",
            exit_code=EXIT_USAGE,
        )
    bundle_id, scd_id = f"bundle:{name}", f"scd:project:{name}"
    bundle_path = ws.path / "bundles" / "concepts" / f"{name}.yaml"
    scd_path = ws.path / "context" / "project" / f"{name}.yaml"
    for path in (bundle_path, scd_path):
        if path.exists():
            raise CommandError(
                "FILE_EXISTS", f"{ws.shown(path)} already exists", path=ws.shown(path)
            )
    if bundle_id in ws.index.bundles or scd_id in ws.index.scds:
        raise CommandError(
            "DUPLICATE_ID", f"{bundle_id} or {scd_id} already exists in this workspace"
        )

    title = title or name.replace("-", " ").title()
    description = description or f"{title}: defined with the owner of this workspace"
    now = datetime.now(timezone.utc).isoformat()
    provenance = {"created_by": created_by, "created_at": now}
    concept_bundle = {
        "id": bundle_id,
        "type": "concept",
        "version": "DRAFT",
        "title": title,
        "description": description,
        **({"owner": owner} if owner else {}),
        "imports": [],
        "scds": [scd_id],
        "provenance": {**provenance, "rationale": f"{title} concept bundle"},
    }
    scd = {
        "id": scd_id,
        "type": "project",
        "title": title,
        "version": "DRAFT",
        "description": description,
        "content": {"summary": description, "prohibitions": [], "directives": [], "facts": []},
        "provenance": {**provenance, "rationale": f"First SCD for the {title} concept"},
    }
    edit = Edit(ws.root)
    edit.writes[bundle_path.resolve()] = _dump(concept_bundle)
    edit.writes[scd_path.resolve()] = _dump(scd)
    root = ws.root_bundle().resolve()
    root_data = yaml.safe_load(root.read_text(encoding="utf-8")) or {}
    if root_data.get("scds"):
        raise CommandError(
            "BUNDLE_XOR_VIOLATION",
            f"{root_data.get('id')} lists SCDs, so it cannot import the new concept",
            path=ws.shown(root),
        )
    edit.writes[root] = add_item(root.read_text(encoding="utf-8"), "imports", bundle_id)
    manifest = load_workspace(ws.path.name, ws.path).ontology_manifest()
    manifest = (manifest or ws.path / ONTOLOGY_MANIFEST).resolve()
    if manifest.is_file():
        text = manifest.read_text(encoding="utf-8")
        concept = f"concept:{name}"
        if f"id: {concept}\n" not in text and f'id: "{concept}"' not in text:
            edit.writes[manifest] = add_concept(text, concept, title, description)
    edit.apply(envelope, dry_run)
    envelope.result = {"bundle": bundle_id, "scd": scd_id}


class _Dumper(yaml.SafeDumper):
    """Lists indented under their key, as the scaffolded files have them."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


def _dump(data: dict) -> str:
    return str(yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100))
