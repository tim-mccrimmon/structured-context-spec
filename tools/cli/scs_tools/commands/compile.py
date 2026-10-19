"""
Compile command - build a runtime artifact from a Domain or Project bundle
"""

import hashlib
import subprocess
import sys
from pathlib import Path

import click


@click.command()
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Write the artifact to this file (default: stdout)",
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
def compile(bundle_file, output, fmt, allow_draft, no_cites, no_validate):
    """
    Compile a Domain or Project bundle into a runtime artifact

    The artifact is one self-contained file holding the bundle's prohibitions and directives
    as rules with stable ids, its facts, a version, and a self-identification rule. It
    contains no timestamps or other volatile content, so the same source always produces the
    same bytes and hash.
    See spec/0.6/runtime-artifact.md.

    \b
    Examples:
        scs compile bundles/domain-bundle.yaml -o global.yaml
        scs compile bundles/project-bundle.yaml -o projects/my-app.yaml
        scs compile bundles/project-bundle.yaml --allow-draft
    """
    try:
        from scs_tools.compiler import compile_bundle, render
    except ImportError as e:  # scs-validator not installed
        raise click.ClickException(
            f"scs compile needs scs-validator ({e}). "
            "Install with: pip install 'scs-tools[validator]'"
        )

    if not no_validate:
        validation = subprocess.run(
            [
                sys.executable,
                "-m",
                "scs_validator",
                "--bundle",
                str(bundle_file),
                "--no-color",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if validation.returncode not in (0, 2):
            click.echo(validation.stdout, err=True)
            if validation.stderr.strip():
                click.echo(validation.stderr, err=True)
            raise click.ClickException("Validation failed; nothing compiled.")

    result = compile_bundle(bundle_file, allow_draft=allow_draft, include_cites=not no_cites)

    for warning in result.warnings:
        click.echo(f"Warning: {warning}", err=True)
    if result.errors:
        for error in result.errors:
            click.echo(f"Error: {error}", err=True)
        raise click.ClickException("Compilation failed.")

    text = render(result.artifact, fmt)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    rule_count = len(result.artifact["rules"]) - 1
    fact_count = len(result.artifact.get("facts", []))
    summary = (
        f"Compiled {result.artifact['id']} {result.artifact['version']}: "
        f"{rule_count} rules, {fact_count} facts, sha256 {digest}"
    )

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(text.encode("utf-8"))
        click.echo(f"{summary} -> {output}")
    else:
        click.echo(text, nl=False)
        click.echo(summary, err=True)
