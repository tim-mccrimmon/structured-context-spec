"""Validation command for SCS CLI."""

import sys
from pathlib import Path
from typing import List

import click

from .. import __version__
from ..bundle_validator import BundleValidator
from ..completeness_validator import CompletenessValidator
from ..parser import Parser
from ..relationship_validator import RelationshipValidator
from ..reporter import Reporter
from ..rules_loader import RulesLoader
from ..schema_validator import SchemaValidator
from ..semantic_validator import SemanticValidator
from ..utils import ValidationError, ValidationResult


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=False)
@click.option(
    "--bundle",
    "-b",
    type=click.Path(exists=True),
    help="Validate an SCD bundle file",
)
@click.option(
    "--schema-dir",
    "-s",
    type=click.Path(exists=True),
    help="Directory containing JSON schema files (default: ../../schema relative to CWD)",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Fail on warnings (exit code 2)",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
@click.option(
    "--skip-completeness",
    is_flag=True,
    help="Skip Level 6 completeness validation",
)
@click.option(
    "--completeness-rules",
    type=click.Path(exists=True),
    help="Path to custom completeness rules file",
)
def validate(
    files: tuple,
    bundle: str | None,
    schema_dir: str | None,
    output: str,
    strict: bool,
    no_color: bool,
    verbose: bool,
    skip_completeness: bool,
    completeness_rules: str | None,
) -> None:
    """Validate SCS documents and bundles.

    Examples:

        \b
        # Validate a single SCD file
        scs validate context/meta/roles.yaml

        \b
        # Validate multiple SCD files
        scs validate context/meta/*.yaml

        \b
        # Validate a bundle
        scs validate --bundle context/bundle.yaml

        \b
        # Strict mode (fail on warnings)
        scs validate --bundle context/bundle.yaml --strict

        \b
        # JSON output
        scs validate --bundle context/bundle.yaml --output json
    """
    try:
        # Determine schema directory
        if schema_dir:
            schema_path = Path(schema_dir)
        else:
            # Default: ../../schema relative to CWD
            schema_path = Path.cwd() / "schema"
            if not schema_path.exists():
                # Try relative to the validator location
                schema_path = Path(__file__).parent.parent.parent.parent.parent / "schema"

        if not schema_path.exists():
            click.echo(
                f"Error: Schema directory not found: {schema_path}\n"
                f"Use --schema-dir to specify the location",
                err=True,
            )
            sys.exit(4)

        # Initialize rules loader and validators
        parser = Parser()
        rules_loader = RulesLoader()
        schema_validator = SchemaValidator(schema_path)
        semantic_validator = SemanticValidator(rules_loader)
        bundle_validator = BundleValidator(rules_loader)
        relationship_validator = RelationshipValidator(rules_loader)

        # Initialize completeness validator with custom rules if provided
        completeness_rules_path = Path(completeness_rules) if completeness_rules else None
        completeness_validator = CompletenessValidator(rules_loader, completeness_rules_path)

        reporter = Reporter(use_color=not no_color)

        results: List[ValidationResult] = []

        if bundle:
            # Validate bundle
            results = validate_bundle(
                bundle,
                parser,
                schema_validator,
                semantic_validator,
                bundle_validator,
                relationship_validator,
                completeness_validator,
                verbose,
                skip_completeness,
            )
        elif files:
            # Validate individual files
            results = validate_files(
                files, parser, schema_validator, semantic_validator, verbose
            )
        else:
            click.echo("Error: No files or bundle specified\n", err=True)
            click.echo(click.get_current_context().get_help())
            sys.exit(3)

        # Generate report
        if output == "json":
            report = reporter.report_json(results, __version__, strict)
        else:
            report = reporter.report_text(results, __version__, strict)

        click.echo(report)

        # Determine exit code
        exit_code = determine_exit_code(results, strict)
        sys.exit(exit_code)

    except ValidationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(5)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(5)


def validate_files(
    file_paths: tuple,
    parser: Parser,
    schema_validator: SchemaValidator,
    semantic_validator: SemanticValidator,
    verbose: bool,
) -> List[ValidationResult]:
    """Validate individual SCD files."""
    syntax_result = ValidationResult("syntax")
    schema_result = ValidationResult("schema")
    semantic_result = ValidationResult("semantic")

    files_checked = 0

    for file_path_str in file_paths:
        file_path = Path(file_path_str)

        if verbose:
            click.echo(f"Validating {file_path}...")

        try:
            # Parse file (syntax validation)
            scd = parser.load_scd(file_path)
            files_checked += 1

            # Schema validation
            result = schema_validator.validate_scd(scd, str(file_path))
            schema_result.errors.extend(result.errors)
            schema_result.warnings.extend(result.warnings)
            if not result.passed:
                schema_result.passed = False

            # Semantic validation
            result = semantic_validator.validate_scd(scd, str(file_path))
            semantic_result.errors.extend(result.errors)
            semantic_result.warnings.extend(result.warnings)
            if not result.passed:
                semantic_result.passed = False

        except ValidationError as e:
            syntax_result.add_error(e)

    syntax_result.details["files_checked"] = files_checked
    schema_result.details["files_checked"] = files_checked
    semantic_result.details["files_checked"] = files_checked

    return [syntax_result, schema_result, semantic_result]


def validate_bundle(
    bundle_path: str,
    parser: Parser,
    schema_validator: SchemaValidator,
    semantic_validator: SemanticValidator,
    bundle_validator: BundleValidator,
    relationship_validator: RelationshipValidator,
    completeness_validator: CompletenessValidator,
    verbose: bool,
    skip_completeness: bool,
) -> List[ValidationResult]:
    """Validate an SCD bundle."""
    syntax_result = ValidationResult("syntax")
    bundle_schema_result = ValidationResult("bundle_schema")
    semantic_result = ValidationResult("semantic")
    bundle_result = ValidationResult("bundle")
    relationship_result = ValidationResult("relationships")
    completeness_result = ValidationResult("completeness")

    if verbose:
        click.echo(f"Validating bundle {bundle_path}...")

    try:
        # Level 1: Parse bundle (syntax validation)
        bundle = parser.load_bundle(Path(bundle_path))
        bundle_id = bundle.get('id', 'unknown')
        bundle_type = bundle.get('type', 'unknown')

        if verbose:
            click.echo(f"Bundle ID: {bundle_id}")
            click.echo(f"Bundle Type: {bundle_type}")

        # Level 2: Validate bundle schema
        bundle_schema_result = schema_validator.validate_bundle(bundle, bundle_path)
        if not bundle_schema_result.passed:
            # Stop here if schema validation fails
            return [syntax_result, bundle_schema_result]

        # Level 5: Validate bundle organization (XOR constraint, bundle type rules)
        bundle_result = bundle_validator.validate_bundle(bundle, bundle_path)

        # Load SCDs for further validation
        all_scds = []
        scd_refs = []

        # Collect SCD references from bundle and imported bundles
        bundle_dir = Path(bundle_path).parent
        # Project root is parent of bundles/ directory
        project_root = bundle_dir.parent if bundle_dir.name == "bundles" else bundle_dir

        # If this is a project bundle, load domain bundles to get SCD references
        if bundle_type == "project":
            imports = bundle.get("imports", [])

            if verbose:
                click.echo(f"Loading {len(imports)} imported bundles...")

            for import_ref in imports:
                # Parse bundle reference: bundle:<name>:<version> or bundle:<name>
                parts = import_ref.split(":")
                if len(parts) >= 2 and parts[0] == "bundle":
                    bundle_name = parts[1]

                    # Skip meta and standards bundles for now
                    if bundle_name in ["meta", "standards"]:
                        continue

                    # Try to find the domain bundle file
                    domain_bundle_path = bundle_dir / "domains" / f"{bundle_name}.yaml"

                    if domain_bundle_path.exists():
                        try:
                            domain_bundle = parser.load_bundle(domain_bundle_path)
                            domain_scds = domain_bundle.get("scds", [])
                            scd_refs.extend(domain_scds)

                            if verbose:
                                click.echo(f"  Loaded {bundle_name}: {len(domain_scds)} SCDs")
                        except Exception as e:
                            if verbose:
                                click.echo(f"  Warning: Could not load {domain_bundle_path}: {e}")
                    else:
                        if verbose:
                            click.echo(f"  Warning: Domain bundle not found: {domain_bundle_path}")
        else:
            # For non-project bundles, use SCDs directly from the bundle
            scd_refs = bundle.get("scds", [])

        if scd_refs and verbose:
            click.echo(f"Loading {len(scd_refs)} SCDs...")

        # Load each SCD file
        for scd_ref in scd_refs:
            # Resolve SCD reference to file path
            # Format: scd:project:system-context → context/project/system-context.yaml
            if scd_ref.startswith("scd:"):
                parts = scd_ref.split(":", 2)
                if len(parts) >= 3:
                    tier = parts[1]  # project, meta, or standards
                    scd_name = parts[2]

                    # Construct file path
                    scd_file = project_root / "context" / tier / f"{scd_name}.yaml"

                    if scd_file.exists():
                        try:
                            scd_data = parser.load_scd(scd_file)
                            all_scds.append(scd_data)

                            # Level 3: Semantic validation for this SCD
                            result = semantic_validator.validate_scd(scd_data, str(scd_file))
                            semantic_result.errors.extend(result.errors)
                            semantic_result.warnings.extend(result.warnings)
                            if not result.passed:
                                semantic_result.passed = False
                        except Exception as e:
                            if verbose:
                                click.echo(f"  Warning: Could not load {scd_file}: {e}")
                    else:
                        if verbose:
                            click.echo(f"  Warning: SCD file not found: {scd_file}")

        if verbose:
            click.echo(f"Successfully loaded {len(all_scds)} SCDs")

        # Level 4: Relationship validation
        if all_scds:
            relationship_result = relationship_validator.validate_relationships(
                all_scds, bundle_type, bundle_path
            )

        # Level 6: Completeness validation (if not skipped)
        if not skip_completeness and bundle_type == "project":
            project_root = Path(bundle_path).parent
            completeness_result = completeness_validator.validate_completeness(
                bundle, all_scds, bundle_path, project_root
            )
        elif skip_completeness and verbose:
            click.echo("Skipping completeness validation (--skip-completeness)")

    except ValidationError as e:
        syntax_result.add_error(e)

    results = [syntax_result, bundle_schema_result, semantic_result, bundle_result]

    if relationship_result.errors or relationship_result.warnings:
        results.append(relationship_result)

    if not skip_completeness and (completeness_result.errors or completeness_result.warnings):
        results.append(completeness_result)

    return results


def determine_exit_code(results: List[ValidationResult], strict: bool) -> int:
    """Determine exit code based on validation results."""
    has_errors = any(not r.passed for r in results)
    has_warnings = any(r.warning_count > 0 for r in results)

    if has_errors:
        return 1
    elif strict and has_warnings:
        return 2
    else:
        return 0
