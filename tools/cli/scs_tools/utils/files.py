"""File and directory utilities"""

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment


def yaml_dq(value: str) -> str:
    """Render a string as a double-quoted YAML scalar, safely escaped.

    A YAML double-quoted scalar's escaping rules are a superset of JSON's, so json.dumps
    produces a valid, correctly escaped result for any string - including embedded double
    quotes (e.g. concept descriptions quoting a term) that would otherwise break templates
    doing `"{{ value }}"` unescaped. Includes the surrounding quotes; use as
    `{{ value | yaml_dq }}`, not `"{{ value }}"`.
    """
    return json.dumps(value)


_JINJA_ENV = Environment()
_JINJA_ENV.filters["yaml_dq"] = yaml_dq


def create_directory_structure(base_path: Path, project_name: str):
    """Create the SCS 0.5.0 project directory structure"""
    dirs = [
        "bundles/domains",  # Domain bundles (e.g., software-development)
        "bundles/concepts",  # Concept bundles (e.g., architecture, security)
        "domain",  # Domain Ontology manifest
        "context/project",  # Project-tier SCDs
        "docs",  # Documentation
        ".scs",  # Configuration
    ]

    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)


def render_template(template_content: str, variables: Dict[str, Any]) -> str:
    """Render a Jinja2 template with the given variables. The `yaml_dq` filter is available
    for values (e.g. free-text descriptions) that need safe YAML double-quoted escaping."""
    template = _JINJA_ENV.from_string(template_content)
    return template.render(**variables)


def write_file(file_path: Path, content: str):
    """Write content to a file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def copy_template(template_path: Path, dest_path: Path, variables: Dict[str, Any] = None):
    """Copy a template file, optionally rendering it with variables"""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    if variables:
        content = render_template(content, variables)

    write_file(dest_path, content)


def get_template_path() -> Path:
    """Get the path to the templates directory"""
    return Path(__file__).parent.parent / "templates"
