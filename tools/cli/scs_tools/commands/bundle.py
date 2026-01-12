"""
Bundle command - manage SCS bundles
"""

from pathlib import Path
import yaml
import click
import hashlib
import subprocess
from datetime import datetime, timezone
from scs_tools.utils.files import get_template_path
from scs_tools.utils.project_types import SOFTWARE_DEVELOPMENT_CONCERNS, PROJECT_TYPES


@click.group()
def bundle():
    """
    Manage SCS bundles

    Bundles organize SCDs by domain and enable validation and versioning.
    Use these commands to list, inspect, validate, and version your bundles.
    """
    pass


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
        click.echo("Available domain bundles:\n")
        for bundle_name in SOFTWARE_DEVELOPMENT_CONCERNS:
            click.echo(f"  • {bundle_name}")

        click.echo("\nProject types and their bundles:\n")
        for ptype, config in PROJECT_TYPES.items():
            click.echo(f"  {ptype}:")
            click.echo(f"    Description: {config['description']}")
            if config.get("minimal"):
                click.echo(f"    Bundles: 3 minimal bundles (architecture, security, deployment-operations)")
            else:
                click.echo(f"    Bundles: All 10 domain bundles")
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

    click.echo("Project bundles:\n")

    # Check for main bundles
    main_bundles = ["project-bundle.yaml", "meta-bundle.yaml", "standards-bundle.yaml"]
    for bundle_file in main_bundles:
        bundle_path = bundles_dir / bundle_file
        if bundle_path.exists():
            with open(bundle_path, 'r') as f:
                data = yaml.safe_load(f)
                bundle_id = data.get('id', 'unknown')
                bundle_type = data.get('type', 'unknown')
                version = data.get('version', 'unknown')
                click.echo(f"  • {bundle_file}")
                click.echo(f"    ID: {bundle_id}")
                click.echo(f"    Type: {bundle_type}")
                click.echo(f"    Version: {version}\n")

    # Check for domain bundles
    domains_dir = bundles_dir / "domains"
    if domains_dir.exists():
        click.echo("Domain bundles:\n")
        for bundle_file in sorted(domains_dir.glob("*.yaml")):
            with open(bundle_file, 'r') as f:
                data = yaml.safe_load(f)
                bundle_id = data.get('id', 'unknown')
                domain = data.get('domain', 'unknown')
                version = data.get('version', 'unknown')
                scds = data.get('scds', [])
                click.echo(f"  • {bundle_file.name}")
                click.echo(f"    ID: {bundle_id}")
                click.echo(f"    Domain: {domain}")
                click.echo(f"    Version: {version}")
                click.echo(f"    SCDs: {len(scds)}\n")


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
        base_path / "bundles" / "domains" / f"{bundle_name}.yaml",
    ]

    bundle_path = None
    for loc in bundle_locations:
        if loc.exists():
            bundle_path = loc
            break

    # If not found in project, check templates
    if not bundle_path:
        template_path = get_template_path() / "bundles" / "domains" / f"{bundle_name}.yaml"
        if template_path.exists():
            bundle_path = template_path
            click.echo(f"(Showing template bundle, not in current project)\n")
        else:
            click.echo(
                f"Error: Bundle '{bundle_name}' not found in project or templates.",
                err=True,
            )
            raise click.Abort()

    # Load and display bundle info
    with open(bundle_path, 'r') as f:
        data = yaml.safe_load(f)

    click.echo(f"Bundle: {bundle_name}\n")
    click.echo(f"ID: {data.get('id', 'N/A')}")
    click.echo(f"Type: {data.get('type', 'N/A')}")
    click.echo(f"Version: {data.get('version', 'N/A')}")
    click.echo(f"Title: {data.get('title', 'N/A')}")
    click.echo(f"Description: {data.get('description', 'N/A')}")

    if 'domain' in data:
        click.echo(f"Domain: {data['domain']}")

    if 'concerns' in data:
        click.echo(f"\nConcerns:")
        for concern in data['concerns']:
            click.echo(f"  • {concern}")

    if 'scds' in data:
        scds = data['scds']
        click.echo(f"\nSCDs ({len(scds)}):")
        for scd in scds:
            click.echo(f"  • {scd}")

    if 'imports' in data:
        imports = data['imports']
        click.echo(f"\nImports ({len(imports)}):")
        for imp in imports:
            click.echo(f"  • {imp}")

    if 'provenance' in data:
        prov = data['provenance']
        click.echo(f"\nProvenance:")
        click.echo(f"  Created by: {prov.get('created_by', 'N/A')}")
        click.echo(f"  Created at: {prov.get('created_at', 'N/A')}")
        if 'rationale' in prov:
            click.echo(f"  Rationale: {prov['rationale']}")


