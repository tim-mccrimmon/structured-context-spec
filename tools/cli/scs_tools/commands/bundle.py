"""
Bundle command - manage SCS bundles
"""

from pathlib import Path
from typing import Optional, Tuple

import click
import yaml
from scs_validator.envelope import relative
from scs_validator.intake import normalize
from scs_validator.names import is_snapshot

from scs_tools import maintain
from scs_tools.machine import (
    EXIT_FILE,
    EXIT_USAGE,
    CommandError,
    Envelope,
    Output,
    machine_command,
)
from scs_tools.utils.files import get_template_path
from scs_tools.utils.project_types import ONTOLOGY_MODELS
from scs_tools.versioning import version_bundle
from scs_tools.workspace import find_workspace, repository_root, select_workspace


@click.group()
def bundle():
    """
    Manage SCS bundles

    A workspace's root bundle is its Domain bundle (bundles/domain-bundle.yaml) or its
    Project bundle (bundles/project-bundle.yaml); concept bundles group its SCDs.
    Use these commands to list, inspect, validate, and version your bundles.
    """
    pass


ROOT_BUNDLE_FILES = ("domain-bundle.yaml", "project-bundle.yaml")


def _root_bundle(base_path: Path) -> Path:
    """The workspace's root bundle: bundles/domain-bundle.yaml or bundles/project-bundle.yaml."""
    found = [base_path / "bundles" / name for name in ROOT_BUNDLE_FILES]
    found = [path for path in found if path.exists()]
    if len(found) != 1:
        problem = "both" if found else "neither"
        click.echo(
            f"Error: Found {problem} of bundles/domain-bundle.yaml and "
            "bundles/project-bundle.yaml; pass the bundle explicitly.",
            err=True,
        )
        raise click.Abort()
    return found[0]


def _base(workspace: Optional[str]) -> Tuple[Path, Optional[Path], Path]:
    """The directory list and info read from, the workspace it is in, and the path base."""
    if workspace:
        base = select_workspace(workspace)
        return base, base, repository_root(base) or base
    cwd = Path.cwd()
    found = find_workspace(cwd.resolve())
    return cwd, found, (repository_root(found) or found) if found else cwd


def _read(path: Path, shown: str) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        raise CommandError(
            "FILE_UNREADABLE", f"{shown} could not be read: {e}", exit_code=EXIT_FILE, path=shown
        )
    return normalize(data) if isinstance(data, dict) else {}


