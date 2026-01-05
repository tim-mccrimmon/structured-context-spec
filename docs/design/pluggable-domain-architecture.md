# Pluggable Domain Module Architecture

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Executive Summary

This document defines the technical architecture for loading, validating, and using pluggable domains in SCS. Domains provide content schemas, templates, and validation rules that define what goes in the `content` field of SCDs for different industries and business functions.

**Key Components:**
- Domain loader and registry
- Schema validation pipeline
- Template rendering system
- Domain lifecycle management
- Plugin interface specification

---

## 2. Core Concepts

### 2.1 What is a Domain (Technical Definition)?

A **domain** is a pluggable module that provides:

1. **Content Schemas** (JSON Schema)
   - `meta-content-schema.json` - Defines content structure for meta-tier SCDs
   - `standards-content-schema.json` - Defines content structure for standards-tier SCDs
   - `project-content-schema.json` - Defines content structure for project-tier SCDs

2. **Templates** (YAML/JSON)
   - SCD templates for each tier
   - Bundle templates for common patterns
   - Scaffolding for new projects

3. **Validation Rules** (Custom logic)
   - Domain-specific validation beyond JSON Schema
   - Cross-SCD relationship validation
   - Business rule enforcement

4. **Metadata** (Domain manifest)
   - Domain identity, version, licensing
   - Dependencies on other domains
   - Documentation and examples

### 2.2 Domain vs. SCD Structure

**What's Domain-Agnostic (stays the same):**
```yaml
# SCD structure (universal across all domains)
id: scd:project:example
type: project
domain: domain:healthcare  # NEW FIELD
title: "Example SCD"
version: "1.0.0"
description: "Description here"

content:
  # THIS IS DOMAIN-SPECIFIC
  # Validated against domain's content schema

relationships:
  # Domain-agnostic

provenance:
  # Domain-agnostic
```

**What's Domain-Specific:**
- The `content` field structure
- Available templates
- Validation rules for content
- Terminology and concepts

---

## 3. Domain Loader Architecture

### 3.1 Domain Loader Class

The Domain Loader is responsible for discovering, loading, and managing domains.

```python
class DomainLoader:
    """
    Loads and manages pluggable domains.

    Responsibilities:
    - Discover installed domains
    - Load domain manifests and schemas
    - Validate domain structure
    - Provide domain resolution
    - Cache loaded domains
    """

    def __init__(self, domains_dir: Path, cache_enabled: bool = True):
        """
        Initialize domain loader.

        Args:
            domains_dir: Directory containing installed domains (~/.scs/domains/)
            cache_enabled: Whether to cache loaded domains
        """
        self.domains_dir = domains_dir
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, Domain] = {}
        self._registry: Optional[DomainRegistry] = None

    def discover_domains(self) -> List[DomainInfo]:
        """
        Discover all installed domains.

        Returns:
            List of domain info objects (id, name, version, path)
        """
        domains = []
        for domain_dir in self.domains_dir.iterdir():
            manifest_path = domain_dir / "domain.yaml"
            if manifest_path.exists():
                info = self._load_domain_info(manifest_path)
                domains.append(info)
        return domains

    def load_domain(self, domain_id: str) -> Domain:
        """
        Load a domain by ID.

        Args:
            domain_id: Domain identifier (e.g., "domain:healthcare")

        Returns:
            Loaded and validated Domain object

        Raises:
            DomainNotFoundError: Domain not installed
            DomainValidationError: Domain manifest/schemas invalid
        """
        # Check cache
        if self.cache_enabled and domain_id in self._cache:
            return self._cache[domain_id]

        # Find domain directory
        domain_name = domain_id.replace("domain:", "")
        domain_path = self.domains_dir / domain_name

        if not domain_path.exists():
            raise DomainNotFoundError(f"Domain {domain_id} not found at {domain_path}")

        # Load and validate domain
        domain = Domain.load(domain_path)

        # Cache if enabled
        if self.cache_enabled:
            self._cache[domain_id] = domain

        return domain

    def get_default_domain(self) -> Domain:
        """
        Get the default domain (software-development).

        Returns:
            Default domain object
        """
        return self.load_domain("domain:software-development")

    def validate_domain(self, domain_path: Path) -> ValidationResult:
        """
        Validate a domain structure.

        Args:
            domain_path: Path to domain directory

        Returns:
            Validation result with errors/warnings
        """
        validator = DomainValidator()
        return validator.validate(domain_path)
```

