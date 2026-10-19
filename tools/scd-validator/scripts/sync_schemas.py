#!/usr/bin/env python3
"""Vendor the repo-root JSON Schemas and meta bundle into the scs-validator package (ISS-035).

The repo-root ``schema/`` and ``meta/`` directories are the source of truth (the spec, examples
and docs all point at them). The validator wheel has to carry its own copies, so this script
mirrors every ``schema/**/*.json`` into ``src/scs_validator/schemas/`` and every
``meta/**/*.yaml`` into ``src/scs_validator/meta/``. Run it after changing either.

    python scripts/sync_schemas.py           # copy schema/ and meta/ into the package
    python scripts/sync_schemas.py --check   # exit 1 if a copy is out of date (used by tests/CI)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKAGE = HERE.parent / "src" / "scs_validator"
# (source dir, vendored dir, glob)
PAIRS = [
    (REPO / "schema", PACKAGE / "schemas", "*.json"),
    (REPO / "meta", PACKAGE / "meta", "*.yaml"),
]


def _files(root: Path, pattern: str) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in sorted(root.rglob(pattern))}


def _sync(source_dir: Path, target_dir: Path, pattern: str, check: bool) -> int:
    if not source_dir.is_dir():
        print(f"error: source directory not found: {source_dir}", file=sys.stderr)
        return 2

    source = _files(source_dir, pattern)
    vendored = _files(target_dir, pattern) if target_dir.is_dir() else {}
    missing = sorted(set(source) - set(vendored))
    extra = sorted(set(vendored) - set(source))
    stale = sorted(
        r for r in set(source) & set(vendored) if source[r].read_bytes() != vendored[r].read_bytes()
    )
    label = source_dir.name + "/"

    if check:
        if missing or extra or stale:
            print(f"vendored {label} is out of date; run: python scripts/sync_schemas.py")
            for kind, items in (("missing", missing), ("extra", extra), ("stale", stale)):
                for item in items:
                    print(f"  {kind}: {item}")
            return 1
        print(f"vendored files match {label} ({len(source)} files)")
        return 0

    for rel in extra:
        vendored[rel].unlink()
    for rel, src in source.items():
        dest = target_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    print(f"synced {len(source)} {label} files into {target_dir.relative_to(REPO)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="only report drift; do not copy")
    args = parser.parse_args()
    return max(_sync(src, dst, pattern, args.check) for src, dst, pattern in PAIRS)


if __name__ == "__main__":
    sys.exit(main())
