"""
Bundle command - manage SCS bundles
"""

import hashlib
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path

import click
import yaml

from scs_tools.utils.files import get_template_path
from scs_tools.utils.project_types import ONTOLOGY_MODELS, PROJECT_TYPES


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


@bundle.command()
@click.option(
    "--available",
    "-a",
    is_flag=True,
    help="List all available bundle templates",
)
def list(available):
    """
    List bundles in the current project or available templates

    \b
    Examples:
        scs bundle list           # List bundles in current project
        scs bundle list --available  # List all available templates
    """
    if available:
        for model, model_config in ONTOLOGY_MODELS.items():
            click.echo(f"Available concept bundles - ontology model '{model}':\n")
            for concept_name in model_config["concepts"]:
                click.echo(f"  • {concept_name}")
            click.echo()

        click.echo("Domain bundles: create one with 'scs new domain <name> [--ontology ...]'.\n")

        click.echo("Project types and their bundles (sdlc ontology only):\n")
        for ptype, config in PROJECT_TYPES.items():
            click.echo(f"  {ptype}:")
            click.echo(f"    Description: {config['description']}")
            if config.get("minimal"):
                click.echo("    Concept bundles: 3 (architecture, security, deployment-operations)")
            else:
                click.echo("    Concept bundles: all 11")
        return

    # List bundles in current project
    base_path = Path.cwd()
    bundles_dir = base_path / "bundles"

    if not bundles_dir.exists():
        click.echo(
            "Error: No bundles directory found. Not an SCS project?\n"
            "Run 'scs init' to initialize or 'scs bundle list --available' to see templates.",
            err=True,
        )
        raise click.Abort()

    click.echo("Root bundle:\n")

    for bundle_file in ROOT_BUNDLE_FILES:
        bundle_path = bundles_dir / bundle_file
        if bundle_path.exists():
            with open(bundle_path, "r") as f:
                data = yaml.safe_load(f)
                bundle_id = data.get("id", "unknown")
                bundle_type = data.get("type", "unknown")
                version = data.get("version", "unknown")
                click.echo(f"  • {bundle_file}")
                click.echo(f"    ID: {bundle_id}")
                click.echo(f"    Type: {bundle_type}")
                click.echo(f"    Version: {version}\n")

    # Check for concept bundles
    concepts_dir = bundles_dir / "concepts"
    if concepts_dir.exists():
        click.echo("Concept bundles:\n")
        for bundle_file in sorted(concepts_dir.glob("*.yaml")):
            with open(bundle_file, "r") as f:
                data = yaml.safe_load(f) or {}
            click.echo(f"  • {bundle_file.name}")
            click.echo(f"    ID: {data.get('id', 'unknown')}")
            click.echo(f"    Version: {data.get('version', 'unknown')}")
            click.echo(f"    SCDs: {len(data.get('scds') or [])}\n")