### 3.2 Domain Class

The Domain class represents a loaded domain with all its schemas and capabilities.

```python
@dataclass
class Domain:
    """
    Represents a loaded pluggable domain.

    A domain provides content schemas, templates, and validation
    rules for a specific industry or business function.
    """

    # Core identity
    id: str  # domain:healthcare
    name: str  # "Healthcare"
    version: str  # "1.0.0"
    description: str
    author: str

    # Licensing
    license: str  # "open", "commercial", "custom"
    license_url: Optional[str] = None

    # Schemas (loaded and validated)
    meta_schema: Dict[str, Any]
    standards_schema: Dict[str, Any]
    project_schema: Dict[str, Any]

    # Templates
    meta_template: Optional[Dict[str, Any]] = None
    standards_template: Optional[Dict[str, Any]] = None
    project_template: Optional[Dict[str, Any]] = None
    bundle_templates: List[BundleTemplate] = field(default_factory=list)

    # Validation
    validation_rules: Optional[Dict[str, Any]] = None
    custom_validators: List[Path] = field(default_factory=list)

    # Dependencies
    dependencies: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Paths
    domain_path: Path
    manifest_path: Path

    @classmethod
    def load(cls, domain_path: Path) -> 'Domain':
        """
        Load a domain from a directory.

        Args:
            domain_path: Path to domain directory

        Returns:
            Loaded Domain object

        Raises:
            DomainLoadError: Failed to load domain
        """
        manifest_path = domain_path / "domain.yaml"
        if not manifest_path.exists():
            raise DomainLoadError(f"No domain.yaml found at {domain_path}")

        # Load manifest
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        domain_data = manifest.get("domain", {})

        # Validate manifest against domain-manifest-schema.json
        validate_against_schema(domain_data, "domain-manifest-schema.json")

        # Load schemas
        schemas_config = domain_data["schemas"]
        meta_schema = cls._load_schema(domain_path, schemas_config["meta"]["content_schema"])
        standards_schema = cls._load_schema(domain_path, schemas_config["standards"]["content_schema"])
        project_schema = cls._load_schema(domain_path, schemas_config["project"]["content_schema"])

        # Load templates (optional)
        meta_template = cls._load_template(domain_path, schemas_config["meta"].get("template"))
        standards_template = cls._load_template(domain_path, schemas_config["standards"].get("template"))
        project_template = cls._load_template(domain_path, schemas_config["project"].get("template"))

        # Load bundle templates
        bundle_templates = []
        for tmpl in domain_data.get("templates", {}).get("bundle_templates", []):
            bundle_templates.append(BundleTemplate(
                name=tmpl["name"],
                description=tmpl.get("description", ""),
                path=domain_path / tmpl["path"]
            ))

        # Load validation rules
        validation_rules = None
        validation_config = domain_data.get("validation", {})
        if "rules" in validation_config:
            rules_path = domain_path / validation_config["rules"]
            if rules_path.exists():
                with open(rules_path) as f:
                    validation_rules = json.load(f)

        # Load custom validators
        custom_validators = []
        for validator_path in validation_config.get("custom_validators", []):
            full_path = domain_path / validator_path
            if full_path.exists():
                custom_validators.append(full_path)

        return cls(
            id=domain_data["id"],
            name=domain_data["name"],
            version=domain_data["version"],
            description=domain_data["description"],
            author=domain_data.get("author", "Unknown"),
            license=domain_data.get("license", "custom"),
            license_url=domain_data.get("license_url"),
            meta_schema=meta_schema,
            standards_schema=standards_schema,
            project_schema=project_schema,
            meta_template=meta_template,
            standards_template=standards_template,
            project_template=project_template,
            bundle_templates=bundle_templates,
            validation_rules=validation_rules,
            custom_validators=custom_validators,
            dependencies=domain_data.get("dependencies", []),
            metadata=domain_data.get("metadata", {}),
            domain_path=domain_path,
            manifest_path=manifest_path
        )

    def validate_scd_content(self, scd: Dict[str, Any]) -> ValidationResult:
        """
        Validate an SCD's content field against this domain's schema.

        Args:
            scd: SCD document to validate

        Returns:
            Validation result
        """
        tier = scd.get("type")
        content = scd.get("content", {})

        if tier == "meta":
            schema = self.meta_schema
        elif tier == "standards":
            schema = self.standards_schema
        elif tier == "project":
            schema = self.project_schema
        else:
            raise ValueError(f"Unknown SCD tier: {tier}")

        # Validate content against schema
        result = validate_against_schema(content, schema)

        # Apply custom validation rules if present
        if self.validation_rules:
            custom_result = self._apply_validation_rules(scd, self.validation_rules)
            result.merge(custom_result)

        return result

    def get_template(self, tier: str) -> Optional[Dict[str, Any]]:
        """Get template for a specific tier."""
        if tier == "meta":
            return self.meta_template
        elif tier == "standards":
            return self.standards_template
        elif tier == "project":
            return self.project_template
        return None

    @staticmethod
    def _load_schema(base_path: Path, schema_path: str) -> Dict[str, Any]:
        """Load a JSON schema file."""
        full_path = base_path / schema_path
        if not full_path.exists():
            raise DomainLoadError(f"Schema not found: {full_path}")

        with open(full_path) as f:
            return json.load(f)

    @staticmethod
    def _load_template(base_path: Path, template_path: Optional[str]) -> Optional[Dict[str, Any]]:
        """Load a template file if specified."""
        if not template_path:
            return None

        full_path = base_path / template_path
        if not full_path.exists():
            return None

        with open(full_path) as f:
            if full_path.suffix == '.json':
                return json.load(f)
            else:
                return yaml.safe_load(f)
```

