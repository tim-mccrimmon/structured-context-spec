"""Compile a Domain or Project bundle into a runtime artifact (spec/0.7/runtime-artifact.md).

The artifact holds prohibitions and directives as rules, and facts, in a fixed order, with no
volatile content, so identical source always produces identical bytes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

RUNTIME_FORMAT = "0.7"
COMPILABLE_TYPES = ("domain", "project")


@dataclass
class CompileResult:
    artifact: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _text(value: Any) -> str:
    """Collapse whitespace, including line breaks from folded YAML."""
    return " ".join(str(value or "").split())


def _prohibition_rule(entry: Dict[str, Any]) -> str:
    subject = _text(entry.get("subject")).rstrip(".")
    instead = _text(entry.get("instead")).rstrip(".")
    rule = f"Prohibited: {subject}."
    return f"{rule} Use instead: {instead}." if instead else rule


def _short_name(prefixed_id: str) -> str:
    """`scd:project:x` -> `x`; `bundle:x` -> `x`."""
    return prefixed_id.rsplit(":", 1)[-1]


def compile_tree(tree: Any, allow_draft: bool = False, include_cites: bool = True) -> CompileResult:
    """Compile a resolved bundle tree (`scs_validator.resolver.BundleTree`)."""
    result = CompileResult()
    root = tree.root

    if root.type not in COMPILABLE_TYPES:
        result.errors.append(
            f"Only domain and project bundles can be compiled; {root.id} is type '{root.type}'."
        )
        return result

    for edge in tree.unresolved_imports:
        result.errors.append(f"Import '{edge.ref}' in {edge.importer.id} could not be resolved.")
    for bundle_id, ref in tree.unresolved_scds:
        result.errors.append(f"SCD '{ref}' listed in {bundle_id} could not be resolved.")
    for cycle in tree.cycles:
        result.errors.append(f"Circular bundle imports: {' -> '.join(cycle)}.")

    drafts = [b.id for b in tree.bundles if b.version == "DRAFT"]
    if drafts and not allow_draft:
        result.errors.append(
            "DRAFT bundles cannot be compiled without --allow-draft: " + ", ".join(drafts)
        )
    if result.errors:
        return result

    # Every versioned bundle in the tree must still match what was versioned, whatever the
    # root's state, and no flag overrides it (D-16). The root's digest goes into the artifact
    # only when it was verified against its manifest (D-18).
    from scs_validator.digest import content_digest, tree_index, verify_tree

    source_digest = None
    for check in verify_tree(tree):
        if check.status == "mismatch":
            changes = ", ".join(check.changes) or "unknown"
            result.errors.append(
                f"{check.bundle.id} version {check.bundle.version} has changed since it was "
                f"versioned (its content no longer matches {check.manifest}); changed: "
                f"{changes}. A changed bundle needs a new version."
            )
        elif check.status == "unrecorded":
            result.warnings.append(
                f"{check.bundle.id} version {check.bundle.version} cannot be verified: "
                f"{check.manifest} has no content_digest (written before SCS 0.7)."
            )
        elif check.bundle is root and not drafts:
            source_digest = content_digest(root, tree_index(tree)).digest
    if result.errors:
        return result

    # Ids carry the root bundle's name so a Domain and a Project artifact never share one,
    # even when both have an SCD of the same name.
    bundle_name = _short_name(root.id)
    prohibitions: List[Dict[str, Any]] = []
    directives: List[Dict[str, Any]] = []
    facts: List[Dict[str, Any]] = []
    seen: Dict[str, str] = {}

    def add(scd: Any, entry: Any, text: str, label: str, out: List[Dict[str, Any]], key: str):
        entry_id = str(entry.get("id", "")).strip() if isinstance(entry, dict) else ""
        if not entry_id or not text:
            result.errors.append(f"{scd.ref} has a {label} without an id or text.")
            return
        if "TODO" in text:
            result.errors.append(
                f"{scd.ref} {label} {entry_id} still contains TODO; "
                "finish or remove it before compiling."
            )
            return
        item_id = f"{bundle_name}/{_short_name(scd.ref)}/{entry_id}"
        if item_id in seen:
            result.errors.append(
                f"Duplicate rule id {item_id} (from {seen[item_id]} and {scd.ref})."
            )
            return
        seen[item_id] = scd.ref
        item: Dict[str, Any] = {"id": item_id, key: text}
        cites = entry.get("cites")
        if include_cites and cites:
            item["cites"] = [str(c) for c in cites]
        out.append(item)

    for scd in tree.scds:
        content = scd.data.get("content")
        content = content if isinstance(content, dict) else {}
        if not any(content.get(k) for k in ("prohibitions", "directives", "facts")):
            result.warnings.append(
                f"{scd.ref} has no directives, prohibitions, or facts and contributes nothing."
            )
            continue
        for entry in content.get("prohibitions") or []:
            text = _prohibition_rule(entry) if _text(entry.get("subject")) else ""
            add(scd, entry, text, "prohibition", prohibitions, "rule")
        for entry in content.get("directives") or []:
            add(scd, entry, _text(entry.get("directive")), "directive", directives, "rule")
        for entry in content.get("facts") or []:
            add(scd, entry, _text(entry.get("fact")), "fact", facts, "fact")

    rules = prohibitions + directives
    if not rules and not facts and not result.errors:
        result.errors.append(f"{root.id} yields no rules or facts; there is nothing to compile.")
    if result.errors:
        return result

    identity_id = f"{bundle_name}/identity"

    sources = [f"{b.id}:{b.version}" for b in tree.bundles[1:]]
    title = " ".join(str(root.data.get("title", "")).split())

    version = root.version or "DRAFT"
    if any(b.version == "DRAFT" for b in tree.bundles):
        body = {"id": root.id, "type": root.type, "title": title, "sources": sources}
        body["rules"] = rules
        if facts:
            body["facts"] = facts
        digest = hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()[:8]
        version = f"DRAFT+{digest}"

    identity = {
        "id": identity_id,
        "rule": (
            "When asked which governance bundles are active, state: "
            f'"{root.type.capitalize()} bundle {root.id} version {version}".'
        ),
    }

    result.artifact = {
        "scs_runtime": RUNTIME_FORMAT,
        "id": root.id,
        "type": root.type,
        "version": version,
    }
    if source_digest:
        result.artifact["source_digest"] = source_digest
    result.artifact.update({"title": title, "sources": sources, "rules": [identity, *rules]})
    if facts:
        result.artifact["facts"] = facts
    return result


class _ArtifactDumper(yaml.SafeDumper):
    """Block-style mappings; lists of scalars (sources, cites) on one line."""


def _represent_list(dumper: yaml.SafeDumper, data: list) -> yaml.Node:
    flow = all(not isinstance(item, (dict, list)) for item in data)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


def _represent_dict(dumper: yaml.SafeDumper, data: dict) -> yaml.Node:
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items(), flow_style=False)


_ArtifactDumper.add_representer(list, _represent_list)
_ArtifactDumper.add_representer(dict, _represent_dict)


def render(artifact: Dict[str, Any], fmt: str = "yaml") -> str:
    """Serialize an artifact deterministically: UTF-8, `\\n` line endings, trailing newline."""
    if fmt == "json":
        return json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    return yaml.dump(
        artifact,
        Dumper=_ArtifactDumper,
        sort_keys=False,
        allow_unicode=True,
        width=1_000_000,
    )


def compile_bundle(
    bundle_path: Path,
    allow_draft: bool = False,
    include_cites: bool = True,
    extra_search_dirs: Optional[tuple] = None,
) -> CompileResult:
    """Resolve the bundle at `bundle_path` and compile it. Does not run validation."""
    from scs_validator.resolver import resolve

    tree = resolve(Path(bundle_path), extra_search_dirs=extra_search_dirs)
    return compile_tree(tree, allow_draft=allow_draft, include_cites=include_cites)
