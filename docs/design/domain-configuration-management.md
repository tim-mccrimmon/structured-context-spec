# Domain Configuration Management

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Executive Summary

This document defines how domain configuration is managed across SCS installations, from global system settings to project-specific and bundle-specific configurations.

**Key Concepts:**
- Three-tier configuration hierarchy (Global → Project → Bundle)
- Domain selection and switching
- License management
- Environment-specific overrides
- Configuration validation and resolution

**Design Goal:** Flexible configuration that works for individual developers, teams, and enterprise deployments.

---

## 2. Configuration Hierarchy

### 2.1 Three Configuration Tiers

```
┌─────────────────────────────────────┐
│  Bundle Configuration               │  ← Highest Priority
│  (bundle.yaml: domain field)        │
└─────────────────────────────────────┘
              ↓ inherits from
┌─────────────────────────────────────┐
│  Project Configuration              │  ← Medium Priority
│  (.scs/config.yaml)                 │
└─────────────────────────────────────┘
              ↓ inherits from
┌─────────────────────────────────────┐
│  Global Configuration               │  ← Lowest Priority
│  (~/.scs/config.yaml)               │
└─────────────────────────────────────┘
```

**Resolution Order:**
1. Bundle-level domain field (if present)
2. Project-level domain setting (if present)
3. Global-level default domain (if present)
4. Hardcoded default (`domain:software-development`)

---

## 3. Global Configuration

### 3.1 Location and Purpose

**File:** `~/.scs/config.yaml` or `$SCS_HOME/config.yaml`

**Purpose:**
- System-wide SCS settings
- Default domain for new projects
- Registry configuration
- License storage location
- Tool preferences

### 3.2 Global Configuration Schema

```yaml
# ~/.scs/config.yaml

scs:
  # SCS version (for compatibility checking)
  version: "0.2.0"

  # Default domain for new projects
  default_domain: "domain:software-development"

  # Domain installation directory
  domains_dir: "~/.scs/domains"

  # License storage
  licenses_dir: "~/.scs/licenses"

  # Registry configuration
  registry:
    url: "https://registry.scs-commercial.com"
    api_version: "v1"
    cache_ttl: 3600  # seconds
    timeout: 30      # seconds
    verify_ssl: true

  # Update checking
  updates:
    check_on_startup: true
    auto_update_domains: false
    frequency: "daily"  # daily, weekly, never

  # CLI preferences
  cli:
    color: true
    verbose: false
    confirm_destructive: true
    pager: "less"

  # Telemetry (optional)
  telemetry:
    enabled: false
    anonymous: true

# Installed domains (auto-managed)
domains:
  software-development:
    version: "1.0.0"
    installed_at: "2025-12-01T00:00:00Z"
    source: "builtin"

  healthcare:
    version: "1.0.0"
    installed_at: "2025-12-12T10:00:00Z"
    source: "registry"
    licensed: true
    license_expires: "2026-12-12T00:00:00Z"
```

### 3.3 Global Configuration Management

```python
class GlobalConfig:
    """
    Manages global SCS configuration.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize global config.

        Args:
            config_path: Path to config file (defaults to ~/.scs/config.yaml)
        """
        if config_path is None:
            config_path = Path.home() / ".scs" / "config.yaml"

        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return self._create_default_config()

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {}

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default = {
            "scs": {
                "version": "0.2.0",
                "default_domain": "domain:software-development",
                "domains_dir": str(Path.home() / ".scs" / "domains"),
                "licenses_dir": str(Path.home() / ".scs" / "licenses"),
                "registry": {
                    "url": "https://registry.scs-commercial.com",
                    "api_version": "v1",
                    "cache_ttl": 3600,
                    "timeout": 30,
                    "verify_ssl": True
                },
                "cli": {
                    "color": True,
                    "verbose": False,
                    "confirm_destructive": True
                }
            },
            "domains": {}
        }

        # Create config directory if needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default config
        with open(self.config_path, 'w') as f:
            yaml.dump(default, f, default_flow_style=False)

        return default

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        config = self._config

        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set value
        config[keys[-1]] = value

        # Save
        self.save()

    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get_default_domain(self) -> str:
        """Get the default domain."""
        return self.get("scs.default_domain", "domain:software-development")

    def set_default_domain(self, domain_id: str) -> None:
        """Set the default domain."""
        self.set("scs.default_domain", domain_id)

    def get_domains_dir(self) -> Path:
        """Get the domains installation directory."""
        return Path(self.get("scs.domains_dir")).expanduser()

    def get_registry_url(self) -> str:
        """Get the registry URL."""
        return self.get("scs.registry.url")
```

