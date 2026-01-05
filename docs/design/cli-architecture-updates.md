# CLI Architecture Updates for Multi-Domain Support

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Executive Summary

This document defines updates to the SCS CLI to support multi-domain functionality. The CLI is the primary interface for developers working with SCS, and must provide intuitive, powerful commands for domain management, bundle creation, validation, and project initialization.

**Key Updates:**
- New `domain` command group for domain management
- Domain-aware existing commands (`init`, `validate`, `new`)
- Enhanced `config` commands
- Improved help system with domain-specific guidance
- Interactive and non-interactive modes

**Design Principles:**
- Backward compatible (existing commands work unchanged)
- Consistent command structure
- Domain-aware but with sensible defaults
- Rich output with progress indicators
- Machine-readable output option (JSON)

---

## 2. CLI Command Structure

### 2.1 Overall Command Hierarchy

```
scs
├── domain               # Domain management (NEW)
│   ├── list
│   ├── search
│   ├── info
│   ├── install
│   ├── uninstall
│   ├── activate
│   ├── deactivate
│   ├── licenses
│   ├── update
│   ├── set
│   ├── current
│   └── validate
│
├── init                 # Initialize project (UPDATED - domain-aware)
├── new                  # Create new artifacts (UPDATED - domain-aware)
│   ├── bundle
│   ├── scd
│   └── project
│
├── validate             # Validate bundles/SCDs (UPDATED - domain-aware)
├── build                # Build/package bundles
├── publish              # Publish to registry
│
├── config               # Configuration management (UPDATED)
│   ├── show
│   ├── get
│   ├── set
│   ├── edit
│   ├── validate
│   ├── resolve
│   └── backup
│
├── bundle               # Bundle operations
│   ├── list
│   ├── info
│   ├── graph
│   └── diff
│
├── registry             # Registry operations (NEW)
│   ├── login
│   ├── logout
│   ├── info
│   └── search
│
├── help                 # Context-sensitive help
├── version              # Show version info
└── upgrade              # Upgrade SCS itself
```

---

## 3. Domain Management Commands

### 3.1 `scs domain list`

**Purpose:** List available and installed domains

**Usage:**
```bash
# List all available domains
scs domain list

# List only installed domains
scs domain list --installed

# List only commercial domains
scs domain list --commercial

# JSON output
scs domain list --json
```

**Example Output:**
```
Available Domains:

  ID                         Name                        Status      License       Version
  ─────────────────────────────────────────────────────────────────────────────────────────
  domain:software-development  Software Development       Installed   Open          1.0.0
  domain:healthcare            Healthcare                 Installed   Commercial    1.0.0  ✓
  domain:sales                 Sales & Marketing          Available   Commercial    1.0.0
  domain:finance               Finance & Accounting       Available   Commercial    1.0.0
  domain:legal                 Legal & Compliance         Available   Commercial    1.0.0

  ✓ = Licensed and activated

To install a domain:
  scs domain install <domain>

To get more info:
  scs domain info <domain>
```

### 3.2 `scs domain search`

**Purpose:** Search for domains by keyword

**Usage:**
```bash
# Search domains
scs domain search health

# Search with filters
scs domain search medical --license commercial

# JSON output
scs domain search health --json
```

**Example Output:**
```
Search Results for "health":

  domain:healthcare
    Healthcare systems, clinical workflows, patient care
    Tags: healthcare, medical, clinical, hipaa, ehr
    License: Commercial | $99/user/month
    More info: scs domain info healthcare

  domain:health-insurance
    Health insurance claims, benefits administration
    Tags: healthcare, insurance, claims
    License: Commercial | $79/user/month
    More info: scs domain info health-insurance
```

### 3.3 `scs domain info`

**Purpose:** Show detailed information about a domain

**Usage:**
```bash
# Show domain information
scs domain info healthcare

# JSON output
scs domain info healthcare --json
```