@bundle.command()
@click.argument("bundle_name")
def info(bundle_name):
    """
    Show detailed information about a bundle

    Displays bundle metadata including ID, version, domain, description,
    included SCDs, imports, and provenance information.

    \b
    Examples:
        scs bundle info architecture         # Show architecture bundle details
        scs bundle info security             # Show security bundle details
        scs bundle info compliance-governance # Show compliance details
    """
    base_path = Path.cwd()

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
            click.echo("(Showing template bundle, not in current project)\n")
        else:
            click.echo(
                f"Error: Bundle '{bundle_name}' not found in project or templates.",
                err=True,
            )
            raise click.Abort()

    # Load and display bundle info
    with open(bundle_path, "r") as f:
        data = yaml.safe_load(f)

    click.echo(f"Bundle: {bundle_name}\n")
    click.echo(f"ID: {data.get('id', 'N/A')}")
    click.echo(f"Type: {data.get('type', 'N/A')}")
    click.echo(f"Version: {data.get('version', 'N/A')}")
    click.echo(f"Title: {data.get('title', 'N/A')}")
    click.echo(f"Description: {data.get('description', 'N/A')}")

    if "domain" in data:
        click.echo(f"Domain: {data['domain']}")

    if "concerns" in data:
        click.echo("\nConcerns (legacy 0.3 field - migrate to ontology.concepts):")
        for concern in data["concerns"]:
            click.echo(f"  • {concern}")

    if "ontology" in data:
        concepts = data["ontology"].get("concepts", [])
        click.echo(f"\nOntology concepts ({len(concepts)}):")
        for concept in concepts:
            click.echo(f"  • {concept.get('id', 'unknown')}")

    if "scds" in data:
        scds = data["scds"]
        click.echo(f"\nSCDs ({len(scds)}):")
        for scd in scds:
            click.echo(f"  • {scd}")

    if "imports" in data:
        imports = data["imports"]
        click.echo(f"\nImports ({len(imports)}):")
        for imp in imports:
            click.echo(f"  • {imp}")

    if "provenance" in data:
        prov = data["provenance"]
        click.echo("\nProvenance:")
        click.echo(f"  Created by: {prov.get('created_by', 'N/A')}")
        click.echo(f"  Created at: {prov.get('created_at', 'N/A')}")
        if "rationale" in prov:
            click.echo(f"  Rationale: {prov['rationale']}")


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
    type=click.Path(exists=True),
    default=None,
    help="Path to bundle file to version (default: the workspace's domain or project bundle)",
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
    help="Approver email (prompted for if omitted; never taken from git config)",
)
@click.option(
    "--notes",
    help="Version notes/release notes",
)
@click.option(
    "--no-git",
    is_flag=True,
    help="Skip git commit and tag creation",
)
@click.option(
    "--no-validate",
    is_flag=True,
    help="Skip validation check (not recommended)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing versioned bundle if it exists",
)
def version(bundle, version_number, approved_by, notes, no_git, no_validate, force):
    """
    Create a versioned, immutable snapshot of a validated bundle

    This command automates Phase 3 (Version) of the SCS workflow by:
    1. Validating the bundle (unless --no-validate)
    2. Creating a versioned snapshot with approval metadata
    3. Generating SHA-256 checksum
    4. Creating a version manifest
    5. Creating git commit and tag (unless --no-git)

    \b
    Examples:
        # Basic usage (interactive prompts for missing info)
        scs bundle version --version 1.0.0

        # With approver and notes
        scs bundle version --version 1.0.0 \
            --approved-by "jane@example.com" --notes "Initial release"

        # Version a specific bundle
        scs bundle version --bundle bundles/concepts/security.yaml --version 2.1.0

        # Skip git operations (manual git workflow)
        scs bundle version --version 1.0.0 --no-git
    """
    click.echo("=== SCS Bundle Versioning ===\n")

    bundle_path = Path(bundle) if bundle else _root_bundle(Path.cwd())
    if not bundle_path.exists():
        click.echo(f"Error: Bundle file not found: {bundle}", err=True)
        raise click.Abort()

    # Validate version number format (basic semantic versioning check)
    version_parts = version_number.split(".")
    if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
        click.echo(
            f"Error: Invalid version number '{version_number}'. "
            "Must be semantic version (e.g., 1.0.0)",
            err=True,
        )
        raise click.Abort()

    # The approver is a person the user names, never inferred from the environment
    # (ISS-047, RFC 0002 sections 3 and 6).
    if approved_by is None:
        approved_by = click.prompt("Approver email", type=str)
    approved_by = approved_by.strip()
    if not approved_by:
        click.echo("Error: An approver is required to version a bundle.", err=True)
        raise click.Abort()

    # Manifests and tags carry the bundle name, so several bundles versioned at the same
    # version don't overwrite each other (ISS-043).
    bundle_name = _bundle_name(bundle_path)
    tag = f"{bundle_name}-v{version_number}"
    if not no_git and _git_tag_exists(tag):
        click.echo(f"Error: Git tag already exists: {tag}", err=True)
        raise click.Abort()

    # The content digest is computed by scs-validator's resolver (ISS-045).
    try:
        from scs_validator.digest import DigestError, content_digest
        from scs_validator.resolver import resolve
    except ImportError as e:
        raise click.ClickException(
            f"scs bundle version needs scs-validator ({e}). "
            "Install with: pip install 'scs-tools[validator]'"
        )

    # Get version notes if not provided
    if not notes:
        notes = click.prompt(
            "Version notes (or press Enter for default)",
            default=f"Version {version_number} release",
            show_default=True,
        )

    click.echo()

    # Step 1: Validate bundle (unless skipped)
    if not no_validate:
        click.echo("Step 1/5: Validating bundle...")
        validation_result = _validate_bundle(bundle_path)
        if not validation_result["passed"]:
            click.echo(
                f"\n✗ Validation failed with {validation_result['errors']} error(s).",
                err=True,
            )
            click.echo("Fix validation errors before versioning.", err=True)
            click.echo("Or use --no-validate to skip (not recommended).", err=True)
            raise click.Abort()
        click.echo(
            f"  ✓ Validation passed "
            f"({validation_result['errors']} errors, {validation_result['warnings']} warnings)\n"
        )
    else:
        click.echo("Step 1/5: Skipping validation (--no-validate)\n")

    # Step 2: Create versioned bundle
    click.echo("Step 2/5: Creating versioned bundle snapshot...")
    versioned_bundle_path = _create_versioned_bundle(
        bundle_path, version_number, approved_by, notes, force, validated=not no_validate
    )
    click.echo(f"  ✓ Created: {versioned_bundle_path}\n")

    # Step 3: Checksum the snapshot file, and digest the content it resolves to: the snapshot,
    # its SCDs and its imports (spec/0.7/bundle-format.md §7.6).
    click.echo("Step 3/5: Generating checksum and content digest...")
    checksum, file_size = _generate_checksum(versioned_bundle_path)
    tree = resolve(versioned_bundle_path)
    try:
        digest = content_digest(tree.root, tree.index)
    except DigestError as e:
        versioned_bundle_path.unlink()
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    content_inputs, _ = digest.inputs()
    for kind in ("bundles", "scds"):
        for ref in [r for r, d in content_inputs[kind].items() if d is None]:
            click.echo(f"  Warning: {ref} not found; recorded as missing", err=True)
    click.echo(f"  ✓ SHA-256: {checksum}")
    click.echo(f"  ✓ Content digest: {digest.digest}\n")

    # Step 4: Create version manifest
    click.echo("Step 4/5: Creating version manifest...")
    manifest_path = _create_version_manifest(
        bundle_path,
        versioned_bundle_path,
        bundle_name,
        tag if not no_git else None,
        version_number,
        approved_by,
        notes,
        checksum,
        file_size,
        digest.digest,
        content_inputs,
        validation_result if not no_validate else None,
    )
    click.echo(f"  ✓ Created: {manifest_path}\n")

    # Step 5: Git commit and tag
    if not no_git:
        click.echo("Step 5/5: Creating git commit and tag...")
        _create_git_version(
            versioned_bundle_path,
            manifest_path,
            bundle_name,
            tag,
            version_number,
            checksum,
            validation_result if not no_validate else None,
        )
        click.echo(f"  ✓ Committed and tagged: {tag}\n")
    else:
        click.echo("Step 5/5: Skipping git operations (--no-git)\n")

    # Summary
    click.echo("=" * 60)
    click.echo("✓ Bundle versioning complete!")
    click.echo("=" * 60)
    click.echo(f"Version: {version_number}")
    click.echo(f"Bundle: {versioned_bundle_path}")
    click.echo(f"Manifest: {manifest_path}")
    click.echo(f"Checksum: {checksum}")
    click.echo(f"Content digest: {digest.digest}")
    if not no_git:
        click.echo(f"Git Tag: {tag}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  • Review the versioned bundle and manifest")
    if not no_git:
        click.echo(f"  • Push to remote: git push && git push origin {tag}")
    click.echo("  • Proceed to Phase 4 (Build) - Configure development environments")
    click.echo()


