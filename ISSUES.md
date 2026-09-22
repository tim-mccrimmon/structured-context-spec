# SCS Issues

Working backlog for SCS **0.5.0** (branch `0.5-dev`). See `ROADMAP.md` for the theme and
workstreams, `rfcs/` for design proposals.

Status: `open` · `in-progress` · `blocked` · `done`

---

## Anchor

### ISS-001 — Domain Ontology: accept RFC-0001
**Status:** done (2026-09-21)
Reviewed and accepted `rfcs/RFC-0001-domain-ontology.md`. Decisions: `type: concept`;
`satisfies[]` sugar kept; minimal relationship set `{depends-on, relates-to, satisfies}`
(no `part-of` yet); migration guide-only (no `scs migrate` helper); `concept` optional on
SCDs. Cross-domain concepts parked indefinitely; approval model (`version_approved_by`
single-source MVP) deferred-open, not blocking.

### ISS-002 — Domain Ontology: schema changes
**Status:** done (2026-09-21)
- `schema/domain/domain-manifest-schema.json`: `concerns` removed, `domain.ontology` added
  (`concepts[]` with `id` / `name` / `description` / `parent` / `relationships[]` /
  `satisfies[]` / `bundle`; optional `relationship_types[]`).
- `concept:` id pattern added (domain manifest, all three SCD tier schemas).
- SCD schema(s) (project/meta/standards): optional `concept` field added.
- Bundle schema: `type: concern` → `type: concept`; structural rules carried over
  (no imports, ≥ 1 SCD).
- Bundle schema: `provenance` gained required `version_approved_by` / `version_approved_at`
  (RFC-0001, Provenance and approval).
- **Refined 2026-09-22 (during ISS-005b):** those two fields are only required when
  `version` is a real semver, not `DRAFT` — via a new `allOf`/`if`/`then` block, same
  pattern the type-specific rules already use. Unconditionally requiring them broke every
  freshly-scaffolded (working, unapproved) bundle the CLI produces.
- Also renamed: `schema/scd/meta-scd-template.json`'s `content.concerns[]` vocabulary block
  → `content.concepts[]` (`concern:` id pattern → `concept:`) — same residue, not called out
  in the original RFC checklist but caught during implementation.
- Not yet migrated (ISS-005): `schema/domain/examples/medical-device-cdmo-domain.yaml` and
  the `examples/` domains still use `concerns:` and will fail validation against the new
  schema until ISS-005 lands.

### ISS-003 — Domain Ontology: validator
**Status:** done (2026-09-21)
New `rules/v0.5.0/` rule set (seeded from v0.3.0, `concern` -> `concept` renamed throughout;
new `domain-ontology-rules.yaml`). New `OntologyValidator` (`ontology_validator.py`)
implementing all 8 RFC-0001 rules: concept id format + uniqueness; acyclic `parent`;
allowed relationship types (covers both `relationships[]` and the `satisfies[]` shorthand);
target resolution; acyclic `depends-on`; SCD `concept` resolves (best-effort, needs SCDs
passed in); concept-bundle SCD/concept agreement as a warning (best-effort, needs SCDs +
bundles passed in); `concern` residue as an error with a migration hint (both
`domain.concerns` and bundle `type: concern`). New `scs validate --domain <manifest>` CLI
path (schema + ontology rules). `rules_loader.py` default path repointed to `rules/v0.5.0/`.

Tested against hand-built valid/invalid fixtures (all 8 rules fire correctly, including
both cycle detections) and against the existing `tests/fixtures/` and `examples/`
content — confirms existing valid SCDs still pass, and that unmigrated `examples/*`
bundles now correctly fail on the new `version_approved_by`/`version_approved_at`
requirement (expected; ISS-005's job to fix).

Note: `tools/scd-validator/tests/` has no actual test functions today (only fixture data,
0 items collected by pytest) - matches ISS-013 ("No CI today"). All verification above was
manual CLI runs, not an automated regression suite.

### ISS-004 — Domain Ontology: spec text
**Status:** open
`spec/0.5/`: rewrite `core-model.md`, `terminology.md`, `bundle-format.md` for the rename
and the `Project → Domain → Concept → SCD` hierarchy. New `spec/0.5/domain-ontology.md`.

### ISS-005 — Domain Ontology: examples + templates + plugins
**Status:** done (2026-09-22)
- [x] Migrate example domains: `examples/medical-device-cdmo` and `examples/med-adherence`
  `concerns/` → `concepts/` (23 bundle files), `type: concern` → `type: concept`,
  `version_approved_by`/`version_approved_at` added to every bundle's provenance.
- [x] Domain manifests: `schema/domain/examples/medical-device-cdmo-domain.yaml` got the
  reference-depth ontology (12 concepts, relationships, `satisfies` mapped to ISO 13485 /
  IEC 62304 / 21 CFR 820 / ISO 14971 / 21 CFR Part 11 - illustrative ids, not researched
  clause citations); `software-development-domain.yaml` got a flat ontology (11 concepts,
  matching what `examples/med-adherence` actually imports - it was missing `concerns`
  entirely before, so this is new content, not just a rename).
- [x] `examples/med-adherence`'s 39 project-tier SCDs got an optional `concept:` field,
  derived mechanically from each concept bundle's own `scds:` list (1:1 mapping, no
  orphans). Domain bundles and top-level meta/standards/project bundles updated too.