---

## 4. Schema Validation Pipeline

### 4.1 Two-Stage Validation

SCD validation happens in two stages:

**Stage 1: Structural Validation (Domain-Agnostic)**
- Validates SCD structure (id, type, title, version, relationships, provenance)
- Uses base SCD schema (`schema/scd/base-scd-schema.json`)
- Ensures required fields present
- Validates field types and patterns

**Stage 2: Content Validation (Domain-Specific)**
- Validates the `content` field against domain's content schema
- Uses domain-provided schema (e.g., `healthcare/project-content-schema.json`)
- Applies domain-specific validation rules
- Runs custom validators if provided

### 4.2 Validation Flow

```python
class SCDValidator:
    """
    Validates SCDs using two-stage process.
    """

    def __init__(self, domain_loader: DomainLoader):
        self.domain_loader = domain_loader
        self.base_validator = BaseValidator()

    def validate_scd(self, scd: Dict[str, Any], domain_id: Optional[str] = None) -> ValidationResult:
        """
        Validate an SCD document.

        Args:
            scd: SCD document to validate
            domain_id: Explicit domain ID (if not specified in SCD)

        Returns:
            Validation result with errors and warnings
        """
        result = ValidationResult()

        # Stage 1: Structural validation (domain-agnostic)
        structural_result = self.base_validator.validate_structure(scd)
        result.merge(structural_result)

        if structural_result.has_errors():
            return result  # Don't continue if structure is invalid

        # Determine domain
        domain_id = domain_id or scd.get("domain") or "domain:software-development"

        try:
            domain = self.domain_loader.load_domain(domain_id)
        except DomainNotFoundError as e:
            result.add_error(f"Domain not found: {domain_id}")
            return result

        # Stage 2: Content validation (domain-specific)
        content_result = domain.validate_scd_content(scd)
        result.merge(content_result)

        return result
```

