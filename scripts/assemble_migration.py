#!/usr/bin/env python3
"""Assemble docs/MIGRATION-0.7.0.md from the fragments in docs/migration.d/.

Each work package adds a fragment as it lands; this script joins them in reading order. Run with
--check to fail if the guide is out of date (CI does).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = ROOT / "docs" / "migration.d"
GUIDE = ROOT / "docs" / "MIGRATION-0.7.0.md"
ORDER = [
    "_intro.md",
    "WP-03.md",  # Domain repositories
    "WP-05.md",  # CLI
    "WP-04.md",  # Validator
    "WP-14.md",  # Versions, compile, diagnostics
    "WP-06.md",  # Authors, scaffolding, maintenance
    "WP-07.md",  # Intake and provenance
    "WP-08.md",  # Change summary
    "WP-16.md",  # Layered context
    "WP-10.md",  # Agent Skills
    "housekeeping.md",
    "ISS-042-045.md",
]


def assemble() -> str:
    present = sorted(p.name for p in FRAGMENTS.glob("*.md"))
    missing = sorted(set(present) - set(ORDER))
    if missing:
        raise SystemExit(f"fragments not in ORDER: {', '.join(missing)}")
    parts = [(FRAGMENTS / name).read_text(encoding="utf-8").strip() for name in ORDER]
    return "\n\n".join(parts) + "\n"


def main() -> int:
    text = assemble()
    if "--check" in sys.argv[1:]:
        if not GUIDE.exists() or GUIDE.read_text(encoding="utf-8") != text:
            print(f"{GUIDE.relative_to(ROOT)} is out of date; run scripts/assemble_migration.py")
            return 1
        print(f"{GUIDE.relative_to(ROOT)} is up to date")
        return 0
    GUIDE.write_text(text, encoding="utf-8")
    print(f"wrote {GUIDE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
