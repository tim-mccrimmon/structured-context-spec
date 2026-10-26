# {{ project_name }}

**Bundle type**: {{ bundle_kind | capitalize }}
**Ontology model**: {{ ontology }}
**Domain repository**: {{ repo_name }}
**Created**: {{ created_at }}

## Overview

{% if bundle_kind == 'domain' -%}
This workspace holds {{ project_name }}'s **Domain bundle**: the governance that applies to all of
{% if ontology == 'personal' %}your work, whichever project it is part of. It uses the personal ontology: it starts with
your boundaries (the prohibited concept) only, and you add the concepts your context needs.{% else %}the organization's work, whichever project it is part of. It starts from the {{ domain_name }}
ontology model; keep what applies, remove what does not, and fill it in with your
organization's own rules.{% endif %}
{%- else -%}
This workspace holds the **Project bundle** for {{ project_name }}: the governance for this
project. It is independent of your organization's Domain bundle; a runtime applies the two side
by side.
{%- endif %}

## Structure

```
{{ workspace_dir }}/
├── bundles/
│   ├── {{ bundle_kind }}-bundle.yaml{{ '     ' if bundle_kind == 'domain' else '    ' }}# The {{ bundle_kind | capitalize }} bundle (compile this)
│   └── concepts/              # One concept bundle per ontology concept
├── context/
│   └── project/               # SCDs: write directives, prohibitions, and facts here
├── ontology/
│   └── domain-manifest.yaml   # The Domain Ontology
├── dist/                      # Compiled artifacts (scs compile)
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
2. Validate: `scs-validate --strict` at the repository root, or `scs bundle validate` here
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
