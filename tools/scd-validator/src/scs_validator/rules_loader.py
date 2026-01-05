"""Rules loader module for loading validation rules from YAML configuration files."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .utils import ValidationError


class RulesLoader:
    """Loads and manages validation rules from YAML configuration files."""

    def __init__(self, rules_dir: Optional[Path] = None):
        """Initialize rules loader.

        Args:
            rules_dir: Directory containing rules files. If None, uses default location.
        """
        if rules_dir is None:
            # Default: rules/v0.3.0 relative to this module
            self.rules_dir = Path(__file__).parent.parent.parent / "rules" / "v0.3.0"
        else:
            self.rules_dir = Path(rules_dir)

        if not self.rules_dir.exists():
            raise ValidationError(f"Rules directory not found: {self.rules_dir}")

        self._rules_cache: Dict[str, Dict[str, Any]] = {}

    def load_scd_rules(self) -> Dict[str, Any]:
        """Load SCD validation rules.

        Returns:
            Dictionary containing SCD rules
        """
        return self._load_rules_file("scd-rules.yaml")

    def load_bundle_rules(self) -> Dict[str, Any]:
        """Load bundle validation rules.

        Returns:
            Dictionary containing bundle rules
        """
        return self._load_rules_file("bundle-rules.yaml")

    def load_relationship_rules(self) -> Dict[str, Any]:
        """Load relationship validation rules.

        Returns:
            Dictionary containing relationship rules
        """
        return self._load_rules_file("relationship-rules.yaml")

    def load_completeness_rules(
        self, custom_rules_path: Optional[Path] = None, project_root: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Load completeness validation rules with priority resolution.

        Priority:
        1. Explicit custom rules path (highest)
        2. Project-specific .scs/completeness-rules.yaml
        3. Default rules (fallback)

        Args:
            custom_rules_path: Optional explicit path to custom rules
            project_root: Optional project root for finding .scs/ directory

        Returns:
            Dictionary containing completeness rules
        """
        # 1. Explicit custom rules path
        if custom_rules_path and custom_rules_path.exists():
            try:
                return self._load_yaml_file(custom_rules_path)
            except Exception as e:
                raise ValidationError(
                    f"Failed to load custom completeness rules from {custom_rules_path}: {e}"
                )

        # 2. Project-specific rules
        if project_root:
            project_rules = project_root / ".scs" / "completeness-rules.yaml"
            if project_rules.exists():
                try:
                    return self._load_yaml_file(project_rules)
                except Exception as e:
                    raise ValidationError(
                        f"Failed to load project completeness rules from {project_rules}: {e}"
                    )

        # 3. Default rules
        return self._load_rules_file("completeness-rules.yaml")

    def _load_rules_file(self, filename: str) -> Dict[str, Any]:
        """Load a rules file from the rules directory (with caching).

        Args:
            filename: Name of the rules file

        Returns:
            Parsed rules as dictionary

        Raises:
            ValidationError: If rules file cannot be loaded
        """
        if filename in self._rules_cache:
            return self._rules_cache[filename]

        rules_path = self.rules_dir / filename
        if not rules_path.exists():
            raise ValidationError(f"Rules file not found: {rules_path}")

        try:
            rules = self._load_yaml_file(rules_path)
            self._rules_cache[filename] = rules
            return rules
        except Exception as e:
            raise ValidationError(f"Failed to load rules file {filename}: {e}")

    @staticmethod
    def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
        """Load a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML as dictionary

        Raises:
            Exception: If file cannot be loaded or parsed
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ValueError("YAML content must be a dictionary")
            return data

    @staticmethod
    def get_error_message(rules: Dict[str, Any], error_key: str, **kwargs) -> str:
        """Get a formatted error message from rules.

        Args:
            rules: Rules dictionary
            error_key: Key for the error message
            **kwargs: Template variables for formatting

        Returns:
            Formatted error message
        """
        error_messages = rules.get("error_messages", {})
        template = error_messages.get(error_key, error_key)

        try:
            return template.format(**kwargs)
        except KeyError:
            # If template variables are missing, return template as-is
            return template

    @staticmethod
    def compile_pattern(pattern: str) -> re.Pattern:
        """Compile a regex pattern from rules.

        Args:
            pattern: Regex pattern string

        Returns:
            Compiled regex pattern
        """
        return re.compile(pattern)

    @staticmethod
    def get_severity(rules: Dict[str, Any], rule_key: str, default: str = "error") -> str:
        """Get severity level for a rule.

        Args:
            rules: Rules dictionary
            rule_key: Key for the rule
            default: Default severity if not found

        Returns:
            Severity level ("error", "warning", "info", "skip")
        """
        # Navigate nested dictionaries to find severity
        keys = rule_key.split(".")
        current = rules

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default

        if isinstance(current, dict):
            return current.get("severity", default)
        return default


class RelationshipTypeValidator:
    """Helper class for validating relationship types and tier constraints."""

    def __init__(self, relationship_rules: Dict[str, Any]):
        """Initialize with relationship rules.

        Args:
            relationship_rules: Relationship rules dictionary
        """
        self.rules = relationship_rules
        self.relationship_types = relationship_rules.get("relationship_types", [])
        self._build_tier_constraint_map()

    def _build_tier_constraint_map(self) -> None:
        """Build a lookup map for tier constraints."""
        self.tier_constraints: Dict[str, List[Dict[str, Any]]] = {}

        for rel_type in self.relationship_types:
            rel_type_name = rel_type.get("type")
            if rel_type_name:
                self.tier_constraints[rel_type_name] = rel_type.get("allowed_tiers", [])

    def is_valid_type(self, relationship_type: str) -> bool:
        """Check if a relationship type is valid.

        Args:
            relationship_type: Relationship type to check

        Returns:
            True if valid, False otherwise
        """
        valid_types = [rt.get("type") for rt in self.relationship_types]
        return relationship_type in valid_types

    def is_valid_tier_combination(
        self, relationship_type: str, source_tier: str, target_tier: str
    ) -> bool:
        """Check if a tier combination is valid for a relationship type.

        Args:
            relationship_type: Relationship type
            source_tier: Source SCD tier
            target_tier: Target SCD tier

        Returns:
            True if valid, False otherwise
        """
        if relationship_type not in self.tier_constraints:
            return False

        allowed = self.tier_constraints[relationship_type]

        for constraint in allowed:
            from_tier = constraint.get("from")
            to_tiers = constraint.get("to", [])

            if from_tier == source_tier and target_tier in to_tiers:
                return True

        return False

    def get_allowed_combinations(self, relationship_type: str) -> List[str]:
        """Get allowed tier combinations for a relationship type.

        Args:
            relationship_type: Relationship type

        Returns:
            List of allowed combinations as strings (e.g., "project→standards")
        """
        if relationship_type not in self.tier_constraints:
            return []

        allowed = self.tier_constraints[relationship_type]
        combinations = []

        for constraint in allowed:
            from_tier = constraint.get("from")
            to_tiers = constraint.get("to", [])

            for to_tier in to_tiers:
                combinations.append(f"{from_tier}→{to_tier}")

        return combinations