---

## 4. Project Configuration

### 4.1 Location and Purpose

**File:** `<project-root>/.scs/config.yaml`

**Purpose:**
- Project-specific domain selection
- License activation for commercial domains
- Project metadata
- Team settings
- Build/deployment configuration

### 4.2 Project Configuration Schema

```yaml
# <project-root>/.scs/config.yaml

project:
  # Project identity
  name: "Patient Care System"
  id: "project:patient-care-v2"
  version: "2.0.0"

  # Domain configuration
  domain: "domain:healthcare"
  domain_version: "1.0.0"

  # License (for commercial domains)
  license:
    key: "HC-XXXX-XXXX-XXXX-XXXX"
    activated: true
    activated_at: "2025-12-12T10:00:00Z"
    expires: "2026-12-12T00:00:00Z"
    seats: 5
    organization: "Acme Healthcare"

  # Bundle locations
  bundles:
    root: "./bundles/project-bundle.yaml"
    directory: "./bundles"

  # Context locations
  context:
    directory: "./context"
    meta: "./context/meta"
    standards: "./context/standards"
    project: "./context/project"

  # Validation settings
  validation:
    strict: true
    fail_on_warnings: false
    auto_fix: false

  # Team settings
  team:
    organization: "Acme Healthcare"
    department: "Clinical Engineering"
    contacts:
      - name: "Dr. Sarah Chen"
        email: "sarah.chen@acme.com"
        role: "Clinical Architect"

  # Environment-specific overrides
  environments:
    development:
      validation:
        strict: false
    production:
      validation:
        strict: true
        fail_on_warnings: true
```

### 4.3 Project Configuration Management

```python
class ProjectConfig:
    """
    Manages project-specific configuration.
    """

    def __init__(self, project_root: Path):
        """
        Initialize project config.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.config_path = project_root / ".scs" / "config.yaml"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration."""
        if not self.config_path.exists():
            return {}

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {}

    def exists(self) -> bool:
        """Check if project configuration exists."""
        return self.config_path.exists()

    def initialize(self, domain: str, project_name: str) -> None:
        """
        Initialize new project configuration.

        Args:
            domain: Domain ID
            project_name: Project name
        """
        config = {
            "project": {
                "name": project_name,
                "domain": domain,
                "bundles": {
                    "root": "./bundles/project-bundle.yaml",
                    "directory": "./bundles"
                },
                "context": {
                    "directory": "./context"
                },
                "validation": {
                    "strict": True,
                    "fail_on_warnings": False
                }
            }
        }

        # Create .scs directory
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        self._config = config

    def get_domain(self) -> Optional[str]:
        """Get project domain."""
        return self._config.get("project", {}).get("domain")

    def set_domain(self, domain_id: str) -> None:
        """Set project domain."""
        if "project" not in self._config:
            self._config["project"] = {}

        self._config["project"]["domain"] = domain_id
        self.save()

    def get_license_key(self) -> Optional[str]:
        """Get license key for current domain."""
        return self._config.get("project", {}).get("license", {}).get("key")

    def set_license(self, license_info: Dict[str, Any]) -> None:
        """Save license information."""
        if "project" not in self._config:
            self._config["project"] = {}

        self._config["project"]["license"] = license_info
        self.save()

    def get_bundle_root(self) -> Path:
        """Get root bundle path."""
        root = self._config.get("project", {}).get("bundles", {}).get("root", "./bundles/project-bundle.yaml")
        return self.project_root / root

    def save(self) -> None:
        """Save configuration."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)
```

