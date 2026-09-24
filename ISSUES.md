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
**Status:** done (2026-09-22)
Scope ended up larger than written here: all 8 files in `spec/0.3/` (not just the 3 named)
reference `concern`, and `spec/0.5/` didn't exist yet, so this was a full-directory
migration, not an edit of 3 files. Tim decided: do `spec/0.3/` → `spec/0.5/` fully, defer
the separate `docs/` website (see ISS-023).

- `core-model.md`, `meta-tier.md`, `project-tier.md`, `standards-tier.md`,
  `governance-and-compliance.md`: light touch — version labels fixed (also resolves
  ISS-018's stale "0.1"/"0.3" internal labels across the whole directory, not just
  `core-model.md`), a few terminology fixes, `concept:` field added to `project-tier.md`
  §4.2, cross-reference to `domain-ontology.md` added to `core-model.md` §6.
- `terminology.md`: heavy rewrite — §2.12 Concern → Concept (full RFC-0001 definition, not
  just a rename: domain-scoped not cross-domain reusable), new §2.13 Domain Ontology, new
  §2.14 Ontology Model, new §2.16 DRAFT/Approved Versions, §2.15 Bundle Types table updated.
- `bundle-format.md`: heavy rewrite — §3.4 Concept Bundle examples rebuilt with correct
  schema fields (DRAFT + versioned-with-approval cases), §3.6 guidance corrected (used to
  say "concerns should be composable across domains" — now correctly says concepts are
  domain-scoped), §9/§10 got the DRAFT-approval-exemption documented, §16 Key Takeaways
  updated.
- New `domain-ontology.md`: the normative spec translation of RFC-0001 — Domain Ontology
  structure, Ontology Models, concept bundles, bundle validity properties, provenance/
  approval (including the DRAFT exemption), all 8 validation rules restated normatively,
  migration guide, open questions, future extensions.
