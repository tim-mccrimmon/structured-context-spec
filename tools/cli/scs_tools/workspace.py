"""Workspace selection and the repository root (D-42).

Workspace-scoped commands take `--workspace <domain|name>`. Without it, the workspace is the
nearest `.scs/config` above the current directory. At a Domain repository root without it,
the command fails with WORKSPACE_REQUIRED. Envelope paths are relative to the repository root.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from scs_validator.workspace import CONFIG, is_repository

from scs_tools.machine import EXIT_USAGE, CommandError


def find_domain_repository(start: Path) -> Optional[Path]:
    """The Domain repository `start` is in, if any."""
    for path in [start, *start.parents]:
        if is_repository(path):
            return path
    return None


def find_workspace(start: Path) -> Optional[Path]:
    """The nearest directory at or above `start` with a `.scs/config`."""
    for path in [start, *start.parents]:
        if (path / CONFIG).is_file():
            return path
    return None


def repository_root(start: Path) -> Optional[Path]:
    """The root that envelope paths are relative to and that writes must stay under: the Domain
    repository, else the git repository, else the workspace (0.6 layout)."""
    start = start.resolve()
    domain_repo = find_domain_repository(start)
    if domain_repo is not None:
        return domain_repo
    for path in [start, *start.parents]:
        if (path / ".git").exists():
            return path
    return find_workspace(start)


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def select_workspace(name: Optional[str], cwd: Optional[Path] = None) -> Path:
    """The workspace a command acts on."""
    cwd = (cwd or Path.cwd()).resolve()
    if name:
        repo = find_domain_repository(cwd)
        if repo is None:
            raise CommandError(
                "WORKSPACE_NOT_FOUND",
                f"--workspace {name} needs a Domain repository; none found above {cwd}",
            )
        path = repo / "domain" if name == "domain" else repo / "projects" / name
        if not (path / CONFIG).is_file():
            raise CommandError("WORKSPACE_NOT_FOUND", f"No workspace '{name}' in {repo}")
        return path
    found = find_workspace(cwd)
    if found is not None:
        return found
    if is_repository(cwd):
        raise CommandError(
            "WORKSPACE_REQUIRED",
            "At the root of a Domain repository, name the workspace with --workspace",
            exit_code=EXIT_USAGE,
        )
    raise CommandError(
        "WORKSPACE_NOT_FOUND",
        "Not in an SCS workspace (no .scs/config here or above). Run 'scs init' first.",
    )
