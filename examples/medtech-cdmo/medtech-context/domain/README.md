# MedTech CDMO

**Bundle type**: Domain
**Ontology model**: cdmo
**Domain repository**: medtech-context
**Created**: 2026-10-01T09:00:00+00:00

## Overview

This workspace holds MedTech CDMO's **Domain bundle**: the governance that applies to all of
the organization's work, whichever project it is part of. It starts from the Medical-Device CDMO
ontology model; keep what applies, remove what does not, and fill it in with your
organization's own rules.

## Structure

```
domain/
├── bundles/
│   ├── domain-bundle.yaml     # The Domain bundle (compile this)
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

The Domain bundle imports `bundle:meta:0.6.0`, the meta bundle published with the SCS
specification. It is not in this workspace; the SCS tools ship a copy.

## Working With This Workspace

1. Write the SCDs under `context/project/`: directives (rules an AI agent should follow),
   prohibitions (tools and practices that are forbidden, with no conditions), and facts
   (what an agent should know). Cite standards with `std:` references.
2. Validate: `scs-validate --strict` at the repository root, or `scs bundle validate` here
3. Compile: `scs compile bundles/domain-bundle.yaml --allow-draft`
4. Version bottom-up: each concept bundle first
   (`scs bundle version --bundle bundles/concepts/<name>.yaml --version 1.0.0 --approved-by "Name <email>"`),
   pin it in `bundles/domain-bundle.yaml` as `bundle:<name>:1.0.0`, then version
   `bundles/domain-bundle.yaml`. Each version is a git tag.
5. Compile the released version: `scs compile bundles/domain-bundle.yaml --version 1.0.0`

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## SCS Resources

- [SCS Specification](https://github.com/tim-mccrimmon/scs-spec)
- [Examples](https://github.com/tim-mccrimmon/scs-spec/tree/main/examples)

## Provenance

- **Author**: Dana Reyes
- **Email**: dana.reyes@medtech-cdmo.test
- **Created At**: 2026-10-01T09:00:00+00:00