@bundle.command()
@click.option(
    "--available",
    "-a",
    is_flag=True,
    help="List all available bundle templates",
)
@click.option(
    "--workspace",
    default=None,
    help="Workspace: domain or a Project name (default: the current directory)",
)
@machine_command("bundle list")
def list(envelope: Envelope, out: Output, available: bool, workspace: Optional[str]) -> None:
    """
    List bundles in the current project or available templates

    \b
    Examples:
        scs bundle list           # List bundles in current project
        scs bundle list --available  # List all available templates
        scs bundle list --workspace domain --json
    """
    if available:
        envelope.result = {
            "available": {
                model: [*model_config["concepts"]]
                for model, model_config in ONTOLOGY_MODELS.items()
            }
        }
        for model, model_config in ONTOLOGY_MODELS.items():
            out.echo(f"Available concept bundles - ontology model '{model}':\n")
            for concept_name in model_config["concepts"]:
                out.echo(f"  • {concept_name}")
            if not model_config["concepts"]:
                out.echo("  (none shipped: concepts are defined with the user)")
            out.echo()

        out.echo("Domain bundles: create one with 'scs new domain <name> [--ontology ...]'.")
        return

    base_path, _, root = _base(workspace)
    bundles_dir = base_path / "bundles"

    if not bundles_dir.exists():
        raise CommandError(
            "WORKSPACE_NOT_FOUND",
            "No bundles directory found. Not an SCS project? Run 'scs new domain' to create "
            "one or 'scs bundle list --available' to see templates.",
        )

    found = []
    out.echo("Root bundle:\n")

    for bundle_file in ROOT_BUNDLE_FILES:
        bundle_path = bundles_dir / bundle_file
        if bundle_path.exists():
            shown = relative(bundle_path, root)
            data = _read(bundle_path, shown)
            entry = {
                "path": shown,
                "kind": "root",
                "id": data.get("id"),
                "type": data.get("type"),
                "version": data.get("version"),
            }
            found.append(entry)
            out.echo(f"  • {bundle_file}")
            out.echo(f"    ID: {data.get('id', 'unknown')}")
            out.echo(f"    Type: {data.get('type', 'unknown')}")
            out.echo(f"    Version: {data.get('version', 'unknown')}\n")

    # Check for concept bundles
    concepts_dir = bundles_dir / "concepts"
    if concepts_dir.exists():
        out.echo("Concept bundles:\n")
        for concept_file in sorted(concepts_dir.glob("*.yaml")):
            if is_snapshot(concept_file) or concept_file.name.endswith("-MANIFEST.yaml"):
                continue
            shown = relative(concept_file, root)
            data = _read(concept_file, shown)
            scds = data.get("scds") or []
            found.append(
                {
                    "path": shown,
                    "kind": "concept",
                    "id": data.get("id"),
                    "type": data.get("type"),
                    "version": data.get("version"),
                    "scds": len(scds),
                }
            )
            out.echo(f"  • {concept_file.name}")
            out.echo(f"    ID: {data.get('id', 'unknown')}")
            out.echo(f"    Version: {data.get('version', 'unknown')}")
            out.echo(f"    SCDs: {len(scds)}\n")

    envelope.result = {"bundles": found}


@bundle.command()
@click.argument("bundle_name")
@click.option(
    "--workspace",
    default=None,
    help="Workspace: domain or a Project name (default: the current directory)",
)
@machine_command("bundle info")
def info(envelope: Envelope, out: Output, bundle_name: str, workspace: Optional[str]) -> None:
    """
    Show detailed information about a bundle

    Displays bundle metadata including ID, version, domain, description,
    included SCDs, imports, and provenance information.

    \b
    Examples:
        scs bundle info architecture         # Show architecture bundle details
        scs bundle info security             # Show security bundle details
        scs bundle info security --json      # The whole bundle, in the envelope's result
    """
    base_path, _, root = _base(workspace)

    # Try to find bundle in project first
    bundle_locations = [
        base_path / "bundles" / f"{bundle_name}.yaml",
        base_path / "bundles" / "concepts" / f"{bundle_name}.yaml",
    ]

    bundle_path = None
    for loc in bundle_locations:
        if loc.exists():
            bundle_path = loc
            break

    source = "workspace"
    # If not found in project, check the concept bundle templates - prefer the current
    # workspace's own ontology model (if any), then fall back to searching every model.
    if not bundle_path:
        from scs_tools.commands.add import _read_ontology_model

        ontology = _read_ontology_model(base_path / ".scs" / "config")
        concept_models = [ontology] + [m for m in ONTOLOGY_MODELS if m != ontology]

        template_path = None
        for model in concept_models:
            candidate = get_template_path() / "bundles" / "concepts" / model / f"{bundle_name}.yaml"
            if candidate.exists():
                template_path = candidate
                break
        if template_path:
            bundle_path = template_path
            source = "template"
            out.echo("(Showing template bundle, not in current project)\n")
        else:
            raise CommandError(
                "BUNDLE_NOT_FOUND", f"Bundle '{bundle_name}' not found in project or templates."
            )

    # Load and display bundle info
    shown = bundle_name if source == "template" else relative(bundle_path, root)
    data = _read(bundle_path, shown)
    envelope.result = {"source": source, "bundle": data}
    if source == "workspace":
        envelope.result["path"] = shown

    out.echo(f"Bundle: {bundle_name}\n")
    out.echo(f"ID: {data.get('id', 'N/A')}")
    out.echo(f"Type: {data.get('type', 'N/A')}")
    out.echo(f"Version: {data.get('version', 'N/A')}")
    out.echo(f"Title: {data.get('title', 'N/A')}")
    out.echo(f"Description: {data.get('description', 'N/A')}")

    if "domain" in data:
        out.echo(f"Domain: {data['domain']}")

    if "concerns" in data:
        out.echo("\nConcerns (legacy 0.3 field - migrate to ontology.concepts):")
        for concern in data["concerns"]:
            out.echo(f"  • {concern}")

    if "ontology" in data:
        concepts = data["ontology"].get("concepts", [])
        out.echo(f"\nOntology concepts ({len(concepts)}):")
        for concept in concepts:
            out.echo(f"  • {concept.get('id', 'unknown')}")

    if "scds" in data:
        scds = data["scds"]
        out.echo(f"\nSCDs ({len(scds)}):")
        for scd in scds:
            out.echo(f"  • {scd}")

    if "imports" in data:
        imports = data["imports"]
        out.echo(f"\nImports ({len(imports)}):")
        for imp in imports:
            out.echo(f"  • {imp}")

    if "provenance" in data:
        prov = data["provenance"]
        out.echo("\nProvenance:")
        out.echo(f"  Created by: {prov.get('created_by', 'N/A')}")
        out.echo(f"  Created at: {prov.get('created_at', 'N/A')}")
        if "rationale" in prov:
            out.echo(f"  Rationale: {prov['rationale']}")


