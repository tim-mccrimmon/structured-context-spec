#!/usr/bin/env python3
"""Vendor the repo-root JSON Schemas into the scs-validator package (ISS-035).

The repo-root ``schema/`` directory is the source of truth (the spec, examples and docs all point at
it). The validator wheel has to carry its own copy, so this script mirrors every ``schema/**/*.json``
into ``src/scs_validator/schemas/``. Run it after changing anything under ``schema/``.

    python scripts/sync_schemas.py           # copy schema/ -> src/scs_validator/schemas/
    python scripts/sync_schemas.py --check   # exit 1 if the copy is out of date (used by tests/CI)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2] / "schema"
TARGET = HERE.parent / "src" / "scs_validator" / "schemas"


def _files(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in sorted(root.rglob("*.json"))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="only report drift; do not copy")
    args = parser.parse_args()

    if not SOURCE.is_dir():
        print(f"error: source schema directory not found: {SOURCE}", file=sys.stderr)
        return 2

    source = _files(SOURCE)
    vendored = _files(TARGET) if TARGET.is_dir() else {}
    missing = sorted(set(source) - set(vendored))
    extra = sorted(set(vendored) - set(source))
    stale = sorted(
        r for r in set(source) & set(vendored) if source[r].read_bytes() != vendored[r].read_bytes()
    )

    if args.check:
        if missing or extra or stale:
            print("vendored schemas are out of date; run: python scripts/sync_schemas.py")
            for label, items in (("missing", missing), ("extra", extra), ("stale", stale)):
                for item in items:
                    print(f"  {label}: {item}")
            return 1
        print(f"vendored schemas match schema/ ({len(source)} files)")
        return 0

    for rel in extra:
        vendored[rel].unlink()
    for rel, src in source.items():
        dest = TARGET / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    print(f"synced {len(source)} schema files into {TARGET.relative_to(HERE.parents[2])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