- **Tested, not just written**: extracted every YAML code block from all 9 files (42 total)
  and confirmed they parse; ran the schema-relevant examples through the real
  `scs-validate` CLI. Found and fixed 3 real bugs this way: `domain-ontology.md`'s example
  had `parent: null` (schema types `parent` as string, not nullable — omit the field
  instead) and a relationship targeting an undefined concept; `bundle-format.md`'s
  pre-existing §3.3 Standards Bundle example violated the XOR constraint (imports + scds
  both set) - same class of bug as ISS-022, but in the spec document itself, so fixed here
  rather than just tracked; and two of my own new §3.4 examples were missing the required
  `description` field.

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
**Status:** done (2026-09-22)
Reframe the spec so structured context is defined for any AI runtime (agent, MCP tool,
workflow step), chat as one case. Concretely: context scoped to **agent + intent**;
**policy-as-context** (a tool/MCP-server's permitted operations as governed context);
context that **flows through a workflow** with a version pinned at a checkpoint. Rewrite
the "SCS maps onto `CLAUDE.md` / `.claude/rules/`" framing to "one consumer among many".

**Design converged via discussion, resolving the three open questions this ticket
originally carried (see the retired `OPEN_QUESTIONS.md` items) around a single
distinction:** context is a guardrail/decision (domain-invariant, worth versioning); state
is a fact looked up because a specific prompt's wording demands it (prompt-contingent,
never worth diffing); a prompt is the literal ask - a third, distinct thing. This directly
resolved all three sub-questions:
- **Scope key**: not session-scoped (sessions are paepae's/the runtime's concern, not
  SCS's) - context is selected by **`(agent, intent)`**, the same pair a checkpoint record
  later reuses to record which version governed a given point.
- **Policy-as-context**: a tool/MCP server's permitted operations are a governed decision
  (who may use what capability, under what constraint), the same as any other guardrail -
  modeled as a **Policy SCD** (project-tier content pattern, not a new schema type,
  following the existing convention for Architecture/Security/Governance SCDs). Tools are
  named by **capability class** (`fetch-data`, `execute-code`, `query-db`, `write-data`,
  `send-communication`, domain-extensible), not by protocol/MCP-endpoint - the binding to
  an actual implementation is a runtime concern, not part of the decision the SCD records.
  Enforcement is explicitly out of scope: SCS declares the policy; a runtime-specific
  compilation step (an MCP gateway, a LangGraph guard, whatever) enforces it.
- **Checkpoint-pinning**: SCS does not model workflows (that's paepae's domain) - it
  defines only the **checkpoint record** shape, a small non-SCD, runtime-generated audit
  artifact recording which `bundle` version was in effect for a given `(agent, intent)` at
  a given `timestamp`, with an opaque `workflow_ref` so it can be traced back to whatever
  the runtime calls "the workflow" without SCS needing a model of what that is.

**Implemented:**
- [x] `spec/0.5/any-ai-actor-model.md` (new) - the normative doc: §2 context scoped to
  agent+intent (incl. the context-vs-state table from the design discussion), §3
  policy-as-context (incl. the capability-class tool taxonomy and the enforcement
  boundary), §4 the checkpoint record (incl. field table), §5 "consumers, not targets".
- [x] `spec/0.5/project-tier.md` §5.7 - new Policy SCD content pattern, with a worked YAML
  example (`applies_to_roles`, `permitted_operations[].capability`/`resource`/
  `requires_approval`).
- [x] `spec/0.5/core-model.md` - cross-reference to `any-ai-actor-model.md` added after the
  Purpose section.
- [x] `README.md` - "SCS and Claude Code" section rewritten: kept the CLAUDE.md/
  `.claude/rules/`/`.claude/agents` mapping table, but reframed the surrounding text from
  "SCS maps directly onto Claude Code's native context hierarchy" to Claude Code as "one
  consumer of SCS content, not the target it's designed around", closing with a pointer to
  `any-ai-actor-model.md` and other valid composition targets (an MCP permission gate, a
  LangGraph node, a checkpoint record).
- [x] `schema/checkpoint/checkpoint-record-schema.json` (new) - the only piece of this
  design needing a schema, since it's a genuinely new artifact type (not an SCD, not a
  bundle). Policy SCDs needed no new schema - they use the existing permissive project-tier
  `content:` object, same as other documented-not-enforced content patterns.
- [x] Validator/CLI support mirroring the existing `--domain` pattern:
  `schema_validator.py`'s `validate_checkpoint_record()`/`_load_checkpoint_record_schema()`,
  `utils.py`'s `find_checkpoint_record_schema()`, `parser.py`'s `load_checkpoint_record()`,
  and `commands/validate.py`'s `--checkpoint`/`-c` option and `validate_checkpoint()`
  dispatch (schema-only - a checkpoint record has no relationships/completeness/ontology
  dimension to check).
- [x] **Tested end-to-end** with the real `scs-validate` CLI: a valid checkpoint record
  passes cleanly; an invalid one (bad bundle-id pattern, missing `intent`/`timestamp`)
  fails with three clear, correctly-targeted errors; the §5.7 Policy SCD example validates
  as a normal project-tier SCD (0 errors, 1 expected warning for the optional
  `provenance.rationale` field).

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
**Status:** done (2026-09-22, resolved as a side effect of ISS-004)
All `spec/0.5/` files now consistently say 0.5.0 — headers and every internal "SCS 0.1" /
"SCS 0.3" / "in 0.1" / "for 0.3" mention (not just `core-model.md`; all 8 files had at
least one).

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

