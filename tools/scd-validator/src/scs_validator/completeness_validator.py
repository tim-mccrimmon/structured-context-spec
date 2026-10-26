"""Completeness validation module for Level 6 validation."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .resolver import BundleTree
from .rules_loader import RulesLoader
from .utils import ValidationError, ValidationResult, ValidationWarning


class CompletenessValidator:
    """Validator for project completeness and compliance (Level 6)."""

    def __init__(self, rules_loader: RulesLoader, custom_rules_path: Optional[Path] = None):
        """Initialize completeness validator.

        Args:
            rules_loader: Rules loader instance
            custom_rules_path: Optional path to custom completeness rules
        """
        self.rules_loader = rules_loader
        self.custom_rules_path = custom_rules_path

    def validate_completeness(
        self,
        bundle: Dict[str, Any],
        all_scds: List[Dict[str, Any]],
        file_path: str | None = None,
        project_root: Optional[Path] = None,
        tree: Optional[BundleTree] = None,
    ) -> ValidationResult:
        """Validate Domain or Project bundle completeness and compliance.

        This implements Level 6 validation:
        - Required bundles present
        - Required domains present
        - Minimum SCDs per domain
        - Recommended SCDs (warnings)
        - Stub detection

        Args:
            bundle: Domain or Project bundle data
            all_scds: List of all SCDs in the resolved bundle tree
            file_path: Optional file path for error messages
            project_root: Optional project root for finding custom rules
            tree: Resolved bundle tree, used to count imports by their actual type

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult("completeness")

        # Load completeness rules (with priority resolution)
        try:
            rules = self.rules_loader.load_completeness_rules(self.custom_rules_path, project_root)
        except ValidationError as e:
            result.add_error(e)
            return result

        # Check if completeness validation is enabled (opt-in)
        # Default is False - completeness validation is opt-in
        if not rules.get("enabled", False):
            return result  # Skip all completeness checks

        # Check rule severity
        severity = rules.get("severity", "warning")

        # Validate required bundles
        self._validate_required_bundles(bundle, rules, severity, result, file_path, tree)

        # Validate required domains
        domain_bundles = self._extract_domain_bundles(bundle, tree)
        self._validate_required_domains(
            domain_bundles, all_scds, rules, severity, result, file_path
        )

        # Validate recommended SCDs
        self._validate_recommended_scds(all_scds, rules, result, file_path)

        # Stub detection
        self._detect_stubs(all_scds, rules, result, file_path)

        return result

    def _validate_required_bundles(
        self,
        bundle: Dict[str, Any],
        rules: Dict[str, Any],
        severity: str,
        result: ValidationResult,
        file_path: str | None,
        tree: Optional[BundleTree] = None,
    ) -> None:
        """Validate required bundle types are imported.

        Args:
            bundle: Domain or Project bundle data
            rules: Completeness rules
            severity: Rule severity level
            result: Validation result to update
            file_path: Optional file path
            tree: Resolved bundle tree; without it, imports are typed by name only
        """
        required_bundles = rules.get("required_bundles", [])
        bundle_type_counts: Dict[str, int] = {}
        for import_type in self._direct_import_types(bundle, tree):
            bundle_type_counts[import_type] = bundle_type_counts.get(import_type, 0) + 1

        # Check requirements
        for req in required_bundles:
            req_type = req.get("type")
            req_count = req.get("count")
            req_min = req.get("min")
            message = req.get("message", f"Required bundle type '{req_type}' missing")

            actual_count = bundle_type_counts.get(req_type, 0)

            if req_count is not None:
                # Exact count required
                if actual_count != req_count:
                    self._add_result(
                        severity,
                        message,
                        result,
                        file_path,
                        error_code="COMPLETENESS_REQUIRED_BUNDLE_MISSING",
                        warning_code="COMPLETENESS_REQUIRED_BUNDLE_MISSING_WARNING",
                    )
            elif req_min is not None:
                # Minimum count required
                if actual_count < req_min:
                    self._add_result(
                        severity,
                        message,
                        result,
                        file_path,
                        error_code="COMPLETENESS_REQUIRED_BUNDLE_MISSING",
                        warning_code="COMPLETENESS_REQUIRED_BUNDLE_MISSING_WARNING",
                    )

    @staticmethod
    def _direct_import_types(bundle: Dict[str, Any], tree: Optional[BundleTree]) -> List[str]:
        """Types of the bundle's direct imports: resolved types when a tree is available,
        otherwise a name-based guess (bundle:meta is meta, anything else is a concept)."""
        if tree is not None:
            return [e.target.type or "unknown" for e in tree.direct_imports() if e.target]
        types = []
        for import_ref in bundle.get("imports", []):
            parts = str(import_ref).split(":")
            types.append("meta" if len(parts) >= 2 and parts[1] == "meta" else "concept")
        return types

    def _extract_domain_bundles(
        self, bundle: Dict[str, Any], tree: Optional[BundleTree] = None
    ) -> Set[str]:
        """Names of the non-meta bundles this bundle imports (without version).

        Args:
            bundle: Domain or Project bundle data
            tree: Resolved bundle tree, used to exclude imports by their actual type

        Returns:
            Set of imported bundle names
        """
        if tree is not None:
            return {
                e.target.id.split(":", 1)[1]
                for e in tree.direct_imports()
                if e.target and e.target.type not in ("meta", "standards")
            }
        names = set()
        for import_ref in bundle.get("imports", []):
            parts = str(import_ref).split(":")
            if len(parts) >= 2 and parts[0] == "bundle" and parts[1] not in ("meta", "standards"):
                names.add(parts[1])
        return names

    def _validate_required_domains(
        self,
        domain_bundles: Set[str],
        all_scds: List[Dict[str, Any]],
        rules: Dict[str, Any],
        severity: str,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate required domains are present with minimum SCDs.

        Args:
            domain_bundles: Set of domain bundle IDs
            all_scds: List of all SCDs
            rules: Completeness rules
            severity: Rule severity level
            result: Validation result to update
            file_path: Optional file path
        """
        required_domains = rules.get("required_domains", [])

        # Group SCDs by domain (from SCD domain field)
        domain_scds: Dict[str, List[Dict[str, Any]]] = {}
        for scd in all_scds:
            # Use the domain field from the SCD itself
            domain = scd.get("domain")
            if domain:
                if domain not in domain_scds:
                    domain_scds[domain] = []
                domain_scds[domain].append(scd)

        # Check each required domain
        for domain_req in required_domains:
            domain_id = domain_req.get("id")
            domain_name = domain_req.get("name", domain_id)
            min_scds = domain_req.get("minimum_scds", 1)

            # Check if domain bundle is imported
            if domain_id not in domain_bundles:
                error_msg = self.rules_loader.get_error_message(
                    rules, "missing_domain", domain=domain_name
                )
                self._add_result(
                    severity,
                    error_msg,
                    result,
                    file_path,
                    error_code="COMPLETENESS_DOMAIN_MISSING",
                    warning_code="COMPLETENESS_DOMAIN_MISSING_WARNING",
                )
                continue

            # Check minimum SCDs in domain
            actual_scds = len(domain_scds.get(domain_id, []))
            if actual_scds < min_scds:
                error_msg = self.rules_loader.get_error_message(
                    rules,
                    "insufficient_scds_in_domain",
                    domain=domain_name,
                    actual=actual_scds,
                    required=min_scds,
                )
                self._add_result(
                    severity,
                    error_msg,
                    result,
                    file_path,
                    error_code="COMPLETENESS_DOMAIN_TOO_FEW_SCDS",
                    warning_code="COMPLETENESS_DOMAIN_TOO_FEW_SCDS_WARNING",
                )

    def _validate_recommended_scds(
        self,
        all_scds: List[Dict[str, Any]],
        rules: Dict[str, Any],
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate recommended SCDs are present (warnings).

        Args:
            all_scds: List of all SCDs
            rules: Completeness rules
            result: Validation result to update
            file_path: Optional file path
        """
        required_domains = rules.get("required_domains", [])

        # Build set of all SCD IDs
        scd_ids = {scd.get("id", "") for scd in all_scds}

        for domain_req in required_domains:
            domain_id = domain_req.get("id")
            recommended_scds = domain_req.get("recommended_scds", [])

            for rec in recommended_scds:
                pattern = rec.get("pattern")
                name = rec.get("name")
                rec_severity = rec.get("severity", "warning")

                if not pattern:
                    continue

                # Check if any SCD matches the pattern
                matched = False
                for scd_id in scd_ids:
                    # Simple pattern matching (contains keywords)
                    if self._matches_pattern(scd_id, pattern):
                        matched = True
                        break

                if not matched:
                    warning_msg = self.rules_loader.get_error_message(
                        rules,
                        "missing_recommended_scd",
                        domain=domain_id,
                        pattern=pattern,
                        name=name,
                    )
                    if rec_severity == "warning":
                        result.add_warning(
                            ValidationWarning(
                                warning_msg,
                                level="completeness",
                                file_path=file_path,
                                code="COMPLETENESS_RECOMMENDED_SCD_MISSING",
                            )
                        )

    def _matches_pattern(self, scd_id: str, pattern: str) -> bool:
        """Check if SCD ID matches a pattern.

        Args:
            scd_id: SCD ID to check
            pattern: Pattern string (keywords separated by |)

        Returns:
            True if matches, False otherwise
        """
        # Convert pattern to regex
        # Pattern like "auth|authn|authz" matches SCDs with those keywords
        keywords = pattern.split("|")
        for keyword in keywords:
            if keyword.lower() in scd_id.lower():
                return True
        return False

    def _detect_stubs(
        self,
        all_scds: List[Dict[str, Any]],
        rules: Dict[str, Any],
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Detect stub/placeholder SCDs.

        Args:
            all_scds: List of all SCDs
            rules: Completeness rules
            result: Validation result to update
            file_path: Optional file path
        """
        stub_config = rules.get("stub_detection", {})
        if not stub_config.get("enabled", True):
            return

        indicators_config = stub_config.get("indicators", [])
        threshold = stub_config.get("stub_threshold", 2)

        for scd in all_scds:
            scd_id = scd.get("id", "unknown")
            version = scd.get("version", "")

            # Skip DRAFT versions (stubs expected)
            if version == "DRAFT":
                continue

            # Count stub indicators
            stub_indicators = []

            for indicator in indicators_config:
                check = indicator.get("check")
                message = indicator.get("message")

                if check == "short_description":
                    threshold_chars = indicator.get("threshold", 50)
                    description = scd.get("description", "")
                    if len(description.strip()) < threshold_chars:
                        stub_indicators.append(message)

                elif check == "minimal_content":
                    threshold_fields = indicator.get("threshold", 2)
                    content = scd.get("content", {})
                    if isinstance(content, dict) and len(content) < threshold_fields:
                        stub_indicators.append(message)

                elif check == "generic_title":
                    patterns = indicator.get("patterns", [])
                    title = scd.get("title", "").lower()
                    for pattern in patterns:
                        if pattern.lower() in title:
                            stub_indicators.append(message)
                            break

                elif check == "no_relationships":
                    relationships = scd.get("relationships", [])
                    if not relationships:
                        stub_indicators.append(message)

            # If enough indicators, warn about stub
            if len(stub_indicators) >= threshold:
                warning_msg = stub_config.get("warning_message", "SCD appears to be a stub")
                warning_msg = warning_msg.format(
                    scd_id=scd_id, indicators="; ".join(stub_indicators)
                )
                result.add_warning(
                    ValidationWarning(
                        warning_msg,
                        level="completeness",
                        scd_id=scd_id,
                        file_path=file_path,
                        code="COMPLETENESS_STUB_SCD",
                    )
                )

    def _add_result(
        self,
        severity: str,
        message: str,
        result: ValidationResult,
        file_path: str | None,
        error_code: str,
        warning_code: str,
    ) -> None:
        """Add error or warning based on severity.

        Args:
            severity: Severity level
            message: Message text
            result: Validation result to update
            file_path: Optional file path
            error_code: Diagnostic code when emitted as an error
            warning_code: Diagnostic code when emitted as a warning
        """
        if severity == "error":
            result.add_error(ValidationError(message, file_path=file_path, code=error_code))
        else:
            result.add_warning(
                ValidationWarning(
                    message, level="completeness", file_path=file_path, code=warning_code
                )
            )
