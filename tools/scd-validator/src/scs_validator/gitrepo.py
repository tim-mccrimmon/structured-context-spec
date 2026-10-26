"""Read-only git access for the integrity checks (D-39).

The validator reads tags, tagged files, and blob ids. It never writes to the repository, and
it reads with the user's configuration switched off where it could change a result: no
replacement objects, and no line-ending conversion when hashing working files.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple

from .names import VERSION_TAG_RE


class GitUnavailable(Exception):
    """git is not installed, or a git command failed."""


def _env() -> Dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM"):
        if key in os.environ:
            env[key] = os.environ[key]
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def _git(cwd: Path, *args: str, input: Optional[bytes] = None) -> subprocess.CompletedProcess:
    if shutil.which("git") is None:
        raise GitUnavailable("git is not installed")
    return subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-C", str(cwd), *args],
        capture_output=True,
        input=input,
        env=_env(),
    )


@dataclass
class VersionTag:
    tag: str
    workspace: str
    name: str
    version: str
    commit: str


@dataclass
class GitRepo:
    """The git repository holding a Domain repository. `prefix` is the Domain repository's
    path inside it (POSIX, empty at the top level)."""

    toplevel: Path
    prefix: str
    _trees: Dict[str, Path] = field(default_factory=dict)
    _tmp: Optional[tempfile.TemporaryDirectory] = None

    @classmethod
    def find(cls, path: Path) -> Optional["GitRepo"]:
        """The repository `path` is in, or None when it is in none. Raises GitUnavailable when
        `path` is in a repository but git is not installed."""
        path = Path(path).resolve()
        if shutil.which("git") is None:
            if any((p / ".git").exists() for p in [path, *path.parents]):
                raise GitUnavailable("git is not installed")
            return None
        proc = _git(path, "rev-parse", "--show-toplevel")
        if proc.returncode != 0:
            return None
        toplevel = Path(proc.stdout.decode().strip()).resolve()
        prefix = path.relative_to(toplevel).as_posix() if path != toplevel else ""
        return cls(toplevel, "" if prefix == "." else prefix)

    def close(self) -> None:
        if self._tmp is not None:
            self._tmp.cleanup()
            self._tmp = None
            self._trees.clear()

    def __enter__(self) -> "GitRepo":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _out(self, *args: str) -> str:
        proc = _git(self.toplevel, *args)
        if proc.returncode != 0:
            raise GitUnavailable(f"git {' '.join(args)}: {proc.stderr.decode().strip()}")
        return str(proc.stdout.decode())

    def path(self, relative: str) -> str:
        """A path under the Domain repository, as a path from the git top level."""
        return str(PurePosixPath(self.prefix, relative)) if self.prefix else relative

    def is_shallow(self) -> bool:
        return self._out("rev-parse", "--is-shallow-repository").strip() == "true"

    def has_commits(self) -> bool:
        return _git(self.toplevel, "rev-parse", "-q", "--verify", "HEAD").returncode == 0

    def version_tags(self) -> List[VersionTag]:
        """Every workspace-qualified version tag, with the commit it points at."""
        out = self._out(
            "for-each-ref", "refs/tags", "--format=%(refname:strip=2) %(objectname) %(*objectname)"
        )
        tags = []
        for line in out.splitlines():
            name, obj, peeled = (line.split(" ") + ["", ""])[:3]
            match = VERSION_TAG_RE.match(name)
            if match:
                tags.append(
                    VersionTag(
                        name,
                        match.group("workspace"),
                        match.group("name"),
                        match.group("version"),
                        peeled or obj,
                    )
                )
        return sorted(tags, key=lambda t: t.tag)

    def tag_commit(self, tag: str) -> Optional[str]:
        proc = _git(self.toplevel, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
        return proc.stdout.decode().strip() if proc.returncode == 0 else None

    def files(self, commit: str, directory: str) -> Dict[str, str]:
        """Path (from the top level) to blob id for every file under `directory` at `commit`."""
        out = self._out("ls-tree", "-r", "-z", "--full-tree", commit, "--", directory)
        files = {}
        for entry in out.split("\0"):
            if not entry:
                continue
            meta, _, path = entry.partition("\t")
            mode, kind, blob = meta.split(" ")
            if kind == "blob":
                files[path] = blob
        return files

    def blob_at(self, commit: str, path: str) -> Optional[str]:
        proc = _git(self.toplevel, "rev-parse", "-q", "--verify", f"{commit}:{path}")
        return proc.stdout.decode().strip() if proc.returncode == 0 else None

    def working_blob(self, path: str) -> Optional[str]:
        """The blob id a working file would have if added, or None when it does not exist."""
        full = self.toplevel / path
        if not full.is_file():
            return None
        return self._out("hash-object", "--path", path, "--", str(full)).strip()

    def checkout(self, commit: str, directory: str) -> Path:
        """The files under `directory` at `commit`, written to a temporary directory. Returns
        that directory's copy of `directory`. Read-only use; removed by `close()`."""
        key = f"{commit}:{directory}"
        if key in self._trees:
            return self._trees[key]
        if self._tmp is None:
            self._tmp = tempfile.TemporaryDirectory(prefix="scs-tag-")
        root = Path(self._tmp.name) / str(len(self._trees))
        files = self.files(commit, directory)
        if files:
            batch = "".join(f"{blob}\n" for blob in files.values()).encode()
            proc = _git(self.toplevel, "cat-file", "--batch", input=batch)
            if proc.returncode != 0:
                raise GitUnavailable(f"git cat-file: {proc.stderr.decode().strip()}")
            data, offset = proc.stdout, 0
            for path in files:
                header_end = data.index(b"\n", offset)
                size = int(data[offset:header_end].split(b" ")[2])
                body = data[header_end + 1 : header_end + 1 + size]
                offset = header_end + 1 + size + 1
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
        self._trees[key] = root / directory
        return root / directory


def workspace_dir(workspace: str) -> str:
    """A workspace's directory in a Domain repository (D-03)."""
    return "domain" if workspace == "domain" else f"projects/{workspace}"


def find_file(root: Path, name: str) -> Optional[Path]:
    """The first file called `name` under `root/bundles`, or None."""
    bundles = root / "bundles"
    if not bundles.is_dir():
        return None
    return next(iter(sorted(bundles.rglob(name))), None)


def split_version(version: str) -> Tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))
