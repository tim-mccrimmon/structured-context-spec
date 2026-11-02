"""
Status command - where each workspace stands (D-83)
"""

from pathlib import Path

import click
from scs_validator.workspace import is_repository

from scs_tools import status as state
from scs_tools.machine import CommandError, machine_command
from scs_tools.workspace import find_domain_repository, find_workspace, select_workspace


@click.command()
@click.option(
    "--workspace",
    default=None,
    help="Workspace: domain or a Project name (default: current, or every workspace at the "
    "repository root)",
)
@machine_command("status")
def status(envelope, out, workspace):
    """
    Show where each workspace stands

    Read-only. Works the status out from the repository each time: the intake record, the
    documents in sources/ and whether they are recorded, SCDs with template placeholders left,
    review findings by decision, versions and changes since the latest one, uncommitted files,
    compiled artifacts, and, for a Project, the Domain's latest released version.

    \b
    Examples:
        scs status                        # at the repository root: every workspace
        scs status --workspace timekeeping
    """
    cwd = Path.cwd().resolve()
    if workspace or find_workspace(cwd) is not None:
        selected = [select_workspace(workspace).resolve()]
        root = find_domain_repository(selected[0])
    elif is_repository(cwd):
        root = cwd
        selected = state.workspaces(root)
    else:
        raise CommandError(
            "WORKSPACE_NOT_FOUND",
            "Not in an SCS workspace or Domain repository. "
            "Create one with 'scs new domain' or 'scs new project'.",
        )
    if root is None:
        root = selected[0]
    envelope.result = state.repository_status(root.resolve(), selected)
    for ws in envelope.result["workspaces"]:
        _echo(out, ws)


def _echo(out, ws):
    version = ws["latest_version"] or "none"
    out.echo(f"{ws['path']} ({ws['bundle']}, {ws['ontology']})")
    out.echo(f"  Released version: {version}; working copy: {ws['working_version']}")
    if ws["changed_since_version"]:
        out.echo(f"  Files changed since {version}: {ws['changed_since_version']}")
    if "domain_latest_version" in ws:
        out.echo(f"  Domain's latest version: {ws['domain_latest_version'] or 'none released'}")
    intake = ws["intake"]
    if intake["present"]:
        findings = ", ".join(f"{n} {d}" for d, n in intake["findings"].items())
        out.echo(f"  Intake: {', '.join(intake['fields']) or 'empty'}; findings: {findings}")
    else:
        out.echo("  Intake: not started")
    sources = ws["sources"]
    out.echo(
        f"  Sources: {len(sources['files'])} file(s), {len(sources['unrecorded'])} not recorded"
    )
    scds = ws["scds"]
    out.echo(f"  SCDs: {scds['count']}, {len(scds['placeholders'])} with placeholders left")
    out.echo(f"  Uncommitted files: {len(ws['uncommitted'])}")
    out.echo(f"  Compiled artifacts: {', '.join(ws['compiled']['artifacts']) or 'none'}")
