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
from typing import Dict, List, Optional, Sequence

ENGINE_NAME = "scs-tools"
ENGINE_EMAIL = "noreply@scs.invalid"
ENGINE_IDENTITY = f"{ENGINE_NAME} <{ENGINE_EMAIL}>"

_OVERRIDES = (
    "commit.gpgsign=false",
    "tag.gpgSign=false",
    "tag.forceSignAnnotated=false",
    f"core.hooksPath={os.devnull}",
    "core.autocrlf=false",
)
_PERSON_RE = re.compile(r"^(?P<name>[^<>]+?)\s*<(?P<email>[^<>\s]+)>$")


class GitError(Exception):
    """A git command failed."""


def available() -> bool:
    return shutil.which("git") is not None


def run(
    repo: Path,
    *args: str,
    author: str = ENGINE_IDENTITY,
    index: Optional[Path] = None,
    input: Optional[str] = None,
) -> str:
    """Run `git -C repo args` with the engine's settings. `author` is `Name <email>`; `index`
    replaces the repository's index file for this command."""
    match = _PERSON_RE.match(author)
    if match is None:
        raise ValueError(f"not a person identifier (Name <email>): {author!r}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM"):
        if key in os.environ:
            env[key] = os.environ[key]
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
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
    proc = subprocess.run(command, env=env, capture_output=True, text=True, input=input)
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


def head(repo: Path) -> Optional[str]:
    """The commit HEAD points at, or None before the first commit."""
    try:
        return run(repo, "rev-parse", "-q", "--verify", "HEAD^{commit}").strip() or None
    except GitError:
        return None


def tag_exists(repo: Path, tag: str) -> bool:
    try:
        run(repo, "rev-parse", "-q", "--verify", f"refs/tags/{tag}")
        return True
    except GitError:
        return False


def ignored(repo: Path, paths: Sequence[str]) -> List[str]:
    """The paths (from the top level) that git ignores and does not track."""
    if not paths:
        return []
    try:
        out = run(repo, "check-ignore", "--stdin", input="\n".join(paths) + "\n")
    except GitError:
        return []  # exit 1: none of them is ignored
    return [line for line in out.splitlines() if line]


def pending_paths(repo: Path, pathspec: Sequence[str]) -> List[Dict[str, str]]:
    """What committing the working tree under `pathspec` would change, relative to HEAD, as
    `{path, status}` (D-09): tracked changes, then untracked files that are not ignored."""
    found: Dict[str, str] = {}
    if head(repo):
        out = run(repo, "diff", "--name-status", "--no-renames", "-z", "HEAD", "--", *pathspec)
        fields = [f for f in out.split("\0") if f]
        for status, path in zip(fields[0::2], fields[1::2]):
            found[path] = status[:1]
    else:
        out = run(repo, "ls-files", "-z", "--", *pathspec)
        found.update({p: "A" for p in out.split("\0") if p})
    out = run(repo, "ls-files", "-z", "--others", "--exclude-standard", "--", *pathspec)
    found.update({p: "A" for p in out.split("\0") if p})
    return [{"path": p, "status": s} for p, s in sorted(found.items())]


def commit_paths(
    repo: Path, pathspec: Sequence[str], message: str, author: str, workdir: Path
) -> str:
    """A commit of the working tree under `pathspec`, and nothing else, on top of HEAD. Nothing
    points at it yet (see `move_head`).

    A temporary index (in `workdir`) starts from HEAD, so changes staged elsewhere in the
    repository stay staged and out of the commit. Plumbing commands run no hooks."""
    parent = head(repo)
    index = workdir / "index"
    if parent:
        run(repo, "read-tree", parent, index=index)
    run(repo, "add", "-A", "--", *pathspec, index=index)
    tree = run(repo, "write-tree", index=index).strip()
    parents = ["-p", parent] if parent else []
    return run(repo, "commit-tree", tree, *parents, "-m", message, author=author).strip()


def move_head(repo: Path, commit: str, old: Optional[str], reason: str) -> None:
    """Point HEAD (its branch, if any) at `commit`, if it still points at `old`."""
    run(repo, "update-ref", "-m", reason, "HEAD", commit, old or "")


def sync_index(repo: Path, pathspec: Sequence[str]) -> None:
    """Make the real index match HEAD under `pathspec`."""
    run(repo, "reset", "-q", "--", *pathspec)
