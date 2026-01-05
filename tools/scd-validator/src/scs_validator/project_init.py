"""Project initialization logic for SCS CLI."""

import shutil
from pathlib import Path
from typing import Optional

import yaml

from .utils import ValidationError


class ProjectInitializer:
    """Handles initialization of new SCS projects."""

    def __init__(self, scs_version: str = "0.2.0"):
        """Initialize the project initializer.

        Args:
            scs_version: SCS version to use for the project
        """
        self.scs_version = scs_version

    def create_project(
        self,
        project_name: str,
        destination: Optional[Path] = None,
        template_source: Optional[Path] = None,
    ) -> Path:
        """Create a new SCS project.

        Args:
            project_name: Name of the project
            destination: Parent directory for the project (defaults to current directory)
            template_source: Path to template source directory (defaults to package location)

        Returns:
            Path to created project directory

        Raises:
            ValidationError: If project creation fails
        """
        # Determine paths
        dest_parent = destination or Path.cwd()
        project_path = dest_parent / project_name

        if project_path.exists():
            raise ValidationError(f"Project directory already exists: {project_path}")

        # Find template source
        if template_source is None:
            # Default: look for docs/domain-docs relative to package
            package_root = Path(__file__).parent.parent.parent.parent.parent
            template_source = package_root / "docs" / "domain-docs"

        if not template_source.exists():
            raise ValidationError(f"Template source not found: {template_source}")

        # Create project structure
        try:
            self._create_directory_structure(project_path)
            self._copy_templates(template_source, project_path)
            self._create_config(project_path, project_name)
            self._copy_domain_meta(project_path)
            self._create_project_bundle(project_path, project_name)
        except Exception as e:
            # Clean up on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise ValidationError(f"Failed to create project: {e}") from e

        return project_path

    def _create_directory_structure(self, project_path: Path) -> None:
        """Create the project directory structure."""
        directories = [
            project_path / "context" / "meta",
            project_path / "context" / "domains",
            project_path / "context" / "scds",
            project_path / "docs" / "domain-docs",
            project_path / ".scs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _copy_templates(self, template_source: Path, project_path: Path) -> None:
        """Copy domain templates to the project.

        Args:
            template_source: Source directory containing domain templates
            project_path: Destination project path
        """
        dest_docs = project_path / "docs" / "domain-docs"

        # Copy all domain directories
        for domain_dir in template_source.iterdir():
            if domain_dir.is_dir():
                dest_domain = dest_docs / domain_dir.name
                shutil.copytree(domain_dir, dest_domain)

    def _create_config(self, project_path: Path, project_name: str) -> None:
        """Create .scs/config.yaml file.

        Args:
            project_path: Project path
            project_name: Name of the project
        """
        config = {
            "project_name": project_name,
            "scs_version": self.scs_version,
            "template_version": "1.0",
            "created_with": "scs init",
        }

        config_path = project_path / ".scs" / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def _copy_domain_meta(self, project_path: Path) -> None:
        """Copy domain-meta.yaml to the project.

        Args:
            project_path: Project path
        """
        # Find domain-meta.yaml in the spec
        package_root = Path(__file__).parent.parent.parent.parent.parent
        source_meta = package_root / "context" / "meta" / "domain-meta.yaml"

        if not source_meta.exists():
            raise ValidationError(f"domain-meta.yaml not found: {source_meta}")

        dest_meta = project_path / "context" / "meta" / "domain-meta.yaml"
        shutil.copy2(source_meta, dest_meta)

    def _create_project_bundle(self, project_path: Path, project_name: str) -> None:
        """Create initial project bundle file.

        Args:
            project_path: Project path
            project_name: Name of the project
        """
        bundle = {
            "id": f"bundle:project:{project_name}",
            "type": "project",
            "version": self.scs_version,
            "metadata": {
                "name": f"{project_name} Project Bundle",
                "description": f"Main project bundle for {project_name}",
                "phase": "intent",
            },
            "imports": [
                # Will be populated as domain bundles are created
            ],
        }

        bundle_path = project_path / "context" / "project-bundle.yaml"
        with open(bundle_path, "w") as f:
            yaml.dump(bundle, f, default_flow_style=False, sort_keys=False)
