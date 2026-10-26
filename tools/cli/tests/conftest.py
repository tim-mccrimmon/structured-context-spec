"""Every diagnostic the test suite produces must have a registered code (D-10).

The registry is schema/diagnostics/codes.yaml. A diagnostic created with no code, or with a
code that is unregistered or registered at another severity, fails the session.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Set, Tuple

import pytest
import yaml
from scs_validator import utils

REGISTRY = Path(__file__).resolve().parents[3] / "schema" / "diagnostics" / "codes.yaml"
SEEN: Set[Tuple[str, Optional[str]]] = set()


def _record(severity: str, code: Optional[str]) -> None:
    SEEN.add((severity, code))


def pytest_sessionstart(session: pytest.Session) -> None:
    utils.DIAGNOSTIC_HOOKS.append(_record)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    codes = (yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}).get("codes") or {}
    problems = sorted(
        f"{severity} {code or '(no code)'}"
        + ("" if code not in codes else f" (registered as {codes[code]['severity']})")
        for severity, code in SEEN
        if code not in codes or codes[code]["severity"] != severity
    )
    if problems:
        print("\nDiagnostics without a registered code (schema/diagnostics/codes.yaml):")
        for line in problems:
            print(f"  {line}")
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """No scs command opens a network connection (WP-05)."""
    import socket

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("an scs command tried to open a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
