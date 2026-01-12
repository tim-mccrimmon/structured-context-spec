"""
Validate command - validates SCS documents and bundles
"""

import sys
from pathlib import Path
import click

try:
    from scs_validator.cli import main as validator_main
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--bundle",
    "-b",
    type=click.Path(exists=True),
    help="Validate an SCD bundle file",
)
@click.option(
    "--schema-dir",
    "-s",
    type=click.Path(exists=True),
    help="Directory containing JSON schema files",
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
    files,
    bundle,
    schema_dir,
    output,
    strict,
    no_color,
    verbose,
    skip_completeness,
    completeness_rules,
):
    """
    Validate SCS documents and bundles

    Runs validation checks across 6 levels: Syntax, Schema, Semantic,
    Relationships, Completeness, and Compliance. Use before versioning
    to ensure bundle quality.

    \b
    Examples:
        scs validate context/project/system-context.yaml  # Validate single SCD
        scs validate context/project/*.yaml               # Validate all SCDs
        scs validate --bundle bundles/project-bundle.yaml # Validate bundle
        scs validate --bundle bundles/project-bundle.yaml --strict  # Fail on warnings
        scs validate --bundle bundles/project-bundle.yaml --output json  # JSON output

    See also: scs bundle validate (shortcut for project bundle validation)
    """
    if not VALIDATOR_AVAILABLE:
        click.echo(
            "Error: scs-validator is not installed.\n"
            "Install it with: pip install scs-validator",
            err=True,
        )
        sys.exit(1)

    # Pass through to the scs-validator CLI
    ctx = click.get_current_context()
    ctx.forward(validator_main)