**Example Output:**
```
Domain: healthcare
─────────────────────────────────────────────────────

  Name:         Healthcare
  ID:           domain:healthcare
  Version:      1.0.0
  Author:       SCS Commercial
  License:      Commercial ($99/user/month)
  Homepage:     https://scs-commercial.com/domains/healthcare

  Description:
    Structured context for healthcare systems, clinical workflows,
    patient care pathways, and medical data governance.

  Features:
    • Clinical workflow modeling
    • HIPAA compliance templates
    • HL7 FHIR integration patterns
    • Patient care pathway design
    • Medical device integration
    • Healthcare analytics

  Use Cases:
    • Electronic Health Records (EHR)
    • Patient portals
    • Clinical decision support
    • Telehealth platforms
    • Care coordination systems
    • Population health management

  Content Schemas:
    ✓ Meta-tier content schema
    ✓ Standards-tier content schema
    ✓ Project-tier content schema

  Templates:
    • ehr-system - Electronic Health Record systems
    • patient-portal - Patient portal applications
    • clinical-decision-support - Clinical decision support systems
    • telehealth-platform - Telehealth/telemedicine platforms

  Status:
    Installed:  Yes
    Location:   ~/.scs/domains/healthcare
    Licensed:   Yes
    Expires:    2026-12-12
    Seats:      5 (2 used)

  Documentation:
    https://docs.scs-commercial.com/domains/healthcare

  To use this domain:
    scs domain set healthcare
```

### 3.4 `scs domain install`

**Purpose:** Install a domain from the registry

**Usage:**
```bash
# Install free domain
scs domain install software-development

# Install commercial domain (prompts for license)
scs domain install healthcare

# Install with license key
scs domain install healthcare --license-key HC-XXXX-XXXX-XXXX-XXXX

# Install specific version
scs domain install healthcare@1.0.0

# Install from local file
scs domain install ./custom-domain.tar.gz

# Force reinstall
scs domain install healthcare --force
```

**Example Output:**
```
Installing domain: healthcare

  ✓ Checking license... Valid (expires 2026-12-12)
  ✓ Downloading package... 1.2 MB
  ✓ Verifying checksum... OK
  ✓ Extracting domain... 156 files
  ✓ Validating manifest... OK
  ✓ Loading schemas... 3 schemas loaded
  ✓ Registering domain... OK

Successfully installed domain:healthcare version 1.0.0

To activate for your project:
  scs domain set healthcare

To see available templates:
  scs domain info healthcare
```

### 3.5 `scs domain uninstall`

**Purpose:** Uninstall a domain

**Usage:**
```bash
# Uninstall domain
scs domain uninstall healthcare

# Force uninstall (skip checks)
scs domain uninstall healthcare --force
```

**Example Output:**
```
Uninstalling domain: healthcare

  Warning: This will remove domain:healthcare from your system.
  Projects using this domain will fail validation until reinstalled.

  Continue? [y/N]: y

  ✓ Removing domain files...
  ✓ Cleaning cache...
  ✓ Updating registry...

Successfully uninstalled domain:healthcare
```

### 3.6 `scs domain activate`

**Purpose:** Activate a license for a commercial domain

**Usage:**
```bash
# Activate with license key
scs domain activate healthcare --license-key HC-XXXX-XXXX-XXXX-XXXX

# Activate with stored key (from project config)
scs domain activate healthcare

# Offline activation
scs domain activate healthcare --offline
```

**Example Output:**
```
Activating license for domain:healthcare

  License Key: HC-****-****-****-XXXX
  Organization: Acme Healthcare
  Seats: 5

  ✓ Verifying license with registry...
  ✓ Activating license for this machine...
  ✓ Saving license information...

Successfully activated domain:healthcare

  Expires: 2026-12-12
  Seats Available: 5
  Seats Used: 1 (this machine)
```

### 3.7 `scs domain deactivate`

**Purpose:** Deactivate a license

**Usage:**
```bash
scs domain deactivate healthcare
```

### 3.8 `scs domain licenses`

**Purpose:** List all active licenses

**Usage:**
```bash
# List licenses
scs domain licenses

# Show detailed license info
scs domain licenses --detailed

# JSON output
scs domain licenses --json
```

**Example Output:**
```
Active Licenses:

  Domain        Status     Expires       Seats    Organization
  ──────────────────────────────────────────────────────────────
  healthcare    Active     2026-12-12    2/5      Acme Healthcare
  sales         Active     2026-11-30    1/10     Acme Corp

To activate a new license:
  scs domain activate <domain> --license-key <key>
```

