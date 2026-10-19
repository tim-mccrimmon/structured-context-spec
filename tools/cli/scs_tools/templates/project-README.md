# {{ project_name }}

**Bundle type**: {{ bundle_kind | capitalize }}
**Ontology model**: {{ ontology }}{% if ontology == 'sdlc' %} ({{ project_type }}){% endif %}
**Created**: {{ created_at }}

## Overview

{% if bundle_kind == 'domain' -%}
This workspace holds {{ project_name }}'s **Domain bundle**: the governance that applies to all of
the organization's work, whichever project it is part of. It starts from the {{ domain_name }}
ontology model; fill it in with your organization's own rules.
{%- else -%}
This workspace holds the **Project bundle** for {{ project_name }}: the governance for this
project. It is independent of your organization's Domain bundle; a runtime applies the two side
by side.
{%- endif %}

## Structure

```
{{ project_name }}/
├── bundles/
│   ├── {{ bundle_kind }}-bundle.yaml{{ '     ' if bundle_kind == 'domain' else '    ' }}# The {{ bundle_kind | capitalize }} bundle (compile this)
│   └── concepts/              # One concept bundle per ontology concept
├── context/
│   └── project/               # SCDs: write directives, prohibitions, and facts here
├── domain/
│   └── domain-manifest.yaml   # The Domain Ontology
├── docs/
│   └── GETTING_STARTED.md
├── .scs/
│   └── config
└── README.md
```
{% if bundle_kind == 'domain' %}
The Domain bundle imports `{{ meta_bundle_ref }}`, the meta bundle published with the SCS
specification. It is not in this workspace; the SCS tools ship a copy.
{% endif %}
## Working With This Workspace

1. Write the SCDs under `context/project/`: directives (rules an AI agent should follow),
   prohibitions (tools and practices that are forbidden, with no conditions), and facts
   (what an agent should know). Cite standards with `std:` references.
2. Validate: `scs bundle validate`
3. Compile: `scs compile bundles/{{ bundle_kind }}-bundle.yaml --allow-draft`
4. Version: `scs bundle version --bundle bundles/{{ bundle_kind }}-bundle.yaml --version 1.0.0`

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## SCS Resources

- [SCS Specification](https://github.com/tim-mccrimmon/scs-spec)
- [Examples](https://github.com/tim-mccrimmon/scs-spec/tree/main/examples)

## Provenance

- **Author**: {{ author }}
- **Email**: {{ email }}
- **Created At**: {{ created_at }}
