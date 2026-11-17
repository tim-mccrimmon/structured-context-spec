"""Check registry: validation checks that run once per workspace.

A check is a function taking a `CheckContext` and returning a `ValidationResult` (or None when
it has nothing to say). Modules in this package register theirs with `@register`; a check
registered from anywhere else runs too, so later work adds checks without editing the
validation command.

In bundle mode the context covers the validated bundle's project root and its tree. In
repository mode there is one context per workspace, with `workspace` set and one tree per
root bundle.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..resolver import BundleTree, Index
from ..utils import ValidationResult
from ..workspace import Workspace


@dataclass
class CheckContext:
    workspace_root: Path
    index: Index  # documents under workspace_root only, not the packaged meta bundle
    trees: List[BundleTree] = field(default_factory=list)
    workspace: Optional[Workspace] = None  # repository mode only
    schema_dir: Optional[Path] = None
    strict: bool = False


Check = Callable[[CheckContext], Optional[ValidationResult]]
_REGISTRY: Dict[str, Check] = {}
_loaded = False


def register(name: str) -> Callable[[Check], Check]:
    """Register a check under `name`; registering a name again replaces it."""

    def decorator(check: Check) -> Check:
        _REGISTRY[name] = check
        return check

    return decorator


def unregister(name: str) -> None:
    _REGISTRY.pop(name, None)


def registered() -> Dict[str, Check]:
    _load_builtin()
    return dict(_REGISTRY)


def _load_builtin() -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    for module in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module.name}")


def run_checks(context: CheckContext) -> List[ValidationResult]:
    """Run every registered check, in name order, keeping results that say something."""
    results = []
    for _, check in sorted(registered().items()):
        result = check(context)
        if result is not None and (
            result.errors or result.warnings or result.infos or not result.passed
        ):
            results.append(result)
    return results
