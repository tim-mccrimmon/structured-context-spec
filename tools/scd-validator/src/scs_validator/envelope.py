"""The machine-mode result envelope (RFC 0002 §3, schema/cli/envelope-schema.json).

In machine mode (`--json`) a command writes exactly one envelope to stdout and nothing else.
Both `scs` and `scs-validate` use this module, so the two cannot drift apart.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import click

from .utils import (
    ValidationError,
    ValidationInfo,
    ValidationResult,
    ValidationWarning,
    _created,
)

# Spec version the tools implement; `tools_version` is the package version.
SCS_VERSION = "0.7.0"

EXIT_OK = 0
EXIT_ERRORS = 1
EXIT_WARNINGS = 2  # warnings under --strict
EXIT_USAGE = 3  # bad arguments or no input
EXIT_FILE = 4  # missing, unreadable, or unwritable file
EXIT_INTERNAL = 5


@dataclass
class Diagnostic:
    severity: str  # error, warning, info
    code: str
    message: str
    path: Optional[str] = None
    suggestion: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        _created(self.severity, self.code)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "suggestion": self.suggestion,
        }


@dataclass
class Change:
    """A file effect (`create`, `modify`, `delete`, with `path`) or a git effect (`git-init`,
    `git-commit`, `git-tag`, with `ref`; a commit also lists `paths`) (D-09)."""

    action: str
    path: Optional[str] = None
    ref: Optional[str] = None
    paths: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"action": self.action}
        if self.path is not None:
            out["path"] = self.path
        if self.ref is not None:
            out["ref"] = self.ref
        if self.paths is not None:
            out["paths"] = self.paths
        return out


@dataclass
class Envelope:
    command: str
    tools_version: str
    changes: List[Change] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    exit_code: Optional[int] = None  # computed from diagnostics when not set

    def error(self, code: str, message: str, path: Optional[str] = None, **suggestion: Any) -> None:
        self.diagnostics.append(Diagnostic("error", code, message, path, suggestion or None))

    def warning(self, code: str, message: str, path: Optional[str] = None) -> None:
        self.diagnostics.append(Diagnostic("warning", code, message, path))

    def info(self, code: str, message: str, path: Optional[str] = None) -> None:
        self.diagnostics.append(Diagnostic("info", code, message, path))

    def has_errors(self) -> bool:
        return any(d.severity == "error" for d in self.diagnostics)

    def final_exit_code(self, strict: bool = False) -> int:
        if self.exit_code is not None:
            return self.exit_code
        if self.has_errors():
            return EXIT_ERRORS
        if strict and any(d.severity == "warning" for d in self.diagnostics):
            return EXIT_WARNINGS
        return EXIT_OK

    def to_dict(self, strict: bool = False) -> Dict[str, Any]:
        code = self.final_exit_code(strict)
        return {
            "scs_version": SCS_VERSION,
            "tools_version": self.tools_version,
            "command": self.command,
            "ok": code == EXIT_OK,
            "exit_code": code,
            "changes": [c.to_dict() for c in self.changes],
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "result": self.result,
        }

    def dumps(self, strict: bool = False) -> str:
        return json.dumps(self.to_dict(strict), indent=2, ensure_ascii=False)


def diagnostics_from_results(results: List[ValidationResult]) -> List[Diagnostic]:
    """Validator findings as envelope diagnostics, in report order."""
    out = []
    for result in results:
        findings: List[Union[ValidationError, ValidationWarning, ValidationInfo]] = [
            *result.errors,
            *result.warnings,
            *result.infos,
        ]
        for found in findings:
            out.append(
                Diagnostic(
                    found.severity,
                    found.code or "UNCODED",
                    found.message,
                    found.file_path,
                )
            )
    return out


def relative(path: Path, root: Path) -> str:
    """`path` as a POSIX path relative to `root` (D-42); absolute if it is outside."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


class MachineMode:
    """Mixin for a click command or group: usage errors exit 3, not click's 2 (D-12), and with
    --json every failure is still one envelope on stdout. Set `tools_version` on the class."""

    tools_version = "unknown"

    def main(  # type: ignore[no-untyped-def]
        self,
        args: Optional[Sequence[str]] = None,
        prog_name: Optional[str] = None,
        complete_var: Optional[str] = None,
        standalone_mode: bool = True,
        **extra: Any,
    ):
        argv = list(sys.argv[1:] if args is None else args)
        machine = "--json" in argv
        try:
            rv = super().main(  # type: ignore[misc]
                args=argv,
                prog_name=prog_name,
                complete_var=complete_var,
                standalone_mode=False,
                **extra,
            )
        except click.UsageError as e:
            command = _command_name(e.ctx)
            if machine:
                envelope = Envelope(command, self.tools_version, exit_code=EXIT_USAGE)
                envelope.error("USAGE_ERROR", e.format_message())
                click.echo(envelope.dumps())
            else:
                e.show()
            sys.exit(EXIT_USAGE)
        except click.Abort:
            click.echo("Aborted!", err=True)
            sys.exit(EXIT_ERRORS)
        except click.ClickException as e:
            e.show()
            sys.exit(e.exit_code)
        if not standalone_mode:
            return rv
        sys.exit(rv if isinstance(rv, int) else 0)


def _command_name(ctx: Optional[click.Context]) -> str:
    """The command path without the program name (`bundle version`)."""
    if ctx is None:
        return ""
    return " ".join(ctx.command_path.split()[1:]) or ctx.command_path
