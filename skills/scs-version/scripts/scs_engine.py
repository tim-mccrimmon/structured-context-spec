#!/usr/bin/env python3
"""Call the SCS engine (`scs`, `scs-validate`) in machine mode for an SCS skill.

    scs_engine.py check                 Is the engine installed and new enough? (D-45, D-56)
    scs_engine.py install-plan [WHEEL...]
                                        The install command to show the user. Installs nothing.
    scs_engine.py stage-wheels WHEEL... Copy uploaded wheels to their standard file names.
    scs_engine.py run scs ARGS...       Run an engine command with --json; print its envelope.
    scs_engine.py run scs-validate ARGS...

Every command prints one JSON object. Standard library only; Python 3.11 or later. This file is
identical in every SCS skill.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MINIMUM_TOOLS_VERSION = "0.7.0"
PACKAGE = "scs-tools"
RELEASE = "0.7.0"
WHEEL_RE = re.compile(r"(scs_(?:tools|validator)-[0-9][^-]*-py3-none-any\.whl)$")
HERE = Path(__file__).resolve().parent


def emit(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def release_tuple(version: str) -> tuple[int, ...] | None:
    """The release part of a PEP 440 version. A pre-release meets its base version (D-56)."""
    match = re.match(r"^(\d+(?:\.\d+)*)", version.strip())
    return tuple(int(p) for p in match.group(1).split(".")) if match else None


def meets(version: str, minimum: str) -> bool:
    have, need = release_tuple(version), release_tuple(minimum)
    if have is None or need is None:
        return False
    width = max(len(have), len(need))
    return have + (0,) * (width - len(have)) >= need + (0,) * (width - len(need))


def engine_version() -> str | None:
    if shutil.which("scs") is None:
        return None
    try:
        out = subprocess.run(
            ["scs", "--version", "--json"], capture_output=True, text=True, timeout=60
        )
        return json.loads(out.stdout)["result"]["tools_version"]
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        return None


def bundled_wheels() -> list[Path]:
    return sorted((HERE.parent / "assets" / "wheels").glob("*.whl"))


def check() -> int:
    version = engine_version()
    ok = version is not None and meets(version, MINIMUM_TOOLS_VERSION)
    result = {
        "ok": ok,
        "installed": version,
        "minimum": MINIMUM_TOOLS_VERSION,
        "python": sys.version.split()[0],
        "git": shutil.which("git") is not None,
    }
    if not ok:
        result["next"] = "Run `scs_engine.py install-plan` and show the user the command."
    emit(result)
    return 0 if ok else 1


def install_plan(wheels: list[str]) -> int:
    """The install command for the user to approve, in the D-27 order. Installs nothing."""
    venv = Path(tempfile.gettempdir()) / "scs-venv"
    pip = f"{venv}/bin/pip"
    staged = [str(p) for p in map(Path, wheels)] or [str(p) for p in bundled_wheels()]
    plans = [
        {
            "source": "PyPI",
            "command": f"python3 -m venv {venv} && {pip} install '{PACKAGE}=={RELEASE}'",
            "note": "Pin the version: an unpinned install gets the old scs-tools 0.1.0.",
        },
        {
            "source": "GitHub tag",
            "command": (
                f"python3 -m venv {venv} && {pip} install "
                "'git+https://github.com/tim-mccrimmon/structured-context-spec"
                f"@v{RELEASE}#subdirectory=tools/scd-validator' "
                "'git+https://github.com/tim-mccrimmon/structured-context-spec"
                f"@v{RELEASE}#subdirectory=tools/cli'"
            ),
            "note": "Some sandboxes block GitHub until the repository is added to the session.",
        },
    ]
    if staged:
        plans.insert(
            0,
            {
                "source": "bundled or uploaded wheels",
                "command": f"python3 -m venv {venv} && {pip} install " + " ".join(staged),
                "note": "Dependencies (click, pyyaml, jinja2, jsonschema, colorama, tabulate, "
                "semver) still come from PyPI. Uploaded wheels must first be staged under "
                "their standard names (stage-wheels).",
            },
        )
    emit(
        {
            "ok": True,
            "plans": plans,
            "after": f"Put {venv}/bin on PATH, then run `scs_engine.py check` again.",
            "rule": "Show the user the command and where the package comes from "
            "(pypi.org/project/scs-tools, github.com/tim-mccrimmon/structured-context-spec). "
            "Install only after the user agrees, or let the user run it.",
        }
    )
    return 0


def stage_wheels(paths: list[str]) -> int:
    """Copy wheels whose names carry an upload prefix (`a6975716-scs_tools-...whl`) to their
    standard names in a temporary directory, unchanged, so pip accepts them."""
    target = Path(tempfile.gettempdir()) / "scs-wheels"
    target.mkdir(exist_ok=True)
    staged, rejected = [], []
    for raw in paths:
        path = Path(raw)
        match = WHEEL_RE.search(path.name)
        if not path.is_file() or not match:
            rejected.append(raw)
            continue
        destination = target / match.group(1)
        shutil.copyfile(path, destination)
        staged.append(str(destination))
    emit({"ok": not rejected and bool(staged), "staged": staged, "rejected": rejected})
    return 0 if staged and not rejected else 1


def run(args: list[str]) -> int:
    if not args or args[0] not in ("scs", "scs-validate"):
        emit({"ok": False, "error": "run takes `scs ...` or `scs-validate ...`"})
        return 3
    if shutil.which(args[0]) is None:
        emit({"ok": False, "error": f"{args[0]} is not installed; run `check`"})
        return 4
    if "--json" not in args:
        args = [*args, "--json"]
    out = subprocess.run(args, capture_output=True, text=True)
    try:
        envelope = json.loads(out.stdout)
    except ValueError:
        emit(
            {
                "ok": False,
                "error": "The engine did not return an envelope",
                "exit_code": out.returncode,
                "stderr": out.stderr[-2000:],
            }
        )
        return out.returncode or 5
    emit(envelope)
    return out.returncode


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 3
    command, rest = argv[0], argv[1:]
    if command == "check":
        return check()
    if command == "install-plan":
        return install_plan(rest)
    if command == "stage-wheels":
        return stage_wheels(rest)
    if command == "run":
        return run(rest)
    print(__doc__, file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
