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

    Scaffold and manage SCS-compliant projects with proper bundle structure,
    domain organization, and compliance templates.

    SCS (Structured Context Documents) are YAML files that capture essential
    project context, organized into domain bundles for validation and versioning.

    \b
    Quick Start:
        scs new project my-app              # Create a new project interactively
        cd my-app
        scs bundle validate                 # Validate the project bundle
        scs validate context/project/*.yaml # Validate SCDs
        scs bundle version --version 1.0.0  # Create versioned snapshot

    \b
    Common Workflow:
        1. Create or initialize project     → scs new project / scs init
        2. Add domains as needed            → scs add bundle [domain]
        3. Edit SCDs in context/project/    → (manual editing)
        4. Validate before versioning       → scs bundle validate / scs validate
           (also: scs validate --domain <manifest>, --checkpoint <record>)
        5. Create immutable version         → scs bundle version
        6. Compile for runtime delivery     → scs compile <bundle> -o <artifact>

    For detailed help on any command, use: scs [command] --help
    Documentation: https://github.com/SCS-Labs/scs-cli
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