---

## 5. Bundle Configuration

### 5.1 Domain Field in Bundles

**Location:** Inline in bundle YAML files

```yaml
# bundles/project-bundle.yaml

id: bundle:patient-care
type: project
version: "1.0.0"
domain: "domain:healthcare"  # Bundle-level domain
title: "Patient Care System"
# ...
```

**Purpose:**
- Explicit domain declaration at bundle level
- Overrides project and global settings
- Highest priority in resolution

### 5.2 Bundle Domain Inheritance

All SCDs in a bundle inherit the bundle's domain unless they specify their own.

---

## 6. Configuration Resolution

### 6.1 Domain Resolution Algorithm

```python
class ConfigResolver:
    """
    Resolves configuration values across the hierarchy.
    """

    def __init__(self, global_config: GlobalConfig, project_config: Optional[ProjectConfig] = None):
        self.global_config = global_config
        self.project_config = project_config

    def resolve_domain(
        self,
        bundle: Optional[Dict[str, Any]] = None,
        explicit_domain: Optional[str] = None,
        environment: Optional[str] = None
    ) -> str:
        """
        Resolve which domain to use.

        Resolution order:
        1. Explicit domain parameter (from CLI or API)
        2. Bundle domain field
        3. Environment-specific project domain
        4. Project domain
        5. Global default domain
        6. Hardcoded default

        Args:
            bundle: Bundle document
            explicit_domain: Explicitly specified domain
            environment: Environment name (dev, prod, etc.)

        Returns:
            Resolved domain ID
        """
        # 1. Explicit parameter (highest priority)
        if explicit_domain:
            return explicit_domain

        # 2. Bundle domain field
        if bundle and "domain" in bundle:
            return bundle["domain"]

        # 3. Environment-specific project domain
        if self.project_config and environment:
            env_domain = self._get_env_domain(environment)
            if env_domain:
                return env_domain

        # 4. Project domain
        if self.project_config:
            project_domain = self.project_config.get_domain()
            if project_domain:
                return project_domain

        # 5. Global default domain
        global_domain = self.global_config.get_default_domain()
        if global_domain:
            return global_domain

        # 6. Hardcoded default (fallback)
        return "domain:software-development"

    def _get_env_domain(self, environment: str) -> Optional[str]:
        """Get environment-specific domain override."""
        if not self.project_config:
            return None

        env_config = self.project_config._config.get("project", {}).get("environments", {}).get(environment, {})
        return env_config.get("domain")

    def resolve_validation_settings(
        self,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve validation settings.

        Args:
            environment: Environment name

        Returns:
            Merged validation settings
        """
        settings = {
            "strict": True,
            "fail_on_warnings": False,
            "auto_fix": False
        }

        # Merge from project config
        if self.project_config:
            project_validation = self.project_config._config.get("project", {}).get("validation", {})
            settings.update(project_validation)

            # Environment overrides
            if environment:
                env_validation = self.project_config._config.get("project", {}).get("environments", {}).get(environment, {}).get("validation", {})
                settings.update(env_validation)

        return settings
```

### 6.2 Resolution Examples

**Example 1: Default (No Config)**
```python
resolver = ConfigResolver(global_config)
domain = resolver.resolve_domain()
# Returns: "domain:software-development" (hardcoded default)
```

**Example 2: Project Config**
```yaml
# .scs/config.yaml
project:
  domain: "domain:healthcare"
```
```python
domain = resolver.resolve_domain()
# Returns: "domain:healthcare" (from project)
```

**Example 3: Bundle Override**
```yaml
# bundle.yaml
domain: "domain:sales"
```
```python
bundle = load_bundle("bundle.yaml")
domain = resolver.resolve_domain(bundle=bundle)
# Returns: "domain:sales" (bundle overrides project)
```

