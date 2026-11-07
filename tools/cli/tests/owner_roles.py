"""Test helper: map every owner role in a repository's workspaces to a test person (D-92), so
fixtures can version bundles without exercising the owner checks."""

from __future__ import annotations

from pathlib import Path

import yaml

PERSON = "Owner Person <owner@structuredcontext.dev>"


def map_owners(root: Path) -> None:
    """Give each workspace under `root` (a Domain repository or one workspace) an intake owners
    entry for every role its working bundles name."""
    for config in Path(root).glob("**/.scs/config"):
        workspace = config.parent.parent
        roles = set()
        for path in (workspace / "bundles").glob("**/*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("owner"):
                roles.add(str(data["owner"]))
        if not roles:
            continue
        intake_path = workspace / "intake.yaml"
        intake = (
            yaml.safe_load(intake_path.read_text(encoding="utf-8"))
            if intake_path.is_file()
            else None
        ) or {"intake_version": "1.0", "scs_version": "0.7.0"}
        known = {o["role"] for o in intake.get("owners") or []}
        intake["owners"] = list(intake.get("owners") or []) + [
            {"role": r, "person": PERSON} for r in sorted(roles - known)
        ]
        intake_path.write_text(yaml.safe_dump(intake, sort_keys=False), encoding="utf-8")
