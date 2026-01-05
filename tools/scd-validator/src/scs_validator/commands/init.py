"""Init command for SCS CLI."""

import sys
from pathlib import Path

import click

from .. import __version__
from ..project_init import ProjectInitializer
from ..utils import ValidationError


@click.command()
@click.argument("project_name")
@click.option(
    "--destination",
    "-d",
    type=click.Path(),
    help="Parent directory for the project (default: current directory)",
)
@click.option(
    "--template-source",
    "-t",
    type=click.Path(exists=True),
    help="Custom template source directory (default: bundled templates)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
def init(
    project_name: str,
    destination: str | None,
    template_source: str | None,
    verbose: bool,
) -> None:
    """Initialize a new SCS project.

    Creates a new project directory with the following structure:

    \b
    <project-name>/
    ├── context/
    │   ├── meta/              # Domain metadata
    │   ├── domains/           # Domain bundles
    │   ├── scds/              # SCD files
    │   └── project-bundle.yaml
    ├── docs/
    │   └── domain-docs/       # Domain templates (11 domains)
    └── .scs/
        └── config.yaml        # Project configuration

    Examples:

    \b
    # Create a new project in the current directory
    scs init my-project

    \b
    # Create a project in a specific location
    scs init my-project --destination /path/to/parent

    \b
    # Use custom templates
    scs init my-project --template-source /path/to/templates
    """
    try:
        if verbose:
            click.echo(f"Initializing SCS project: {project_name}")
            click.echo(f"SCS version: {__version__}")

        # Convert paths
        dest_path = Path(destination) if destination else None
        template_path = Path(template_source) if template_source else None

        # Initialize project
        initializer = ProjectInitializer(scs_version=__version__)
        project_path = initializer.create_project(
            project_name=project_name,
            destination=dest_path,
            template_source=template_path,
        )

        if verbose:
            click.echo(f"\nProject structure created:")
            click.echo(f"  - context/meta/domain-meta.yaml")
            click.echo(f"  - context/project-bundle.yaml")
            click.echo(f"  - docs/domain-docs/ (11 domains)")
            click.echo(f"  - .scs/config.yaml")

        click.echo(f"\n✓ Successfully created project: {project_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. cd {project_name}")
        click.echo(f"  2. Review docs/domain-docs/business-context/README.md")
        click.echo(f"  3. Complete the business-context template first")
        click.echo(f"  4. Use 'scs generate' to create SCDs from templates (coming soon)")

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