**Example 4: Explicit Override**
```bash
scs validate --domain domain:finance
```
```python
domain = resolver.resolve_domain(explicit_domain="domain:finance")
# Returns: "domain:finance" (explicit overrides everything)
```

---

## 7. Environment-Specific Configuration

### 7.1 Use Cases

**Development Environment:**
- Less strict validation
- Fast feedback loops
- Auto-fix enabled

**Staging Environment:**
- Moderate validation
- Test commercial domains
- Compliance checking enabled

**Production Environment:**
- Strict validation
- Fail on warnings
- Full compliance validation
- Licensed domains required

### 7.2 Environment Configuration

```yaml
# .scs/config.yaml

project:
  domain: "domain:healthcare"

  validation:
    strict: true  # Default

  environments:
    development:
      validation:
        strict: false
        fail_on_warnings: false
        auto_fix: true

    staging:
      validation:
        strict: true
        fail_on_warnings: false

    production:
      validation:
        strict: true
        fail_on_warnings: true
      license:
        verify_online: true
```

### 7.3 Environment Selection

```bash
# Set environment via CLI
scs validate --env production

# Or via environment variable
export SCS_ENV=production
scs validate

# Or in project config
scs config set project.environment production
```

---

## 8. Configuration Commands

### 8.1 Global Configuration

```bash
# View global config
scs config show --global

# Set global default domain
scs config set scs.default_domain domain:healthcare --global

# Get specific value
scs config get scs.registry.url --global

# Edit config file directly
scs config edit --global
```

### 8.2 Project Configuration

```bash
# Initialize project
scs init --domain healthcare

# View project config
scs config show

# Set project domain
scs config set project.domain domain:healthcare

# Get project domain
scs config get project.domain

# Edit project config
scs config edit
```

### 8.3 Configuration Validation

```bash
# Validate configuration
scs config validate

# Check configuration resolution
scs config resolve

# Show effective configuration (merged hierarchy)
scs config show --effective
```

---

## 9. License Management Integration

### 9.1 License Storage

**Global Licenses:** `~/.scs/licenses/<domain-name>.license`
**Project Licenses:** `.scs/licenses/<domain-name>.license` (override global)

### 9.2 License Configuration

```yaml
# Project config
project:
  domain: "domain:healthcare"

  license:
    key: "HC-XXXX-XXXX-XXXX-XXXX"
    activated: true
    activated_at: "2025-12-12T10:00:00Z"
    activated_by: "tim@acme.com"
    expires: "2026-12-12T00:00:00Z"
    seats: 5
    seats_used: 2
    organization: "Acme Healthcare"

    # License verification
    verify_online: true  # Check with registry on load
    verify_interval: 86400  # seconds (daily)
    last_verified: "2025-12-12T10:00:00Z"

    # Offline mode
    offline_grace_period: 7  # days
```

### 9.3 License Resolution

```python
class LicenseResolver:
    """
    Resolves license information for domains.
    """

    def __init__(self, global_config: GlobalConfig, project_config: Optional[ProjectConfig] = None):
        self.global_config = global_config
        self.project_config = project_config

    def get_license_info(self, domain_id: str) -> Optional[Dict[str, Any]]:
        """
        Get license information for a domain.

        Resolution order:
        1. Project license (if exists)
        2. Global license (if exists)
        3. None

        Args:
            domain_id: Domain to get license for

        Returns:
            License info dict or None
        """
        # 1. Project license
        if self.project_config:
            project_license = self.project_config._config.get("project", {}).get("license", {})
            if project_license:
                return project_license

        # 2. Global license
        domain_name = domain_id.replace("domain:", "")
        licenses_dir = Path(self.global_config.get("scs.licenses_dir")).expanduser()
        license_file = licenses_dir / f"{domain_name}.license"

        if license_file.exists():
            with open(license_file) as f:
                return json.load(f)

        return None
```

---

## 10. Configuration Migration and Upgrades

