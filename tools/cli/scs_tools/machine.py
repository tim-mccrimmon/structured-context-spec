"""Machine mode for `scs` commands (RFC 0002 §3, plan section 4).

A command decorated with `@machine_command("name")` gains `--json` and receives an `Envelope`
and an `Output`. It records what it did in the envelope (changes, diagnostics, result) and
prints human text only through `Output`, so under `--json` stdout carries exactly one envelope.
Failures are raised as `CommandError`; anything else unexpected becomes INTERNAL_ERROR, exit 5.
"""

from __future__ import annotations

import functools
import sys
from typing import Any, Callable, Dict, Optional

import click
from scs_validator.envelope import (
    EXIT_ERRORS,
    EXIT_FILE,
    EXIT_INTERNAL,
    EXIT_USAGE,
    Diagnostic,
    Envelope,
)

from scs_tools import __version__

__all__ = [
    "CommandError",
    "EXIT_ERRORS",
    "EXIT_FILE",
    "EXIT_USAGE",
    "Envelope",
    "Output",
    "machine_command",
]


class CommandError(Exception):
    """A failure with a registered diagnostic code and the exit code it maps to."""

    def __init__(
        self,
        code: str,
        message: str,
        exit_code: int = EXIT_ERRORS,
        path: Optional[str] = None,
        suggestion: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.path = path
        self.suggestion = suggestion


class Output:
    """Human-readable output, silent in machine mode."""

    def __init__(self, machine: bool):
        self.machine = machine

    def echo(self, message: str = "", err: bool = False, nl: bool = True) -> None:
        if not self.machine:
            click.echo(message, err=err, nl=nl)


def _report(envelope: Envelope, out: Output, strict: bool) -> int:
    code = envelope.final_exit_code(strict)
    if out.machine:
        click.echo(envelope.dumps(strict))
    else:
        for d in envelope.diagnostics:
            label = {"error": "Error", "warning": "Warning", "info": "Note"}[d.severity]
            where = f"{d.path}: " if d.path else ""
            click.echo(f"{label}: {where}{d.message}", err=True)
            if d.suggestion:
                hint = ", ".join(f"{k}={v}" for k, v in d.suggestion.items())
                click.echo(f"  Suggestion: {hint}", err=True)
    return code


def machine_command(name: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Add `--json` to a click command callback and run it in machine mode when set."""

    def decorator(f: Callable[..., None]) -> Callable[..., None]:
        @click.option(
            "--json",
            "json_mode",
            is_flag=True,
            help="Machine mode: write one JSON result envelope to stdout (RFC 0002 section 3)",
        )
        @functools.wraps(f)
        def wrapper(*args: Any, json_mode: bool = False, **kwargs: Any) -> None:
            envelope = Envelope(name, __version__)
            out = Output(json_mode)
            strict = bool(kwargs.get("strict", False))
            try:
                f(envelope, out, *args, **kwargs)
            except CommandError as e:
                envelope.diagnostics.append(
                    Diagnostic("error", e.code, e.message, e.path, e.suggestion)
                )
                envelope.exit_code = e.exit_code
            except (click.exceptions.Exit, click.Abort, click.UsageError):
                raise
            except Exception as e:  # anything unexpected is an internal error (exit 5)
                envelope.diagnostics.append(
                    Diagnostic("error", "INTERNAL_ERROR", f"{type(e).__name__}: {e}")
                )
                envelope.exit_code = EXIT_INTERNAL
            sys.exit(_report(envelope, out, strict))

        return wrapper

    return decorator
