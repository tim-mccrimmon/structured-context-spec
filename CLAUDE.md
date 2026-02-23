# Structured Context Specification (SCS) — Project Context

## What This Project Is

The **open-source SCS specification** — a community-governed standard for structuring,
versioning, and delivering context to AI agents.

This is the **spec repo**, not the product. SCS defines the format (SCDs, bundles, tiers,
relationships). SCP (Supervisory Control Plane) is the commercial runtime product built on top
of SCS — it lives in a separate private repo.

**Current spec version**: 0.3
**License**: Apache 2.0
**Website**: https://structuredcontext.dev
**Registry/product**: SCP (separate repo: `SCP-2`)

---

## Repository Structure

```
structured-context-spec/
├── spec/0.3/               # The specification documents (source of truth)
│   ├── overview.md         # Top-level spec overview
│   ├── core-model.md       # SCDs, bundles, tiers
│   ├── bundle-format.md    # Bundle manifest format
│   ├── meta-tier.md        # Meta tier specification
│   ├── standards-tier.md   # Standards tier specification
│   ├── project-tier.md     # Project tier specification
│   ├── terminology.md      # Canonical definitions
│   └── governance-and-compliance.md
├── rfcs/                   # Requests for Comments (spec changes)
│   ├── README.md           # RFC process guide
│   └── 0000-template.md    # Template for new RFCs
├── schema/                 # JSON Schema validation files
├── templates/              # Starter templates
│   ├── bundles/            # Bundle manifest templates
│   └── scd/                # SCD templates by tier
├── examples/               # Reference implementations
├── plugins/                # Editor/tool integrations
│   ├── scs-vibe/           # Cursor/Windsurf plugin
│   └── scs-team/           # Claude Code multi-agent plugin
├── tools/                  # CLI and validator tools
│   ├── cli/                # scs CLI
│   └── scd-validator/      # YAML structure validator
├── dog-food/               # SCS documenting itself with SCS
│   └── SCS-MED-CONTEXT/    # Bundles + SCDs for SCS's own context
├── context/                # Additional spec context documents
├── docs/                   # Non-spec documentation
└── CONTRIBUTING.md         # Contribution guide
```

---

## RFC Process (Spec Changes)

Significant changes to SCS require an RFC. The process:

1. **Discuss** — Open a GitHub Discussion in "Ideas" to gauge interest
2. **Write** — Copy `rfcs/0000-template.md`, fill in all sections with concrete examples
3. **Submit PR** — Maintainer assigns a number (e.g., `0001-my-feature.md`)
4. **Review** — 2-week minimum community review period
5. **Decision** — Accept / Reject / Defer within 4 weeks
6. **Implement** — Update spec, schemas, examples; create tracking issue

**When RFC is required**: New SCD tiers, schema changes, new required fields, changes to relationship semantics.
**When RFC is NOT required**: Typo fixes, doc clarifications, additional examples, bug fixes.

See `rfcs/README.md` for full process details.

---

## Key Concepts (Spec Level)

- **SCD** (Structured Context Document) — YAML file containing context content
  - Format: `scd:<tier>:<name>` (e.g., `scd:project:company-overview`)
  - Tiers: `meta`, `standards`, `project`
- **Bundle** — Manifest grouping SCDs + imports
  - Types: meta, standards, concern, domain, project
  - Concern bundles are leaf nodes (no imports)
  - Domain bundles aggregate concerns (no direct SCDs)
- **Relationships** — Explicit edges between SCDs for graph traversal (`references`, `applies_to`, `governed_by`)
- **Validation**: Loose (structure only) in Phase 1 / DRAFT; strict in Phase 2 / versioned

---

## Dogfooding Pattern (`dog-food/`)

The spec documents itself using SCS. This is:
- Proof that SCS works in practice
- The reference implementation for what good bundles look like
- Actual context used when developing the spec

`dog-food/SCS-MED-CONTEXT/` contains the live bundles and SCDs for SCS itself.
When working on the spec, load this context to see SCS applied to SCS.

---

## Plugins

- **scs-vibe** (`plugins/scs-vibe/`) — Cursor and Windsurf integration for design-time context
- **scs-team** (`plugins/scs-team/`) — Claude Code multi-agent team coordination

---

## SCS vs SCP — Critical Distinction

| | SCS (this repo) | SCP (SCP-2 repo) |
|---|---|---|
| **What** | Open spec / standard | Commercial runtime product |
| **Use case** | Design-time (coding agents) | Runtime (production agents) |
| **Context** | Full 11 concerns for dev agents | Governance subset for prod agents |
| **Who** | Community-governed | Ohana Tech commercial product |
| **Governed by** | RFC process | Internal development |

SCS defines the **format**. SCP implements **runtime delivery** of that format.
Don't add SCP product details to spec documents. Don't add SCS spec format details to SCP architecture.

---

## Contribution Conventions

- PRs for spec changes: include updated schema files AND updated examples
- Don't break existing examples without RFC justification
- Spec language: use "MUST", "SHOULD", "MAY" per RFC 2119 conventions
- Keep examples realistic (healthcare, fintech — our primary target verticals)
- Test schema changes against `tools/scd-validator/` before submitting

---

**Last Updated**: 2026-02-23
**Current Version**: SCS 0.3
**Global product context**: see `~/.claude/CLAUDE.md`
