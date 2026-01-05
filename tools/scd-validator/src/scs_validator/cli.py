"""Command-line interface for SCS Validator."""

import click

from . import __version__
from .commands.init import init
from .commands.validate import validate


@click.group()
@click.version_option(version=__version__, prog_name="scs")
def cli():
    """SCS - Structured Context Specification CLI.

    Manage, validate, and generate SCS projects and bundles.
    """
    pass


# Register commands
cli.add_command(init)
cli.add_command(validate)


if __name__ == "__main__":
    cli()
