# Changelog

All notable changes to the SCS CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive help text improvements across all commands
- Quick start guide in main `scs --help` output
- Common workflow documentation in help text
- "See also" cross-references between related commands
- Detailed explanations of SCDs and bundles in help text
- Context explanations for all command descriptions

### Changed
- Enhanced help text for all commands with more detailed descriptions
- Improved examples in command help with inline comments
- Simplified `scs bundle version` examples (removed line continuation issues)
- Refined CONTRIBUTING.md with CLI-specific development guidelines

### Fixed
- Fixed formatting issues in `scs bundle version` help text

## [0.1.0] - 2024-12-10

### Added
- Initial release of SCS CLI
- `scs new project` command for creating new SCS projects
  - Support for 6 project types: healthcare, fintech, saas, government, minimal, standard
  - Interactive mode for guided project creation
  - Non-interactive mode for automation
  - Automatic directory structure creation
  - Template-based SCD generation
  - Bundle configuration based on project type
- `scs init` command for adding SCS to existing projects
  - Creates `.scs/`, `bundles/`, and `context/` directories
  - Generates basic configuration files
  - Support for all project types
- `scs add scd` command for adding individual SCDs
  - Add any SCD from template library
  - Provenance tracking (author, email, timestamp)
  - Automatic project detection
- `scs add bundle` command for adding domain bundles
  - Support for 11 domain bundles
  - Automatic SCD inclusion
  - Domain-specific templates
- `scs bundle list` command for listing bundles
  - List project bundles with metadata
  - List available templates with `--available` flag
  - Show bundle details (ID, version, SCDs, etc.)
- `scs bundle info` command for bundle inspection
  - Display bundle metadata
  - Show included SCDs
  - Display imports and provenance
- `scs bundle validate` command for quick validation
  - Shortcut for validating project bundle
  - Integration with scs-validator
- `scs bundle version` command for creating versioned bundles
  - Automated Phase 3 (Version) workflow
  - Bundle validation before versioning
  - SHA-256 checksum generation
  - Version manifest creation
  - Git commit and tag automation
  - Interactive prompts for missing information
  - Semantic versioning enforcement
- `scs validate` command for SCD and bundle validation
  - Integration with scs-validator package
  - Support for individual file validation
  - Support for bundle validation
  - Multiple output formats (text, JSON)
  - 6 validation levels: Syntax, Schema, Semantic, Relationships, Completeness, Compliance
  - Strict mode for failing on warnings
  - Custom schema directory support
- Template system with 39 SCD templates
  - Business context templates (6 SCDs)
  - Architecture templates (4 SCDs)
  - Security templates (4 SCDs)
  - Performance/reliability templates (4 SCDs)
  - Usability/accessibility templates (3 SCDs)
  - Compliance/governance templates (4 SCDs)
  - Data provenance templates (3 SCDs)
  - Testing/validation templates (3 SCDs)
  - Deployment/operations templates (3 SCDs)
  - Safety/risk templates (2 SCDs)
  - Ethics/AI/accountability templates (3 SCDs)
- Bundle template system with 14 bundle templates
  - 3 foundation bundles (project, meta, standards)
  - 11 domain bundles
- Domain documentation templates
  - Markdown templates for each domain
  - User-fillable brief templates
- Jinja2 template rendering
  - Support for project variables (name, author, email, etc.)
  - Dynamic content generation
  - Timestamp tracking
- Project type configurations
  - Minimal project (11 SCDs, 3 bundles)
  - Standard project (38+ SCDs, 11 bundles)
  - Healthcare project (HIPAA, CHAI, TEFCA focus)
  - Fintech project (PCI-DSS, SOX focus)
  - SaaS project (GDPR, SOC2 focus)
  - Government project (NIST, FedRAMP focus)
- Comprehensive documentation
  - Detailed README with examples
  - Installation instructions
  - Command reference
  - Common workflows
  - CI/CD integration examples
  - MIT License

### Developer Experience
- Click-based CLI framework
- Modular command structure
- Utility functions for file operations
- Template path resolution
- Configuration file management
- Color-coded terminal output
- Progress indicators
- Error handling with actionable messages
- Git integration for versioning workflow
- Provenance tracking throughout

## Release Notes

### Version 0.1.0 - Initial Release

This is the first public release of the SCS CLI tool. It provides a complete workflow for:
1. Creating SCS-compliant projects with proper structure
2. Adding SCDs and bundles to projects
3. Validating SCDs and bundles
4. Creating versioned, immutable bundle snapshots

The tool supports multiple project types with domain-specific compliance focuses, making it easy to scaffold projects for healthcare, fintech, SaaS, government, and general use cases.

---

## Version History

- **0.1.0** (2024-12-10) - Initial release

[Unreleased]: https://github.com/SCS-Labs/scs-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/SCS-Labs/scs-cli/releases/tag/v0.1.0
