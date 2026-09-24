"""
Add command - add SCDs or bundles to an existing SCS project
"""

import os
from pathlib import Path
from datetime import datetime, timezone
import click
from scs_tools.utils.files import (
    get_template_path,
    copy_template,
)


@click.group()
def add():
    """
    Add SCDs or bundles to an existing SCS project

    SCDs (Structured Context Documents) capture specific aspects of your project.
    Bundles group related SCDs by domain (architecture, security, compliance, etc.).

    Use 'scs bundle list --available' to see all available templates.
    """
    pass


@add.command()
@click.argument("scd_name")
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
def scd(scd_name, author, email):
    """
    Add an individual SCD to the project

    SCDs are YAML files that document specific aspects like system-context,
    tech-stack, security policies, compliance requirements, etc.

    \b
    Examples:
        scs add scd system-context        # Add system context SCD
        scs add scd tech-stack            # Add technology stack SCD
        scs add scd hipaa-compliance      # Add HIPAA compliance SCD
        scs add scd authn-authz --author "Jane Doe"  # With provenance

    See also: scs bundle list --available
    """
    base_path = Path.cwd()

    # Check if SCS is initialized
    if not (base_path / ".scs" / "config").exists():
        click.echo(
            "Error: Not an SCS project. Run 'scs init' first.",
            err=True,
        )
        raise click.Abort()

    # Check if context/project directory exists
    context_dir = base_path / "context" / "project"
    if not context_dir.exists():
        click.echo("Creating context/project directory...")
        context_dir.mkdir(parents=True, exist_ok=True)

    # Check if SCD already exists
    scd_file = context_dir / f"{scd_name}.yaml"
    if scd_file.exists():
        if not click.confirm(f"SCD '{scd_name}' already exists. Overwrite?"):
            click.echo("Aborted.")
            raise click.Abort()

    # Template variables
    now = datetime.now(timezone.utc).isoformat()
    author_info = author or os.getenv("USER", "developer")
    email_info = email or f"{author_info}@example.com"

    # Read project name from config
    config_file = base_path / ".scs" / "config"
    project_name = base_path.name
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if line.startswith("project_name:"):
                    project_name = line.split(":", 1)[1].strip()
                    break

    variables = {
        "project_name": project_name,
        "author": author_info,
        "email": email_info,
        "created_at": now,
    }

    # Find and copy template
    template_path = get_template_path() / "scds" / f"{scd_name}.yaml"
    if not template_path.exists():
        click.echo(
            f"Error: Template for '{scd_name}' not found.\n"
            f"Available templates are in: {get_template_path() / 'scds'}",
            err=True,
        )
        raise click.Abort()

    click.echo(f"Adding SCD: {scd_name}")
    copy_template(template_path, scd_file, variables)

    click.echo(f"✓ SCD '{scd_name}' added successfully!")
    click.echo(f"  Location: {scd_file.relative_to(base_path)}")


@add.command()
@click.argument("bundle_name")
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
def bundle(bundle_name, author, email):
    """
    Add a concept or domain bundle to the project

    Concept bundles group the SCDs for one concept (architecture, security,
    compliance-governance, data-provenance, testing-validation,
    deployment-operations, and more) and are written to bundles/concepts/.
    Domain bundles (software-development) import concept bundles and are
    written to bundles/domains/.

    \b
    Examples:
        scs add bundle architecture          # Add the architecture concept bundle
        scs add bundle security              # Add the security concept bundle
        scs add bundle software-development  # Add the software-development domain bundle
        scs add bundle data-provenance --author "Jane Doe"  # With provenance

    See also: scs bundle list --available
    """
    base_path = Path.cwd()

    # Check if SCS is initialized
    if not (base_path / ".scs" / "config").exists():
        click.echo(
            "Error: Not an SCS project. Run 'scs init' first.",
            err=True,
        )
        raise click.Abort()

    # Find the template: a concept bundle or a domain bundle
    templates_root = get_template_path() / "bundles"
    kind = next(
        (k for k in ("concepts", "domains") if (templates_root / k / f"{bundle_name}.yaml").exists()),
        None,
    )
    if kind is None:
        available = sorted(
            p.stem for k in ("concepts", "domains") for p in (templates_root / k).glob("*.yaml")
        )
        click.echo(
            f"Error: Bundle '{bundle_name}' not found.\n"
            f"Available bundles: {', '.join(available)}",
            err=True,
        )
        raise click.Abort()
    template_path = templates_root / kind / f"{bundle_name}.yaml"

    # Check if the destination directory exists
    bundles_dir = base_path / "bundles" / kind
    if not bundles_dir.exists():
        click.echo(f"Creating bundles/{kind} directory...")
        bundles_dir.mkdir(parents=True, exist_ok=True)

    # Check if bundle already exists
    bundle_file = bundles_dir / f"{bundle_name}.yaml"
    if bundle_file.exists():
        if not click.confirm(f"Bundle '{bundle_name}' already exists. Overwrite?"):
            click.echo("Aborted.")
            raise click.Abort()

    # Template variables
    now = datetime.now(timezone.utc).isoformat()
    author_info = author or os.getenv("USER", "developer")
    email_info = email or f"{author_info}@example.com"

    # Read project name from config
    config_file = base_path / ".scs" / "config"
    project_name = base_path.name
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                if line.startswith("project_name:"):
                    project_name = line.split(":", 1)[1].strip()
                    break

    variables = {
        "project_name": project_name,
        "author": author_info,
        "email": email_info,
        "created_at": now,
        "bundles": [],  # Not used in domain bundles
        # A domain bundle imports the concept bundles this project has; a project with none yet
        # gets the full reference set
        "concepts": _project_concepts(base_path),
    }

    click.echo(f"Adding bundle: {bundle_name}")
    copy_template(template_path, bundle_file, variables)

    click.echo(f"✓ Bundle '{bundle_name}' added successfully!")
    click.echo(f"  Location: {bundle_file.relative_to(base_path)}")


def _project_concepts(base_path: Path) -> list:
    """Concept bundles present in the project, in reference order (all of them if none exist yet)"""
    from scs_tools.utils.project_types import SOFTWARE_DEVELOPMENT_CONCEPTS

    concepts_dir = base_path / "bundles" / "concepts"
    present = {p.stem for p in concepts_dir.glob("*.yaml")} if concepts_dir.is_dir() else set()
    ordered = [c for c in SOFTWARE_DEVELOPMENT_CONCEPTS if c in present]
    return ordered or list(SOFTWARE_DEVELOPMENT_CONCEPTS)
