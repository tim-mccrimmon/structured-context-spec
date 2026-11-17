"""Placeholder provenance (D-66, D-71).

Provenance is read at validation and versioning. A `created_by` that was never true, such as
the `$USER@example.com` an older scaffold wrote, is reported so it can be corrected; any other
value passes, since `created_by` may name a person, a team, or an organization.
"""

from __future__ import annotations

import re
from typing import Any

PLACEHOLDER_NAMES = frozenset({"developer"})
PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net")
PLACEHOLDER_TLDS = (".example", ".invalid")
_PERSON_RE = re.compile(r"^(?P<name>[^<>]*?)\s*<(?P<email>[^<>]*)>$")


def _placeholder_email(email: str) -> bool:
    domain = email.rpartition("@")[2].lower().rstrip(".")
    if any(domain == d or domain.endswith("." + d) for d in PLACEHOLDER_DOMAINS):
        return True
    return domain.endswith(PLACEHOLDER_TLDS) or domain.lstrip(".") in ("example", "invalid")


def is_placeholder(created_by: Any) -> bool:
    """True for a `created_by` that names no one: `developer`, an empty name in `Name <email>`,
    or an address at a reserved example domain (`example.com`, `.example`, `.invalid`, ...).
    An empty value is not reported here; the semantic validator requires a value."""
    if not isinstance(created_by, str) or not created_by.strip():
        return False
    value = created_by.strip()
    match = _PERSON_RE.match(value)
    if match:
        name, email = match.group("name").strip(), match.group("email").strip()
        return not name or name.lower() in PLACEHOLDER_NAMES or _placeholder_email(email)
    if value.lower() in PLACEHOLDER_NAMES:
        return True
    return "@" in value and _placeholder_email(value)
