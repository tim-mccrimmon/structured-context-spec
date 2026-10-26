"""Validation command for SCS CLI."""

import sys
from pathlib import Path

import click

from .. import __version__, api
from ..reporter import Reporter
from ..utils import SCHEMA_DIR_ENV_VAR, ValidationError


@click.command()
@click.version_option(version=__version__, prog_name="scs-validate")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--bundle",
    "-b",
    type=click.Path(exists=True),
    help="Validate an SCD bundle file",
)
@click.option(
    "--domain",
    "-d",
    type=click.Path(exists=True),
    help="Validate a domain manifest file (schema + Domain Ontology rules, RFC-0001)",
)
@click.option(
    "--checkpoint",
    "-c",
    type=click.Path(exists=True),
    help="Validate a checkpoint record file (any-ai-actor-model.md, RFC-0001/ISS-006)",
)
@click.option(
    "--repo",
    "-r",
    type=click.Path(exists=True, file_okay=False),
    help=(
        "Validate every workspace of a Domain repository (the default with no other input "
        "when run at a Domain repository root)"
    ),
)
@click.option(
    "--schema-dir",
    "-s",
    type=click.Path(exists=True),
    help=(
        "Directory containing JSON schema files (default: $SCS_SCHEMA_DIR, else a schema/ dir "
        "found from the current directory upward or in the source checkout, else the packaged copy)"
    ),
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Fail on warnings (exit code 2)",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
@click.option(
    "--skip-completeness",
    is_flag=True,
    help="Skip Level 6 completeness validation",
)
@click.option(
    "--completeness-rules",
    type=click.Path(exists=True),
    help="Path to custom completeness rules file",
)
def validate(
    files: tuple,
    bundle: str | None,
    domain: str | None,
    checkpoint: str | None,
    repo: str | None,
    schema_dir: str | None,
    output: str,
    strict: bool,
    no_color: bool,
    verbose: bool,
    skip_completeness: bool,
    completeness_rules: str | None,
) -> None:
    """Validate SCS documents and bundles.

    Examples:

        \b
        # Validate a single SCD file
        scs validate context/meta/roles.yaml

        \b
        # Validate multiple SCD files
        scs validate context/meta/*.yaml

        \b
        # Validate a bundle
        scs validate --bundle context/bundle.yaml

        \b
        # Validate every workspace of a Domain repository (run at its root)
        scs-validate --strict

        \b
        # Validate a domain manifest (Domain Ontology, RFC-0001)
        scs validate --domain domain-manifest.yaml

        \b
        # Validate a checkpoint record (any-ai-actor-model.md, RFC-0001/ISS-006)
        scs validate --checkpoint checkpoint.yaml

        \b
        # Strict mode (fail on warnings)
        scs validate --bundle context/bundle.yaml --strict

        \b
        # JSON output
        scs validate --bundle context/bundle.yaml --output json
    """

    def log(message: str) -> None:
        if verbose:
            click.echo(message)

    try:
        try:
            v = api.Validators(schema_dir, completeness_rules)
        except api.SchemaDirNotFound as e:
            looked = "\n".join(f"  {p}" for p in e.searched)
            click.echo(
                "Error: Schema directory not found.\n"
                f"Looked in:\n{looked}\n"
                f"Use --schema-dir or set {SCHEMA_DIR_ENV_VAR} to specify the location",
                err=True,
            )
            sys.exit(4)

        if bundle:
            report = api.validate_bundle(
                bundle, skip_completeness=skip_completeness, strict=strict, validators=v, log=log
            )
        elif domain:
            report = api.validate_domain_manifest(domain, validators=v, log=log)
        elif checkpoint:
            report = api.validate_checkpoint(checkpoint, validators=v, log=log)
        elif files:
            report = api.validate_files(files, validators=v, log=log)
        elif repo or api.find_repository(Path.cwd()):
            report = api.validate_repository(
                Path(repo) if repo else Path.cwd(),
                skip_completeness=skip_completeness,
                strict=strict,
                validators=v,
                log=log,
            )
        else:
            click.echo("Error: No files or bundle specified\n", err=True)
            click.echo(click.get_current_context().get_help())
            sys.exit(3)

        reporter = Reporter(use_color=not no_color)
        if output == "json":
            click.echo(reporter.report_json(report, __version__, strict))
        else:
            click.echo(reporter.report_text(report, __version__, strict))
        sys.exit(report.exit_code(strict))

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(5)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(5)