- [x] Docs swept for stray `concern` text (`README.md`s, `context-intake-template.md`,
  `chai-standards-bundle/README.md`); `examples/llm-portability/` deliberately left alone -
  it's a frozen historical experiment snapshot, not living reference content.
- [x] Tested: every migrated bundle validates individually (`scs validate --bundle`), both
  domain manifests validate via the new `--domain` path (CDMO's `satisfies` targets get the
  expected "unresolved in this context" warnings, 0 errors on both).
- Found and tracked, not fixed here (pre-existing, unrelated to the rename): ISS-020, ISS-021
  (bundle-tree SCD loading never actually recurses into concept bundles, so full
  project-bundle validation doesn't exercise SCD-level checks), ISS-022 (a pre-existing XOR
  violation + malformed import in `examples/med-adherence/standards-bundle.yaml`).

**scs-tools done 2026-09-22:**
- [x] `templates/bundles/concerns/` → `.../concepts/`; all 12 concept bundle templates
  renamed (`type`, `title`, `rationale`); `meta-bundle.yaml`'s `scd:meta:concerns` →
  `scd:meta:concepts`; `domains/software-development.yaml` renamed too.
- [x] Real Python logic renamed, not just templates: `utils/project_types.py`
  (`SOFTWARE_DEVELOPMENT_CONCERNS` → `_CONCEPTS`, `get_concerns_for_project_type` →
  `get_concepts_for_project_type`, `minimal_concerns` → `minimal_concepts`, `"concerns"` key
  in `AVAILABLE_DOMAINS` → `"concepts"`); `utils/files.py`; `commands/new.py` (functions,
  variables, CLI messages); `commands/bundle.py` (display logic, `SOFTWARE_DEVELOPMENT_CONCEPTS`
  import, a stale "10 domain bundles" count fixed to 11).
- [x] **Found and fixed a real bug**, not just a rename: `bundle.py`'s `scs bundle version`
  command wrote `approved_by`/`approved_at` to provenance - different field names than the
  schema's required `version_approved_by`/`version_approved_at` (ISS-002). Fixed to match;
  every bundle this command versions was previously going to fail validation.
