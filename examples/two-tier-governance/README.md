# Two-Tier Governance — Domain and Project Bundles

A fictional medical-device contract manufacturer, **MedTech CDMO**, with:

- an organization **Domain bundle** (`org/`) holding rules that apply to every project, and
- an independent **Project bundle** (`infusion-pump-fw/`) holding one project's rules,

each compiled to a **runtime artifact** (`compiled/`) with `scs compile`.

```
examples/two-tier-governance/
├── org/                                 # Organization governance (normally its own repo)
│   ├── bundles/domain-bundle.yaml       # bundle:medtech-cdmo — the Domain ("Global") bundle
│   ├── bundles/concepts/                # ai-use, design-controls
│   └── context/project/                 # SCDs holding the organization's directives
├── infusion-pump-fw/                    # One project's governance (normally its own repo)
│   ├── bundles/project-bundle.yaml      # bundle:infusion-pump-fw — lists its SCDs directly
│   └── context/project/
└── compiled/
    ├── global.yaml                      # Compiled Domain bundle
    └── projects/infusion-pump-fw.yaml   # Compiled Project bundle
```

## Directives

Only `content.directives` is compiled. Each directive becomes a rule with the id
`<scd-name>/<directive-id>`, for example `design-change-control/DCC-001`:

```yaml
content:
  summary: Design changes follow the QMS design change procedure.
  directives:
    - id: DCC-001
      directive: >-
        Design changes require documented review and approval before implementation.
      cites:
        - std:iso-13485:2016#7.3.9
```

The rest of an SCD (summary, provenance, other content) stays in the source for reviewers.

## Compile

```bash
scs compile org/bundles/domain-bundle.yaml -o compiled/global.yaml
scs compile infusion-pump-fw/bundles/project-bundle.yaml -o compiled/projects/infusion-pump-fw.yaml
```

Each command validates the bundle tree, then writes the artifact and prints its SHA-256. The
same source always produces the same bytes. The artifacts carry no timestamps or authors, and
each begins with a self-identification rule, so asking an agent "which governance bundles
are active?" reports both bundles and their versions.

The two bundles are compiled separately and never import each other. A runtime applies them
side by side: Domain first, then Project.

The Domain bundle imports `bundle:meta:0.6.0`, the meta bundle published with the spec
(`meta/` at the repo root). The tools ship a copy of it, so the import resolves without the
meta bundle being in the organization's workspace. Its directives (`governance-context/M-*`)
come first in `global.yaml` and tell the agent how Domain and Project rules combine and how
to treat citations.

See `spec/0.6/runtime-artifact.md`.