@bundle.command()
def validate():
    """
    Validate the workspace's root bundle and everything it imports

    This is a shortcut for: scs validate --bundle bundles/domain-bundle.yaml
    (or bundles/project-bundle.yaml in a Project workspace)

    \b
    Example:
        scs bundle validate
    """
    root_bundle = _root_bundle(Path.cwd())

    # Import and call the validate command
    from scs_tools.commands.validate import validate as validate_cmd

    ctx = click.get_current_context()
    ctx.invoke(validate_cmd, bundle=str(root_bundle))


@bundle.command()
@click.option(
    "--bundle",
    "-b",
    "bundle_file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Bundle file to version (default: the workspace's domain or project bundle)",
)
@click.option(
    "--version",
    "-v",
    "version_number",
    required=True,
    help="Version number (e.g., 1.0.0)",
)
@click.option(
    "--approved-by",
    help="The approver, Name <email> (required; never taken from git config)",
)
@click.option("--notes", help="Version notes")
@click.option(
    "--no-validate",
    is_flag=True,
    help="Skip content validation (integrity checks still run; recorded in the manifest)",
)
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing")
@machine_command("bundle version")
def version(
    envelope: Envelope,
    out: Output,
    bundle_file,
    version_number,
    approved_by,
    notes,
    no_validate,
    dry_run,
):
    """
    Release a bundle as a version: a snapshot, a manifest, a commit, and a tag

    The version is the git tag <workspace>/<bundle-name>-v<version> on a commit holding the
    whole workspace except dist/. The commit's author is the approver; its committer and the
    tag's tagger are scs-tools. Every import must be pinned to a released version that still
    matches its tag. A version is never overwritten; make a new one instead.

    \b
    Examples:
        scs bundle version --bundle bundles/concepts/security.yaml --version 1.0.0 \\
            --approved-by "Jane Doe <jane@acme.com>"
        scs bundle version --version 1.0.0 --approved-by "Jane Doe <jane@acme.com>" --dry-run
    """
    if bundle_file is None:
        found = [Path.cwd() / "bundles" / name for name in ROOT_BUNDLE_FILES]
        found = [path for path in found if path.exists()]
        if len(found) != 1:
            raise CommandError(
                "NO_INPUT",
                "Pass the bundle to version with --bundle (no single root bundle here)",
                exit_code=EXIT_USAGE,
            )
        bundle_file = found[0]
    version_bundle(
        envelope, out, bundle_file, version_number, approved_by, notes, no_validate, dry_run
    )