### 4.3 Base SCD Schema (Domain-Agnostic)

Create new base schema that all SCDs must conform to:

```json
// schema/scd/base-scd-schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SCS Base SCD Schema",
  "description": "Domain-agnostic base schema for all SCDs",
  "type": "object",
  "required": ["id", "type", "title", "version", "description", "content", "provenance"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^scd:(meta|standards|project):[a-zA-Z0-9._-]+$"
    },
    "type": {
      "type": "string",
      "enum": ["meta", "standards", "project"]
    },
    "domain": {
      "type": "string",
      "pattern": "^domain:[a-z][a-z0-9-]*$",
      "description": "Domain this SCD belongs to (e.g., domain:healthcare)"
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "version": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string",
      "minLength": 1
    },
    "content": {
      "type": "object",
      "description": "Domain-specific content (validated separately)"
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "target"],
        "properties": {
          "type": {
            "type": "string"
          },
          "target": {
            "type": "string"
          },
          "description": {
            "type": "string"
          }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["created_by", "created_at"],
      "properties": {
        "created_by": {
          "type": "string"
        },
        "created_at": {
          "type": "string",
          "format": "date-time"
        },
        "updated_by": {
          "type": "string"
        },
        "updated_at": {
          "type": "string",
          "format": "date-time"
        },
        "rationale": {
          "type": "string"
        }
      }
    }
  }
}
```

---

## 5. Template Rendering System

### 5.1 Template Engine

```python
class TemplateEngine:
    """
    Renders SCD and bundle templates with user-provided values.
    """

    def __init__(self, domain_loader: DomainLoader):
        self.domain_loader = domain_loader

    def render_scd_template(
        self,
        tier: str,
        domain_id: str,
        values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render an SCD template.

        Args:
            tier: SCD tier (meta, standards, project)
            domain_id: Domain to use
            values: User-provided values to populate template

        Returns:
            Rendered SCD document
        """
        domain = self.domain_loader.load_domain(domain_id)
        template = domain.get_template(tier)

        if not template:
            # Generate minimal template from schema
            template = self._generate_template_from_schema(domain, tier)

        # Merge user values with template
        rendered = self._merge_template(template, values)

        # Add domain field
        rendered["domain"] = domain_id

        return rendered

    def render_bundle_template(
        self,
        template_name: str,
        domain_id: str,
        values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Render a bundle template.

        Args:
            template_name: Name of bundle template
            domain_id: Domain to use
            values: User-provided values

        Returns:
            Rendered bundle document
        """
        domain = self.domain_loader.load_domain(domain_id)

        # Find template
        template = None
        for tmpl in domain.bundle_templates:
            if tmpl.name == template_name:
                with open(tmpl.path) as f:
                    template = yaml.safe_load(f)
                break

        if not template:
            raise TemplateNotFoundError(f"Template {template_name} not found in {domain_id}")

        # Merge values
        rendered = self._merge_template(template, values)

        # Add domain field to all SCDs in bundle
        for scd_ref in rendered.get("scds", []):
            if isinstance(scd_ref, dict):
                scd_ref["domain"] = domain_id

        return rendered

    def list_templates(self, domain_id: str) -> Dict[str, List[str]]:
        """
        List available templates for a domain.

        Returns:
            Dict with keys: scd_templates, bundle_templates
        """
        domain = self.domain_loader.load_domain(domain_id)

        return {
            "scd_templates": ["meta", "standards", "project"],
            "bundle_templates": [t.name for t in domain.bundle_templates]
        }
```

---

## 6. Domain Configuration Management

### 6.1 Configuration Hierarchy

Domains can be configured at three levels:

1. **Global** (`~/.scs/config.yaml`) - System-wide defaults
2. **Project** (`.scs/config.yaml`) - Project-specific settings
3. **Bundle** (`bundle.yaml`) - Bundle-level domain specification

**Resolution Order:** Bundle > Project > Global > Default