def _validate_bundle(bundle_path):
    """Run validation on the bundle and return results.

    Runs the validator as ``python -m scs_validator`` with this interpreter, so it works whether or
    not the ``scs``/``scs-validate`` scripts are on PATH. Schema lookup is the validator's own
    (``--schema-dir``, ``SCS_SCHEMA_DIR``, then discovery).
    """
    import re
    import sys

    try:
        result = subprocess.run(
            [sys.executable, "-m", "scs_validator", "--bundle", str(bundle_path), "--no-color"],
            capture_output=True,
            text=True,
            check=False,
        )

        # The summary block reads "  N errors" / "  M warnings"
        error_match = re.search(r"^\s*(\d+) errors?", result.stdout, re.M)
        warning_match = re.search(r"^\s*(\d+) warnings?", result.stdout, re.M)
        errors = int(error_match.group(1)) if error_match else (0 if result.returncode == 0 else 1)
        warnings = int(warning_match.group(1)) if warning_match else 0

        if result.returncode != 0 and result.stderr.strip():
            click.echo(f"  {result.stderr.strip()}", err=True)

        return {"passed": result.returncode == 0, "errors": errors, "warnings": warnings}

    except Exception as e:
        click.echo(f"  Warning: Could not run validation: {e}")
        return {"passed": False, "errors": 1, "warnings": 0}