def _edit_options(default: str):
    def decorate(f):
        for option in reversed(
            [
                click.option(
                    "--bundle",
                    "-b",
                    "bundle_file",
                    type=click.Path(dir_okay=False, path_type=Path),
                    default=None,
                    help=f"The bundle to change (default: {default})",
                ),
                click.option(
                    "--workspace",
                    default=None,
                    help="Workspace: domain or a Project name (default: the current one)",
                ),
                click.option("--dry-run", is_flag=True, help="Report the change; write nothing"),
            ]
        ):
            f = option(f)
        return f

    return decorate


def _done(out: Output, envelope: Envelope, dry_run: bool) -> None:
    verb = "Would change" if dry_run else "Changed"
    if not envelope.changes:
        out.echo("Nothing to change")
    for change in envelope.changes:
        out.echo(f"{verb}: {change.action} {change.path}")


@bundle.command("pin")
@click.argument("name")
@click.option("--version", "-v", "version_number", required=True, help="A released version")
@_edit_options("the workspace's root bundle")
@machine_command("bundle pin")
def pin(envelope, out, name, version_number, bundle_file, workspace, dry_run):
    """
    Pin an import to a released version

    Changes the one import of bundle:NAME in the bundle to bundle:NAME:VERSION. The version
    must already be released (scs bundle version).

    \b
    Examples:
        scs bundle pin security --version 1.0.0
        scs bundle pin bundle:security --version 1.1.0 --bundle bundles/project-bundle.yaml
    """
    ws = maintain.open_workspace(workspace, bundle_file)
    maintain.pin(envelope, ws, bundle_file, name, version_number, dry_run)
    _done(out, envelope, dry_run)


@bundle.command("add-import")
@click.argument("ref")
@_edit_options("the workspace's root bundle")
@machine_command("bundle add-import")
def add_import(envelope, out, ref, bundle_file, workspace, dry_run):
    """
    Add an import to a Domain or Project bundle

    REF is bundle:NAME (unpinned, the working concept) or bundle:NAME:VERSION. It must resolve
    in the workspace.

    \b
    Examples:
        scs bundle add-import security
        scs bundle add-import bundle:security:1.0.0
    """
    ws = maintain.open_workspace(workspace, bundle_file)
    maintain.add_import(envelope, ws, bundle_file, ref, dry_run)
    _done(out, envelope, dry_run)


@bundle.command("add-scd")
@click.argument("scd_id")
@_edit_options("the workspace's root bundle")
@machine_command("bundle add-scd")
def add_scd(envelope, out, scd_id, bundle_file, workspace, dry_run):
    """
    List an existing SCD in a bundle

    \b
    Examples:
        scs bundle add-scd scd:project:release-gates --bundle bundles/concepts/security.yaml
    """
    ws = maintain.open_workspace(workspace, bundle_file)
    maintain.add_scd(envelope, ws, bundle_file, scd_id, dry_run)
    _done(out, envelope, dry_run)


@bundle.command("remove-scd")
@click.argument("scd_id")
@_edit_options("the bundle that lists it")
@machine_command("bundle remove-scd")
def remove_scd(envelope, out, scd_id, bundle_file, workspace, dry_run):
    """
    Retire an SCD: remove it from its bundle

    The SCD file is deleted when no other bundle lists it; released versions keep it at their
    tags. A concept bundle left with no SCDs is removed too, with the imports of it and its
    ontology manifest entry.

    \b
    Examples:
        scs bundle remove-scd scd:project:tefca-participation
        scs bundle remove-scd scd:project:threat-model --dry-run
    """
    ws = maintain.open_workspace(workspace, bundle_file)
    maintain.remove_scd(envelope, ws, bundle_file, scd_id, dry_run)
    _done(out, envelope, dry_run)
