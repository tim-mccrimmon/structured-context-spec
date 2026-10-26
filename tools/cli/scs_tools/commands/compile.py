"""
Compile command - build a runtime artifact from a Domain or Project bundle
"""

import hashlib
from pathlib import Path

import click
from scs_validator import api
from scs_validator.envelope import Change, diagnostics_from_results, relative
from scs_validator.names import bundle_name
from scs_validator.resolver import find_project_root

from scs_tools.compiler import compile_bundle, render
from scs_tools.machine import EXIT_FILE, EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.workspace import repository_root, within


@click.command()
@click.argument("bundle_file", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write the artifact here (default: dist/<bundle-name>-<version>.yaml in the workspace)",
)
@click.option(
    "--stdout",
    "to_stdout",
    is_flag=True,
    help="Write the artifact to stdout instead of a file (not with --json)",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    show_default=True,
    help="Artifact serialization",
)
@click.option(
    "--allow-draft",
    is_flag=True,
    help="Compile DRAFT bundles; the artifact version becomes DRAFT+<digest>",
)
@click.option("--no-cites", is_flag=True, help="Leave standard citations out of the artifact")
@click.option("--no-validate", is_flag=True, help="Skip validation before compiling")
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing")
@machine_command("compile")
def compile(
    envelope: Envelope,
    out: Output,
    bundle_file: Path,
    output: Path,
    to_stdout: bool,
    fmt: str,
    allow_draft: bool,
    no_cites: bool,
    no_validate: bool,
    dry_run: bool,
) -> None:
    """
    Compile a Domain or Project bundle into a runtime artifact

    The artifact is one self-contained file holding the bundle's prohibitions and directives
    as rules with stable ids, its facts, a version, and a self-identification rule. It
    contains no timestamps or other volatile content, so the same source always produces the
    same bytes and hash. It is written to the workspace's dist/ directory as
    <bundle-name>-<version>.yaml unless --output or --stdout says otherwise.
    See spec/0.7/runtime-artifact.md.

    \b
    Examples:
        scs compile bundles/domain-bundle.yaml
        scs compile bundles/project-bundle.yaml --allow-draft
        scs compile bundles/project-bundle.yaml --stdout
    """
    if to_stdout and (out.machine or output or dry_run):
        raise CommandError(
            "USAGE_ERROR",
            "--stdout cannot be combined with --json, --output, or --dry-run",
            exit_code=EXIT_USAGE,
        )
    if not bundle_file.is_file():
        raise CommandError(
            "FILE_NOT_FOUND", f"No such bundle file: {bundle_file}", exit_code=EXIT_FILE
        )

    root = repository_root(bundle_file.parent) or find_project_root(bundle_file)

    if not no_validate:
        try:
            report = api.validate_bundle(bundle_file)
        except api.SchemaDirNotFound:
            raise CommandError(
                "SCHEMA_DIR_NOT_FOUND",
                "Schema directory not found; set SCS_SCHEMA_DIR",
                exit_code=EXIT_FILE,
            )
        if report.exit_code() == 1:
            envelope.diagnostics.extend(
                d for d in diagnostics_from_results(report.all_results()) if d.severity == "error"
            )
            envelope.result = {"compiled": False}
            out.echo("Validation failed; nothing compiled.", err=True)
            return

    result = compile_bundle(bundle_file, allow_draft=allow_draft, include_cites=not no_cites)
    for warning in result.warnings:
        envelope.warning("COMPILE_WARNING", warning)
    if result.errors or result.artifact is None:
        for error in result.errors:
            envelope.error("COMPILE_ERROR", error)
        envelope.result = {"compiled": False}
        return

    artifact = result.artifact
    text = render(artifact, fmt)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    rule_count = len(artifact["rules"]) - 1
    fact_count = len(artifact.get("facts", []))
    summary = (
        f"Compiled {artifact['id']} {artifact['version']}: "
        f"{rule_count} rules, {fact_count} facts, sha256 {digest}"
    )

    if to_stdout:
        click.echo(text, nl=False)
        click.echo(summary, err=True)
        return

    target = output or (
        find_project_root(bundle_file)
        / "dist"
        / f"{bundle_name(str(artifact['id']))}-{artifact['version']}.{fmt}"
    )
    shown = relative(target, root)
    if not within(target, root):
        raise CommandError(
            "OUTPUT_OUTSIDE_REPO",
            f"{target} is outside the repository ({root}); compile output stays inside it",
            path=shown,
        )

    data = text.encode("utf-8")
    if not (target.is_file() and target.read_bytes() == data):
        envelope.changes.append(Change("modify" if target.exists() else "create", path=shown))
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    envelope.result = {
        "compiled": True,
        "path": shown,
        "id": artifact["id"],
        "version": artifact["version"],
        "sha256": digest,
        "source_digest": artifact.get("source_digest"),
    }
    out.echo(f"{summary} -> {shown}" + (" (dry run, nothing written)" if dry_run else ""))
