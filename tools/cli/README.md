# SCS Tools

Complete CLI toolkit for creating, managing, and validating Structured Context Specification (SCS) projects.

## Overview

`scs-tools` provides everything you need to work with SCS projects:

- **Scaffold** new SCS projects with proper structure and templates
- **Initialize** SCS in existing projects
- **Add** SCDs and domain bundles incrementally
- **Manage** bundles and project configuration
- **Validate** SCDs and bundles against the specification

## Do I Need Both Tools?

**No - just install `scs-tools`.**

The SCS ecosystem includes two packages:
- **`scs-tools`** (this package) - Full CLI toolkit for project management
- **`scs-validator`** (in `scs-spec/tools/scd-validator`) - Standalone validator

The `scs-validator` is included as a dependency of `scs-tools`, so installing `scs-tools` gives you everything. The standalone validator is only needed if you want validation without the project management features.

## Installation

### From PyPI

```bash
pip install scs-tools
```

This automatically installs `scs-validator` as an optional dependency (use `pip install scs-tools[validator]` for validation features).

### From Source

```bash
# Clone the main repo
git clone https://github.com/tim-mccrimmon/structured-context-spec.git

# Navigate to CLI directory
cd structured-context-spec/tools/cli

# Install in development mode
pip install -e .
```

### For Development

```bash
cd scs-cli
pip install -e ".[dev]"
```

## Commands

The `scs` command provides five main subcommands:

### 1. `scs new` - Create New Projects

Scaffold a complete SCS project from templates.

```bash
# Basic usage - creates standard project
scs new project my-project

# Healthcare application (HIPAA, CHAI, TEFCA)
scs new project medication-adherence --type healthcare

# Financial services (PCI-DSS, SOX)
scs new project banking-app --type fintech

# SaaS product (GDPR, SOC2)
scs new project my-saas --type saas

# Government application (NIST, FedRAMP)
scs new project gov-portal --type government

# Minimal project (11 essential SCDs)
scs new project prototype --type minimal

# Standard project (38 minimum SCDs)
scs new project my-app --type standard
```

**Options:**
```bash
# Specify output directory
scs new project my-app --dir /path/to/projects

# Add author information
scs new project my-app --author "Jane Doe" --email "jane@example.com"

# Interactive mode (prompts for all options)
scs new project my-app --interactive
```

### 2. `scs init` - Initialize Existing Projects

Add SCS structure to an existing project.

```bash
# Initialize in current directory
scs init

# Initialize with specific project type
scs init --type healthcare

# Initialize in specific directory
scs init --dir /path/to/existing/project
```

### 3. `scs add` - Add SCDs and Bundles

Incrementally add SCDs or domain bundles to your project.

```bash
# Add a specific SCD
scs add scd system-context

# Add a domain bundle
scs add bundle security

# Add multiple SCDs
scs add scd authn-authz data-protection threat-model

# Add domain bundle with all related SCDs
scs add bundle compliance-governance --with-scds
```

### 4. `scs bundle` - Manage Bundles

Create and manage SCD bundles.

```bash
# Create a bundle from SCDs
scs bundle create --name my-bundle --scds context/project/*.yaml

# List all bundles
scs bundle list

# Update a bundle
scs bundle update bundles/project-bundle.yaml

# Validate bundle completeness
scs bundle check bundles/project-bundle.yaml
```

### 5. `scs validate` - Validate SCDs and Bundles

Validate SCS documents against the specification. This command wraps the `scs-validator` tool.

```bash
# Validate a single SCD file
scs validate context/project/system-context.yaml

# Validate multiple SCD files
scs validate context/project/*.yaml

# Validate a bundle
scs validate --bundle bundles/project-bundle.yaml

# Strict mode (fail on warnings)
scs validate --bundle bundles/project-bundle.yaml --strict

# JSON output
scs validate --bundle bundles/project-bundle.yaml --output json

# Skip completeness checks
scs validate --bundle bundles/project-bundle.yaml --skip-completeness
```

**Validation Options:**
- `--bundle` - Validate a bundle file instead of individual SCDs
- `--schema-dir` - Specify custom schema directory
- `--output [text|json]` - Output format (default: text)
- `--strict` - Fail on warnings (exit code 2)
- `--no-color` - Disable colored output
- `--verbose` - Verbose output
- `--skip-completeness` - Skip Level 6 completeness validation

