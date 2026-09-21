# SCS 0.5.0 Release Checklist

Status-tracking checklist for shipping SCS 0.5.0. Sequencing follows `ROADMAP.md`'s
workstreams and `ISSUES.md`'s issue numbers; this doc adds order, phase gates, and a single
place to see where things stand. Update the checkboxes and the Status line as work lands —
check this first when picking up 0.5.0 work.

**Target:** `v0.5.0`, tagged and pushed to origin, before 2026-12-01 (TaskWarrior task 61,
gates GTC DC attendance).

**Current phase:** 0 — RFC-0001 acceptance

---

## Phase 0 — Accept RFC-0001 (blocks everything else)

RFC-0001 (`rfcs/RFC-0001-domain-ontology.md`) has five open bikeshed-level questions left
before it can move from Draft to Accepted. None require deep new design — each is a call
only you can make, and any reasonable answer is fine to commit to:

- [ ] **Bundle type name**: `type: concept` or `type: concept-bundle`?
- [ ] **`satisfies[]` sugar**: keep the shorthand, or require the full `relationships` form?
- [ ] **Relationship set**: is `{depends-on, relates-to, satisfies}` enough, or add
      `part-of` distinct from `parent`?
- [ ] **Migration tooling**: ship an automated `scs migrate 0.3→0.5.0`, or guide-only?
- [ ] **`concept` on SCDs**: optional or required for SCDs in a concept bundle?
- [ ] Mark RFC-0001 `Status: Accepted`; fill in `RFC PR` / `Tracking Issue` fields
- [ ] Update `rfcs/README.md`: move RFC-0001 from "Under Review" to "Accepted (Pending
      Implementation)"
- [ ] Update `ISSUES.md`: ISS-001 → `done`

Not blocking, already settled: cross-domain concepts is parked indefinitely; the approval
model is decided (`version_approved_by` ships as a single-source MVP, per-perspective
attestation deferred to ISS-011).

---

## Phase 1 — Domain Ontology anchor (ISS-002 – ISS-005)

The core rename + schema work. Nothing downstream unblocks until this phase is done and
tested against real content.

- [ ] **ISS-002 — Schema changes**
  - [ ] `schema/domain/domain-manifest-schema.json`: remove `concerns`, add `domain.ontology`
  - [ ] Add `concept:` id pattern
  - [ ] SCD schema(s): add `concept` field (per Phase 0's optional/required decision)
  - [ ] Bundle schema: `type: concern` → `type: concept`
  - [ ] Bundle schema: add `version_approved_by` / `version_approved_at` to `provenance`
        (required)
- [ ] **ISS-003 — Validator**
  - [ ] New ontology-validation rules module (RFC-0001's Validation rules 1–8)
  - [ ] Enforce `version_approved_by` / `version_approved_at` presence on bundles
  - [ ] Rename all `concern` handling; `concern` residue → error with migration hint
- [ ] **ISS-004 — Spec text**
  - [ ] `spec/0.5/core-model.md`, `terminology.md`, `bundle-format.md` rewritten for the
        rename + `Project → Domain → Concept → SCD` hierarchy
  - [ ] New `spec/0.5/domain-ontology.md`
- [ ] **ISS-005 — Examples, templates, plugins**
  - [ ] `examples/medical-device-cdmo`: `concerns/` → `concepts/`, add `ontology` block
        (this is the reference example — give it real depth, not just a flat list)
  - [ ] `examples/med-adherence`: same, flat is fine
  - [ ] `scs-tools`: `templates/bundles/concerns/` → `.../concepts/`; `scs new concept`;
        domain-manifest scaffold emits `ontology`
  - [ ] `scs-vibe`, `scs-team`: update skill prompts and templates
- [ ] **Test**: run `scs validate` against both migrated examples; fix anything the new
      rules catch

---

## Phase 2 — "Any AI actor" reframe (ISS-006)

- [ ] Rewrite model/spec docs: context scoped to agent + intent, not just "session"
- [ ] Document policy-as-context (tool/MCP-server permitted operations as governed context)
- [ ] Document context flowing through a workflow, version pinned at a checkpoint
- [ ] Rewrite "SCS maps onto CLAUDE.md / .claude/rules/" framing to "one consumer among many"

## Phase 3 — Runtime decisions (ISS-007 – ISS-009)

- [ ] ISS-007: normative decision on immutability scope (per execution/task/session)
- [ ] ISS-008: how a context version "in effect" is chosen, pinned, superseded
- [ ] ISS-009: normative definition of context drift + detection signal

## Phase 4 — Metadata additions (ISS-010 – ISS-011)

- [ ] ISS-010: model-routing metadata field, scope, precedence
- [ ] ISS-011: per-perspective/multi-author attestation — extends the Phase 1
      `version_approved_by` MVP; only pursue if single-source approval proves insufficient
      (see RFC-0001, Provenance and approval)

## Phase 5 — Tier stack (ISS-012)

- [ ] Reconcile `core-model.md` tier naming (meta/standards/project) with Corporate/Project
      framing, or document the mapping

## Phase 6 — Tooling & release engineering (ISS-013 – ISS-015)

- [ ] ISS-013: CI for `scs-tools` and `scs-validator` (lint + test + schema validation)
- [ ] ISS-014: verify current PyPI state; publish pinned releases
- [ ] ISS-015: converge validator rules on `rules/v0.5.0/`; retire `v0.1.0`, `v0.3.0`

## Phase 7 — Migration (ISS-016 – ISS-017)

- [ ] ISS-016: `docs/MIGRATION-0.5.0.md`
- [ ] ISS-017: decide + ship (or explicitly skip) the `scs migrate` helper

## Phase 8 — Housekeeping (ISS-018 – ISS-019, not release-blocking)

- [ ] ISS-018: fix stale "0.1" version labels under `spec/0.3/`
- [ ] ISS-019: decide `.claude/` / `project-starter.md` — gitignore or commit

---

## Phase 9 — Ship

- [ ] Full `scs validate` pass across all examples on `0.5-dev`
- [ ] `RELEASE-NOTES-0.5.0.md` written
- [ ] Merge `0.5-dev` → `main`
- [ ] Tag `v0.5.0`, push tag to origin
- [ ] Update `ROADMAP.md`: move "Active development" line to whatever's next
- [ ] Close TaskWarrior task 61

---

*This file is the `ref` target for TaskWarrior task 61 ("SCS v0.5.0 release"). Update it as
phases complete — it's the single place to check status.*
