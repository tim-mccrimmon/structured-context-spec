"""Who wrote something, and who approved it (D-13, D-71).

A person is never inferred from the environment. Git's `user.name` and `user.email` are offered
only as prompt defaults in interactive mode, or as a `suggestion` on the diagnostic when a value
is missing; they are never written on their own.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, Optional, Tuple

import click

from scs_tools.machine import EXIT_USAGE, CommandError


def git_identity() -> Tuple[Optional[str], Optional[str]]:
    """Git's `user.name` and `user.email`, each None when unset or git is missing."""
    if shutil.which("git") is None:
        return None, None
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")}

    def get(key: str) -> Optional[str]:
        proc = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, text=True, env=env
        )
        value = proc.stdout.strip()
        return value or None

    return get("user.name"), get("user.email")


def person_suggestion() -> Optional[str]:
    """`Name <email>` from git, for a suggestion only, or None."""
    name, email = git_identity()
    return f"{name} <{email}>" if name and email else None


def author(
    given_author: Optional[str], given_email: Optional[str], prompt: bool
) -> Tuple[str, str]:
    """The author and email for provenance: as given, else prompted (with git's values as
    defaults) when `prompt`, else NO_INPUT with git's values as the suggestion."""
    name, email = given_author, given_email
    if prompt:
        git_name, git_email = git_identity()
        if not name:
            name = click.prompt("Author name", default=git_name or "", show_default=bool(git_name))
        if not email:
            email = click.prompt(
                "Author email", default=git_email or "", show_default=bool(git_email)
            )
    name, email = (name or "").strip(), (email or "").strip()
    if name and email:
        return name, email
    missing = " and ".join(
        option for option, value in (("--author", name), ("--email", email)) if not value
    )
    suggestion: Dict[str, str] = {}
    git_name, git_email = git_identity()
    if not name and git_name:
        suggestion["author"] = git_name
    if not email and git_email:
        suggestion["email"] = git_email
    raise CommandError(
        "NO_INPUT",
        f"Provenance names who created this: pass {missing}. They are never taken from git "
        "configuration",
        exit_code=EXIT_USAGE,
        suggestion=suggestion or None,
    )
