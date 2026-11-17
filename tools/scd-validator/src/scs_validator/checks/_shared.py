"""Helpers shared by the built-in checks."""

from __future__ import annotations

from pathlib import Path


def shown(path: Path) -> str:
    """A path relative to the current directory when it is under it, for messages."""
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
