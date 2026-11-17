#!/usr/bin/env python3
"""Package each SCS skill as a ZIP for upload to Claude (claude.ai), optionally with wheels.

Each ZIP holds one skill directory at its root. With --wheels, the scs-tools and scs-validator
wheels in that directory are added under `assets/wheels/`, where `scripts/scs_engine.py
install-plan` finds them, for clients that cannot reach a package index.

    python skills/package.py --out dist/skills
    python skills/package.py --out dist/skills --wheels dist
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

SKILLS = Path(__file__).resolve().parent
WHEEL_RE = re.compile(r"^scs_(?:tools|validator)-[0-9][^-]*-py3-none-any\.whl$")
SKIP = {"__pycache__", ".DS_Store"}


def wheels(directory: Path) -> list[Path]:
    found = sorted(p for p in directory.glob("*.whl") if WHEEL_RE.match(p.name))
    names = {p.name.split("-")[0] for p in found}
    if names != {"scs_tools", "scs_validator"} or len(found) != 2:
        raise SystemExit(f"{directory}: need exactly one scs_tools and one scs_validator wheel")
    return found


def package(skill: Path, out: Path, bundled: list[Path]) -> Path:
    target = out / f"{skill.name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill.rglob("*")):
            if path.is_file() and not SKIP.intersection(path.parts):
                archive.write(path, f"{skill.name}/{path.relative_to(skill).as_posix()}")
        for wheel in bundled:
            archive.write(wheel, f"{skill.name}/assets/wheels/{wheel.name}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="directory for the ZIPs")
    parser.add_argument("--wheels", type=Path, help="directory holding the two wheels to bundle")
    args = parser.parse_args()
    bundled = wheels(args.wheels) if args.wheels else []
    args.out.mkdir(parents=True, exist_ok=True)
    for skill in sorted(p.parent for p in SKILLS.glob("*/SKILL.md")):
        print(package(skill, args.out, bundled))
    return 0


if __name__ == "__main__":
    sys.exit(main())
