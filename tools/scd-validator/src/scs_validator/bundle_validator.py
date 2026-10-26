"""Bundle validation module for Level 5 validation."""

from typing import Any, Dict, List

from .digest import verify_tree
from .resolver import BundleTree
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
                    code="BUNDLE_TYPE_MISSING",
                )
            )
            return result

        # RFC-0001 Validation rule 8: 'concern' residue is an error, with a
        # migration hint (not just the generic "unknown bundle type" warning).
        if bundle_type == "concern":
            error_msg = self.rules_loader.get_error_message(
                self.rules, "legacy_concern_type", bundle_id=bundle_id
            )
            result.add_error(
                ValidationError(error_msg, file_path=file_path, code="BUNDLE_LEGACY_CONCERN_TYPE")
            )
            return result

        if self.rules.get("bundle_types", {}).get(bundle_type, {}).get("deprecated"):
            warning_msg = self.rules_loader.get_error_message(
                self.rules, "deprecated_standards_bundle", bundle_id=bundle_id
            )
            result.add_warning(
                ValidationWarning(
                    warning_msg,
                    level="bundle",
                    file_path=file_path,
                    code="BUNDLE_STANDARDS_DEPRECATED",
                )
            )

        for ref in bundle.get("scds") or []:
            if str(ref).startswith("scd:standards:") and bundle_type != "standards":
                warning_msg = self.rules_loader.get_error_message(
                    self.rules, "deprecated_standards_scd", ref=ref
                )
                result.add_warning(
                    ValidationWarning(
                        warning_msg,
                        level="bundle",
                        file_path=file_path,
                        code="BUNDLE_STANDARDS_SCD_DEPRECATED",
                    )
                )

        # Validate XOR constraint
        self._validate_xor_constraint(bundle, bundle_id, bundle_type, result, file_path)

        # Validate bundle type-specific rules
        self._validate_bundle_type_rules(bundle, bundle_id, bundle_type, result, file_path)

        # Validate meta bundle requirements
        if bundle_type == "meta":
            self._validate_meta_bundle(bundle, bundle_id, result, file_path)

        return result

    def validate_tree(self, tree: BundleTree) -> ValidationResult:
        """Validate a resolved bundle tree: import types, resolution, cycles, meta pinning.

        Each bundle in the tree is checked against its own type's import rules, using the
        resolved type of every bundle it imports.
        """
        result = ValidationResult("bundle")
        bundle_types = self.rules.get("bundle_types", {})

        for cycle in tree.cycles:
            result.add_error(
                ValidationError(
                    self.rules_loader.get_error_message(
                        self.rules, "import_cycle", cycle=" -> ".join(cycle)
                    ),
                    file_path=str(tree.root.path),
                    code="IMPORT_CYCLE",
                )
            )

        for importer in tree.bundles:
            edges = [e for e in tree.edges if e.importer is importer]
            type_rules = bundle_types.get(importer.type or "", {})
            path = str(importer.path)
            fmt = dict(bundle_id=importer.id, bundle_type=(importer.type or "unknown").capitalize())
            counts: Dict[str, int] = {}

            for edge in edges:
                if edge.target is None:
                    result.add_error(
                        ValidationError(
                            self.rules_loader.get_error_message(
                                self.rules, "unresolved_import", ref=edge.ref, **fmt
                            ),
                            file_path=path,
                            code="IMPORT_UNRESOLVED",
                        )
                    )
                    continue
                if edge.version_mismatch:
                    result.add_warning(
                        ValidationWarning(
                            self.rules_loader.get_error_message(
                                self.rules,
                                "import_version_mismatch",
                                ref=edge.ref,
                                version=edge.target.version,
                                **fmt,
                            ),
                            level="bundle",
                            file_path=path,
                            code="IMPORT_VERSION_MISMATCH",
                        )
                    )
                import_type = edge.target.type or "unknown"
                counts[import_type] = counts.get(import_type, 0) + 1
                if import_type in type_rules.get("forbidden_import_types", []):
                    result.add_error(
                        ValidationError(
                            self.rules_loader.get_error_message(
                                self.rules,
                                "forbidden_import_type",
                                ref=edge.ref,
                                import_type=import_type,
                                **fmt,
                            ),
                            file_path=path,
                            code="IMPORT_TYPE_FORBIDDEN",
                        )
                    )
                elif (
                    "allowed_import_types" in type_rules
                    and import_type not in type_rules["allowed_import_types"]
                ):
                    result.add_error(
                        ValidationError(
                            self.rules_loader.get_error_message(
                                self.rules,
                                "import_type_not_allowed",
                                ref=edge.ref,
                                import_type=import_type,
                                allowed=", ".join(type_rules["allowed_import_types"]),
                                **fmt,
                            ),
                            file_path=path,
                            code="IMPORT_TYPE_NOT_ALLOWED",
                        )
                    )
                if import_type == "meta" and ":" not in edge.ref[len("bundle:") :]:
                    result.add_warning(
                        ValidationWarning(
                            self.rules_loader.get_error_message(
                                self.rules, "meta_import_unpinned", ref=edge.ref, **fmt
                            ),
                            level="bundle",
                            file_path=path,
                            code="IMPORT_META_UNPINNED",
                        )
                    )

            for import_type, limit in type_rules.get("max_imports_of_type", {}).items():
                if counts.get(import_type, 0) > limit:
                    result.add_error(
                        ValidationError(
                            self.rules_loader.get_error_message(
                                self.rules,
                                "too_many_imports_of_type",
                                import_type=import_type,
                                count=counts[import_type],
                                max=limit,
                                **fmt,
                            ),
                            file_path=path,
                            code="IMPORT_TYPE_LIMIT_EXCEEDED",
                        )
                    )

            # Only judge missing types when every import resolved; otherwise the
            # unresolved-import error already explains the gap.
            if importer is tree.root and all(e.target is not None for e in edges):
                for import_type in type_rules.get("expected_import_types", []):
                    if counts.get(import_type, 0) == 0:
                        result.add_warning(
                            ValidationWarning(
                                self.rules_loader.get_error_message(
                                    self.rules,
                                    "missing_expected_import_type",
                                    import_type=import_type,
                                    **fmt,
                                ),
                                level="bundle",
                                file_path=path,
                                code="IMPORT_EXPECTED_TYPE_MISSING",
                            )
                        )

        # Unresolved SCDs stay warnings: an ontology template may list SCD slots that
        # the adopting organization has not written yet. Compilation rejects them.
        for bundle_id, ref in tree.unresolved_scds:
            result.add_warning(
                ValidationWarning(
                    self.rules_loader.get_error_message(
                        self.rules, "unresolved_scd", ref=ref, bundle_id=bundle_id
                    ),
                    level="bundle",
                    file_path=str(tree.root.path),
                    code="BUNDLE_SCD_UNRESOLVED",
                )
            )

        return result

    def validate_digests(self, tree: BundleTree) -> ValidationResult:
        """Check every versioned bundle in the tree against the content digest in its version
        manifest (spec/0.7/bundle-format.md §7.6). A mismatch is an error in every mode."""
        result = ValidationResult("bundle")
        for check in verify_tree(tree):
            fmt = dict(
                bundle_id=check.bundle.id, version=check.bundle.version, manifest=check.manifest
            )
            path = str(check.bundle.path)
            if check.status == "mismatch":
                changes = ", ".join(check.changes) or "unknown (no content_inputs recorded)"
                result.add_error(
                    ValidationError(
                        self.rules_loader.get_error_message(
                            self.rules, "content_digest_mismatch", changes=changes, **fmt
                        ),
                        file_path=path,
                        code="CONTENT_DIGEST_MISMATCH",
                    )
                )
            elif check.status == "unrecorded":
                result.add_warning(
                    ValidationWarning(
                        self.rules_loader.get_error_message(
                            self.rules, "content_digest_unrecorded", **fmt
                        ),
                        level="bundle",
                        file_path=path,
                        code="CONTENT_DIGEST_UNRECORDED",
                    )
                )
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
                result.add_error(
                    ValidationError(error_msg, file_path=file_path, code="BUNDLE_XOR_VIOLATION")
                )
            else:
                result.add_warning(
                    ValidationWarning(
                        error_msg,
                        level="bundle",
                        file_path=file_path,
                        code="BUNDLE_XOR_VIOLATION_WARNING",
                    )
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
                    code="BUNDLE_TYPE_UNKNOWN",
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
            result.add_error(
                ValidationError(error_msg, file_path=file_path, code="BUNDLE_TOO_FEW_ITEMS")
            )

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
            result.add_error(
                ValidationError(error_msg, file_path=file_path, code="BUNDLE_TOO_MANY_ITEMS")
            )

        # Check required (must have at least 1)
        required = constraints.get("required", False)
        if required and array_len == 0:
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "required_field_empty",
                field=field_name,
                bundle_type=bundle_type,
            )
            result.add_error(
                ValidationError(error_msg, file_path=file_path, code="BUNDLE_REQUIRED_FIELD_EMPTY")
            )

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
                        ValidationWarning(
                            error_msg,
                            level="bundle",
                            file_path=file_path,
                            code="BUNDLE_META_VERSION_INVALID",
                        )
                    )