### 3.9 `scs domain update`

**Purpose:** Update domains to newer versions

**Usage:**
```bash
# Check for updates
scs domain update --check

# Update specific domain
scs domain update healthcare

# Update all domains
scs domain update --all

# Dry run (show what would be updated)
scs domain update --all --dry-run
```

**Example Output:**
```
Checking for domain updates...

  Updates Available:

  Domain           Current    Latest    Release Date
  ──────────────────────────────────────────────────
  healthcare       1.0.0      1.1.0     2025-12-10
  sales            1.0.0      1.0.1     2025-12-08

  To update:
    scs domain update healthcare
    scs domain update sales

  Or update all:
    scs domain update --all
```

### 3.10 `scs domain set`

**Purpose:** Set the active domain for the current project

**Usage:**
```bash
# Set project domain
scs domain set healthcare

# Set global default domain
scs domain set healthcare --global
```

**Example Output:**
```
Setting project domain to: healthcare

  ✓ Checking domain installed... OK
  ✓ Checking license... Valid
  ✓ Updating project config...

Project domain set to domain:healthcare

Your bundles and SCDs will now use healthcare domain schemas.

To create a new bundle:
  scs new bundle my-healthcare-system

Available templates:
  • ehr-system
  • patient-portal
  • clinical-decision-support
  • telehealth-platform
```

### 3.11 `scs domain current`

**Purpose:** Show the current active domain

**Usage:**
```bash
# Show current domain
scs domain current

# Show domain resolution (how domain was selected)
scs domain current --resolve
```

**Example Output:**
```
Current Domain: healthcare

  ID:       domain:healthcare
  Version:  1.0.0
  Scope:    Project (from .scs/config.yaml)
  Licensed: Yes (expires 2026-12-12)

Domain Resolution:
  1. Bundle domain: (not set)
  2. Project domain: domain:healthcare ← Active
  3. Global default: domain:software-development
  4. Hardcoded default: domain:software-development
```

### 3.12 `scs domain validate`

**Purpose:** Validate a domain installation

**Usage:**
```bash
# Validate domain
scs domain validate healthcare

# Validate all installed domains
scs domain validate --all
```

**Example Output:**
```
Validating domain: healthcare

  ✓ Domain manifest... OK
  ✓ Meta-tier schema... OK
  ✓ Standards-tier schema... OK
  ✓ Project-tier schema... OK
  ✓ Templates... OK (4 templates)
  ✓ Validation rules... OK
  ✓ Examples... OK (2 examples)
  ✓ Dependencies... OK

Domain validation passed!
```

---

## 4. Updated Existing Commands

### 4.1 `scs init` (Updated)

**Purpose:** Initialize a new SCS project with domain support

**Usage:**
```bash
# Initialize with default domain
scs init

# Initialize with specific domain
scs init --domain healthcare

# Initialize with template
scs init --domain healthcare --template ehr-system

# Initialize with name
scs init --name "Patient Care System" --domain healthcare

# Non-interactive mode
scs init --domain healthcare --name "My Project" --no-interactive
```

**Example Output (Interactive):**
```
Initialize New SCS Project
─────────────────────────────────────

  Project Name: Patient Care System
  Directory: ./patient-care-system

  Select Domain:
    1. software-development (Open)
    2. healthcare (Commercial) ✓ Licensed
    3. sales (Commercial)
    4. Other...

  Choice [2]: 2

  Domain: healthcare

  Select Template:
    1. ehr-system - Electronic Health Record systems
    2. patient-portal - Patient portal applications
    3. clinical-decision-support - Clinical decision support systems
    4. telehealth-platform - Telehealth/telemedicine platforms
    5. Start from scratch

  Choice [1]: 1

  Creating project...

  ✓ Creating directory structure...
  ✓ Initializing configuration...
  ✓ Creating bundle from template...
  ✓ Creating example SCDs...
  ✓ Initializing git repository...

Successfully created project: Patient Care System

  Location: ./patient-care-system
  Domain: healthcare
  Template: ehr-system

Next steps:
  cd patient-care-system
  scs validate
  scs new scd my-clinical-workflow
```

### 4.2 `scs validate` (Updated)

**Purpose:** Validate bundles and SCDs with domain awareness

