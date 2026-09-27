# SCS Roadmap

Current stable: **0.5.0** (tagged `v0.5.0`). No active development branch is open right now —
see "Beyond 0.5.0," below, for candidate next work; none of it is scheduled yet.

This document supersedes the forward-looking "Roadmap" section of
`RELEASE-NOTES-0.3.md` for 0.5.0 and beyond. Granular backlog: `ISSUES.md`.

## SCS 0.5.0 — theme

**Structured context is the governed context layer for any AI actor** — chat assistants,
autonomous agents, MCP tool invocations, and multi-agent workflows — not just chat. 0.5.0
makes the domain model explicit, resolves the runtime-facing open questions, and hardens
the tooling so downstream systems can depend on it.

0.5.0 is a **breaking change** — expected pre-1.0, per semver; the spec is still settling
and isn't claiming stability yet (see Governance, below).

## Workstreams

### 1. Domain Ontology (anchor)

Replace "concern" with the **Domain Ontology**: a domain-defined set of **concepts** with
an optional shallow taxonomy, a small fixed set of typed relationships, and a mapping from
each concept to the standards it satisfies. Hierarchy becomes
`Project → Domain → Concept → SCD`. Design: `rfcs/RFC-0001-domain-ontology.md`.

Everything else in 0.5.0 sequences behind this.

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

### 4. Metadata additions — deferred out of 0.5.0 (2026-09-27)

- **Model-routing metadata** — bundle / SCD metadata expressing which model(s) a governed
  workload should route to, so routing is governed rather than hardcoded downstream.
  Deferred: not blocking, and routing is runtime/orchestration behavior, out of scope on
  the same grounds as workflow modeling (see workstream 2).
- **Multi-author provenance** — provenance that names the real per-perspective owner
  (compliance, IT, engineering …), not a single source, with a review/approval workflow.
  Deferred: conditional from the start on single-source approval proving insufficient,
  which hasn't happened. See "Beyond 0.5.0."

### 5. Tier stack

Corporate / Project tiers only in 0.5.0. (The Personal tier is deferred.)

### 6. Tooling & release engineering

- CI for `scs-tools` and `scs-validator` (none today).
- Published, pinned releases (PyPI) so downstream builds can depend on a fixed version.
- Converge validator rules on a single `rules/v0.5.0/` set; retire `v0.1.0` and `v0.3.0`.

### 7. Migration

- `spec/0.5/` docs, a 0.3 → 0.5.0 migration guide, and (open) a `scs migrate` helper for the
  mechanical concern → concept rename.

## Governance

Through 0.5.0, the specification is maintained by Tim McCrimmon as sole maintainer; RFCs
and Discussions are informative, not gating. The transition to broader community governance
(the 0.3 roadmap's "path to 1.0") is **deferred to 1.0**, which is likewise not scheduled by
this roadmap — 0.5.0 is deliberately pre-1.0 while the domain model and runtime decisions
are still settling.

## Beyond 0.5.0

Carried forward from the 0.3 roadmap, not scheduled:

- Domain registry / marketplace
- Legal, Clinical, Financial and other expert-authored domains
- Cross-domain dependency management; shared/importable concept libraries
- Public working group formation and the community-governance transition

Deferred out of 0.5.0's workstream 4 (2026-09-27), not scheduled:

- **Model-routing metadata** (ISS-010) — not blocking, and routing is runtime/orchestration
  behavior, the same class of thing SCS already keeps out of scope for workflows.
- **Multi-author provenance** (ISS-011) — conditional from the start ("only pursue if
  single-source approval proves insufficient"); revisit if that limit is actually hit.

Deferred out of workstream 6 (2026-09-27), not scheduled:

- **Publishing `scs-tools`/`scs-validator` to PyPI** (ISS-014) — the version-bump and
  packaging/bug-fix work is done, but the actual publish is cut: local editable installs
  cover current use, and the release tag does not depend on it. Revisit when a `pip
  install`-without-a-clone user actually shows up.