def _bundle_name(bundle_path):
    """The bundle's name from its id (`bundle:<name>`), falling back to the file stem."""
    from scs_validator.names import bundle_name

    with open(bundle_path, "r") as f:
        bundle_id = str((yaml.safe_load(f) or {}).get("id", ""))
    return bundle_name(bundle_id, Path(bundle_path))


def _git_tag_exists(tag):
    result = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _git_output(*args):
    """Output of a git command, or None outside a repository or on error."""
    try:
        return (
            subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL, text=True).strip()
            or None
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _validator_version():
    """Return the installed scs-validator package version, or "unknown" if it can't be read.

    `_validate_bundle` runs the validator as a subprocess of this same interpreter (see above),
    so if that call produced a real result, scs-validator is installed in this environment and
    this lookup should succeed. Read from package metadata rather than hardcoding a version
    string, which goes stale the moment either package is re-versioned.
    """
    try:
        return pkg_version("scs-validator")
    except PackageNotFoundError:
        return "unknown"


def _create_versioned_bundle(bundle_path, version_number, approved_by, notes, force, validated):
    """Create versioned bundle with approval metadata."""
    # Load original bundle
    with open(bundle_path, "r") as f:
        bundle_data = yaml.safe_load(f)

    # Get current timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # The snapshot is the released bundle: it carries the released version (not DRAFT), which is
    # what the approval fields below attest to and what `bundle:<name>:<version>` imports pin.
    bundle_data["version"] = version_number

    # Add approval metadata to provenance. Field names match the schema's
    # required version_approved_by/version_approved_at (RFC-0001, Provenance
    # and approval) - this command is exactly what's meant to populate them.
    if "provenance" not in bundle_data:
        bundle_data["provenance"] = {}

    bundle_data["provenance"]["version_approved_by"] = approved_by
    bundle_data["provenance"]["version_approved_at"] = timestamp
    # Recorded from what happened: under --no-validate the bundle is approved, not validated.
    bundle_data["provenance"]["approval_status"] = "validated" if validated else "approved"
    bundle_data["provenance"]["validation_passed"] = validated
    if validated:
        bundle_data["provenance"]["validation_date"] = timestamp
    bundle_data["provenance"]["version_notes"] = notes

    # Create versioned filename
    bundle_dir = bundle_path.parent
    bundle_name = bundle_path.stem  # e.g., "project-bundle"
    versioned_filename = f"{bundle_name}-v{version_number}.yaml"
    versioned_path = bundle_dir / versioned_filename

    # Check if file exists
    if versioned_path.exists() and not force:
        click.echo(
            f"Error: Versioned bundle already exists: {versioned_path}",
            err=True,
        )
        click.echo("Use --force to overwrite", err=True)
        raise click.Abort()

    # Write versioned bundle
    with open(versioned_path, "w") as f:
        yaml.dump(bundle_data, f, default_flow_style=False, sort_keys=False)

    return versioned_path


