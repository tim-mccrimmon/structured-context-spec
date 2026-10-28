#!/usr/bin/env python3
"""Keep the copies inside the SCS skills in step with their sources.

A skill must be self-contained, so some files are copied into it:

- `scripts/scs_engine.py` into every skill, from `scs-intake/scripts/scs_engine.py`;
- `scs-validate/references/diagnostics.md`, generated from `schema/diagnostics/codes.yaml`;
- `scs-compile/references/placement/*.md`, from `docs/placement/`.

    python skills/sync.py          # write the copies
    python skills/sync.py --check  # exit 1 if any copy differs (CI)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict

import yaml

SKILLS = Path(__file__).resolve().parent
ROOT = SKILLS.parent
ENGINE_SOURCE = SKILLS / "scs-intake" / "scripts" / "scs_engine.py"
CODES = ROOT / "schema" / "diagnostics" / "codes.yaml"
PLACEMENT = ROOT / "docs" / "placement"
SPEC_LINK = re.compile(r"\]\(\.\./\.\./spec/0\.7/([a-z-]+\.md)\)")
SPEC_URL = "https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/"


def skills() -> list:
    return sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))


def diagnostics() -> str:
    codes = yaml.safe_load(CODES.read_text(encoding="utf-8"))["codes"]
    lines = [
        "# Diagnostic Codes",
        "",
        "Every code the SCS tools emit, with its severity. Generated from",
        "`schema/diagnostics/codes.yaml` by `skills/sync.py`; do not edit.",
        "",
        "| Code | Severity | Meaning |",
        "|---|---|---|",
    ]
    for code in sorted(codes):
        meaning = " ".join(str(codes[code]["meaning"]).split()).replace("|", "\\|")
        lines.append(f"| `{code}` | {codes[code]['severity']} | {meaning} |")
    return "\n".join(lines) + "\n"


def placement_page(text: str) -> str:
    # Relative links into the spec do not resolve inside a skill; link to the repository.
    return SPEC_LINK.sub(lambda m: f"]({SPEC_URL}{m.group(1)})", text)


def expected() -> Dict[Path, str]:
    files: Dict[Path, str] = {}
    engine = ENGINE_SOURCE.read_text(encoding="utf-8")
    for skill in skills():
        files[skill / "scripts" / "scs_engine.py"] = engine
    files[SKILLS / "scs-validate" / "references" / "diagnostics.md"] = diagnostics()
    for page in sorted(PLACEMENT.glob("*.md")):
        target = SKILLS / "scs-compile" / "references" / "placement" / page.name
        files[target] = placement_page(page.read_text(encoding="utf-8"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="Report drift; write nothing")
    args = parser.parse_args()
    drift = []
    for path, content in expected().items():
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current == content:
            continue
        drift.append(path.relative_to(ROOT).as_posix())
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        if drift:
            print("Out of date (run python skills/sync.py):\n  " + "\n  ".join(drift))
            return 1
        print(f"skill copies match their sources ({len(expected())} files)")
        return 0
    print(f"wrote {len(drift)} file(s)" if drift else "nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
