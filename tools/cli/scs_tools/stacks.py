"""Stacks of compiled artifacts (RFC 0002 section 13, D-67, runtime-artifact.md §5).

A stack is an ordered list of runtime artifacts, outermost layer first. This module reads the
layers, lists their combined context in stack order, and runs the checks that can be decided
exactly. It never merges, reorders, or drops a rule.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jsonschema import Draft202012Validator

RUNTIME_SCHEMA = ("runtime", "runtime-artifact-schema.json")
PROHIBITION_RE = re.compile(r"^Prohibited: (?P<subject>.+?)\.(?:$| Use instead: )", re.DOTALL)
DRAFT_RE = re.compile(r"^DRAFT\+[0-9a-f]{8}$")


@dataclass
class Layer:
    position: int  # 1 is the outermost layer
    path: Path
    shown: str
    artifact: Dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.artifact["id"])

    @property
    def version(self) -> str:
        return str(self.artifact["version"])

    def label(self) -> str:
        return f"layer {self.position} ({self.id} {self.version})"

    def rules(self) -> List[Dict[str, Any]]:
        """The layer's rules, without its self-identification rule."""
        return [r for r in self.artifact["rules"] if not str(r["id"]).endswith("/identity")]

    def facts(self) -> List[Dict[str, Any]]:
        return list(self.artifact.get("facts") or [])


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: Optional[str] = None


def read(path: Path, shown: str, schema_dir: Path) -> Dict[str, Any]:
    """The artifact at `path`. Raises ValueError with a reason when it is not one."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        raise ValueError(f"{shown} is not YAML or JSON: {e}")
    schema = json.loads(schema_dir.joinpath(*RUNTIME_SCHEMA).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(data), key=lambda e: list(map(str, e.path))
    )
    if errors:
        first = errors[0]
        where = ".".join(str(p) for p in first.absolute_path) or "(root)"
        more = f" (and {len(errors) - 1} more)" if len(errors) > 1 else ""
        raise ValueError(f"{shown} is not a runtime artifact: {where}: {first.message}{more}")
    return data


def subject(rule: str) -> Optional[str]:
    """The subject of a compiled prohibition (`Prohibited: <subject>.`), else None."""
    match = PROHIBITION_RE.match(rule)
    return match.group("subject") if match else None


def context(layers: List[Layer]) -> List[Dict[str, Any]]:
    """Every rule and fact of every layer, in stack order, each with the layer it came from."""
    entries: List[Dict[str, Any]] = []
    for layer in layers:
        for rule in layer.artifact["rules"]:
            entries.append({"layer": layer.position, "id": rule["id"], "rule": rule["rule"]})
        for fact in layer.facts():
            entries.append({"layer": layer.position, "id": fact["id"], "fact": fact["fact"]})
    return entries


def check(layers: List[Layer]) -> List[Finding]:
    """The exact checks of runtime-artifact.md §5.2, in a fixed order."""
    findings: List[Finding] = []

    seen: Dict[str, Layer] = {}
    for layer in layers:
        first = seen.get(layer.id)
        if first is not None:
            findings.append(
                Finding(
                    "error",
                    "STACK_BUNDLE_REPEATED",
                    f"{layer.id} is in {first.label()} and {layer.label()}; a stack holds one "
                    "version of each bundle",
                    layer.shown,
                )
            )
        else:
            seen[layer.id] = layer

    prohibitions = [
        (layer, rule, subject(str(rule["rule"])))
        for layer in layers
        for rule in layer.rules()
        if subject(str(rule["rule"]))
    ]
    for layer in layers:
        for rule in layer.rules():
            text = str(rule["rule"])
            if subject(text):
                continue
            for other, prohibition, what in prohibitions:
                if other is layer or what is None or what.lower() not in text.lower():
                    continue
                findings.append(
                    Finding(
                        "warning",
                        "STACK_PROHIBITION_DIRECTED",
                        f"Directive {rule['id']} in {layer.label()} mentions '{what}', which "
                        f"prohibition {prohibition['id']} in {other.label()} forbids; check "
                        "whether they conflict",
                        layer.shown,
                    )
                )

    by_text: Dict[str, List[str]] = {}
    layers_by_text: Dict[str, set] = {}
    for layer in layers:
        for entry, key in [(r, "rule") for r in layer.rules()] + [
            (f, "fact") for f in layer.facts()
        ]:
            text = " ".join(str(entry[key]).split())
            by_text.setdefault(text, []).append(f"{entry['id']} (layer {layer.position})")
            layers_by_text.setdefault(text, set()).add(layer.position)
    for text, where in by_text.items():
        if len(layers_by_text[text]) > 1:
            findings.append(
                Finding(
                    "info",
                    "STACK_RULE_DUPLICATE",
                    f"The same text is in more than one layer: {', '.join(where)}",
                )
            )

    for layer in layers:
        if DRAFT_RE.match(layer.version):
            findings.append(
                Finding(
                    "info",
                    "STACK_LAYER_DRAFT",
                    f"{layer.label()} is a DRAFT artifact, compiled from an unversioned bundle",
                    layer.shown,
                )
            )
    return findings