### 6.2 Configuration Schema

```yaml
# ~/.scs/config.yaml (Global)
scs:
  version: "0.2.0"

  # Default domain for new projects
  default_domain: "domain:software-development"

  # Domain registry settings
  registry:
    url: "https://registry.scs-commercial.com"
    cache_ttl: 3600  # seconds

  # License storage
  licenses_dir: "~/.scs/licenses"

  # Installed domains
  domains_dir: "~/.scs/domains"
```

```yaml
# project-root/.scs/config.yaml (Project)
project:
  name: "Patient Care System"

  # Domain for this project
  domain: "domain:healthcare"
  domain_version: "1.0.0"

  # License activation
  license:
    key: "HC-XXXX-XXXX-XXXX-XXXX"
    activated: true
    expires: "2026-12-12T00:00:00Z"
```

### 6.3 Domain Resolution

```python
class DomainResolver:
    """
    Resolves which domain to use based on configuration hierarchy.
    """

    def __init__(self, global_config: Path, project_config: Optional[Path] = None):
        self.global_config = self._load_config(global_config)
        self.project_config = self._load_config(project_config) if project_config else {}

    def resolve_domain(
        self,
        explicit_domain: Optional[str] = None,
        bundle: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Resolve which domain to use.

        Priority:
        1. Explicit domain parameter
        2. Bundle domain field
        3. Project config domain
        4. Global config default_domain
        5. Hardcoded default (domain:software-development)

        Args:
            explicit_domain: Explicitly specified domain
            bundle: Bundle document (may contain domain field)

        Returns:
            Domain ID to use
        """
        # 1. Explicit parameter
        if explicit_domain:
            return explicit_domain

        # 2. Bundle domain field
        if bundle and "domain" in bundle:
            return bundle["domain"]

        # 3. Project config
        if "project" in self.project_config:
            project_domain = self.project_config["project"].get("domain")
            if project_domain:
                return project_domain

        # 4. Global config
        if "scs" in self.global_config:
            global_domain = self.global_config["scs"].get("default_domain")
            if global_domain:
                return global_domain

        # 5. Hardcoded default
        return "domain:software-development"
```

---

## 7. Integration Points

### 7.1 SCD Structure Changes

**Current SCD:**
```yaml
id: scd:project:example
type: project
# ... other fields ...
content:
  # Hardcoded software-dev schema
```

**New SCD (with domain support):**
```yaml
id: scd:project:example
type: project
domain: "domain:healthcare"  # NEW FIELD (optional)
# ... other fields ...
content:
  # Validated against domain:healthcare project schema
  clinical_workflows: [...]
  care_pathways: [...]
```

### 7.2 Bundle Structure Changes

**Current Bundle:**
```yaml
id: bundle:example
type: project
version: "1.0.0"
# ... other fields ...
```

**New Bundle (with domain support):**
```yaml
id: bundle:example
type: project
version: "1.0.0"
domain: "domain:healthcare"  # NEW FIELD (optional)
# ... other fields ...
```

### 7.3 Validator Integration

The existing validator needs to be updated to use the domain loader:

```python
# OLD
from scs.validator import validate_scd

result = validate_scd(scd_path)

# NEW
from scs.validator import SCDValidator
from scs.domains import DomainLoader

loader = DomainLoader(domains_dir=Path("~/.scs/domains"))
validator = SCDValidator(domain_loader=loader)

result = validator.validate_scd(scd_dict, domain_id="domain:healthcare")
```

---

## 8. Domain Lifecycle

### 8.1 Domain States

Domains go through these lifecycle states:

1. **Uninstalled** - Available in registry but not installed
2. **Installing** - Being downloaded and installed
3. **Installed** - Available for use
4. **Activated** - Licensed (for commercial domains)
5. **Updating** - New version being installed
6. **Uninstalling** - Being removed

### 8.2 License Verification

For commercial domains, license must be verified before loading:

```python
class LicenseManager:
    """
    Manages licenses for commercial domains.
    """

    def __init__(self, licenses_dir: Path):
        self.licenses_dir = licenses_dir

    def verify_license(self, domain_id: str) -> bool:
        """
        Verify a domain license.

        Args:
            domain_id: Domain to verify

        Returns:
            True if licensed, False otherwise
        """
        domain_name = domain_id.replace("domain:", "")
        license_file = self.licenses_dir / f"{domain_name}.license"

        if not license_file.exists():
            return False

        # Load license
        with open(license_file) as f:
            license_data = json.load(f)

        # Check expiration
        expires_at = datetime.fromisoformat(license_data.get("expires_at", ""))
        if datetime.now() > expires_at:
            return False

        # TODO: Verify with registry (online check)

        return True

    def get_license_info(self, domain_id: str) -> Optional[Dict[str, Any]]:
        """Get license information for a domain."""
        domain_name = domain_id.replace("domain:", "")
        license_file = self.licenses_dir / f"{domain_name}.license"

        if not license_file.exists():
            return None

        with open(license_file) as f:
            return json.load(f)
```

---

## 9. Error Handling

### 9.1 Exception Hierarchy

```python
class DomainError(Exception):
    """Base exception for domain-related errors."""
    pass

class DomainNotFoundError(DomainError):
    """Domain is not installed."""
    pass

class DomainLoadError(DomainError):
    """Failed to load domain."""
    pass

class DomainValidationError(DomainError):
    """Domain structure is invalid."""
    pass

class LicenseRequiredError(DomainError):
    """Domain requires a valid license."""
    pass

class InvalidLicenseError(DomainError):
    """License is invalid or expired."""
    pass

class TemplateNotFoundError(DomainError):
    """Requested template not found."""
    pass
```

### 9.2 Graceful Degradation

When a domain is not found or invalid:

1. **Validation Mode**: Warn user but don't fail
2. **Creation Mode**: Fail with clear error message
3. **Display Mode**: Show domain as "unknown" but render structure

---

## 10. Performance Considerations

### 10.1 Domain Caching

- Loaded domains are cached in memory
- Cache invalidation on domain update
- Configurable cache TTL

### 10.2 Lazy Loading

- Schemas loaded on first use
- Custom validators loaded only if needed
- Templates loaded on demand

### 10.3 Schema Compilation

- JSON schemas compiled on load for faster validation
- Compiled schemas cached

---

## 11. Testing Strategy

### 11.1 Unit Tests

- Domain loader tests
- Schema validation tests
- Template rendering tests
- Configuration resolution tests

### 11.2 Integration Tests

- Multi-domain scenarios
- Domain switching
- License verification
- Template rendering end-to-end

### 11.3 Domain Examples

Each domain must include:
- Valid example SCDs for all tiers
- Valid example bundles
- Test cases for validation

---

## 12. Implementation Checklist

- [ ] Create base SCD schema (domain-agnostic)
- [ ] Implement DomainLoader class
- [ ] Implement Domain class
- [ ] Implement SCDValidator with two-stage validation
- [ ] Implement TemplateEngine
- [ ] Implement DomainResolver
- [ ] Implement LicenseManager
- [ ] Update existing schemas to add optional `domain` field
- [ ] Create domain validation rules
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update CLI to use domain loader
- [ ] Update documentation

---

## 13. Open Questions

1. **Custom Validator Format**: Should we support Python plugins, JavaScript, or both?
2. **Schema References**: How do we handle `$ref` in domain schemas that reference other schemas?
3. **Domain Dependencies**: How do we handle domains that depend on other domains?
4. **Version Constraints**: Do we support semver ranges for domain versions?
5. **Hot Reload**: Should domains support hot reloading during development?

---

## 14. Next Steps

1. Review and approve this design
2. Begin implementation of core classes
3. Create reference implementation with software-dev domain
4. Test with healthcare domain proof-of-concept
5. Iterate and refine based on feedback

---

*This design provides the foundation for pluggable domains in SCS, enabling multi-industry support while maintaining backwards compatibility.*
