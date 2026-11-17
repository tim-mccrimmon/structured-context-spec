"""
SCD command - write SCD content through the engine (D-08)
"""

import sys
from pathlib import Path

import click
import yaml
from scs_validator import api
from scs_validator.envelope import Change, diagnostics_from_results, relative

from scs_tools.machine import EXIT_FILE, EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.workspace import repository_root, within


@click.group()
def scd():
    """
    Write SCDs

    Agents and scripts write SCD content through this command rather than editing files, so
    every write is validated first and reported in the result envelope.
    """


@scd.command("write")
@click.argument("path", type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "--from-file",
    "source",
    required=True,
    help="Read the SCD's YAML from this file; '-' reads stdin",
)
@click.option("--dry-run", is_flag=True, help="Validate and report the change; write nothing")
@machine_command("scd write")
def write(envelope: Envelope, out: Output, path: Path, source: str, dry_run: bool) -> None:
    """
    Validate an SCD and write it to PATH

    The content is checked against the SCD schema and rules before anything is written; an
    invalid SCD is not written. PATH must be inside the repository.

    \b
    Examples:
        scs scd write context/project/release-gates.yaml --from-file - < release-gates.yaml
        scs scd write context/project/release-gates.yaml --from-file draft.yaml --dry-run
    """
    if source == "-":
        text = sys.stdin.read()
    else:
        try:
            text = Path(source).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise CommandError("FILE_UNREADABLE", f"Cannot read {source}: {e}", exit_code=EXIT_FILE)
    if not text.strip():
        raise CommandError("INPUT_EMPTY", "No SCD content was given", exit_code=EXIT_USAGE)

    root = repository_root(path.parent if path.parent.exists() else Path.cwd())
    if root is None or not within(path, root):
        raise CommandError(
            "OUTPUT_OUTSIDE_REPO",
            f"{path} is outside the repository; SCDs are written inside it",
            path=str(path),
        )
    shown = relative(path, root)

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise CommandError("PARSE_YAML_SYNTAX", f"The SCD is not valid YAML: {e}", path=shown)

    try:
        report = api.validate_scd_data(data, shown)
    except api.SchemaDirNotFound:
        raise CommandError(
            "SCHEMA_DIR_NOT_FOUND", "Schema directory not found; set SCS_SCHEMA_DIR", EXIT_FILE
        )
    envelope.diagnostics.extend(diagnostics_from_results(report.all_results()))
    envelope.result = {"path": shown, "id": data.get("id") if isinstance(data, dict) else None}
    if report.exit_code() == 1:
        envelope.result["written"] = False
        return

    if not (path.is_file() and path.read_text(encoding="utf-8") == text):
        envelope.changes.append(Change("modify" if path.exists() else "create", path=shown))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    envelope.result["written"] = bool(envelope.changes) and not dry_run
    out.echo(
        f"{'Would write' if dry_run else 'Wrote'} {shown}"
        if envelope.changes
        else f"{shown} unchanged"
    )