### 10.1 Version Compatibility

```python
class ConfigMigrator:
    """
    Migrates configuration between SCS versions.
    """

    def migrate(self, config: Dict[str, Any], from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Migrate configuration from one version to another.

        Args:
            config: Configuration to migrate
            from_version: Source version
            to_version: Target version

        Returns:
            Migrated configuration
        """
        migrations = []

        # Collect applicable migrations
        if self._version_less_than(from_version, "0.2.0") and self._version_gte(to_version, "0.2.0"):
            migrations.append(self._migrate_to_0_2_0)

        # Apply migrations in order
        for migration in migrations:
            config = migration(config)

        return config

    def _migrate_to_0_2_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate to SCS 0.2.0 (adds multi-domain support).

        Changes:
        - Adds default_domain field if missing
        - Adds domains section if missing
        - Adds registry configuration if missing
        """
        if "scs" not in config:
            config["scs"] = {}

        # Add version
        config["scs"]["version"] = "0.2.0"

        # Add default_domain
        if "default_domain" not in config["scs"]:
            config["scs"]["default_domain"] = "domain:software-development"

        # Add domains section
        if "domains" not in config:
            config["domains"] = {}

        # Add registry config
        if "registry" not in config["scs"]:
            config["scs"]["registry"] = {
                "url": "https://registry.scs-commercial.com",
                "api_version": "v1"
            }

        return config
```

### 10.2 Configuration Backup

```bash
# Backup configuration before changes
scs config backup

# Restore from backup
scs config restore <backup-file>

# List backups
scs config backups
```

---

## 11. Configuration Validation

### 11.1 Schema Validation

```python
class ConfigValidator:
    """
    Validates configuration files.
    """

    def validate_global_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate global configuration."""
        result = ValidationResult()

        # Required fields
        if "scs" not in config:
            result.add_error("Missing 'scs' section")
            return result

        # Validate registry URL
        registry_url = config.get("scs", {}).get("registry", {}).get("url")
        if registry_url and not self._is_valid_url(registry_url):
            result.add_error(f"Invalid registry URL: {registry_url}")

        # Validate default domain
        default_domain = config.get("scs", {}).get("default_domain")
        if default_domain and not self._is_valid_domain_id(default_domain):
            result.add_error(f"Invalid domain ID: {default_domain}")

        return result

    def validate_project_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate project configuration."""
        result = ValidationResult()

        if "project" not in config:
            result.add_warning("Missing 'project' section")
            return result

        # Validate domain
        domain = config.get("project", {}).get("domain")
        if domain and not self._is_valid_domain_id(domain):
            result.add_error(f"Invalid domain ID: {domain}")

        # Validate license key format
        license_key = config.get("project", {}).get("license", {}).get("key")
        if license_key and not self._is_valid_license_key(license_key):
            result.add_error(f"Invalid license key format: {license_key}")

        return result
```

---

## 12. Implementation Checklist

- [ ] Implement GlobalConfig class
- [ ] Implement ProjectConfig class
- [ ] Implement ConfigResolver class
- [ ] Implement LicenseResolver class
- [ ] Implement ConfigValidator class
- [ ] Implement ConfigMigrator class
- [ ] Create configuration schemas
- [ ] Implement CLI commands (config, init)
- [ ] Add environment support
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update documentation

---

## 13. Open Questions

1. **Configuration Sync**: Should teams be able to sync project config via registry?
2. **Secrets Management**: How should sensitive values (license keys) be handled in version control?
3. **Configuration Profiles**: Should we support named profiles (like AWS CLI)?
4. **Configuration Templates**: Should we provide config templates for common setups?
5. **Remote Configuration**: Should configuration support remote URLs (e.g., team configs)?

---

## 14. Next Steps

1. Review and approve this design
2. Implement configuration classes
3. Integrate with domain loader
4. Add CLI commands
5. Create configuration examples
6. Write documentation

---

*This design provides flexible, hierarchical configuration management for multi-domain SCS deployments.*
