"""File and directory utilities"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from jinja2 import Template


def create_directory_structure(base_path: Path, project_name: str):
    """Create the SCS 0.3 project directory structure"""
    dirs = [
        "bundles/domains",     # Domain bundles (e.g., software-development)
        "bundles/concerns",    # Concern bundles (e.g., architecture, security)
        "context/project",     # Project-tier SCDs
        "docs",               # Documentation
        ".scs",                # Configuration
    ]

    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)


def render_template(template_content: str, variables: Dict[str, Any]) -> str:
    """Render a Jinja2 template with the given variables"""
    template = Template(template_content)
    return template.render(**variables)


def write_file(file_path: Path, content: str):
    """Write content to a file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy_template(template_path: Path, dest_path: Path, variables: Dict[str, Any] = None):
    """Copy a template file, optionally rendering it with variables"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if variables:
        content = render_template(content, variables)

    write_file(dest_path, content)


def get_template_path() -> Path:
    """Get the path to the templates directory"""
    return Path(__file__).parent.parent / "templates"
