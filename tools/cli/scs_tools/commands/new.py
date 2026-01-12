"""
New project command - scaffolds a new SCS project
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
from scs_tools.utils.project_types import (
    get_bundles_for_project_type,
    get_domains_for_project_type,
    get_concerns_for_project_type,
    get_project_type_config,
    PROJECT_TYPES,
)


@click.group()
def new():
    """
    Create new SCS artifacts

    Currently supports creating complete SCS projects with directory structure,
    bundles, SCDs, and documentation templates.
    """
    pass


@new.command()
@click.argument("name", required=False)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(list(PROJECT_TYPES.keys())),
    default=None,
    help="Type of project to scaffold",
)
@click.option(
    "--dir",
    "directory",
    type=click.Path(),
    default=None,
    help="Directory to create project in (default: current directory)",
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
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode with prompts",
)
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Disable interactive mode (use defaults/flags only)",
)
def project(name, project_type, directory, author, email, interactive, no_interactive):
    """
    Create a new SCS project with proper structure and templates

    By default, prompts for missing required information interactively.
    Use --no-interactive to disable prompts and require all flags.

    Project types: healthcare, fintech, saas, government, minimal, standard

    \b
    Examples:
        scs new project                           # Interactive mode (default)
        scs new project medication-adherence      # Interactive for missing fields
        scs new project my-app --type healthcare  # Specify type
        scs new project my-app --type healthcare --author "Jane Doe" --email "jane@example.com" --no-interactive

    See also: scs init (for adding SCS to existing projects)
    """

    # Determine if we should be interactive
    # Interactive by default unless --no-interactive is specified
    should_prompt = not no_interactive or interactive

    # Interactive mode - prompt for missing values
    if should_prompt:
        # Show welcome message
        if not name and not project_type:
            click.echo("=== SCS Project Setup ===\n")
            click.echo("Let's create your SCS project!\n")

        # Prompt for project name if not provided
        if not name:
            name = click.prompt("Project name", type=str)

        # Show project types if not specified
        if not project_type:
            click.echo("\nAvailable project types:")
            for idx, (ptype, config) in enumerate(PROJECT_TYPES.items(), 1):
                click.echo(f"  {idx}. {ptype:15} - {config['description']}")

            click.echo()
            project_type = click.prompt(
                "Project type",
                type=click.Choice(list(PROJECT_TYPES.keys())),
                default="standard",
                show_choices=False,
            )

        # Prompt for author if not provided
        if not author:
            default_author = os.getenv("USER", "")
            author = click.prompt(
                "Author name",
                default=default_author,
                show_default=True,
            )

        # Prompt for email if not provided
        if not email:
            default_email = f"{author}@example.com" if author else ""
            email = click.prompt(
                "Author email",
                default=default_email,
                show_default=True,
            )

        # Prompt for directory if not provided
        if not directory:
            use_cwd = click.confirm(
                f"\nCreate project in current directory ({Path.cwd()})?",
                default=True,
            )
            if not use_cwd:
                directory = click.prompt(
                    "Project directory",
                    type=click.Path(),
                    default=str(Path.cwd()),
                )

        click.echo()  # Empty line before creation starts
    else:
        # Non-interactive mode - require all parameters
        if not name:
            click.echo("Error: Project name is required in non-interactive mode", err=True)
            raise click.Abort()

        # Set defaults for optional parameters
        if not project_type:
            project_type = "standard"
        if not author:
            author = os.getenv("USER", "developer")
        if not email:
            email = f"{author}@example.com"

    # Determine project directory
    if directory:
        base_path = Path(directory) / name
    else:
        base_path = Path.cwd() / name

    # Check if directory already exists
    if base_path.exists():
        click.echo(f"Error: Directory '{base_path}' already exists", err=True)
        raise click.Abort()

    click.echo(f"Creating SCS project: {name}")
    click.echo(f"Project type: {project_type}")
    click.echo(f"Location: {base_path}\n")

    # Get project configuration
    config = get_project_type_config(project_type)
    domains = get_domains_for_project_type(project_type)
    concerns = get_concerns_for_project_type(project_type)
    bundles = domains  # For backwards compatibility in templates

    # Create directory structure
    click.echo("Creating directory structure...")
    create_directory_structure(base_path, name)

    # Template variables
    now = datetime.now(timezone.utc).isoformat()
    author_info = author or os.getenv("USER", "developer")
    email_info = email or f"{author_info}@example.com"

    variables = {
        "project_name": name,
        "project_type": project_type,
        "author": author_info,
        "email": email_info,
        "created_at": now,
        "bundles": bundles,
        "config": config,
    }

    # Create bundle files
    click.echo("Creating bundle files...")
    _create_bundles(base_path, domains, concerns, variables)

    # Create SCD files
    click.echo("Creating SCD files...")
    _create_scds(base_path, concerns, variables, config)

    # Create concern documentation templates
    click.echo("Creating concern documentation templates...")
    _create_concern_docs(base_path, concerns, variables)

    # Create supporting files
    click.echo("Creating supporting files...")
    _create_supporting_files(base_path, variables)

    click.echo(f"\n✓ Project '{name}' created successfully!")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {name}")
    click.echo(f"  # Edit SCDs in context/project/")
    click.echo(f"  # Edit bundles in bundles/")
    click.echo(f"  # Review docs/GETTING_STARTED.md")


def _create_bundles(base_path: Path, domains: list, concerns: list, variables: dict):
    """Create bundle YAML files for SCS 0.3 architecture"""
    template_path = get_template_path() / "bundles"

    # Create project bundle
    project_bundle_template = template_path / "project-bundle.yaml"
    if project_bundle_template.exists():
        copy_template(
            project_bundle_template,
            base_path / "bundles" / "project-bundle.yaml",
            variables,
        )

    # Create meta bundle
    meta_bundle_template = template_path / "meta-bundle.yaml"
    if meta_bundle_template.exists():
        copy_template(
            meta_bundle_template,
            base_path / "bundles" / "meta-bundle.yaml",
            variables,
        )

    # Create standards bundle
    standards_bundle_template = template_path / "standards-bundle.yaml"
    if standards_bundle_template.exists():
        copy_template(
            standards_bundle_template,
            base_path / "bundles" / "standards-bundle.yaml",
            variables,
        )

    # Create domain bundles (e.g., software-development)
    for domain in domains:
        domain_template = template_path / "domains" / f"{domain}.yaml"
        if domain_template.exists():
            copy_template(
                domain_template,
                base_path / "bundles" / "domains" / f"{domain}.yaml",
                variables,
            )
        else:
            click.echo(f"Warning: Template for domain '{domain}' not found, skipping...")

    # Create concern bundles (the 11 functional areas)
    for concern in concerns:
        concern_template = template_path / "concerns" / f"{concern}.yaml"
        if concern_template.exists():
            copy_template(
                concern_template,
                base_path / "bundles" / "concerns" / f"{concern}.yaml",
                variables,
            )
        else:
            click.echo(f"Warning: Template for concern '{concern}' not found, skipping...")


def _create_scds(base_path: Path, bundles: list, variables: dict, config: dict):
    """Create SCD YAML files"""
    template_path = get_template_path() / "scds"

    # SCD mapping by domain
    scd_mapping = {
        "business-context": [
            "problem-definition",
            "stakeholders",
            "business-objectives",
            "opportunity-analysis",
            "constraints-and-assumptions",
            "success-criteria",
        ],
        "architecture": [
            "system-context",
            "tech-stack",
            "integration-map",
            "component-model",
        ],
        "security": [
            "authn-authz",
            "data-protection",
            "data-handling",
            "threat-model",
        ],
        "performance-reliability": [
            "response-time",
            "availability",
            "fault-tolerance",
            "scalability",
        ],
        "usability-accessibility": [
            "ux-principles",
            "accessibility-compliance",
            "error-handling-ux",
        ],
        "compliance-governance": [
            "soc2-controls",
            "hipaa-compliance",
            "chai-adherence",
            "tefca-participation",
        ],
        "data-provenance": [
            "data-model",
            "provenance-tracking",
            "retention-policy",
        ],
        "testing-validation": [
            "test-coverage",
            "validation-plan",
            "qa-procedures",
        ],
        "deployment-operations": [
            "infrastructure-definition",
            "observability",
            "incident-response",
        ],
        "safety-risk": [
            "risk-assessment",
            "safety-checklist",
        ],
        "ethics-ai-accountability": [
            "ai-usage-policy",
            "audit-trail",
            "model-bias",
        ],
    }

    # Get excluded SCDs from config
    exclude_scds = config.get("exclude_scds", [])

    for bundle in bundles:
        scds = scd_mapping.get(bundle, [])
        for scd_name in scds:
            # Skip excluded SCDs
            if scd_name in exclude_scds:
                continue

            scd_template = template_path / f"{scd_name}.yaml"
            if scd_template.exists():
                copy_template(
                    scd_template,
                    base_path / "context" / "project" / f"{scd_name}.yaml",
                    variables,
                )


def _create_concern_docs(base_path: Path, concerns: list, variables: dict):
    """Create concern documentation markdown templates for users to fill in"""
    import shutil

    template_path = get_template_path() / "docs"

    for concern in concerns:
        concern_template_dir = template_path / concern
        if concern_template_dir.exists():
            # Find the template markdown file in this concern directory
            template_files = list(concern_template_dir.glob("*-template.md"))
            if template_files:
                template_file = template_files[0]
                # Destination: docs/{concern}/{concern}-brief.md
                dest_file = template_file.name.replace("-template", "")
                dest_path = base_path / "docs" / concern / dest_file

                # Create parent directory if it doesn't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file directly without Jinja2 rendering (these are user templates)
                shutil.copy2(template_file, dest_path)
        else:
            click.echo(f"Warning: Concern docs template for {concern} not found, skipping...")


def _create_supporting_files(base_path: Path, variables: dict):
    """Create README, .gitignore, VERSION, and other supporting files"""
    template_path = get_template_path()

    # Create README.md
    readme_template = template_path / "project-README.md"
    if readme_template.exists():
        copy_template(
            readme_template,
            base_path / "README.md",
            variables,
        )

    # Create .gitignore
    gitignore_template = template_path / "project.gitignore"
    if gitignore_template.exists():
        copy_template(
            gitignore_template,
            base_path / ".gitignore",
            variables,
        )

    # Create VERSION
    write_file(base_path / "VERSION", "1.0.0\n")

    # Create GETTING_STARTED.md
    getting_started_template = template_path / "GETTING_STARTED.md"
    if getting_started_template.exists():
        copy_template(
            getting_started_template,
            base_path / "docs" / "GETTING_STARTED.md",
            variables,
        )

    # Create .scs/config
    scs_config = f"""# SCS Project Configuration
project_name: {variables['project_name']}
project_type: {variables['project_type']}
scs_version: 0.1.0
"""
    write_file(base_path / ".scs" / "config", scs_config)
