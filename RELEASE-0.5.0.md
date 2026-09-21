# SCS 0.5.0 Release Checklist

Status-tracking checklist for shipping SCS 0.5.0. Sequencing follows `ROADMAP.md`'s
workstreams and `ISSUES.md`'s issue numbers; this doc adds order, phase gates, and a single
place to see where things stand. Update the checkboxes and the Status line as work lands —
check this first when picking up 0.5.0 work.

**Target:** `v0.5.0`, tagged and pushed to origin, before 2026-12-01 (TaskWarrior task 61,
gates GTC DC attendance).

**Current phase:** 1 — Domain Ontology anchor (schema, validator, spec text, examples)

---

## Phase 0 — Accept RFC-0001 (blocks everything else) — DONE 2026-09-21

Five bikeshed-level questions, decided:

- [x] **Bundle type name**: `type: concept`
- [x] **`satisfies[]` sugar**: kept
- [x] **Relationship set**: minimal 3 (`depends-on`, `relates-to`, `satisfies`); `part-of`
      deferred
- [x] **Migration tooling**: guide-only, no automated helper
- [x] **`concept` on SCDs**: optional
- [x] RFC-0001 `Status: Accepted`; `Tracking` field points at ISS-001–005
- [x] `rfcs/README.md`: RFC-0001 moved to "Accepted (Pending Implementation)"
- [x] `ISSUES.md`: ISS-001 → `done`

Not blocking, already settled: cross-domain concepts is parked indefinitely; the approval
model is decided (`version_approved_by` ships as a single-source MVP, per-perspective
attestation deferred to ISS-011).

---

## Phase 1 — Domain Ontology anchor (ISS-002 – ISS-005)

The core rename + schema work. Nothing downstream unblocks until this phase is done and
tested against real content.

- [x] **ISS-002 — Schema changes** — done 2026-09-21
  - [x] `schema/domain/domain-manifest-schema.json`: `concerns` removed, `domain.ontology` added
  - [x] `concept:` id pattern added (domain manifest + all 3 SCD tier schemas)
  - [x] SCD schema(s): optional `concept` field added (project/meta/standards)
  - [x] Bundle schema: `type: concern` → `type: concept`
  - [x] Bundle schema: `version_approved_by` / `version_approved_at` added to `provenance`
        (required)
  - [x] Bonus: `meta-scd-template.json`'s `content.concerns[]` → `content.concepts[]`
        (caught during implementation, wasn't in the original checklist)
  - Note: existing example data (`schema/domain/examples/medical-device-cdmo-domain.yaml`,
    `examples/*`) still uses `concerns:` and will fail validation until ISS-005 migrates it
- [x] **ISS-003 — Validator** — done 2026-09-21
  - [x] New `rules/v0.5.0/` set (seeded from v0.3.0, concern→concept renamed); new
        `domain-ontology-rules.yaml`
  - [x] New `OntologyValidator` implementing all 8 RFC-0001 rules (`ontology_validator.py`)
  - [x] `version_approved_by` / `version_approved_at` presence enforced (via ISS-002's
        schema `required`, confirmed working against a real example bundle)
  - [x] `concern` residue → error with migration hint (both `domain.concerns` and bundle
        `type: concern`)
  - [x] New `scs validate --domain <manifest>` CLI path; `rules_loader.py` default
        repointed to `rules/v0.5.0/`
  - [x] Set up a venv (`tools/scd-validator/venv/`, gitignored) and manually verified all
        8 rules against hand-built valid/invalid fixtures, plus regression-checked against
        existing `tests/fixtures/` and `examples/` content
  - Note: `tools/scd-validator/tests/` has no actual test functions yet (0 collected by
    pytest) — that's ISS-013's job, not this one
- [ ] **ISS-004 — Spec text**
  - [ ] `spec/0.5/core-model.md`, `terminology.md`, `bundle-format.md` rewritten for the
        rename + `Project → Domain → Concept → SCD` hierarchy
  - [ ] New `spec/0.5/domain-ontology.md`
- [x] **ISS-005a — Examples** — done 2026-09-21
  - [x] `examples/medical-device-cdmo`: `concerns/` → `concepts/`; domain manifest got real
        depth (12 concepts, relationships, `satisfies` mapped to ISO 13485 / IEC 62304 /
        21 CFR 820 / ISO 14971 / 21 CFR Part 11)
  - [x] `examples/med-adherence`: same rename; domain manifest ontology is flat (11
        concepts); 39 SCDs got a `concept:` field derived from each concept bundle's own
        `scds:` list
  - [x] All bundles' provenance gained `version_approved_by`/`version_approved_at`
  - [x] **Test**: every bundle validates individually; both domain manifests validate via
        `scs validate --domain` (0 errors on both)
  - Found 3 pre-existing, unrelated bugs while testing — tracked as ISS-020, ISS-021,
    ISS-022, not fixed here
- [ ] **ISS-005b — scs-tools** — not started
  - [ ] `templates/bundles/concerns/` → `.../concepts/`; `scs new concept`; domain-manifest
        scaffold emits `ontology`
  - [ ] Real Python logic to rename too (`commands/new.py`, `utils/project_types.py`,
        `utils/files.py`, `commands/bundle.py` all reference `concern` in variable/function
        names, CLI messages, and file paths — not just template data)
- [ ] **ISS-005c — scs-vibe, scs-team plugins** — not started
  - [ ] Update skill prompts and templates referencing `concern`

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
