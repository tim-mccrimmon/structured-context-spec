# SCS Issues

Working backlog for SCS **2.0** (branch `2.0-dev`). See `ROADMAP.md` for the theme and
workstreams, `rfcs/` for design proposals.

Status: `open` · `in-progress` · `blocked` · `done`

---

## Anchor

### ISS-001 — Domain Ontology: accept RFC-0001
**Status:** open · **Blocks:** most of the rest
Review and accept `rfcs/RFC-0001-domain-ontology.md`. Resolve its Unresolved Questions
(bundle type name, `satisfies[]` sugar, minimal relationship set, cross-domain concepts,
migration tooling, `concept` required-vs-optional on SCDs).

### ISS-002 — Domain Ontology: schema changes
**Status:** blocked (ISS-001)
- `schema/domain/domain-manifest-schema.json`: remove `concerns`, add `domain.ontology`
  (`concepts[]` with `id` / `name` / `description` / `parent` / `relationships[]` /
  `satisfies[]` / `bundle`; optional `relationship_types[]`).
- Add the `concept:` id pattern.
- SCD schema(s): add optional `concept` field.
- Bundle schema: `type: concern` → `type: concept`; carry over the structural rules
  (no imports, ≥ 1 SCD).

### ISS-003 — Domain Ontology: validator
**Status:** blocked (ISS-002)
New ontology-validation rules (concept id format + uniqueness; acyclic `parent`; allowed
relationship types; target resolution; acyclic `depends-on`; SCD `concept` resolves;
concept-bundle SCD/concept agreement as a warning; `concern` residue as an error with a
migration hint). Rename all `concern` handling in the validator.

### ISS-004 — Domain Ontology: spec text
**Status:** blocked (ISS-001)
`spec/2.0/`: rewrite `core-model.md`, `terminology.md`, `bundle-format.md` for the rename
and the `Project → Domain → Concept → SCD` hierarchy. New `spec/2.0/domain-ontology.md`.

### ISS-005 — Domain Ontology: examples + templates + plugins
**Status:** blocked (ISS-002)
- Migrate example domains (`examples/medical-device-cdmo`, `examples/med-adherence`, …):
  `concerns/` → `concepts/`, add `ontology` blocks (flat first; add depth for the CDMO
  example as the reference).
- `scs-tools`: `templates/bundles/concerns/` → `.../concepts/`; `scs new concept`;
  domain-manifest scaffold emits `ontology`.
- `scs-vibe`, `scs-team`: update skill prompts and templates.

---

## Reframe

### ISS-006 — "Any AI actor" model rewrite
**Status:** open
Reframe the spec so structured context is defined for any AI runtime (agent, MCP tool,
workflow step), chat as one case. Concretely: context scoped to **agent + intent**;
**policy-as-context** (a tool/MCP-server's permitted operations as governed context);
context that **flows through a workflow** with a version pinned at a checkpoint. Rewrite
the "SCS maps onto `CLAUDE.md` / `.claude/rules/`" framing to "one consumer among many".

### ISS-007 — Runtime decisions: immutability scope
**Status:** open
Make a normative decision: is a context version immutable per execution, per task, or per
session? Document the rule and its rationale. (`OPEN_QUESTIONS.md` → spec.)

### ISS-008 — Runtime decisions: versioning ↔ runtime behaviour
**Status:** open
Specify how a context version "in effect" is selected, pinned, and superseded at runtime,
and how a consumer records which version governed a request.

### ISS-009 — Runtime decisions: context drift
**Status:** open
Normative definition of "context drift" and the signal a consumer uses to detect it (the
input a reconciliation/attestation process needs).

---

## Metadata

### ISS-010 — Model-routing metadata
**Status:** open
Add bundle/SCD metadata expressing which model(s) a governed workload should route to, so
routing is governed rather than hardcoded downstream. Define the field, its scope
(bundle-level / SCD-level), and precedence.

### ISS-011 — Multi-author provenance
**Status:** open
Provenance that names the real per-perspective owner (compliance, IT, engineering, …), not
a single source. Extend the provenance schema; define an authoring/review/approval
workflow (who approves, recorded how). Check what the current `provenance` block already
supports.

---

## Structure

### ISS-012 — Tier stack: Corporate / Project only
**Status:** open
2.0 ships Corporate and Project tiers; Personal is deferred. Reconcile spec text and
schemas (the current tier names in `core-model.md` are meta / standards / project — align
tier naming with the Corporate/Project framing, or document the mapping).

---

## Tooling & release engineering

### ISS-013 — CI for scs-tools and scs-validator
**Status:** open
No CI today. Add lint + test + schema-validation CI for both `tools/cli` and
`tools/scd-validator`.

### ISS-014 — Published, pinned releases
**Status:** open
Publish `scs-tools` and `scs-validator` (PyPI or equivalent) with versioned releases, so
downstream builds can pin a fixed version. Verify current PyPI state first.

### ISS-015 — Converge validator rules on v2.0.0
**Status:** blocked (ISS-003)
Retire `rules/v0.1.0/` and `rules/v0.3.0/`; single `rules/v2.0.0/` set.

---

## Migration

### ISS-016 — 0.3 → 2.0 migration guide
**Status:** blocked (ISS-002, ISS-004)
`docs/MIGRATION-2.0.md`: the concern → concept rename, the domain-manifest `ontology`
conversion, incremental depth, SCD `concept` field.

### ISS-017 — `scs migrate` helper (open)
**Status:** open
Decide whether to ship an automated helper for the mechanical parts of the 0.3 → 2.0
migration (concern → concept rename, flat `concerns[]` → flat `ontology.concepts[]`), or
keep migration guide-only.

---

## Housekeeping (not 2.0-blocking)

### ISS-018 — Spec file version labels
**Status:** open
`spec/0.3/core-model.md` and others are under `spec/0.3/` but internally labelled "0.1".
Fix version headers when creating `spec/2.0/`.

### ISS-019 — `.claude/` and scaffold files in the repo
**Status:** open
`.claude/` (machine-local `settings.local.json`) and `project-starter.md` are untracked in
the working tree. Decide: `.gitignore` them (likely) or commit intentionally. `.gitignore`
also has an uncommitted `.envrc` line.
