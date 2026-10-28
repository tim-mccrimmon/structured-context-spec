"""
Add command - add SCDs or bundles to an existing SCS project
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import yaml
from scs_validator.envelope import Change, relative
from scs_validator.names import RESERVED_BUNDLE_NAMES, bundle_name
from scs_validator.workspace import load_workspace

from scs_tools import identity, maintain
from scs_tools.machine import EXIT_USAGE, CommandError, Envelope, Output, machine_command
from scs_tools.utils.files import get_template_path, render_template, write_file
from scs_tools.utils.project_types import get_project_type_config
from scs_tools.workspace import repository_root, select_workspace


@click.group()
def add():
    """
    Add SCDs or bundles to an existing SCS project

    SCDs (Structured Context Documents) capture specific aspects of your project.
    Bundles group related SCDs by domain (architecture, security, compliance, etc.).

    Use 'scs bundle list --available' to see all available templates.
    """
    pass


def _common_options(f):
    for option in reversed(
        [
            click.option("--author", default=None, help="Author name for provenance"),
            click.option("--email", default=None, help="Author email for provenance"),
            click.option("--force", is_flag=True, help="Overwrite the file if it exists"),
            click.option("--dry-run", is_flag=True, help="Report what would be written"),
            click.option(
                "--workspace",
                default=None,
                help="Workspace to add to: domain or a Project name (default: the current one)",
            ),
        ]
    ):
        f = option(f)
    return f


def _variables(base_path: Path, author, email, out: Output) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    # Never invented (D-13, D-71)
    author_info, email_info = identity.author(author, email, prompt=not out.machine)
    project_name = _bundle_owner_name(base_path)
    return {
        "project_name": project_name,
        "author": author_info,
        "email": email_info,
        # Provenance identifies a person as `Name <email>` (D-28, D-63)
        "created_by": f"{author_info} <{email_info}>",
        "created_at": now,
    }


def _write(
    envelope: Envelope,
    out: Output,
    template_path: Path,
    dest: Path,
    variables: dict,
    force: bool,
    dry_run: bool,
) -> None:
    """Render a template to `dest`, recording the change. Overwriting needs --force."""
    root = repository_root(dest.parent)
    shown = relative(dest, root) if root else str(dest)
    if dest.exists() and not force:
        raise CommandError("FILE_EXISTS", f"{shown} already exists; use --force to overwrite")
    content = render_template(template_path.read_text(encoding="utf-8"), variables)
    envelope.changes.append(Change("modify" if dest.exists() else "create", path=shown))
    envelope.result = {"path": shown}
    if not dry_run:
        write_file(dest, content)


@add.command()
@click.argument("scd_name")
@_common_options
@machine_command("add scd")
def scd(envelope, out, scd_name, author, email, force, dry_run, workspace):
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
    base_path = select_workspace(workspace)
    config_file = base_path / ".scs" / "config"

    # Find the template in the workspace's own ontology model
    ontology = _read_ontology_model(config_file)
    template_path = get_template_path() / "scds" / ontology / f"{scd_name}.yaml"
    if not template_path.exists():
        template_path = get_template_path() / "scds" / "common" / f"{scd_name}.yaml"
    if not template_path.exists():
        raise CommandError(
            "TEMPLATE_NOT_FOUND",
            f"Template for '{scd_name}' not found in the '{ontology}' ontology model. "
            f"Available templates are in: {get_template_path() / 'scds' / ontology}",
        )

    scd_file = base_path / "context" / "project" / f"{scd_name}.yaml"
    _write(
        envelope,
        out,
        template_path,
        scd_file,
        _variables(base_path, author, email, out),
        force,
        dry_run,
    )
    if not dry_run:
        out.echo(f"✓ SCD '{scd_name}' added successfully!")
        out.echo(f"  Location: {scd_file.relative_to(base_path)}")


@add.command()
@click.argument("bundle_name")
@_common_options
@click.option(
    "--new",
    "new_concept",
    is_flag=True,
    help="Create a concept with no shipped template: its bundle, a first SCD, its ontology "
    "entry, and the root bundle's import of it",
)
@click.option("--title", default=None, help="With --new: the concept's title")
@click.option("--description", default=None, help="With --new: the concept's description")
@machine_command("add bundle")
def bundle(
    envelope,
    out,
    bundle_name,
    author,
    email,
    force,
    dry_run,
    workspace,
    new_concept,
    title,
    description,
):
    """
    Add a concept bundle to the workspace

    Concept bundles group the SCDs for one concept (architecture, security,
    compliance-governance, data-provenance, testing-validation,
    deployment-operations, and more) and are written to bundles/concepts/.
    Add the new concept to your Domain or Project bundle's imports.

    A Domain bundle is a workspace of its own: create one with 'scs new domain'.

    \b
    Examples:
        scs add bundle architecture          # Add the architecture concept bundle
        scs add bundle security              # Add the security concept bundle
        scs add bundle data-provenance --author "Jane Doe"  # With provenance

    With --new, the concept need not have a template: the run creates
    bundles/concepts/NAME.yaml listing a first, empty SCD context/project/NAME.yaml, adds
    concept:NAME to the ontology manifest, and adds bundle:NAME to the root bundle's imports.

    \b
        scs add bundle groceries --new --title "Groceries" --author "Jane Doe" --email jane@acme.org

    See also: scs bundle list --available
    """
    from scs_tools.utils.project_types import ONTOLOGY_MODELS

    if new_concept:
        if force:
            raise CommandError(
                "USAGE_ERROR", "--new never overwrites; drop --force", exit_code=EXIT_USAGE
            )
        ws = maintain.open_workspace(workspace, None)
        variables = _variables(ws.path, author, email, out)
        maintain.new_concept(
            envelope, ws, bundle_name, title, description, variables["created_by"], dry_run
        )
        verb = "Would create" if dry_run else "Created"
        out.echo(f"{verb} concept {bundle_name}:")
        for change in envelope.changes:
            out.echo(f"  {change.action} {change.path}")
        return

    if bundle_name in RESERVED_BUNDLE_NAMES:
        raise CommandError(
            "RESERVED_BUNDLE_NAME",
            f"'{bundle_name}' is reserved for a later release; choose another bundle name",
        )

    base_path = select_workspace(workspace)
    config_file = base_path / ".scs" / "config"
    ontology = _read_ontology_model(config_file)
    concepts_root = get_template_path() / "bundles" / "concepts" / ontology
    template_path = concepts_root / f"{bundle_name}.yaml"
    if not template_path.exists():
        template_path = concepts_root.parent / "common" / f"{bundle_name}.yaml"

    if bundle_name in {m["domain"] for m in ONTOLOGY_MODELS.values()}:
        raise CommandError(
            "CONCEPT_IS_A_DOMAIN",
            f"'{bundle_name}' is a domain, not a concept bundle. A Domain bundle is its own "
            "workspace: create one with 'scs new domain <name>'.",
        )
    if not template_path.exists():
        available = sorted(concepts_root.glob("*.yaml"))
        raise CommandError(
            "TEMPLATE_NOT_FOUND",
            f"Bundle '{bundle_name}' not found in the '{ontology}' ontology model. "
            f"Available bundles: {', '.join(p.stem for p in available)}",
        )

    variables = _variables(base_path, author, email, out)
    # Which SCDs a concept bundle lists: the full set (D-64), except in a 0.6 workspace made
    # with `scs init --type`, whose project type still applies
    project_type = _read_project_type(config_file) if ontology == "sdlc" else None
    variables["config"] = (
        get_project_type_config(project_type) if project_type else {"exclude_scds": []}
    )
    bundle_file = base_path / "bundles" / "concepts" / f"{bundle_name}.yaml"
    _write(envelope, out, template_path, bundle_file, variables, force, dry_run)
    if not dry_run:
        out.echo(f"✓ Bundle '{bundle_name}' added successfully!")
        out.echo(f"  Location: {bundle_file.relative_to(base_path)}")

    # A concept added to the workspace also belongs in the Domain Ontology manifest
    _remind_about_ontology(base_path, bundle_name, out)


def _bundle_owner_name(base_path: Path) -> str:
    """The name templates call `project_name`: the root bundle's name (`bundle:<name>`), else
    the 0.6 `project_name` config key, else the workspace directory's name. In a 0.7 Domain
    workspace the config `name` is `domain` (D-03), not the organization's name."""
    for path in sorted((base_path / "bundles").glob("*-bundle.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and str(data.get("id", "")).startswith("bundle:"):
            return bundle_name(data["id"])
    config_file = base_path / ".scs" / "config"
    if config_file.exists():
        for line in config_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("project_name:"):
                return line.split(":", 1)[1].strip()
    return base_path.name


def _remind_about_ontology(base_path: Path, concept: str, out: Output):
    """If the project has a Domain Ontology manifest that lacks this concept, say how to add it"""
    found = load_workspace(base_path.name, base_path).ontology_manifest()
    if found is None:
        return
    manifest = found
    concept_id = f"concept:{concept}"
    if f"id: {concept_id}" in manifest.read_text(encoding="utf-8"):
        return
    out.echo(
        f"\nNote: {concept_id} is not in {manifest.relative_to(base_path).as_posix()} yet. "
        "Add it under\n"
        f"ontology.concepts so the ontology matches your concept bundles:\n"
        f"  - id: {concept_id}\n"
        f'    name: "..."'
    )


def _read_project_type(config_file: Path) -> Optional[str]:
    """Project type recorded in .scs/config by the removed `scs init --type` (0.6), or None.
    0.7 workspaces have none: their templates depend on the ontology only (D-64)."""
    from scs_tools.utils.project_types import PROJECT_TYPES

    if config_file.exists():
        for line in config_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("project_type:"):
                value = line.split(":", 1)[1].strip()
                if value in PROJECT_TYPES:
                    return value
    return None


def _read_ontology_model(config_file: Path) -> str:
    """Ontology model recorded in .scs/config (`ontology`, or the 0.6 key `ontology_model`), or
    'sdlc' if missing or unknown. Projects scaffolded before the --ontology selector existed
    have neither line - 'sdlc' is also the correct default for those."""
    from scs_tools.utils.project_types import ONTOLOGY_MODELS

    if config_file.exists():
        for line in config_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(("ontology:", "ontology_model:")):
                value = line.split(":", 1)[1].strip()
                if value in ONTOLOGY_MODELS:
                    return value
    return "sdlc"
