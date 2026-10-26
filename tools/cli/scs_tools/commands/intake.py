"""
Intake command - write a workspace's intake record (intake.yaml)
"""

import sys

import click

from scs_tools import intake as record
from scs_tools.machine import Envelope, Output, machine_command

FINDING_KINDS = (
    "framework-conflict",
    "missing-protection",
    "technical-risk",
    "ethical-risk",
    "layer-conflict",
)


@click.group()
def intake():
    """
    Write the intake record (intake.yaml)

    The intake record holds a workspace's intake answers, approvers, source documents, and
    review findings (RFC 0002 sections 4 and 12). It is not an SCD and is never compiled.
    These commands are its only writers; each change is validated before it is written.
    """
    pass


def _done(out: Output, envelope: Envelope, dry_run: bool) -> None:
    verb = "Would change" if dry_run else "Changed"
    if not envelope.changes:
        out.echo("Nothing to change")
    for change in envelope.changes:
        out.echo(f"{verb}: {change.action} {change.path}")


@intake.command("set")
@click.argument("field")
@click.argument("value")
@click.option(
    "--workspace", default=None, help="Workspace: domain or a Project name (default: current)"
)
@click.option("--dry-run", is_flag=True, help="Report the change; write nothing")
@machine_command("intake set")
def set_field(envelope, out, field, value, workspace, dry_run):
    """
    Set one field of the intake record

    VALUE is YAML; '-' reads it from stdin. For answers and source_documents (keyed by id) and
    approvers (keyed by person), a single object replaces the entry with the same key or is
    added. Any other value replaces the field. An answer without answered_at gets the current
    time (UTC).

    \b
    Examples:
        scs intake set audience organization
        scs intake set certifications '[std:iso-13485:2016, std:iec-62304:2006-a1]'
        scs intake set approvers '{person: Jane Doe <jane@acme-health.org>, role: QA Lead}'
        scs intake set answers - < answer.yaml
    """
    stdin = sys.stdin.read() if value == "-" else None
    record.set_field(envelope, workspace, field, value, stdin, dry_run)
    _done(out, envelope, dry_run)


@intake.command("record-finding")
@click.option("--id", "finding_id", default=None, help="Finding id (default: the next rf-N)")
@click.option("--kind", required=True, type=click.Choice(FINDING_KINDS), help="Finding kind")
@click.option("--target", required=True, help="The SCD item: scd:<tier>:<name>#<item-id>")
@click.option("--finding", required=True, help="The finding, in plain language")
@click.option("--cites", multiple=True, help="A citation the finding rests on (repeatable)")
@click.option("--decision", required=True, type=click.Choice(["changed", "kept", "deferred"]))
@click.option("--rationale", default=None, help="Why; required when the decision is kept")
@click.option("--decided-by", default=None, help="Name <email>, or role:<name>")
@click.option("--decided-at", default=None, help="ISO 8601 time (default: now, UTC)")
@click.option(
    "--workspace", default=None, help="Workspace: domain or a Project name (default: current)"
)
@click.option("--dry-run", is_flag=True, help="Report the change; write nothing")
@machine_command("intake record-finding")
def record_finding(
    envelope,
    out,
    finding_id,
    kind,
    target,
    finding,
    cites,
    decision,
    rationale,
    decided_by,
    decided_at,
    workspace,
    dry_run,
):
    """
    Record a review finding and the user's decision

    The review is advisory (RFC 0002 section 12): a finding never blocks an operation. Giving
    an existing --id replaces that finding, for example when a deferred finding is decided.

    \b
    Examples:
        scs intake record-finding --kind framework-conflict \\
            --target scd:project:design-history#DC-004 \\
            --finding "Lets the assistant mark DHR records approved" \\
            --cites std:21-cfr-820 --decision changed \\
            --decided-by "Jane Doe <jane@acme-health.org>"
    """
    record.record_finding(
        envelope,
        workspace,
        finding_id,
        kind,
        target,
        finding,
        list(cites),
        decision,
        rationale,
        decided_by,
        decided_at,
        dry_run,
    )
    _done(out, envelope, dry_run)
