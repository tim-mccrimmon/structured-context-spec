"""Compile a Domain or Project bundle into a runtime artifact (spec/0.6/runtime-artifact.md).

The artifact holds directives only, in a fixed order, with no volatile content, so identical
source always produces identical bytes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

RUNTIME_FORMAT = "0.6"
COMPILABLE_TYPES = ("domain", "project")


@dataclass
class CompileResult:
    artifact: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


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

    rules: List[Dict[str, Any]] = []
    seen: Dict[str, str] = {}
    for scd in tree.scds:
        content = scd.data.get("content")
        directives = content.get("directives") if isinstance(content, dict) else None
        if not directives:
            result.warnings.append(f"{scd.ref} has no directives and contributes no rules.")
            continue
        scd_name = _short_name(scd.ref)
        for directive in directives:
            directive_id = str(directive.get("id", "")).strip()
            text = " ".join(str(directive.get("directive", "")).split())
            if not directive_id or not text:
                result.errors.append(f"{scd.ref} has a directive without an id or text.")
                continue
            if "TODO" in text:
                result.errors.append(
                    f"{scd.ref} directive {directive_id} still contains TODO; "
                    "finish or remove it before compiling."
                )
                continue
            rule_id = f"{scd_name}/{directive_id}"
            if rule_id in seen:
                result.errors.append(
                    f"Duplicate rule id {rule_id} (from {seen[rule_id]} and {scd.ref})."
                )
                continue
            seen[rule_id] = scd.ref
            rule: Dict[str, Any] = {"id": rule_id, "rule": text}
            cites = directive.get("cites")
            if include_cites and cites:
                rule["cites"] = [str(c) for c in cites]
            rules.append(rule)

    if not rules and not result.errors:
        result.errors.append(f"{root.id} yields no directives; there is nothing to compile.")
    if result.errors:
        return result

    bundle_name = _short_name(root.id)
    identity_id = f"{bundle_name}/identity"
    if identity_id in seen:
        result.errors.append(f"Rule id {identity_id} is reserved for the self-identification rule.")
        return result

    sources = [f"{b.id}:{b.version}" for b in tree.bundles[1:]]
    title = " ".join(str(root.data.get("title", "")).split())

    version = root.version or "DRAFT"
    if any(b.version == "DRAFT" for b in tree.bundles):
        body = {"id": root.id, "type": root.type, "title": title, "sources": sources}
        body["rules"] = rules
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
        "title": title,
        "sources": sources,
        "rules": [identity, *rules],
    }
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
    extra_search_dirs: tuple = (),
) -> CompileResult:
    """Resolve the bundle at `bundle_path` and compile it. Does not run validation."""
    from scs_validator.resolver import resolve

    tree = resolve(Path(bundle_path), extra_search_dirs=extra_search_dirs)
    return compile_tree(tree, allow_draft=allow_draft, include_cites=include_cites)