**Usage:**
```bash
# Validate current project
scs validate

# Validate specific bundle
scs validate bundles/project-bundle.yaml

# Validate with explicit domain
scs validate --domain healthcare

# Validate with environment
scs validate --env production

# Strict mode (warnings become errors)
scs validate --strict

# JSON output
scs validate --json

# Watch mode (continuous validation)
scs validate --watch
```

**Example Output:**
```
Validating SCS Project
─────────────────────────────────────

  Project: Patient Care System
  Domain: healthcare (1.0.0)
  Bundle: bundles/project-bundle.yaml

  Structural Validation:
    ✓ Bundle schema... OK
    ✓ SCD references... OK (24 SCDs)
    ✓ Import resolution... OK (12 imports)

  Domain Validation (healthcare):
    ✓ Meta-tier content... OK (3 SCDs)
    ✓ Standards-tier content... OK (5 SCDs)
    ✓ Project-tier content... OK (16 SCDs)

  Relationship Validation:
    ✓ Cross-references... OK
    ✓ Dependency cycles... None found
    ⚠ Missing relationships... 2 warnings

  Compliance Validation:
    ✓ HIPAA requirements... OK
    ✓ HL7 FHIR compliance... OK

  Warnings (2):
    • SCD scd:project:patient-data missing relationship to security bundle
    • SCD scd:project:care-pathways missing clinical_protocols field

Validation passed with 2 warnings.

To fix warnings:
  scs validate --fix

To see detailed report:
  scs validate --verbose
```

### 4.3 `scs new` (Updated)

**Purpose:** Create new bundles and SCDs with domain-aware templates

**Usage:**
```bash
# Create new bundle from template
scs new bundle my-system

# Create new bundle with specific template
scs new bundle my-system --template ehr-system

# Create new SCD
scs new scd care-pathways --tier project

# Create new SCD with explicit domain
scs new scd care-pathways --tier project --domain healthcare

# Interactive mode
scs new scd --interactive
```

**Example Output:**
```
Create New SCD
─────────────────────────────────────

  Name: care-pathways
  Tier: project
  Domain: healthcare (from project config)
  Template: project-scd (healthcare)

  ✓ Creating SCD file...
  ✓ Populating from template...
  ✓ Validating...

Successfully created: context/project/care-pathways.yaml

  SCD ID: scd:project:care-pathways
  Domain: healthcare
  Content Schema: Healthcare project-tier schema

Next steps:
  1. Edit context/project/care-pathways.yaml
  2. Add clinical workflows and care pathways
  3. Validate: scs validate
  4. Add to bundle: scs bundle add scd:project:care-pathways
```

---

## 5. Configuration Commands (Updated)

### 5.1 `scs config show`

**Purpose:** Display configuration

**Usage:**
```bash
# Show project config
scs config show

# Show global config
scs config show --global

# Show effective config (merged hierarchy)
scs config show --effective

# Show specific section
scs config show project

# JSON output
scs config show --json
```

### 5.2 `scs config get`

**Purpose:** Get a specific configuration value

**Usage:**
```bash
# Get value with dot notation
scs config get project.domain

# Get from global config
scs config get scs.default_domain --global

# Output only the value (for scripting)
scs config get project.domain --value-only
```

### 5.3 `scs config set`

**Purpose:** Set a configuration value

**Usage:**
```bash
# Set project config value
scs config set project.domain domain:healthcare

# Set global config value
scs config set scs.default_domain domain:healthcare --global

# Set nested value
scs config set project.validation.strict true
```

### 5.4 `scs config resolve`

**Purpose:** Show how configuration is resolved

**Usage:**
```bash
# Show domain resolution
scs config resolve domain

# Show validation settings resolution
scs config resolve validation

# Show full resolution
scs config resolve --all
```

**Example Output:**
```
Configuration Resolution: domain
─────────────────────────────────────

  Source                  Value                        Priority
  ──────────────────────────────────────────────────────────────
  Bundle                  (not set)                    1 (highest)
  Project                 domain:healthcare            2 ← Active
  Global                  domain:software-development  3
  Hardcoded Default       domain:software-development  4 (lowest)

Effective Value: domain:healthcare (from Project config)
```

---

## 6. New Registry Commands

