"""Schema validation module for SCDs."""

from pathlib import Path
from typing import Any, Dict

import jsonschema
from jsonschema import Draft202012Validator

from .parser import Parser
from .utils import ValidationError, ValidationResult, get_tier_from_id, find_schema_file


class SchemaValidator:
    """Validator for JSON Schema compliance."""

    def __init__(self, schema_dir: Path):
        """Initialize schema validator.

        Args:
            schema_dir: Root directory containing schema files
        """
        self.schema_dir = schema_dir
        self._schema_cache: Dict[str, Dict[str, Any]] = {}

    def validate_scd(
        self, scd: Dict[str, Any], file_path: str | None = None
    ) -> ValidationResult:
        """Validate an SCD against its tier-specific schema.

        Args:
            scd: SCD data as dictionary
            file_path: Optional file path for error messages

        Returns:
            ValidationResult with errors if validation fails
        """
        result = ValidationResult("schema")

        # Extract SCD ID and tier
        scd_id = scd.get("id")
        if not scd_id:
            result.add_error(
                ValidationError("Missing required field 'id'", file_path=file_path)
            )
            return result

        # Get tier from ID
        tier = get_tier_from_id(scd_id)
        if not tier:
            result.add_error(
                ValidationError(
                    f"Invalid SCD ID format: '{scd_id}'. Expected format: scd:<tier>:<name>",
                    scd_id=scd_id,
                    file_path=file_path,
                )
            )
            return result

        # Load schema for tier
        try:
            schema = self._load_schema(tier)
        except ValidationError as e:
            result.add_error(e)
            return result

        # Validate against schema
        try:
            validator = Draft202012Validator(schema)
            errors = list(validator.iter_errors(scd))

            if errors:
                for error in errors:
                    error_msg = self._format_schema_error(error)
                    result.add_error(
                        ValidationError(error_msg, scd_id=scd_id, file_path=file_path)
                    )
        except Exception as e:
            result.add_error(
                ValidationError(
                    f"Schema validation failed: {e}", scd_id=scd_id, file_path=file_path
                )
            )

        if result.passed:
            result.details["tier"] = tier
            result.details["scd_id"] = scd_id

        return result

    def validate_bundle(
        self, bundle: Dict[str, Any], file_path: str | None = None
    ) -> ValidationResult:
        """Validate a bundle against the bundle schema.

        Args:
            bundle: Bundle data as dictionary
            file_path: Optional file path for error messages

        Returns:
            ValidationResult with errors if validation fails
        """
        result = ValidationResult("bundle_schema")

        # Load bundle schema
        try:
            schema = self._load_bundle_schema()
        except ValidationError as e:
            result.add_error(e)
            return result

        # Validate against schema
        try:
            validator = Draft202012Validator(schema)
            errors = list(validator.iter_errors(bundle))

            if errors:
                for error in errors:
                    error_msg = self._format_schema_error(error)
                    result.add_error(ValidationError(error_msg, file_path=file_path))
        except Exception as e:
            result.add_error(
                ValidationError(f"Bundle schema validation failed: {e}", file_path=file_path)
            )

        if result.passed:
            bundle_id = bundle.get("id", "unknown")
            result.details["bundle_id"] = bundle_id

        return result

    def _load_schema(self, tier: str) -> Dict[str, Any]:
        """Load schema for a specific tier (with caching).

        Args:
            tier: Tier name (meta, project, standards)

        Returns:
            Schema as dictionary

        Raises:
            ValidationError: If schema cannot be loaded
        """
        if tier in self._schema_cache:
            return self._schema_cache[tier]

        try:
            schema_file = find_schema_file(tier, self.schema_dir)
            schema = Parser.load_schema(schema_file)
            self._schema_cache[tier] = schema
            return schema
        except FileNotFoundError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Failed to load schema for tier '{tier}': {e}")

    def _load_bundle_schema(self) -> Dict[str, Any]:
        """Load bundle schema (with caching).

        Returns:
            Bundle schema as dictionary

        Raises:
            ValidationError: If schema cannot be loaded
        """
        cache_key = "__bundle__"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        try:
            from .utils import find_bundle_schema

            schema_file = find_bundle_schema(self.schema_dir)
            schema = Parser.load_schema(schema_file)
            self._schema_cache[cache_key] = schema
            return schema
        except FileNotFoundError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Failed to load bundle schema: {e}")

    @staticmethod
    def _format_schema_error(error: jsonschema.ValidationError) -> str:
        """Format a JSON Schema validation error into a readable message.

        Args:
            error: JSON Schema validation error

        Returns:
            Formatted error message
        """
        # Get the path to the error location
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"

        # Handle different error types
        if error.validator == "required":
            missing_field = error.message.split("'")[1] if "'" in error.message else "unknown"
            return f"Missing required field: '{missing_field}'"
        elif error.validator == "pattern":
            return f"Field '{path}' does not match required pattern: {error.message}"
        elif error.validator == "type":
            return f"Field '{path}' has incorrect type: {error.message}"
        elif error.validator == "const":
            return f"Field '{path}' must be: {error.message}"
        elif error.validator == "minLength":
            return f"Field '{path}' is too short: {error.message}"
        else:
            return f"Field '{path}': {error.message}"
