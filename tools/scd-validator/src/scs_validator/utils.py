"""Utility functions for SCS Validator."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_DIR_ENV_VAR = "SCS_SCHEMA_DIR"


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


def find_domain_manifest_schema(schema_dir: Path) -> Path:
    """Find the domain manifest schema file.

    Args:
        schema_dir: Root schema directory

    Returns:
        Path to domain manifest schema file

    Raises:
        FileNotFoundError: If schema file not found
    """
    schema_file = schema_dir / "domain" / "domain-manifest-schema.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"Domain manifest schema file not found: {schema_file}")
    return schema_file


def find_checkpoint_record_schema(schema_dir: Path) -> Path:
    """Find the checkpoint record schema file.

    Args:
        schema_dir: Root schema directory

    Returns:
        Path to checkpoint record schema file

    Raises:
        FileNotFoundError: If schema file not found
    """
    schema_file = schema_dir / "checkpoint" / "checkpoint-record-schema.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"Checkpoint record schema file not found: {schema_file}")
    return schema_file


def _looks_like_schema_dir(path: Path) -> bool:
    """A directory is the SCS schema dir if it has the ``bundles/`` and ``scd/`` schema folders."""
    return (path / "bundles").is_dir() and (path / "scd").is_dir()


def packaged_schema_dir() -> Path:
    """The copy of the JSON Schemas vendored inside this package (see scripts/sync_schemas.py)."""
    return Path(__file__).resolve().parent / "schemas"


def _checkout_schema_dir(searched: List[Path]) -> Optional[Path]:
    """The ``schema/`` directory of the source checkout this package is installed from, if any."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "schema"
        if candidate in searched:
            continue
        searched.append(candidate)
        if _looks_like_schema_dir(candidate):
            return candidate
    return None


def resolve_schema_dir(explicit: Optional[str] = None) -> Tuple[Optional[Path], List[Path]]:
    """Locate the SCS JSON Schema directory.

    Lookup order (first match wins):

    1. ``explicit`` (the ``--schema-dir`` option), used as given
    2. the ``SCS_SCHEMA_DIR`` environment variable, used as given
    3. a ``schema/`` directory in the current directory or any parent
    4. the ``schema/`` directory of the source checkout this package is installed from
    5. the copy of the schemas packaged inside ``scs_validator`` (what an installed wheel uses)

    Candidates found by search (3, 4) must look like the SCS schema directory, so an unrelated
    ``schema/`` folder in a user's project is not picked up by mistake. In a source checkout the
    repo-root ``schema/`` is the source of truth and wins over the packaged copy.

    Returns ``(path, searched)``: ``path`` is ``None`` when nothing was found, and ``searched``
    lists every location that was considered, for the error message.
    """
    searched: List[Path] = []

    if explicit:
        return Path(explicit), [Path(explicit)]

    env_value = os.environ.get(SCHEMA_DIR_ENV_VAR)
    if env_value:
        return Path(env_value), [Path(env_value)]

    here = Path.cwd().resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "schema"
        searched.append(candidate)
        if _looks_like_schema_dir(candidate):
            return candidate, searched

    checkout = _checkout_schema_dir(searched)
    if checkout is not None:
        return checkout, searched

    packaged = packaged_schema_dir()
    searched.append(packaged)
    if _looks_like_schema_dir(packaged):
        return packaged, searched

    return None, searched