### 6.1 `scs registry login`

**Purpose:** Authenticate with domain registry

**Usage:**
```bash
# Login with credentials
scs registry login

# Login with token
scs registry login --token <token>
```

### 6.2 `scs registry info`

**Purpose:** Show registry information

**Usage:**
```bash
# Show registry info
scs registry info

# Check connection
scs registry info --check
```

### 6.3 `scs registry search`

**Purpose:** Search registry for domains

**Usage:**
```bash
# Search registry
scs registry search healthcare

# Advanced search
scs registry search --tag clinical --license commercial
```

---

## 7. CLI Architecture

### 7.1 Command Framework

```python
# cli/__init__.py

import click
from .commands import domain, init, validate, config, new, bundle

@click.group()
@click.version_option()
@click.option('--config', '-c', help='Config file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--json', is_flag=True, help='JSON output')
@click.pass_context
def cli(ctx, config, verbose, json):
    """SCS - Structured Context Specification CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['json_output'] = json
    ctx.obj['config_path'] = config

# Register command groups
cli.add_command(domain.domain)
cli.add_command(init.init)
cli.add_command(validate.validate)
cli.add_command(config.config)
cli.add_command(new.new)
cli.add_command(bundle.bundle)
```

### 7.2 Domain Command Group

```python
# cli/commands/domain.py

import click
from scs.domains import DomainLoader, DomainRegistry

@click.group()
def domain():
    """Manage pluggable domains"""
    pass

@domain.command()
@click.option('--installed', is_flag=True, help='Show only installed domains')
@click.option('--commercial', is_flag=True, help='Show only commercial domains')
@click.option('--json', is_flag=True, help='JSON output')
@click.pass_context
def list(ctx, installed, commercial, json):
    """List available domains"""
    loader = DomainLoader()
    registry = DomainRegistry()

    if installed:
        domains = loader.discover_domains()
    else:
        domains = registry.list_domains()

    if commercial:
        domains = [d for d in domains if d.license == 'commercial']

    if json or ctx.obj.get('json_output'):
        output_json(domains)
    else:
        output_table(domains)

@domain.command()
@click.argument('domain_id')
@click.option('--license-key', '-k', help='License key for commercial domains')
@click.option('--force', is_flag=True, help='Force reinstall')
def install(domain_id, license_key, force):
    """Install a domain from registry"""
    # Implementation
    pass

# ... more commands ...
```

---

## 8. Output Formatting

### 8.1 Rich Terminal Output

Use `rich` library for beautiful terminal output:

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel

console = Console()

def output_table(domains):
    """Display domains as a rich table"""
    table = Table(title="Available Domains")

    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("License")
    table.add_column("Version")

    for domain in domains:
        table.add_row(
            domain.id,
            domain.name,
            "Installed" if domain.installed else "Available",
            domain.license,
            domain.version
        )

    console.print(table)

def output_progress(tasks):
    """Show progress for long-running operations"""
    with Progress() as progress:
        task = progress.add_task("[cyan]Installing domain...", total=len(tasks))

        for subtask in tasks:
            progress.console.print(f"  ✓ {subtask}")
            progress.advance(task)
```

### 8.2 JSON Output

All commands support `--json` flag for machine-readable output:

```python
def output_json(data):
    """Output data as JSON"""
    import json
    print(json.dumps(data, indent=2, default=str))
```

---

## 9. Interactive Mode

### 9.1 Interactive Prompts

Use `questionary` or `click.prompt` for interactive flows:

```python
import questionary

def interactive_init():
    """Interactive project initialization"""

    # Project name
    name = questionary.text(
        "Project name:",
        default="my-project"
    ).ask()

    # Domain selection
    domains = loader.discover_domains()
    domain_choices = [f"{d.name} ({d.license})" for d in domains]

    domain_selection = questionary.select(
        "Select domain:",
        choices=domain_choices
    ).ask()

    # Template selection
    templates = get_templates(selected_domain)
    template = questionary.select(
        "Select template:",
        choices=templates
    ).ask()

    # Confirmation
    confirmed = questionary.confirm(
        f"Create project '{name}' with domain '{domain}'?"
    ).ask()

    if confirmed:
        create_project(name, domain, template)