**Note:** The `scs validate` command uses the `scs-validator` package under the hood. For detailed validation documentation, see the [SCS Validator README](https://github.com/tim-mccrimmon/scs-spec/tree/main/tools/scd-validator).

### Help

Get help for any command:

```bash
scs --help
scs new --help
scs init --help
scs add --help
scs bundle --help
scs validate --help
```

## Project Structure

A generated SCS project has this structure:

```
my-project/
├── bundles/                    # SCS bundles
│   ├── project-bundle.yaml    # Top-level bundle
│   ├── meta-bundle.yaml       # Meta vocabulary
│   ├── standards-bundle.yaml  # Compliance standards
│   └── domains/               # Domain bundles
│       ├── architecture.yaml
│       ├── security.yaml
│       ├── performance-reliability.yaml
│       ├── usability-accessibility.yaml
│       ├── compliance-governance.yaml
│       ├── data-provenance.yaml
│       ├── testing-validation.yaml
│       ├── deployment-operations.yaml
│       ├── safety-risk.yaml
│       └── ethics-ai-accountability.yaml
├── context/                   # SCD files
│   └── project/              # Project-tier SCDs
│       ├── system-context.yaml
│       ├── tech-stack.yaml
│       ├── integration-map.yaml
│       ├── component-model.yaml
│       ├── authn-authz.yaml
│       ├── data-protection.yaml
│       └── ... (30+ more SCDs)
├── docs/
│   └── GETTING_STARTED.md
├── .scs/
│   └── config
├── .gitignore
├── README.md
└── VERSION
```

## Domain Bundles

Projects include 10 domain bundles covering:

1. **Architecture**: System design, tech stack, integrations, components
2. **Security**: Authentication, data protection, threat model
3. **Performance & Reliability**: Response time, availability, fault tolerance, scalability
4. **Usability & Accessibility**: UX principles, accessibility compliance, error handling
5. **Compliance & Governance**: Regulatory requirements (HIPAA, SOC2, etc.)
6. **Data & Provenance**: Data model, lineage tracking, retention policies
7. **Testing & Validation**: Test coverage, validation plans, QA procedures
8. **Deployment & Operations**: Infrastructure, observability, incident response
9. **Safety & Risk**: Risk assessment, safety checklists
10. **Ethics & AI Accountability**: AI usage policy, audit trails, bias mitigation

## SCD Templates

Each SCD template includes:

- Proper YAML structure with id, type, version, status
- Domain and concern tags
- Comprehensive content placeholders with examples
- Provenance tracking
- Inline documentation and guidance

## Project Types Comparison

| Feature | Minimal | Standard | Healthcare | Fintech | SaaS | Government |
|---------|---------|----------|------------|---------|------|------------|
| Architecture SCDs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Security SCDs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Performance SCDs | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| Compliance SCDs | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| HIPAA/CHAI | - | - | ✓ | - | - | - |
| PCI-DSS/SOX | - | - | - | ✓ | - | - |
| GDPR | - | - | - | - | ✓ | - |
| NIST/FedRAMP | - | - | - | - | - | ✓ |
| Total SCDs | ~11 | ~38 | ~38 | ~38 | ~38 | ~38 |

## Validation

The `scs validate` command provides comprehensive validation:

### Validation Levels

1. **Syntax Validation** - Ensures YAML/JSON is well-formed
2. **Schema Validation** - Validates against tier-specific JSON schemas
3. **Semantic Validation** - Checks type/tier matching, semver, provenance
4. **Relationship Validation** - Validates references between SCDs
5. **Bundle Completeness** - Ensures all required SCDs are present
6. **Compliance Validation** - Domain-specific requirement checks

### Exit Codes

- `0` - Validation passed (no errors)
- `1` - Validation failed (errors found)
- `2` - Validation passed with warnings (when `--strict` enabled)
- `3` - Invalid command-line arguments
- `4` - File not found or permission error
- `5` - Internal validator error

## What is SCS?

The Structured Context Specification (SCS) provides a standardized way to organize project context for AI-assisted development, compliance, and governance.

SCS enables:

- **AI Context Injection**: Provide LLMs with precise, relevant context
- **Compliance Evidence**: Map requirements to implementation
- **Knowledge Management**: Version-controlled project knowledge
- **Team Alignment**: Shared understanding of decisions and rationale
- **Audit Trails**: Track what was decided, when, and why

## OICP Control Plane Integration

The `scs-tools` CLI creates and validates bundles **locally** (file-based workflow). For **Context as a Service** deployment, use the OICP Control Plane.

### Publishing to OICP Control Plane

Once you've built and validated bundles locally, publish them to the OICP Registry:

```bash
# Build and validate locally
scs new project my-healthcare-app --type healthcare
cd my-healthcare-app
scs validate --bundle bundles/project-bundle.yaml

# Publish to OICP Control Plane (via API)
curl -X POST http://localhost:8000/api/bundles \
  -H "Content-Type: application/json" \
  -d @bundles/project-bundle.yaml

# Create tag for agents to subscribe to
curl -X POST http://localhost:8000/api/tags \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "my-app:latest",
    "bundle_id": "bundle:my-healthcare-app:1.0.0"
  }'
```

### Context Streaming to AI Agents

Once published, AI agents can subscribe to your bundles:

```python
# Agent subscribes to tag and receives context stream
import grpc
from context_service import context_service_pb2_grpc

stream = context_service.Subscribe(
    tag="my-app:latest",
    agent_id="agent-001"
)

# Agent receives context and automatic updates
for message in stream:
    # Use context in agent execution
    ...
```

**Benefits of OICP Deployment:**
- **Real-time updates**: Update context across all agents instantly (zero downtime)
- **Perfect audit trail**: Track what context each agent had at any timestamp
- **Version management**: Tags + semantic versioning (like Docker)
- **Import resolution**: Automatically resolve bundle dependencies

**See Also:**
- [Control Plane README](/control-plane/README.md) - OICP architecture and APIs
- [Agent Integration Test Case](/test-plan/AGENT-CONTEXT-INJECTION.md) - How agents use context
- [Context Service README](/control-plane/context_service/README.md) - gRPC streaming details

## Common Workflows

### Starting a New Healthcare Project

```bash
# Create project
scs new project patient-portal --type healthcare --author "Dr. Smith"
cd patient-portal

# Customize SCDs
# Edit context/project/system-context.yaml
# Edit context/project/hipaa-compliance.yaml
# Edit context/project/chai-adherence.yaml

# Validate your work
scs validate --bundle bundles/project-bundle.yaml

# Create versioned bundle for AI context
scs bundle create --name v1.0.0 --scds context/project/*.yaml
```

### Adding SCS to Existing Project

```bash
# Navigate to your project
cd my-existing-project

# Initialize SCS
scs init --type saas

# Add specific domains you need
scs add bundle security --with-scds
scs add bundle compliance-governance --with-scds

# Customize for your project
# Edit the generated SCDs

# Validate
scs validate context/project/*.yaml
```

### Incremental SCD Development

```bash
# Start minimal
scs new project mvp --type minimal

# Add SCDs as you need them
scs add scd system-context
scs add scd tech-stack
scs add scd authn-authz

# Validate incrementally
scs validate context/project/system-context.yaml

# When ready, add full domain
scs add bundle security --with-scds

# Validate complete bundle
scs validate --bundle bundles/project-bundle.yaml --strict
```

## Examples

### Healthcare Application

```bash
scs new project medication-adherence --type healthcare
cd medication-adherence

# The project includes:
# - HIPAA compliance SCDs
# - CHAI adherence SCDs
# - TEFCA interoperability SCDs
# - Standard security, architecture, operations

# Customize and validate
scs validate --bundle bundles/project-bundle.yaml
```

### SaaS Product

```bash
scs new project todo-app --type saas
cd todo-app

# The project includes:
# - GDPR compliance SCDs
# - SOC2 controls
# - Multi-tenancy architecture
# - Standard security and operations

# Validate
scs validate --bundle bundles/project-bundle.yaml --strict
```

### Minimal Prototype

```bash
scs new project mvp --type minimal
cd mvp

# Includes only essential SCDs:
# - System context
# - Tech stack
# - Authentication/authorization
# - Data protection
# - Deployment config
# - (11 core SCDs)

# Expand later with:
scs add bundle performance-reliability --with-scds
scs add bundle compliance-governance --with-scds
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate SCS

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install SCS Tools
        run: pip install scs-tools

      - name: Validate SCS Bundle
        run: |
          scs validate --bundle bundles/project-bundle.yaml \
            --strict \
            --output json > validation-report.json

      - name: Upload validation report
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating SCS bundle..."
scs validate --bundle bundles/project-bundle.yaml --strict

if [ $? -ne 0 ]; then
  echo "❌ SCS validation failed"
  exit 1
fi

echo "✓ SCS validation passed"
```

## Resources

- [SCS Specification](https://github.com/tim-mccrimmon/scs-spec)
- [SCS Validator](https://github.com/tim-mccrimmon/scs-spec/tree/main/tools/scd-validator) - Standalone validation tool
- [Documentation](https://github.com/tim-mccrimmon/scs-spec/tree/main/docs)
- [Minimum Project SCDs](https://github.com/tim-mccrimmon/scs-spec/blob/main/docs/random_docs/minimum-project-scds.md)
- [Examples](https://github.com/tim-mccrimmon/scs-spec/tree/main/examples)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

See [CONTRIBUTING.md](https://github.com/tim-mccrimmon/scs-spec/blob/main/CONTRIBUTING.md) for details.

## License

MIT License - see LICENSE file for details

## Support

- [GitHub Issues](https://github.com/tim-mccrimmon/scs-spec/issues)
- [Discussions](https://github.com/tim-mccrimmon/scs-spec/discussions)

## Version

Current version: 0.1.0

## Changelog

### 0.1.0 (Initial Release)

- Project scaffolding with `scs new project`
- Project initialization with `scs init`
- Incremental SCD/bundle addition with `scs add`
- Bundle management with `scs bundle`
- Integrated validation with `scs validate`
- Support for 6 project types (minimal, standard, healthcare, fintech, saas, government)
- 38 SCD templates across 10 domains
- Jinja2 templating system
- Comprehensive documentation