def _generate_checksum(file_path):
    """Generate SHA-256 checksum of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    checksum = sha256_hash.hexdigest()
    file_size = file_path.stat().st_size

    return checksum, file_size


def _create_version_manifest(
    original_bundle_path,
    versioned_bundle_path,
    bundle_name,
    tag,
    version_number,
    approved_by,
    notes,
    checksum,
    file_size,
    content_digest,
    content_inputs,
    validation_result,
):
    """Create version manifest file."""
    # Load bundle to get metadata
    with open(original_bundle_path, "r") as f:
        bundle_data = yaml.safe_load(f)

    bundle_id = bundle_data.get("id", "unknown")
    bundle_type = bundle_data.get("type", "project")
    imports = bundle_data.get("imports", [])

    # Count SCDs in project
    context_dir = original_bundle_path.parent.parent / "context" / "project"
    scd_count = 0
    if context_dir.exists():
        scd_count = len([f for f in context_dir.iterdir() if f.suffix == ".yaml"])

    meta_bundles = [imp for imp in imports if imp.split(":")[1:2] == ["meta"]]
    imported_bundles = [imp for imp in imports if imp not in meta_bundles]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "version": version_number,
        "release_date": timestamp,
        "status": "validated" if validation_result else "approved",
        "project": bundle_name,
        "bundle": {
            "id": bundle_id,
            "type": bundle_type,
            "file": versioned_bundle_path.name,
            "sha256": checksum,
            "size_bytes": file_size,
        },
        "content_digest": content_digest,
        "content_inputs": content_inputs,
    }

    if validation_result:
        manifest["validation"] = {
            "validator_version": _validator_version(),
            "validation_date": timestamp,
            "passed": validation_result["passed"],
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"],
            "scd_count": scd_count,
            "import_count": len(imports),
        }

    manifest["components"] = {
        "meta_bundles": meta_bundles,
        "imported_bundles": imported_bundles,
        "total_scds": scd_count,
    }

    manifest["approval"] = {
        "approved_by": approved_by,
        "approved_at": timestamp,
        "approval_notes": notes,
    }

    manifest["phases"] = {
        "phase_1_intent": "completed",
        "phase_2_validate": "completed" if validation_result else "skipped",
        "phase_3_version": "completed",
        "phase_4_build": "pending",
    }

    manifest["release_notes"] = notes

    # Repository and branch come from git, not the bundle name; without git they're omitted.
    distribution = {}
    if tag:
        toplevel = _git_output("rev-parse", "--show-toplevel")
        branch = _git_output("symbolic-ref", "--short", "-q", "HEAD")
        if toplevel:
            distribution["repository"] = Path(toplevel).name
        if branch:
            distribution["branch"] = branch
        distribution["tag"] = tag
    distribution["immutable"] = True
    distribution["authoritative"] = True
    manifest["distribution"] = distribution

    # Write manifest
    manifest_filename = f"{bundle_name}-v{version_number}-MANIFEST.yaml"
    manifest_path = versioned_bundle_path.parent / manifest_filename

    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    return manifest_path


def _create_git_version(
    versioned_bundle_path,
    manifest_path,
    bundle_name,
    tag,
    version_number,
    checksum,
    validation_result,
):
    """Create git commit and tag for the version."""
    try:
        # Check if git is available and we're in a repo
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
        )

        # Stage files
        subprocess.run(
            ["git", "add", str(versioned_bundle_path), str(manifest_path)],
            check=True,
        )

        # Create commit message
        validation_summary = ""
        if validation_result:
            validation_summary = f"""
Phase 2 (Validate) Results:
- {validation_result.get('errors', 0)} validation errors
- {validation_result.get('warnings', 0)} warnings
"""

        commit_message = f"""Release {tag} - Phase 3 (Version) Complete

Created immutable versioned snapshot of validated SCD bundle.
{validation_summary}
Deliverables:
- Versioned bundle: {versioned_bundle_path.name}
- Version manifest: {manifest_path.name}
- SHA-256 checksum: {checksum}

This bundle is now the authoritative source of truth.
"""

        # Create commit
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True,
        )

        # Create annotated tag
        phase_2 = (
            "✓ Phase 2: Validate - Bundle validated"
            if validation_result
            else "- Phase 2: Validate - skipped (--no-validate)"
        )
        tag_message = f"""SCD Bundle {bundle_name} v{version_number}

Validation Status: {'✓ PASSED' if validation_result else 'SKIPPED (--no-validate)'}
Bundle Checksum (SHA-256): {checksum}

Phase Completion:
✓ Phase 1: Intent - SCDs generated
{phase_2}
✓ Phase 3: Version - Immutable snapshot created

Ready for Phase 4 (Build) - development environment configuration.
"""

        subprocess.run(
            ["git", "tag", "-a", tag, "-m", tag_message],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        click.echo(f"  Warning: Git operation failed: {e}", err=True)
        click.echo("  Files were created but not committed to git", err=True)
        raise click.Abort()
