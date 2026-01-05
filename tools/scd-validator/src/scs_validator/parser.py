"""Parser module for loading SCD and bundle files."""

import json
from pathlib import Path
from typing import Any, Dict

import yaml

from .utils import ValidationError


class Parser:
    """Parser for SCD and bundle files."""

    @staticmethod
    def load_scd(file_path: Path) -> Dict[str, Any]:
        """Load an SCD file (YAML or JSON).

        Args:
            file_path: Path to the SCD file

        Returns:
            Parsed SCD as dictionary

        Raises:
            ValidationError: If file cannot be loaded or parsed
        """
        if not file_path.exists():
            raise ValidationError(
                f"File not found: {file_path}", file_path=str(file_path)
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try to parse based on file extension
            if file_path.suffix in [".yaml", ".yml"]:
                return Parser._parse_yaml(content, file_path)
            elif file_path.suffix == ".json":
                return Parser._parse_json(content, file_path)
            else:
                # Try YAML first, then JSON
                try:
                    return Parser._parse_yaml(content, file_path)
                except Exception:
                    return Parser._parse_json(content, file_path)

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Failed to load file: {e}",
                file_path=str(file_path)
            )

    @staticmethod
    def load_bundle(file_path: Path) -> Dict[str, Any]:
        """Load a bundle file (YAML or JSON).

        Args:
            file_path: Path to the bundle file

        Returns:
            Parsed bundle as dictionary

        Raises:
            ValidationError: If file cannot be loaded or parsed
        """
        # Bundle loading is the same as SCD loading
        return Parser.load_scd(file_path)

    @staticmethod
    def _parse_yaml(content: str, file_path: Path) -> Dict[str, Any]:
        """Parse YAML content.

        Args:
            content: YAML content as string
            file_path: Path to file (for error messages)

        Returns:
            Parsed content as dictionary

        Raises:
            ValidationError: If YAML is invalid
        """
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                raise ValidationError(
                    "YAML content must be an object/dictionary",
                    file_path=str(file_path)
                )
            return data
        except yaml.YAMLError as e:
            # Extract line and column information if available
            error_msg = f"Invalid YAML syntax: {e}"
            if hasattr(e, "problem_mark"):
                mark = e.problem_mark
                error_msg = f"Invalid YAML syntax at line {mark.line + 1}, column {mark.column + 1}: {e.problem}"
            raise ValidationError(error_msg, file_path=str(file_path))

    @staticmethod
    def _parse_json(content: str, file_path: Path) -> Dict[str, Any]:
        """Parse JSON content.

        Args:
            content: JSON content as string
            file_path: Path to file (for error messages)

        Returns:
            Parsed content as dictionary

        Raises:
            ValidationError: If JSON is invalid
        """
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValidationError(
                    "JSON content must be an object",
                    file_path=str(file_path)
                )
            return data
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON syntax at line {e.lineno}, column {e.colno}: {e.msg}",
                file_path=str(file_path)
            )

    @staticmethod
    def load_schema(schema_path: Path) -> Dict[str, Any]:
        """Load a JSON schema file.

        Args:
            schema_path: Path to the schema file

        Returns:
            Parsed schema as dictionary

        Raises:
            ValidationError: If schema cannot be loaded
        """
        if not schema_path.exists():
            raise ValidationError(f"Schema file not found: {schema_path}")

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON schema at line {e.lineno}, column {e.colno}: {e.msg}",
                file_path=str(schema_path)
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to load schema: {e}",
                file_path=str(schema_path)
            )
