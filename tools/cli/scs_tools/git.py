"""Git for the engine's own commits and tags (D-55, D-58).

The engine's commits do not depend on the user's git configuration or environment: the committer
(and tagger) is a fixed identity, the author is passed in, and signing, hooks, and line-ending
conversion are switched off for the engine's own commands.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

ENGINE_NAME = "scs-tools"
ENGINE_EMAIL = "noreply@scs.invalid"
ENGINE_IDENTITY = f"{ENGINE_NAME} <{ENGINE_EMAIL}>"

_OVERRIDES = (
    "commit.gpgsign=false",
    "tag.gpgSign=false",
    f"core.hooksPath={os.devnull}",
    "core.autocrlf=false",
)
_PERSON_RE = re.compile(r"^(?P<name>[^<>]+?)\s*<(?P<email>[^<>\s]+)>$")


class GitError(Exception):
    """A git command failed."""


def available() -> bool:
    return shutil.which("git") is not None


def run(repo: Path, *args: str, author: str = ENGINE_IDENTITY) -> str:
    """Run `git -C repo args` with the engine's settings. `author` is `Name <email>`."""
    match = _PERSON_RE.match(author)
    if match is None:
        raise ValueError(f"not a person identifier (Name <email>): {author!r}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME=match.group("name"),
        GIT_AUTHOR_EMAIL=match.group("email"),
        GIT_COMMITTER_NAME=ENGINE_NAME,
        GIT_COMMITTER_EMAIL=ENGINE_EMAIL,
    )
    command = ["git"]
    for setting in _OVERRIDES:
        command += ["-c", setting]
    command += ["-C", str(repo), *args]
    proc = subprocess.run(command, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {(proc.stderr or proc.stdout).strip()}")
    return proc.stdout


def committed_paths(repo: Path, ref: str = "HEAD") -> List[Dict[str, str]]:
    """The paths a commit changed, as `{path, status}` with status A, M, or D (D-09)."""
    output = run(repo, "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", ref)
    paths = []
    for line in output.splitlines():
        status, _, path = line.partition("\t")
        paths.append({"path": path, "status": status[:1]})
    return paths
