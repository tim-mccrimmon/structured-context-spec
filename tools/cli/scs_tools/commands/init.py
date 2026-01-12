"""
Init command - initialize SCS in an existing project
"""

import os
from pathlib import Path
from datetime import datetime, timezone
import click
from scs_tools.utils.files import (
    create_directory_structure,
    get_template_path,
    copy_template,
    write_file,
)
from scs_tools.utils.project_types import PROJECT_TYPES


@click.command()
@click.option(
    "--type",
    "project_type",
    type=click.Choice(list(PROJECT_TYPES.keys())),
    default="standard",
    help="Type of project to initialize",
)
@click.option(
    "--author",
    default=None,
    help="Author name for provenance",
)
@click.option(
    "--email",
    default=None,
    help="Author email for provenance",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing SCS configuration",
)
def init(project_type, author, email, force):
    """
    Initialize SCS in an existing project

    Creates the necessary directory structure (.scs/, bundles/, context/)
    and basic configuration files in the current directory. Use this for
    adding SCS to an existing codebase. For new projects, use 'scs new project'.

    \b
    Examples:
        scs init                                # Initialize with defaults
        scs init --type healthcare              # Healthcare project type
        scs init --author "Jane Doe" --email "jane@example.com"  # With metadata
        scs init --force                        # Overwrite existing config

    See also: scs new project (for creating new projects from scratch)
    """
    base_path = Path.cwd()
    project_name = base_path.name

    # Check if already initialized
    scs_config = base_path / ".scs" / "config"
    if scs_config.exists() and not force:
        click.echo(
            f"Error: SCS already initialized in {base_path}\n"
            f"Use --force to reinitialize",
            err=True,
        )
        raise click.Abort()

    click.echo(f"Initializing SCS in: {base_path}")
    click.echo(f"Project name: {project_name}")
    click.echo(f"Project type: {project_type}\n")

    # Create directory structure
    click.echo("Creating directory structure...")
    create_directory_structure(base_path, project_name)

    # Template variables
    now = datetime.now(timezone.utc).isoformat()
    author_info = author or os.getenv("USER", "developer")
    email_info = email or f"{author_info}@example.com"

    variables = {
        "project_name": project_name,
        "project_type": project_type,
        "author": author_info,
        "email": email_info,
        "created_at": now,
    }

    # Create .scs/config
    click.echo("Creating SCS configuration...")
    scs_config_content = f"""# SCS Project Configuration
project_name: {project_name}
project_type: {project_type}
scs_version: 0.1.0
author: {author_info}
email: {email_info}
"""
    write_file(base_path / ".scs" / "config", scs_config_content)

    # Create VERSION if it doesn't exist
    version_file = base_path / "VERSION"
    if not version_file.exists():
        write_file(version_file, "1.0.0\n")

    # Create .gitignore if it doesn't exist
    gitignore_file = base_path / ".gitignore"
    if not gitignore_file.exists():
        template_path = get_template_path()
        gitignore_template = template_path / "project.gitignore"
        if gitignore_template.exists():
            copy_template(gitignore_template, gitignore_file, variables)

    click.echo(f"\n✓ SCS initialized successfully!")
    click.echo(f"\nNext steps:")
    click.echo(f"  scs new project {project_name}  # Generate full project structure")
    click.echo(f"  scs add scd <name>              # Add individual SCDs")
    click.echo(f"  scs bundle list                 # List available bundles")