```

---

## 10. Error Handling

### 10.1 User-Friendly Error Messages

```python
class CLIError(Exception):
    """Base CLI error with user-friendly message"""

    def __init__(self, message, suggestion=None, details=None):
        self.message = message
        self.suggestion = suggestion
        self.details = details

def handle_error(error):
    """Display user-friendly error"""
    console.print(f"\n[bold red]Error:[/bold red] {error.message}\n")

    if error.suggestion:
        console.print(f"[yellow]Suggestion:[/yellow] {error.suggestion}\n")

    if error.details and verbose:
        console.print(Panel(error.details, title="Details"))
```

**Example Error Output:**
```
Error: Domain 'domain:healthcare' not found.

Suggestion: To install this domain:
  scs domain install healthcare

Details:
  Looked in: ~/.scs/domains/healthcare
  Available domains: software-development, sales
  Registry URL: https://registry.scs-commercial.com
```

---

## 11. Help System

### 11.1 Context-Sensitive Help

```python
@click.command()
@click.pass_context
def help(ctx):
    """
    Show help based on current context (project domain, config).
    """
    # Detect current domain
    domain = resolve_domain()

    # Show domain-specific help
    console.print(f"\n[bold]SCS Help - {domain.name} Domain[/bold]\n")

    # Show relevant commands
    console.print("[cyan]Common commands:[/cyan]")
    console.print("  scs new bundle <name>  - Create new bundle")
    console.print(f"  scs new scd <name>     - Create new {domain.name} SCD")
    console.print("  scs validate           - Validate project")

    # Show domain-specific templates
    console.print(f"\n[cyan]Available templates:[/cyan]")
    for template in domain.templates:
        console.print(f"  • {template.name} - {template.description}")
```

---

## 12. Implementation Plan

### 12.1 Phase 1: Core Commands

- [ ] Implement `domain` command group
- [ ] Update `init` command for domain support
- [ ] Update `validate` command for domain validation
- [ ] Implement `config` commands

### 12.2 Phase 2: Enhanced Commands

- [ ] Update `new` command with domain templates
- [ ] Implement `registry` commands
- [ ] Add interactive modes
- [ ] Implement rich output formatting

### 12.3 Phase 3: Polish

- [ ] Add progress indicators
- [ ] Improve error messages
- [ ] Add context-sensitive help
- [ ] Implement `--json` output for all commands
- [ ] Add shell completion (bash, zsh, fish)

---

## 13. Testing Strategy

### 13.1 Unit Tests

```python
def test_domain_list_command():
    """Test domain list command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['domain', 'list'])
    assert result.exit_code == 0
    assert 'software-development' in result.output

def test_domain_install_command():
    """Test domain install"""
    runner = CliRunner()
    result = runner.invoke(cli, ['domain', 'install', 'healthcare'])
    # Assert success
```

### 13.2 Integration Tests

```python
def test_init_with_domain(tmp_path):
    """Test project initialization with domain"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, [
            'init',
            '--name', 'test-project',
            '--domain', 'healthcare',
            '--no-interactive'
        ])

        assert result.exit_code == 0
        assert (tmp_path / 'test-project' / '.scs' / 'config.yaml').exists()
```

---

## 14. Dependencies

**Required Libraries:**
- `click` - CLI framework
- `rich` - Rich terminal output
- `questionary` - Interactive prompts
- `pyyaml` - YAML parsing
- `requests` - HTTP client for registry
- `jsonschema` - Schema validation

**Optional:**
- `click-completion` - Shell completion
- `colorama` - Windows color support

---

## 15. Open Questions

1. **Shell Completion**: Which shells to support (bash, zsh, fish)?
2. **Progress Indicators**: How detailed should progress output be?
3. **Offline Mode**: Should all commands have an offline fallback?
4. **Plugin System**: Should CLI support plugins for custom commands?
5. **Telemetry**: Should we collect anonymous usage data?

---

## 16. Next Steps

1. Review and approve this design
2. Set up CLI project structure
3. Implement core command framework
4. Implement domain commands
5. Update existing commands
6. Add tests
7. Write CLI documentation
8. Create demo videos

---

*This design provides a comprehensive, user-friendly CLI for managing multi-domain SCS projects.*
