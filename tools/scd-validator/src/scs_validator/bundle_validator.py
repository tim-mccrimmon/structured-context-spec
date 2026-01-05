"""Bundle validation module for Level 5 validation."""

from pathlib import Path
from typing import Any, Dict, List

from .rules_loader import RulesLoader
from .utils import ValidationError, ValidationResult, ValidationWarning


class BundleValidator:
    """Validator for bundle organization and structure (Level 5)."""

    def __init__(self, rules_loader: RulesLoader):
        """Initialize bundle validator.

        Args:
            rules_loader: Rules loader instance
        """
        self.rules_loader = rules_loader
        self.rules = rules_loader.load_bundle_rules()

    def validate_bundle(
        self, bundle: Dict[str, Any], file_path: str | None = None
    ) -> ValidationResult:
        """Validate bundle organization and structure.

        This implements Level 5 validation:
        - XOR constraint (imports OR scds, not both)
        - Bundle type-specific rules
        - Meta bundle requirements

        Args:
            bundle: Bundle data as dictionary
            file_path: Optional file path for error messages

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult("bundle")

        bundle_id = bundle.get("id", "unknown")
        bundle_type = bundle.get("type")

        if not bundle_type:
            result.add_error(
                ValidationError(
                    "Bundle missing required 'type' field",
                    file_path=file_path,
                )
            )
            return result

        # Validate XOR constraint
        self._validate_xor_constraint(bundle, bundle_id, bundle_type, result, file_path)

        # Validate bundle type-specific rules
        self._validate_bundle_type_rules(
            bundle, bundle_id, bundle_type, result, file_path
        )

        # Validate meta bundle requirements
        if bundle_type == "meta":
            self._validate_meta_bundle(bundle, bundle_id, result, file_path)

        return result

    def _validate_xor_constraint(
        self,
        bundle: Dict[str, Any],
        bundle_id: str,
        bundle_type: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate XOR constraint: bundles contain imports OR scds, not both.

        Args:
            bundle: Bundle data
            bundle_id: Bundle ID
            bundle_type: Bundle type
            result: Validation result to update
            file_path: Optional file path
        """
        xor_rules = self.rules.get("xor_constraint", {})
        if not xor_rules.get("enabled", True):
            return

        imports = bundle.get("imports", [])
        scds = bundle.get("scds", [])

        has_imports = len(imports) > 0
        has_scds = len(scds) > 0

        # XOR: (imports AND NOT scds) OR (scds AND NOT imports)
        xor_satisfied = (has_imports and not has_scds) or (has_scds and not has_imports)

        if not xor_satisfied:
            severity = xor_rules.get("severity", "error")
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "xor_violation",
                bundle_id=bundle_id,
                bundle_type=bundle_type,
                imports_count=len(imports),
                scds_count=len(scds),
            )

            if severity == "error":
                result.add_error(ValidationError(error_msg, file_path=file_path))
            else:
                result.add_warning(
                    ValidationWarning(error_msg, level="bundle", file_path=file_path)
                )

    def _validate_bundle_type_rules(
        self,
        bundle: Dict[str, Any],
        bundle_id: str,
        bundle_type: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate bundle type-specific rules.

        Args:
            bundle: Bundle data
            bundle_id: Bundle ID
            bundle_type: Bundle type
            result: Validation result to update
            file_path: Optional file path
        """
        bundle_types = self.rules.get("bundle_types", {})
        type_rules = bundle_types.get(bundle_type)

        if not type_rules:
            result.add_warning(
                ValidationWarning(
                    f"Unknown bundle type '{bundle_type}' - no validation rules found",
                    level="bundle",
                    file_path=file_path,
                )
            )
            return

        imports = bundle.get("imports", [])
        scds = bundle.get("scds", [])

        # Validate imports rules
        import_rules = type_rules.get("imports", {})
        if import_rules:
            self._validate_array_constraints(
                imports,
                import_rules,
                "imports",
                bundle_id,
                bundle_type,
                result,
                file_path,
            )

        # Validate scds rules
        scd_rules = type_rules.get("scds", {})
        if scd_rules:
            self._validate_array_constraints(
                scds, scd_rules, "scds", bundle_id, bundle_type, result, file_path
            )

    def _validate_array_constraints(
        self,
        array: List[Any],
        constraints: Dict[str, Any],
        field_name: str,
        bundle_id: str,
        bundle_type: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate array field constraints (min, max, required).

        Args:
            array: Array to validate
            constraints: Constraint rules
            field_name: Name of field being validated
            bundle_id: Bundle ID
            bundle_type: Bundle type
            result: Validation result to update
            file_path: Optional file path
        """
        array_len = len(array)

        # Check minimum
        min_val = constraints.get("min")
        if min_val is not None and array_len < min_val:
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "insufficient_items",
                field=field_name,
                bundle_type=bundle_type,
                actual=array_len,
                required=min_val,
            )
            result.add_error(ValidationError(error_msg, file_path=file_path))

        # Check maximum
        max_val = constraints.get("max")
        if max_val is not None and array_len > max_val:
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "excessive_items",
                field=field_name,
                bundle_type=bundle_type,
                actual=array_len,
                allowed=max_val,
            )
            result.add_error(ValidationError(error_msg, file_path=file_path))

        # Check required (must have at least 1)
        required = constraints.get("required", False)
        if required and array_len == 0:
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "required_field_empty",
                field=field_name,
                bundle_type=bundle_type,
            )
            result.add_error(ValidationError(error_msg, file_path=file_path))

    def _validate_meta_bundle(
        self,
        bundle: Dict[str, Any],
        bundle_id: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate meta bundle requirements.

        Args:
            bundle: Bundle data
            bundle_id: Bundle ID
            result: Validation result to update
            file_path: Optional file path
        """
        meta_rules = self.rules.get("meta_bundle_requirements", {})
        if not meta_rules:
            return

        # Check version format (should align with SCS spec version)
        version_pattern = meta_rules.get("version_pattern")
        if version_pattern:
            version = bundle.get("version")
            if version:
                import re

                if not re.match(version_pattern, version):
                    error_msg = self.rules_loader.get_error_message(
                        self.rules,
                        "invalid_meta_version",
                        version=version,
                        pattern=version_pattern,
                    )
                    result.add_warning(
                        ValidationWarning(error_msg, level="bundle", file_path=file_path)
                    )
