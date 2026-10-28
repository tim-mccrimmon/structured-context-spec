#!/usr/bin/env python3
"""Check that relative links in the spec, docs, RFCs, and skills point to files that exist.

External links (http, mailto) and in-page anchors are not checked. Links inside code blocks are
ignored, and so is released history (FROZEN).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREES = ["spec", "docs", "rfcs", "skills"]
FILES = ["README.md", "CONTRIBUTING.md", "RELEASE-NOTES-0.7.0.md"]
# Released history, kept as published.
FROZEN = ["spec/0.3", "spec/0.5", "docs/MIGRATION-0.3.md"]
LINK_RE = re.compile(r"\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.DOTALL | re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def pages():
    for tree in TREES:
        for page in sorted((ROOT / tree).rglob("*.md")):
            if not any(page.relative_to(ROOT).as_posix().startswith(f) for f in FROZEN):
                yield page
    for name in FILES:
        if (ROOT / name).exists():
            yield ROOT / name


def broken(page: Path):
    text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", page.read_text(encoding="utf-8")))
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        path = target.split("#", 1)[0]
        resolved = (ROOT / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
        if not resolved.exists():
            yield target


def main() -> int:
    failures = [(p, t) for p in pages() for t in broken(p)]
    for page, target in failures:
        print(f"{page.relative_to(ROOT)}: {target}")
    print(f"{len(failures)} broken link(s)" if failures else "all relative links resolve")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
