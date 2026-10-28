"""
SCS CLI - Command-line interface for Structured Context Specification tools
"""

import importlib
import pkgutil
import sys

import click
from scs_validator.envelope import Envelope, MachineMode

from scs_tools import __version__, commands


class SCSGroup(MachineMode, click.Group):
    tools_version = __version__


@click.group(cls=SCSGroup, invoke_without_command=True)
@click.option("--version", "show_version", is_flag=True, help="Show the version and exit.")
@click.option(
    "--json",
    "json_mode",
    is_flag=True,
    help="With --version: write a JSON result envelope (RFC 0002 section 3)",
)
@click.pass_context
def cli(ctx, show_version, json_mode):
    """
    SCS Tools - CLI for Structured Context Specification

    Create, version, and compile an organization's or a person's context in a
    Domain repository: one Domain workspace (governance for all work) and one
    workspace per Project.

    \b
    Quick Start:
        scs new domain acme                 # Create the Domain repository acme-context/
        cd acme-context
        scs new project portal              # Add a Project workspace
        scs-validate --strict               # Validate every workspace
        cd domain
        scs bundle version --version 1.0.0 --approved-by "Jane Doe <jane@acme.com>"
        scs compile bundles/domain-bundle.yaml --version 1.0.0

    \b
    Common Workflow:
        1. Create the repository and Projects → scs new domain / scs new project
        2. Add concepts as needed             → scs add bundle <concept> [--new]
        3. Write SCDs and the intake record   → scs scd write / scs intake set
        4. Validate                           → scs-validate / scs bundle validate
        5. Release a version                  → scs bundle version
        6. Compile for runtime delivery       → scs compile <bundle> --version <v>

    Commands that change files take --dry-run and --json (machine mode).
    For detailed help on any command, use: scs [command] --help
    """
    if show_version:
        from scs_validator.envelope import SCS_VERSION

        if json_mode:
            envelope = Envelope("--version", __version__)
            envelope.result = {"scs_version": SCS_VERSION, "tools_version": __version__}
            click.echo(envelope.dumps())
        else:
            click.echo(f"scs, version {__version__}")
        sys.exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _discover() -> None:
    """Register every command in scs_tools.commands: each module defines a click command or
    group named like the module (`scd.py` defines `scd`), so adding a command needs no edit
    here."""
    for info in sorted(pkgutil.iter_modules(commands.__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{commands.__name__}.{info.name}")
        command = getattr(module, info.name, None)
        if isinstance(command, click.Command):
            cli.add_command(command)


_discover()


if __name__ == "__main__":
    cli()
