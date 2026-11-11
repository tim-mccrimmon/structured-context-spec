# Infusion Pump Firmware

**Bundle type**: Project
**Ontology model**: cdmo
**Domain repository**: medtech-context
**Created**: 2026-10-01T09:00:00+00:00

## Overview

This workspace holds the **Project bundle** for Infusion Pump Firmware: the governance for this
project. It is independent of your organization's Domain bundle; a runtime applies the two side
by side.

## Structure

```
projects/infusion-pump-fw/
├── bundles/
│   ├── project-bundle.yaml    # The Project bundle (compile this)
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

## Working With This Workspace

1. Write the SCDs under `context/project/`: directives (rules an AI agent should follow),
   prohibitions (tools and practices that are forbidden, with no conditions), and facts
   (what an agent should know). Cite standards with `std:` references.
2. Validate: `scs-validate --strict` at the repository root, or `scs bundle validate` here
3. Compile: `scs compile bundles/project-bundle.yaml --allow-draft`
4. Version bottom-up: each concept bundle first
   (`scs bundle version --bundle bundles/concepts/<name>.yaml --version 1.0.0 --approved-by "Name <email>"`),
   pin it in `bundles/project-bundle.yaml` as `bundle:<name>:1.0.0`, then version
   `bundles/project-bundle.yaml`. Each version is a git tag.
5. Compile the released version: `scs compile bundles/project-bundle.yaml --version 1.0.0`

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

## SCS Resources

- [SCS Specification](https://github.com/tim-mccrimmon/scs-spec)
- [Examples](https://github.com/tim-mccrimmon/scs-spec/tree/main/examples)

## Provenance

- **Author**: Dana Reyes
- **Email**: dana.reyes@medtech-cdmo.test
- **Created At**: 2026-10-01T09:00:00+00:00