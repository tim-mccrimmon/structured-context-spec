"""Relationship validation module for Level 4 validation."""

from typing import Any, Dict, List, Set

from .rules_loader import RelationshipTypeValidator, RulesLoader
from .utils import ValidationError, ValidationResult, ValidationWarning, get_tier_from_id


class RelationshipValidator:
    """Validator for SCD relationships (Level 4)."""

    def __init__(self, rules_loader: RulesLoader):
        """Initialize relationship validator.

        Args:
            rules_loader: Rules loader instance
        """
        self.rules_loader = rules_loader
        self.rules = rules_loader.load_relationship_rules()
        self.type_validator = RelationshipTypeValidator(self.rules)

    def validate_relationships(
        self,
        scds: List[Dict[str, Any]],
        bundle_type: str = "project",
        file_path: str | None = None,
    ) -> ValidationResult:
        """Validate relationships in a collection of SCDs.

        This implements Level 4 validation:
        - Relationship type validity
        - Tier constraint validation
        - Target existence checks
        - Circular dependency detection (for depends-on)

        Args:
            scds: List of SCD dictionaries
            bundle_type: Type of bundle being validated
            file_path: Optional file path for error messages

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult("relationships")

        # Build SCD lookup
        scd_lookup = {scd.get("id"): scd for scd in scds if scd.get("id")}

        # Track validation mode (standalone vs complete)
        is_complete_project = bundle_type == "project"

        # Validate each SCD's relationships
        for scd in scds:
            scd_id = scd.get("id")
            if not scd_id:
                continue

            relationships = scd.get("relationships", [])
            if not relationships:
                continue

            for rel in relationships:
                self._validate_relationship(
                    scd_id, rel, scd_lookup, is_complete_project, result, file_path
                )

        # Detect circular dependencies
        self._detect_circular_dependencies(scds, result, file_path)

        return result

    def _validate_relationship(
        self,
        source_id: str,
        relationship: Dict[str, Any],
        scd_lookup: Dict[str, Dict[str, Any]],
        is_complete_project: bool,
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Validate a single relationship.

        Args:
            source_id: Source SCD ID
            relationship: Relationship dictionary
            scd_lookup: Lookup of all SCDs by ID
            is_complete_project: Whether this is a complete project bundle
            result: Validation result to update
            file_path: Optional file path
        """
        rel_type = relationship.get("type")
        target_id = relationship.get("target")

        if not rel_type:
            result.add_error(
                ValidationError(
                    f"Relationship missing 'type' field in SCD '{source_id}'",
                    scd_id=source_id,
                    file_path=file_path,
                )
            )
            return

        if not target_id:
            result.add_error(
                ValidationError(
                    f"Relationship missing 'target' field in SCD '{source_id}'",
                    scd_id=source_id,
                    file_path=file_path,
                )
            )
            return

        # Validate relationship type
        if not self.type_validator.is_valid_type(rel_type):
            error_msg = self.rules_loader.get_error_message(
                self.rules,
                "invalid_type",
                type=rel_type,
                allowed_types=", ".join(
                    [rt.get("type") for rt in self.rules.get("relationship_types", [])]
                ),
            )
            result.add_error(
                ValidationError(error_msg, scd_id=source_id, file_path=file_path)
            )
            return

        # Validate no self-reference
        if source_id == target_id:
            error_msg = self.rules_loader.get_error_message(
                self.rules, "self_reference", scd_id=source_id, type=rel_type
            )
            result.add_error(
                ValidationError(error_msg, scd_id=source_id, file_path=file_path)
            )
            return

        # Validate target exists
        target_exists = target_id in scd_lookup
        if not target_exists:
            # Different severity based on bundle type
            if is_complete_project:
                error_msg = self.rules_loader.get_error_message(
                    self.rules,
                    "target_not_found",
                    target=target_id,
                    source=source_id,
                    type=rel_type,
                )
                result.add_error(
                    ValidationError(error_msg, scd_id=source_id, file_path=file_path)
                )
            else:
                # Warning for standalone domain bundles
                warning_msg = f"Relationship target '{target_id}' not found in this bundle. May exist in another bundle."
                result.add_warning(
                    ValidationWarning(
                        warning_msg, level="relationships", scd_id=source_id, file_path=file_path
                    )
                )
            return

        # Validate tier constraints
        source_tier = get_tier_from_id(source_id)
        target_tier = get_tier_from_id(target_id)

        if source_tier and target_tier:
            if not self.type_validator.is_valid_tier_combination(
                rel_type, source_tier, target_tier
            ):
                allowed = self.type_validator.get_allowed_combinations(rel_type)
                error_msg = self.rules_loader.get_error_message(
                    self.rules,
                    "tier_constraint_violation",
                    type=rel_type,
                    from_tier=source_tier,
                    to_tier=target_tier,
                    allowed=", ".join(allowed),
                )
                result.add_error(
                    ValidationError(error_msg, scd_id=source_id, file_path=file_path)
                )

    def _detect_circular_dependencies(
        self,
        scds: List[Dict[str, Any]],
        result: ValidationResult,
        file_path: str | None,
    ) -> None:
        """Detect circular dependencies in depends-on relationships.

        Args:
            scds: List of SCD dictionaries
            result: Validation result to update
            file_path: Optional file path
        """
        circular_detection = self.rules.get("circular_dependency_detection", {})
        if not circular_detection.get("enabled", True):
            return

        # Build dependency graph for depends-on relationships
        graph: Dict[str, List[str]] = {}
        for scd in scds:
            scd_id = scd.get("id")
            if not scd_id:
                continue

            dependencies = []
            relationships = scd.get("relationships", [])
            for rel in relationships:
                if rel.get("type") == "depends-on":
                    target = rel.get("target")
                    if target:
                        dependencies.append(target)

            if dependencies:
                graph[scd_id] = dependencies

        # Detect cycles using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node: str, path: List[str]) -> bool:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Check all neighbors
            neighbors = graph.get(node, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    if has_cycle(neighbor, path[:]):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycle_str = " → ".join(cycle)

                    error_msg = self.rules_loader.get_error_message(
                        self.rules, "circular_dependency", cycle=cycle_str
                    )
                    result.add_warning(
                        ValidationWarning(
                            error_msg, level="relationships", file_path=file_path
                        )
                    )
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        # Check each connected component
        for node in graph:
            if node not in visited:
                has_cycle(node, [])