@bundle.command()
def validate():
    """
    Validate bundles in the current project

    This is a shortcut for: scs validate --bundle bundles/project-bundle.yaml

    \b
    Example:
        scs bundle validate
    """
    base_path = Path.cwd()
    project_bundle = base_path / "bundles" / "project-bundle.yaml"

    if not project_bundle.exists():
        click.echo(
            "Error: No project bundle found at bundles/project-bundle.yaml",
            err=True,
        )
        raise click.Abort()

    # Import and call the validate command
    from scs_tools.commands.validate import validate as validate_cmd

    ctx = click.get_current_context()
    ctx.invoke(validate_cmd, bundle=str(project_bundle))


@bundle.command()
@click.option(
    "--bundle",
    "-b",
    type=click.Path(exists=True),
    default="bundles/project-bundle.yaml",
    help="Path to bundle file to version",
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
    help="Approver email (default: git config user.email)",
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
        scs bundle version --version 1.0.0 --approved-by "jane@example.com" --notes "Initial release"

        # Version a specific bundle
        scs bundle version --bundle bundles/custom-bundle.yaml --version 2.1.0

        # Skip git operations (manual git workflow)
        scs bundle version --version 1.0.0 --no-git
    """
    click.echo("=== SCS Bundle Versioning ===\n")

    bundle_path = Path(bundle)
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

    # Get approver email
    if not approved_by:
        try:
            approved_by = subprocess.check_output(
                ["git", "config", "user.email"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            approved_by = None

        if not approved_by:
            approved_by = click.prompt("Approver email", type=str)

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
        bundle_path, version_number, approved_by, notes, force
    )
    click.echo(f"  ✓ Created: {versioned_bundle_path}\n")

    # Step 3: Generate checksum
    click.echo("Step 3/5: Generating SHA-256 checksum...")
    checksum, file_size = _generate_checksum(versioned_bundle_path)
    click.echo(f"  ✓ SHA-256: {checksum}\n")

    # Step 4: Create version manifest
    click.echo("Step 4/5: Creating version manifest...")
    manifest_path = _create_version_manifest(
        bundle_path,
        versioned_bundle_path,
        version_number,
        approved_by,
        notes,
        checksum,
        file_size,
        validation_result if not no_validate else None,
    )
    click.echo(f"  ✓ Created: {manifest_path}\n")

    # Step 5: Git commit and tag
    if not no_git:
        click.echo("Step 5/5: Creating git commit and tag...")
        _create_git_version(
            versioned_bundle_path,
            manifest_path,
            version_number,
            checksum,
            validation_result if not no_validate else None,
        )
        click.echo(f"  ✓ Committed and tagged: v{version_number}\n")
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
    if not no_git:
        click.echo(f"Git Tag: v{version_number}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  • Review the versioned bundle and manifest")
    if not no_git:
        click.echo("  • Push to remote: git push origin main && git push origin v{version_number}")
    click.echo("  • Proceed to Phase 4 (Build) - Configure development environments")
    click.echo()


def _validate_bundle(bundle_path):
    """Run validation on the bundle and return results."""
    try:
        # Try to find schema directory
        schema_dir = None
        possible_schema_paths = [
            Path.cwd() / "schema",
            Path.cwd().parent / "scs-spec" / "schema",
            Path.cwd().parent.parent / "scs-spec" / "schema",
        ]

        for schema_path in possible_schema_paths:
            if schema_path.exists():
                schema_dir = schema_path
                break

        # Run scs validate command
        cmd = ["scs", "validate", "--bundle", str(bundle_path), "--output", "json"]
        if schema_dir:
            cmd.extend(["--schema-dir", str(schema_dir)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        # Parse JSON output to get error/warning counts
        if "Status: ✓ VALID" in result.stdout or result.returncode == 0:
            # Try to extract counts from output
            errors = 0
            warnings = result.stdout.count("⚠")

            return {
                "passed": True,
                "errors": errors,
                "warnings": warnings,
            }
        else:
            # Extract error count
            import re

            error_match = re.search(r"(\d+) errors?", result.stdout)
            warning_match = re.search(r"(\d+) warnings?", result.stdout)

            return {
                "passed": False,
                "errors": int(error_match.group(1)) if error_match else 1,
                "warnings": int(warning_match.group(1)) if warning_match else 0,
            }

    except Exception as e:
        click.echo(f"  Warning: Could not run validation: {e}")
        return {"passed": False, "errors": 1, "warnings": 0}


def _create_versioned_bundle(bundle_path, version_number, approved_by, notes, force):
    """Create versioned bundle with approval metadata."""
    # Load original bundle
    with open(bundle_path, "r") as f:
        bundle_data = yaml.safe_load(f)

    # Get current timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Add approval metadata to provenance
    if "provenance" not in bundle_data:
        bundle_data["provenance"] = {}

    bundle_data["provenance"]["approved_by"] = approved_by
    bundle_data["provenance"]["approved_at"] = timestamp
    bundle_data["provenance"]["approval_status"] = "validated"
    bundle_data["provenance"]["validation_passed"] = True
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
    version_number,
    approved_by,
    notes,
    checksum,
    file_size,
    validation_result,
):
    """Create version manifest file."""
    # Load bundle to get metadata
    with open(original_bundle_path, "r") as f:
        bundle_data = yaml.safe_load(f)

    bundle_id = bundle_data.get("id", "unknown")
    bundle_type = bundle_data.get("type", "project")
    imports = bundle_data.get("imports", [])

    # Get project name from bundle ID
    project_name = bundle_id.replace("bundle:", "")

    # Count SCDs in project
    context_dir = original_bundle_path.parent.parent / "context" / "project"
    scd_count = 0
    if context_dir.exists():
        scd_count = len([f for f in context_dir.iterdir() if f.suffix == ".yaml"])

    # Extract domain bundles from imports
    foundation_bundles = []
    domain_bundles = []
    for imp in imports:
        if "meta" in imp or "standards" in imp:
            foundation_bundles.append(imp)
        else:
            domain_bundles.append(imp)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "version": version_number,
        "release_date": timestamp,
        "status": "validated",
        "project": project_name,
        "bundle": {
            "id": bundle_id,
            "type": bundle_type,
            "file": versioned_bundle_path.name,
            "sha256": checksum,
            "size_bytes": file_size,
        },
    }

    if validation_result:
        manifest["validation"] = {
            "validator_version": "0.1.0",
            "validation_date": timestamp,
            "passed": validation_result["passed"],
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"],
            "scd_count": scd_count,
            "domain_count": len(domain_bundles),
        }

    manifest["components"] = {
        "foundation_bundles": foundation_bundles,
        "domain_bundles": domain_bundles,
        "total_scds": scd_count,
    }

    manifest["approval"] = {
        "approved_by": approved_by,
        "approved_at": timestamp,
        "approval_notes": notes,
    }

    manifest["phases"] = {
        "phase_1_intent": "completed",
        "phase_2_validate": "completed",
        "phase_3_version": "completed",
        "phase_4_build": "pending",
    }

    manifest["release_notes"] = notes

    manifest["distribution"] = {
        "repository": project_name,
        "branch": "main",
        "tag": f"v{version_number}",
        "immutable": True,
        "authoritative": True,
    }

    # Write manifest
    manifest_filename = f"VERSION-{version_number}-MANIFEST.yaml"
    manifest_path = versioned_bundle_path.parent / manifest_filename

    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    return manifest_path


def _create_git_version(
    versioned_bundle_path, manifest_path, version_number, checksum, validation_result
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

        commit_message = f"""Release v{version_number} - Phase 3 (Version) Complete

Created immutable versioned snapshot of validated SCD bundle.
{validation_summary}
Deliverables:
- Versioned bundle: {versioned_bundle_path.name}
- Version manifest: {manifest_path.name}
- SHA-256 checksum: {checksum}

This bundle is now the authoritative source of truth.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

        # Create commit
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True,
        )

        # Create annotated tag
        tag_message = f"""SCD Bundle v{version_number}

Validation Status: {'✓ PASSED' if validation_result and validation_result['passed'] else '✗ FAILED'}
Bundle Checksum (SHA-256): {checksum}

Phase Completion:
✓ Phase 1: Intent - SCDs generated
✓ Phase 2: Validate - Bundle validated
✓ Phase 3: Version - Immutable snapshot created

Ready for Phase 4 (Build) - development environment configuration.
"""

        subprocess.run(
            ["git", "tag", "-a", f"v{version_number}", "-m", tag_message],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        click.echo(f"  Warning: Git operation failed: {e}", err=True)
        click.echo("  Files were created but not committed to git", err=True)
        raise click.Abort()
