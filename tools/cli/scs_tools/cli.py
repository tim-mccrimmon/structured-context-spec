"""
SCS CLI - Command-line interface for Structured Context Specification tools
"""

import click
from scs_tools import __version__
from scs_tools.commands.new import new
from scs_tools.commands.init import init
from scs_tools.commands.add import add
from scs_tools.commands.bundle import bundle
from scs_tools.commands.validate import validate


@click.group()
@click.version_option(version=__version__, prog_name="scs")
def cli():
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
        scs validate                        # Validate all SCDs
        scs bundle version --version 1.0.0  # Create versioned snapshot

    \b
    Common Workflow:
        1. Create or initialize project     → scs new project / scs init
        2. Add domains as needed            → scs add bundle [domain]
        3. Edit SCDs in context/project/    → (manual editing)
        4. Validate before versioning       → scs validate / scs bundle validate
        5. Create immutable version         → scs bundle version

    For detailed help on any command, use: scs [command] --help
    Documentation: https://github.com/SCS-Labs/scs-cli
    """
    pass


# Register commands
cli.add_command(new)
cli.add_command(init)
cli.add_command(add)
cli.add_command(bundle)
cli.add_command(validate)


if __name__ == "__main__":
    cli()
