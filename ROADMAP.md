# SCS Roadmap

Current stable: **0.3** (tagged `v0.3.0`). Active development: **2.0** on the `2.0-dev`
branch.

This document supersedes the forward-looking "Roadmap" section of
`RELEASE-NOTES-0.3.md` for 2.0 and beyond. Granular backlog: `ISSUES.md`.

## SCS 2.0 — theme

**Structured context is the governed context layer for any AI actor** — chat assistants,
autonomous agents, MCP tool invocations, and multi-agent workflows — not just chat. 2.0
makes the domain model explicit, resolves the runtime-facing open questions, and hardens
the tooling so downstream systems can depend on it.

2.0 is a **breaking change**.

## Workstreams

### 1. Domain Ontology (anchor)

Replace "concern" with the **Domain Ontology**: a domain-defined set of **concepts** with
an optional shallow taxonomy, a small fixed set of typed relationships, and a mapping from
each concept to the standards it satisfies. Hierarchy becomes
`Project → Domain → Concept → SCD`. Design: `rfcs/RFC-0001-domain-ontology.md`.

Everything else in 2.0 sequences behind this.

### 2. "Any AI actor" reframe

Rewrite the model and spec docs so structured context is defined for any AI runtime, with
chat and editor plugins as one case:

- context scoped to **agent + intent**, not just "session"
- **policy-as-context** — a tool / MCP-server's permitted operations expressed as governed
  context
- context that **flows through a workflow** — per-step, per-agent, version pinned at a
  checkpoint

### 3. Runtime decisions

Turn the runtime-blocking items in `OPEN_QUESTIONS.md` into normative spec decisions:

- **immutability scope** — per execution / task / session
- **versioning ↔ runtime behaviour** — how a context version in effect is chosen, pinned,
  and superseded
- **context drift** — a normative definition and the signal a consumer uses to detect it

### 4. Metadata additions

- **Model-routing metadata** — bundle / SCD metadata expressing which model(s) a governed
  workload should route to, so routing is governed rather than hardcoded downstream.
- **Multi-author provenance** — provenance that names the real per-perspective owner
  (compliance, IT, engineering …), not a single source, with a review/approval workflow.

### 5. Tier stack

Corporate / Project tiers only in 2.0. (The Personal tier is deferred.)

### 6. Tooling & release engineering

- CI for `scs-tools` and `scs-validator` (none today).
- Published, pinned releases (PyPI) so downstream builds can depend on a fixed version.
- Converge validator rules on a single `rules/v2.0.0/` set; retire `v0.1.0` and `v0.3.0`.

### 7. Migration

- `spec/2.0/` docs, a 0.3 → 2.0 migration guide, and (open) a `scs migrate` helper for the
  mechanical concern → concept rename.

## Governance

Through 2.0, the specification is maintained by Tim McCrimmon as sole maintainer; RFCs and
Discussions are informative, not gating. The transition to broader community governance
(the 0.3 roadmap's "path to 1.0") is **deferred to after 2.0 ships**.

## Beyond 2.0

Carried forward from the 0.3 roadmap, not scheduled:

- Domain registry / marketplace
- Legal, Clinical, Financial and other expert-authored domains
- Cross-domain dependency management; shared/importable concept libraries
- Public working group formation and the community-governance transition