### ISS-023 — `docs/` documentation website: migrate to concept terminology
**Status:** open (deferred, scoped out of ISS-004 by Tim 2026-09-22)
A separate tree from `spec/` - the mkdocs-built site (`mkdocs.yml`, `docs_dir: docs`).
45 files, ~9,300 lines, 15 referencing `concern`. Has its own **"Concern Docs" nav section**
(11 subdirectories, `docs/concern-docs/<concept>/README.md`, one per concept) plus
`quick-start-guide.md`, `scd-guide.md`, `validation-guide.md`, `FAQ.md`,
`MIGRATION-0.3.md`, `bundle-lifecycle.md`, `scs-overview.md`, `glossary.yaml`. Overlaps
conceptually with `spec/` but is a distinct, separately-maintained tree - not touched by
the ISS-004 `spec/0.3/` → `spec/0.5/` migration. Rename `docs/concern-docs/` →
`docs/concept-docs/` (matches the `templates/docs/` rename pattern from ISS-005b) plus a
full terminology sweep, whenever this gets picked up.

### ISS-024 — Regulatory classification block on the Context of Use SCD (proposed)
**Status:** proposed — **originated in the SCP repo, not SCS.** Source: SCP FR-014
(`scp-2/docs/feature-requests/FR-014-regulatory-classification-adverse-determination-review.md`,
draft, not approved by Tim; drafted by Claude 2026-09-24). Tim agreed 2026-09-24 that the SCS
side should carry this; scope and naming still need an SCS decision. Depends on SCP FR-010's
proposed Context of Use SCD (itself an unapproved SCP draft, not yet an SCS content pattern).
Add an optional block to the Context of Use SCD:
- `regulatory_classification[]`: `regime`, `reference` (customer-asserted, e.g. an EU AI Act
  Annex III point), `declared_by`. SCS records the declaration and its approver; it does not
  classify anything.
- `determination_review`: which determination types (e.g. `adverse`) require human review,
  reviewer qualification, review window. SCP reads this to report determinations lacking a
  linked review record; SCP holds no rule of its own.
Decide whether this belongs in 0.5.0 or later, and whether it needs an RFC. Related: ISS-007 to
ISS-009 (runtime decisions). Expect to be revisited in the SCS refresh planned for the week of
2026-09-28.

### ISS-025 — EU AI Act baseline changed by the Digital Omnibus: re-verify before encoding (unverified)
**Status:** open — **unverified input, added 2026-09-24 at Tim's request.** Origin: SCP-side
review (Claude session in `scp-2`), not an SCS decision. A stated goal of the next SCS release is
to support EU rules as far as possible, so the EU baseline the spec maps to must be checked
against primary text first.
What was found (secondary sources only; EUR-Lex pages returned empty content to the tools used,
so **the legal text has not been read**):
- Regulation (EU) 2026/1744 ("Digital Omnibus on AI"), reportedly adopted 2026-07-08, published
  in the OJ 2026-07-24, in force 2026-07-27, amends Regulation (EU) 2024/1689.
- Reported new application dates: stand-alone Annex III high-risk **2027-12-02** (was
  2026-08-02); AI in regulated products, Annex I, **2028-08-02**. Medical-device AI is likely
  under Annex I; not confirmed for any customer.
- **Disputed:** whether a Commission-triggered earlier date remains. Gibson Dunn (dated
  2026-05-27, pre-adoption) says fixed dates replaced the trigger; a Cloud Security Alliance note
  says the trigger remains.
- Unknown: what else the Omnibus amended. Article numbers and obligations SCS maps to may have
  changed. Example already found: post-market monitoring is **Art. 72** in the adopted Act;
  Art. 61 is 2021 proposal numbering.
To do:
1. Obtain the consolidated Regulation (EUR-Lex CELEX `02024R1689-20260727`) and the Omnibus text
   into the repo or `~/kb/inbox/`.
2. Confirm the application dates and the trigger question from the text.
3. Re-check every EU AI Act Article/Annex reference in `spec/`, `docs/`, and any mapping or
   standards bundle (Art. 9, 10, 11, 12, 13, 14, 72; Annex III).
4. Update `~/.claude/rules/identity.md` and `~/Projects/work/CLAUDE.md` if the dates change (both
   were edited 2026-09-24 with unverified dates).
Related: ISS-024 (regulatory classification block, from SCP FR-014), ISS-009 (drift; Art. 72
monitoring). To be picked up in the SCS refresh week of 2026-09-28.