- [x] **Found and fixed a design gap**: the schema unconditionally required
  `version_approved_by`/`version_approved_at` on every bundle, including fresh `DRAFT`
  working bundles that haven't been approved yet by design - which meant every
  freshly-scaffolded `scs new project` failed validation immediately. Fixed in the schema
  (see ISS-002's refinement note above) and switched the CLI's scaffold templates from a
  hardcoded `version: "1.0.0"` to `version: "DRAFT"`, with unversioned `imports:` to match
  (a DRAFT bundle can't meaningfully import a pinned version of another DRAFT bundle).
- [x] A third, distinct `concerns:` field found in the 41 SCD content templates
  (`templates/scds/*.yaml`) - a free-text per-SCD topic-tag list, unrelated to the Domain
  Ontology. Renamed to `topics:` rather than `concepts:` to avoid colliding with the new
  formal `concept:` singular field on SCDs (ISS-002) - a judgment call, flagged here rather
  than silently decided.
- [x] Docs swept (`README.md`, `GETTING_STARTED.md`, `project-README.md`, the
  `acme-health` example's README). `CLI-AUDIT-2026-01-01.md` deliberately left alone - a
  dated historical audit report, same treatment as `examples/llm-portability/`.
- [x] **Tested end-to-end**: set up a venv, ran `scs new project` for real, validated the
  full output (`scs validate --bundle bundles/project-bundle.yaml` → 0 errors) including
  every individual bundle; ran `scs bundle version` for real and confirmed the resulting
  versioned bundle has correct field names and validates.
- Found, not fixed (pre-existing, unrelated): `bundle.py`'s `_validate_bundle()` shells out
  to a bare `scs` on `$PATH`, which silently fails outside an activated venv (`--no-validate`
  works around it). Minor, not tracked as a numbered issue.

**scs-vibe / scs-team plugins done 2026-09-22 (ISS-005c):**
- [x] `scs-team`: all 7 skill files (`init`, `draft`, `validate`, `status`, `use`, `add`,
  `version`), `README.md`, `demo/README.md`, `demo/DEMO-SCRIPT.md` renamed (124
  replacements) - directory paths (`.scs/concerns/` → `.scs/concepts/`), `type: concern` →
  `type: concept`, and all prose. One generic-English "concerned about" correctly preserved.
- [x] `scs-vibe`: `scs-vibe-plugin-overview.md` and `demo/DEMO-SCRIPT.md` renamed (5
  replacements). `spec/examples/care-plan-tracker/` left alone - its 5 `concern(s)` hits are
  all generic English ("separation of concerns," "any issues or concerns," "concurrent
  access concerns"), not the SCS term.
- [x] **Found a third variant of the ISS-005b provenance field bug**: `scs-team`'s `version`
  skill (the plugin equivalent of `scs bundle version`) told the model to write
  `versioned_by`/`versioned_at`/`version_rationale` — none of which match the schema's
  `version_approved_by`/`version_approved_at`/`rationale`. Fixed. This is the third distinct
  naming attempt found across the codebase for the same concept (CLI's original
  `approved_by`/`approved_at`, this plugin's `versioned_by`/`versioned_at`, and the actual
  schema) - worth remembering when touching any other approval-writing code path.
- [x] Verified: all 7 `SKILL.md` YAML frontmatter blocks still parse after the bulk rename.
- Not deeply tested end-to-end (these are Claude Code skill prompts, not executable code -
  no venv/CLI to run them through the way ISS-005a/b were tested).

**ISS-005 (examples + templates + plugins) is now fully done.**

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
0.5.0 ships Corporate and Project tiers; Personal is deferred. Reconcile spec text and
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

### ISS-015 — Converge validator rules on v0.5.0
**Status:** blocked (ISS-003)
Retire `rules/v0.1.0/` and `rules/v0.3.0/`; single `rules/v0.5.0/` set.

---

## Migration

### ISS-016 — 0.3 → 0.5.0 migration guide
**Status:** blocked (ISS-002, ISS-004)
`docs/MIGRATION-0.5.0.md`: the concern → concept rename, the domain-manifest `ontology`
conversion, incremental depth, SCD `concept` field.

### ISS-017 — `scs migrate` helper (open)
**Status:** open
Decide whether to ship an automated helper for the mechanical parts of the 0.3 → 0.5.0
migration (concern → concept rename, flat `concerns[]` → flat `ontology.concepts[]`), or
keep migration guide-only.

---

## Housekeeping (not 0.5.0-blocking)

### ISS-018 — Spec file version labels
**Status:** open
`spec/0.3/core-model.md` and others are under `spec/0.3/` but internally labelled "0.1".
Fix version headers when creating `spec/0.5/`.

### ISS-019 — `.claude/` and scaffold files in the repo
**Status:** open
`.claude/` (machine-local `settings.local.json`) and `project-starter.md` are untracked in
the working tree. Decide: `.gitignore` them (likely) or commit intentionally. `.gitignore`
also has an uncommitted `.envrc` line.

---

## Validator engine gaps (found during ISS-005 testing, pre-existing, not RFC-0001 scope)

### ISS-020 — Bundle-tree SCD loading never recurses into concept bundles
**Status:** open
`commands/validate.py`'s `validate_bundle()` resolves project bundle -> domain bundle, then
reads `domain_bundle.get("scds", [])` directly - but domain bundles are required to have an
*empty* `scds` array by design (they aggregate concept bundles via `imports`). This means
`--bundle` on a project bundle has never actually loaded real SCDs through a correctly
structured domain hierarchy; it silently reports "0 SCDs loaded" instead of erroring. Fix:
recurse one more level - read the domain bundle's `imports`, load each concept bundle, and
collect *their* `scds`.

### ISS-021 — Hardcoded SCD file path template doesn't match example layouts
**Status:** open
The same code resolves an SCD reference to `project_root / "context" / <tier> / <name>.yaml`.
`examples/med-adherence`'s actual SCDs live under `scds/project/`, not `context/project/` -
so even with ISS-020 fixed, SCD files wouldn't resolve for this example. Needs either a
configurable path convention or a documented one the examples are made to match.

### ISS-022 — `examples/med-adherence/standards-bundle.yaml` pre-existing violations
**Status:** open
Two bugs unrelated to the concern->concept rename, confirmed present before this session's
changes (only `provenance` was touched here for ISS-005): the `imports` entry
`bundle:standards:soc2-type2:2023.1` doesn't match the bundle reference pattern (extra
segment, non-semver version `2023.1`), and the bundle has both `imports` and `scds` set,
violating the standards-bundle XOR rule. `scs validate --bundle` fails on this file.
