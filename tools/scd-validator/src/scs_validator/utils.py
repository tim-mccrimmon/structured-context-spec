"""Utility functions for SCS Validator."""

from pathlib import Path
from typing import Any, Dict


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, scd_id: str | None = None, file_path: str | None = None):
        self.message = message
        self.scd_id = scd_id
        self.file_path = file_path
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format the error message with context."""
        parts = []
        if self.file_path:
            parts.append(f"{self.file_path}")
        if self.scd_id:
            parts.append(f"({self.scd_id})")
        parts.append(f"- {self.message}")
        return " ".join(parts)


class ValidationWarning:
    """Represents a validation warning."""

    def __init__(
        self, message: str, level: str, scd_id: str | None = None, file_path: str | None = None
    ):
        self.message = message
        self.level = level
        self.scd_id = scd_id
        self.file_path = file_path

    def __str__(self) -> str:
        """String representation of warning."""
        parts = []
        if self.file_path:
            parts.append(f"{self.file_path}")
        if self.scd_id:
            parts.append(f"({self.scd_id})")
        parts.append(f"- {self.message}")
        return " ".join(parts)


class ValidationResult:
    """Container for validation results."""

    def __init__(self, level_name: str):
        self.level_name = level_name
        self.passed = True
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationWarning] = []
        self.details: Dict[str, Any] = {}

    def add_error(self, error: ValidationError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.passed = False

    def add_warning(self, warning: ValidationWarning) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    @property
    def error_count(self) -> int:
        """Get the number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Get the number of warnings."""
        return len(self.warnings)


def get_tier_from_id(scd_id: str) -> str | None:
    """Extract tier from SCD ID.

    Args:
        scd_id: SCD ID in format scd:<tier>:<name>

    Returns:
        Tier name (meta, project, standards) or None if invalid
    """
    parts = scd_id.split(":")
    if len(parts) >= 2 and parts[0] == "scd":
        tier = parts[1]
        if tier in ["meta", "project", "standards"]:
            return tier
    return None


def find_schema_file(tier: str, schema_dir: Path) -> Path:
    """Find the schema file for a given tier.

    Args:
        tier: Tier name (meta, project, standards)
        schema_dir: Root schema directory

    Returns:
        Path to schema file

    Raises:
        FileNotFoundError: If schema file not found
    """
    schema_file = schema_dir / "scd" / f"{tier}-scd-template.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    return schema_file


def find_bundle_schema(schema_dir: Path) -> Path:
    """Find the bundle schema file.

    Args:
        schema_dir: Root schema directory

    Returns:
        Path to bundle schema file

    Raises:
        FileNotFoundError: If schema file not found
    """
    schema_file = schema_dir / "bundles" / "scd-bundle-schema.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"Bundle schema file not found: {schema_file}")
    return schema_file
