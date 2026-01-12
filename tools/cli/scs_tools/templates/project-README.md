# {{ project_name }}

**Project Type**: {{ project_type }}
**SCS Version**: 0.1.0
**Created**: {{ created_at }}

## Overview

This project follows the Structured Context Specification (SCS) for organizing project context, requirements, and compliance information.

## Project Structure

```
{{ project_name }}/
├── bundles/                    # SCS bundles
│   ├── project-bundle.yaml    # Top-level project bundle
│   ├── meta-bundle.yaml       # Meta vocabulary bundle
│   ├── standards-bundle.yaml  # Compliance standards bundle
│   └── domains/               # Domain-specific bundles
│       ├── architecture.yaml
│       ├── security.yaml
│       └── ...
├── context/                   # SCD files
│   └── project/              # Project-tier SCDs
│       ├── system-context.yaml
│       ├── tech-stack.yaml
│       └── ...
├── docs/                      # Documentation
│   └── GETTING_STARTED.md
├── .scs/                      # SCS configuration
│   └── config
└── README.md                  # This file
```

## Getting Started

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed instructions on:
- Understanding the SCS structure
- Editing SCDs and bundles
- Working with domains and concerns
- Validating your context

## SCDs Included

This project includes the minimum recommended set of SCDs for a {{ project_type }} project:

{% for bundle in bundles -%}
- **{{ bundle }}**: Domain bundle for {{ bundle }} concerns
{% endfor %}

## Editing Context

All context is stored in YAML files:

1. **SCDs** (`context/project/*.yaml`): Structured Context Documents containing specific project information
2. **Bundles** (`bundles/**/*.yaml`): Organize and group related SCDs

Start by editing the SCDs in `context/project/` to match your project requirements.

## SCS Resources

- [SCS Specification](https://github.com/tim-mccrimmon/scs-spec)
- [Documentation](https://github.com/tim-mccrimmon/scs-spec/tree/main/docs)
- [Examples](https://github.com/tim-mccrimmon/scs-spec/tree/main/examples)

## Provenance

- **Author**: {{ author }}
- **Email**: {{ email }}
- **Created At**: {{ created_at }}
- **Generator**: scs-tools v0.1.0
