# Survey: Spec text and agent interface

Surveyed 2026-10-25 on worktree `structured-context-spec-0.7`, branch `0.7-dev` (HEAD `f1c9d11`
"Start spec/0.7: copy spec/0.6, bump headers to 0.7.0"). **[UNCOMMITTED]** marks content that
exists only as uncommitted working-tree changes. Line numbers refer to the working tree.
"Inference" marks conclusions not stated in a source.

## Scope read

- `rfcs/RFC-0002-agent-mediated-scs.md` (all 931 lines). **[UNCOMMITTED]** amendment: reserved
  `plan/`, `test-plan/`, `qa/` directories and bundle names (RFC:8-9, 575-577, 592-593, 736-738, 886-888).
- `ROADMAP.md` (workstreams 1-10), `ISSUES.md` ISS-042..055 (lines ~845-990). **[UNCOMMITTED]**
  ISS-045 marked done (ISSUES.md:891, 911-918).
- `spec/0.7/` all 12 files (outlines in full; normative sections read). **[UNCOMMITTED]** edits
  in `bundle-format.md` (§1 "What changed in 0.7.0", §7.3 addendum, new §7.6, new §9.6) and
  `runtime-artifact.md` (§3.1 `scs_runtime: '0.7'` + `source_digest`, §3.5, §4 step 4/9).
- `meta/` (README, `bundles/meta-bundle.yaml`, `context/meta/governance-context.yaml`).
- `plugins/scs-vibe`, `plugins/scs-team` (plugin.json, READMEs, all SKILL.md, templates,
  standards library, demo dirs), `plugins/temp-test.md`.
- `docs/MIGRATION-0.7.0.md` (**[UNCOMMITTED]** rows/steps for ISS-045), `docs/resources.md`,
  `README.md` (agent/plugin sections), repo `CLAUDE.md`.
- `rfcs/RFC-0003-review-profiles.md` (stub, head), `rfcs/0.8.DRAFT-plan-development.md`
  (**[UNCOMMITTED, untracked]**, head only).
- Engine surface only as it bears on the skill contract: `tools/cli/scs_tools/cli.py`,
  `commands/{bundle,compile,new,add,validate}.py` option/prompt lines,
  `tools/scd-validator/src/scs_validator/{commands/validate.py,reporter.py}`.
- External: Agent Skills spec, https://agentskills.io/specification (fetched live 2026-10-25).
- No placement guide, agent-interface doc, intake schema, or `derived_from` schema exists
  anywhere in the repo (grep of `schema/ spec/ tools/ meta/ plugins/ docs/` for
  `derived_from|intake|placement`: only unrelated hits in mca templates/`project_types.py`).

## Components (spec docs, plugins, skills, meta bundle: responsibility, files)

| Component | Responsibility | Files |
|---|---|---|
| Spec overview | Scope, out-of-scope, doc index | `spec/0.7/overview.md` (§6 "Scope of the 0.6.0 Specification" :268, §7 :303, §11 :390-408) |
| Terminology | Canonical definitions (Domain, bundle types, DRAFT/approval, provenance, AI agent) | `spec/0.7/terminology.md` |
| Core model | SCD/tier/bundle/versioning model; Corporate/Project/Personal note | `spec/0.7/core-model.md` |
| Bundle format | Bundle types, independence, immutability, digest, directory layout, validation, lifecycle | `spec/0.7/bundle-format.md` |
| Domain ontology | Ontologies, concept bundles, `version_approved_by` provenance (§7) | `spec/0.7/domain-ontology.md` |
| Runtime artifact | Compiled artifact format and compiler conformance | `spec/0.7/runtime-artifact.md` |
| Citations | `std:` references; no standard text | `spec/0.7/citations.md` |
| Tier docs | Meta / Project / deprecated Standards tier | `spec/0.7/{meta-tier,project-tier,standards-tier}.md` |
| Governance & compliance | Governance workflow, role of AI agents | `spec/0.7/governance-and-compliance.md` |
| Any AI Actor | Runtime-side model: checkpoint records, consumers | `spec/0.7/any-ai-actor-model.md` |
| Meta bundle | `bundle:meta:0.6.0`; 4 terms + 3 reading directives compiled into every Domain artifact | `meta/bundles/meta-bundle.yaml`, `meta/context/meta/governance-context.yaml` |
| scs-vibe plugin (v1.0.0) | Claude Code plugin; writes `CLAUDE.md`, `.claude/rules/*.md`, `CONSIDERATIONS.md` directly (no SCDs) | `plugins/scs-vibe/` (skills `init`, `validate`, `explain`; `init/templates/*.md`) |
| scs-team plugin (v2.0.0) | Claude Code plugin; `.scs/` with 11 concept bundles, hand-written SCDs, hand-compiled `.claude/rules/` | `plugins/scs-team/` (skills `init`, `add`, `draft`, `use`, `status`, `validate`, `version`; `standards/` library) |
| Engine (layer 1) | `scs` CLI and `scs-validate`; the only layer that may validate/version/compile (RFC:298-299) | `tools/cli/`, `tools/scd-validator/` |
| Migration guide | User-facing 0.7 changes | `docs/MIGRATION-0.7.0.md` |

## Spec changes required by RFC 0002 (table: spec file | what RFC 0002 requires | current state)

The RFC does not say which spec files carry its normative text (see Gaps G1). The mapping
below is by subject.

| Spec file | What RFC 0002 requires | Current state |
|---|---|---|
| `overview.md` | 0.7 scope: agent interface (§1-3, 6), Domain repositories (§9), intake/provenance (§4-5), verifiable immutability (§11), advisory review (§12); SCS ends at versioned bundle + artifact; placement, multi-user review, registries, hosting, runtime serving out of scope (RFC:290-294); doc index entries for any new docs | Header bumped only. §6 still titled "Scope of the 0.6.0 Specification" (:268); §7 "Out of Scope (For 0.6.0)" (:303) lists "lifecycle and workflow specifications" and "SCS Tooling Suite full implementations" as out of scope, which RFC 0002 partly brings in; §11 says "The SCS 0.6.0 specification includes" (:392, :408); no agent interface, Domain repository, intake |
| `terminology.md` | Define Domain repository, workspace, personal Domain, intake / intake record, `derived_from`, advisory review finding, content digest / `source_digest`, placement guide, rendering; Domain is "the capacity someone works in, not the person" (RFC:113-116) | §2.11 defines Domain as "An **organization** (or an organizational unit...)" (:164-167), no individual capacity; §3.4 says "Personal ... is not governance and is out of scope for SCS" (:362-366), contradicting RFC personal Domain (ROADMAP: "personal tier ... becomes the personal Domain"); §4.2 Provenance generic (:385-394); §2.15/2.16 have no digest |
| `core-model.md` | Personal Domain replaces deferred "Personal" layer; item-level `derived_from` (RFC §5) in SCD content model; bundle versioning now covers resolved content (§11) | §5.4 "Personal ... out of scope for 0.6.0 (ROADMAP.md workstream 5)" (:166-168) (stale ROADMAP pointer; workstream 5 is now Agent Skills); §8.3 "SCS 0.6.0 defines" (:291); §10 "tooling is out of scope for 0.6.0" (:335) |
| `bundle-format.md` | §9 Domain repository layout replacing §8 two-repo layout; workspace- and name-qualified tags and manifests (`<workspace>/<bundle-name>-v<version>`, RFC:587-593); reserved bundle names `plan`/`test-plan`/`qa` (RFC:738); repo-level validation (one `domain/`, RFC:733-735); reserved dirs not validated (RFC:736-737); non-empty `approved_by` in version manifest (RFC:728); `content_digest` + verification (§11); truthful `validation_passed` | **[UNCOMMITTED]** §7.3 addendum (:518-521), §7.6 Content Digest (:536-600), §9.6 (:675-678) cover §11 fully. §7.6 names manifests `<bundle-name>-v<version>-MANIFEST.yaml` (:563-564), not workspace-qualified. §8 still says "Domain and Project bundles normally live in separate repositories" (:604-605) with `org-governance/` and `project-name/` repos (:608-631), contradicting RFC §9 (Alternative 5 rejected, RFC:800-807). §10.3 workflow (:706-718) step 7 "compiled and published for runtime use" (publication/placement now out of scope). §14 lists "Scoping a Project bundle to a named Domain bundle" as a future extension (:764), which RFC Alternative 6 rejects (RFC:809-813). §1 "In SCS 0.6.0" (:22); §9.4 meta pin `bundle:meta:0.6.0` (:668). No reserved names, no repo-level rules |
| `runtime-artifact.md` | `source_digest` (§11, RFC:652-655); `scs compile` MUST NOT emit `derived_from` (RFC:729); compile output SHOULD go to workspace `dist/<bundle-name>-<version>.yaml` (RFC:595-597); placement out of scope (RFC:605-608) | **[UNCOMMITTED]** `source_digest` in §3.1 (:172, :201), §3.5 (:257-266), §4 steps 4, 9 (:284-295). §2.2-2.4 field tables (:66-70, :97-104, :124-128) do not list `derived_from` or mark it "not compiled" (prohibitions table has a "Compiled" column; directives and facts do not). No `dist/` convention. §1 "how a runtime stores, selects, or injects artifacts is outside this specification" (:17-18) is consistent with RFC §10 |
| `domain-ontology.md` | Intake proposes an ontology (RFC:383, 925-926); approval single-person per version (unchanged); possibly ontology-declared intake profiles (Future, RFC:865-866) | §7 Provenance and Approval (:249-289) unchanged and consistent. No intake linkage. §7 notes git config nowhere (fine) |
| `citations.md` | Drafting from sources MUST NOT copy standard text; citations remain `std:` (RFC §8, :523-524) | Already says standards are cited not reproduced (§2, §5 :131-136). No change strictly required; RFC §8 adds an agent-side obligation that has no home here (inference) |
| `governance-and-compliance.md` | Human confirmation (RFC §6), advisory review with recorded decisions (§12), no agent-supplied approver | §8 workflow (:220-257) is PR/issue-based with `status-context.yaml`; §9 "AI agents in SCS must ... generate missing context ... keep status-context.yaml up to date" and "must NOT autonomously merge changes" (:259-275). No confirmation rules, no review-finding record. §7.1 SCD provenance `created_by: human-or-agent` (:186) is silent on agent authorship vs RFC §6.2 (approver never the agent). §10 "SCS 0.6.0 requires" (:279), §10.5 (:297) |
| `project-tier.md` | `derived_from` on items (if documented per tier); scope from including bundle (already) | §1 scope-by-bundle (:20-22) consistent; §9 "In SCS 0.6.0" (:323). No `derived_from` |
| `meta-tier.md` | Meta bundle version pin moves with spec? (not stated by RFC) | "Ownership (0.6.0): ... `bundle:meta:0.6.0`" (:26-27); §9 "In SCS 0.6.0" (:276). RFC is silent on whether 0.7 ships `bundle:meta:0.7.0` (Gap G9) |
| `standards-tier.md` | None | Deprecation unchanged |
| `any-ai-actor-model.md` | None normative. §6 "Consumers, Not Targets" (:265-280) aligns with RFC §10 renderings | §5.2 "SCS 0.6.0 does not define the pin's storage mechanism" (:234) — version text only |
| *(no file)* | Agent interface conformance: scope (§1), three layers (§2), machine mode envelope (§3), intake fields + record (§4), confirmation rules (§6), change summary (§7), drafting from sources (§8), Domain repository + agent instructions file + CI (§9), placement (§10), advisory review (§12), schema/validation rules (RFC:691-738) | Not present in `spec/0.7/`. Inference: either the RFC remains the normative reference for these, or new spec documents are needed; RFC does not decide (G1) |

## Existing agent interface (plugins/skills inventory: name, what it does, reusable for 0.7? why)

Both plugins are Claude Code plugins (`.claude-plugin/plugin.json`). Repo `CLAUDE.md` calls
scs-vibe a "Cursor/Windsurf plugin" and scs-team a "multi-agent plugin", which does not match
plugin.json (inconsistency). `README.md` already labels both "pre-0.6 ... haven't been updated"
(README.md:146-152).

| Plugin:skill | What it does | Reusable for 0.7? Why |
|---|---|---|
| scs-vibe:init (`skills/init/SKILL.md`, 410 lines) | Scans repo signals (:36-55), asks 3 questions incl. personal vs commercial (:57-65), builds CONSIDERATIONS checklist (:67-138), walks each item with Will Address / Accepted Risk / N/A / Already Done and pushes back on risky "Accepted Risk" (:140-186), confirms file list before writing (:188-207), writes `CLAUDE.md` + `.claude/rules/*.md` directly into the app repo (:219-323) | **Partial.** Reusable patterns: signal detection, the personal/commercial routing question (maps to `audience`/`regulated`), considerations walk-through (closest prior art to §12 advisory review and `missing-protection`), decision-with-rationale recording (maps to `review_findings.decision/rationale`), tone guidance (:325-333), confirm-before-write. Not reusable: output target (writes in the app repo, violating RFC §9 "Application repositories ... MUST NOT be used to author it" RFC:533-534 and §6.8), no SCDs/bundles/validator, writes renderings directly (RFC §10 forbids tools placing renderings) |
| scs-vibe:init/templates (`healthcare.md`, `fintech.md`, `saas.md`, `minimal.md`, `CONSIDERATIONS-example.md`) | Markdown CLAUDE.md templates with placeholders | **Low.** CLAUDE.md-shaped, not SCD-shaped. Considerations lists could seed `missing-protection` prompts (inference) |
| scs-vibe:init `SKILL-v1-backup.md` | Stray backup (68 non-blank lines) | No |
| scs-vibe:validate | Checks CLAUDE.md sections/placeholders/stale paths by reading files | **No** for validation (RFC §2: validation only via engine). Placeholder/stale-reference heuristics could inform the explain/review skill (inference) |
| scs-vibe:explain | Pitch for why structured context matters | **Low.** RFC "explain" means explaining existing context in plain language (RFC:285), not marketing |
| scs-team:init | Scaffolds `.scs/` with 11 hard-coded concept bundles (pre-0.5 concern model) by writing YAML directly | **No.** Superseded by `scs new domain/project` with ontologies; writes directly instead of via engine; layout differs from RFC §9 |
| scs-team:add | Reads a document, maps to 11 concepts, writes SCDs, hand-compiles `.claude/rules/` (:130-147) | **Partial.** Document-type extraction guidance and "Don't invent requirements ... Flag ambiguities for human review" (:168-169) carry over to RFC §8. Its `provenance.source_document` (:119) is the predecessor of item-level `derived_from` (different level, non-schema field). Concept map, direct writes, and hand compilation are not reusable |
| scs-team:draft | Per-concept question banks for 11 concepts | **Partial.** Question banks (security, compliance, data) could seed profile/boundary questions; concept list is obsolete (ontologies replace it) |
| scs-team:use | Copies pre-built `scd:standards:*` SCDs (HIPAA, SOC2, PCI, CHAI, GDPR) | **No.** Standards tier deprecated (`standards-tier.md`); standards SCDs paraphrase requirements (`standards/hipaa/hipaa-phi-handling.yaml:2` `tier: standards`, `implementation_guidance` :15) which RFC §8 forbids copying into SCDs. Possible input to RFC 0003 review profiles (inference) |
| scs-team:status | Inventory and coverage against 11 concepts | **Low.** Could become part of "explain" (plain-language summary of a workspace); coverage logic tied to obsolete concepts |
| scs-team:validate | Five "levels" done by reading YAML; Level 4 content quality (:34-38) and Level 5 compile-sync (:40-45) | **No** for levels 1-3 and 5 (engine's job). Level 4 heuristics (TBD/placeholder detection) are review-like (inference) |
| scs-team:version | Hand-edits `version:` fields, sets `version_approved_by: "<User>"` (:81), recompiles to `.claude/rules/` (:86), git commit + tag `scs-v1.0.0` (:110, :121) | **No** as procedure: bypasses `scs bundle version` (no digest, no manifest), tag format conflicts with RFC §9, bumps SCD versions. Reusable: semver guidance and bottom-up order (concepts first, then root) which matches `bundle-format.md` §10.3 |
| Cross-cutting: frontmatter | `name`, `description`, `argument-hint`, `allowed-tools` (comma-separated) | Agent Skills spec requires `name` matching directory, `description` ≤1024 chars; `allowed-tools` is optional, experimental, **space-separated**; `argument-hint` is not in the open spec (Claude Code extension). Two skills named `init` and two named `validate` across plugins collide if installed side by side outside plugin namespaces (inference) |
| Cross-cutting: invocation | Every skill says "User-initiated only ... Do NOT invoke unless the user explicitly runs `/scs-team:...`" | Open Agent Skills activate from `description` matching (progressive disclosure); slash-only invocation is client-specific. RFC intends conversational activation (RFC:134-137) |
| Cross-cutting: confirm-before-write | Present summary of files, get confirmation | Reusable as behavior; RFC §6.1 makes it concrete (show `--dry-run` `changes`) |

## Skills needed by RFC 0002 (intake, draft, review, validate, version, compile, explain)

Common to all: call the engine in machine mode via scripts (RFC:316-317); never reimplement
validation/versioning/compilation (RFC:298-299); never write outside the Domain repository
(RFC:542-543, §6.8); never claim success without `ok: true` (§6.4); never pass `--force`,
`--no-validate`, `--allow-draft` unless the user asked in this conversation (§6.3); refuse
out-of-scope requests (placement, multi-user review, registries, hosting, runtime serving)
by saying they are outside SCS (RFC:269-271, 290-294).

### intake

- **Required behavior.** First step establishes the Domain repository, existing or new
  (RFC:371-373); Domain workspace built before any Project in a new repo. Always ask routing:
  `audience`, `domain`, `workspace`, `regulated` (+frameworks), `ontology` (proposed, confirmed)
  (RFC:375-383). Ask profile questions only when routing calls for it: personal Domain
  (`owner`, `boundaries`, `practices`), organization (`organization`, `certifications`,
  `source_documents`, `approvers`, `boundaries`), project (`project`, `risk`, `data`,
  `boundaries`) (RFC:385-413). Infer and ask to confirm rather than ask one by one (RFC:368-369).
  Save `intake.yaml` at the workspace root (RFC:415-419). Repo naming `<domain-name>-context`
  SHOULD (RFC:545-546). Agent instructions file (`AGENTS.md` + client pointer) generated by
  scaffold (RFC:579-585).
- **Engine operations.** `scs new domain` (creates repo, `domain/`, `projects/`, `AGENTS.md`,
  CI; `--profile personal`), `scs new project` (under `projects/`), both with `--json --dry-run`
  (RFC:883-890). Writing/validating `intake.yaml` (schema `schema/intake.schema.json`,
  RFC:418-419, 724) — RFC does not name an engine command that writes it (G4).
- **Confirmation points.** Ontology proposal (RFC:383); planned `changes` before scaffold
  (§6.1); approvers named by the user (feeds version).
- **Reuse.** scs-vibe:init signal detection and personal/commercial question; scs-team:draft
  question banks; scs-team:init repo scanning. None maps to the routing/profile schema.

### draft

- **Required behavior.** Turn intent into prohibitions, directives, facts (RFC:315-316);
  prohibitions binary with no conditional words (`runtime-artifact.md` §2.3 :106-109); facts
  checkable, rules-as-facts go to directives (§2.4 :130-131); each item SHOULD carry
  `derived_from` (`intake: <answer id>` or `source: <doc id>` + `locator`) (RFC §5); items from
  documents MUST carry it, SHOULD carry locator; no standard text, only `std:` citations;
  source documents stay in the workspace (`sources/`) and go only to the user's own client
  (RFC §8). Maintain: add, edit, retire, re-scope SCDs, add concept bundles (RFC:285).
- **Engine operations.** `scs add scd|bundle --json --dry-run`; validator on drafts. RFC does
  not define an engine operation for editing SCD content, retiring, or re-scoping (G5).
- **Confirmation points.** Planned `changes` before writing (§6.1); every content change made
  to resolve a review finding (§12, RFC:676-678).
- **Reuse.** scs-team:add document-type extraction guidance and "don't invent / flag
  ambiguity"; scs-team:draft question banks; `runtime-artifact.md` §2.2-2.4 as the authoring
  reference.

### review (advisory)

- **Required behavior.** While drafting and before versioning, review for `framework-conflict`,
  `missing-protection`, `technical-risk`, `ethical-risk` (RFC:660-672). Never block; never change
  content without confirmation; present each finding in plain language naming the SCD item and
  citation; record decision `changed` / `kept` (with rationale) / `deferred` plus who and when
  in the workspace `intake.yaml` `review_findings` (RFC:674-685, example RFC:450-459); re-raise
  `deferred` before next version. Findings never compiled.
- **Engine operations.** None defined; findings are written into `intake.yaml` (no engine
  writer named, G4). Validator checks `intake.yaml` schema.
- **Confirmation points.** Each finding's decision (§6.7 MUST record); open findings shown
  before versioning (§6.7 SHOULD).
- **Reuse.** scs-vibe:init considerations walk-through, decision options, push-back pattern
  (:140-186), CONSIDERATIONS.md as decision record (:209-217). RFC 0003 (stub) will add
  declarative profiles; not available for 0.7.

### validate

- **Required behavior.** Run the validator, explain results in plain language before proposing
  fixes (§6.5), propose fixes (RFC:286); never report success without `ok: true`.
- **Engine operations.** `scs validate --json` / `scs-validate --output json` (exists; validator
  report carried in `result`, findings mapped to `diagnostics`, RFC:361-362); repo-root
  validation of all workspaces (RFC:733-735, not built).
- **Confirmation points.** Fixes are writes, so `--dry-run` + confirmation.
- **Reuse.** Nothing from plugin validate skills beyond tone; both reimplement validation.

### version

- **Required behavior.** Pin imports; version bundles bottom-up; record approver and notes
  (RFC:287). Approver from the user in the current conversation, never agent/model, never
  environment without confirmation (§6.2). Show plain-language change summary from
  `scs bundle diff` before versioning (§6.6, §7). Show open/deferred findings (§6.7). Tags
  `<workspace>/<bundle-name>-v<version>` (RFC:587-591).
- **Engine operations.** `scs bundle version --json --dry-run --approved-by ... --notes ...`;
  `scs bundle diff --json` (ISS-052, not built); import pinning (no engine command named, G5).
- **Confirmation points.** Approver; change summary; planned `changes`; any `--no-validate`/
  `--force` only on explicit user request.
- **Reuse.** scs-team:version semver guidance and bottom-up ordering; its procedure is not reusable.

### compile

- **Required behavior.** Produce the runtime artifact (RFC:288); write to workspace `dist/`
  (RFC:595-597); after compiling, tell the user where the artifact belongs using the placement
  guide and leave placement to them (§6.8, §10); never place or transform renderings
  (RFC:607-608).
- **Engine operations.** `scs compile --json --dry-run` (artifact into `dist/`); compile refuses
  on digest mismatch with no override (**[UNCOMMITTED]** `runtime-artifact.md` §4 step 4).
- **Confirmation points.** Planned `changes`; `--allow-draft` only if user asked.
- **Reuse.** None of the plugins' hand-compilation to `.claude/rules/`. scs-vibe:init
  path-specific rules guidance (:248-297) is placement-adjacent knowledge for a guide, not a
  skill behavior (inference).

### explain

- **Required behavior.** "Explain existing context in plain language" (RFC:285) and explain
  validator output (RFC:316); includes placement advice per Implementation Note 5 ("including
  placement advice from the guide", RFC:893-894) — whether placement advice lives in explain,
  compile, or both is not specified.
- **Engine operations.** Read-only: `scs bundle info`/`list` (exist, prose only), validator
  JSON, `scs bundle diff`; compiled artifact as a readable summary (inference).
- **Confirmation points.** None (read-only).
- **Reuse.** scs-team:status inventory structure; scs-vibe:explain tone only.

## Interfaces (skill-to-engine contract the skills will depend on)

Required contract (RFC §3, :324-362) vs what the engine exposes today.

| Contract element | RFC requirement | As-built |
|---|---|---|
| `--json` on every agent-used command | MUST (RFC:326); ISS-049 lists `new`, `add`, `bundle`, `validate`, `compile` | None in `scs` CLI. `scs-validate --output json` exists (`scd-validator/.../commands/validate.py:53-55`); `scs compile --format json` is artifact serialization, not the envelope (`compile.py:21-27`) |
| No prompts in machine mode | MUST (RFC:328) | Prompts: `bundle version` approver (`bundle.py:328-329`) and notes (`bundle.py:354-358`); `add scd/bundle` overwrite confirm (`add.py:78`, `add.py:200`); `new` interactive prompts (`new.py:210-252`) with `--no-interactive` flag (`new.py:111`) |
| No inferred human values | MUST; suggestions only in result (RFC:329-330) | Git-config approver default removed (ISS-047, `bundle.py:325-333`); no suggestion mechanism yet. `new --author/--email` defaults not checked here |
| Single JSON object on stdout | MUST (RFC:331) | Not implemented; `bundle version` prints step prose (`bundle.py:309` onward) |
| Exit codes 0/1/2/3/4/5 | Keep (RFC:332-333) | Validator uses 3, 4, 5 and `determine_exit_code` (`validate.py:142, 186, 197-209, 438`); `scs` commands use `click.Abort` (exit 1) |
| Envelope fields | `scs_version`, `command`, `ok`, `exit_code`, `changes[]{action,path}`, `diagnostics[]{severity,code,message,path,suggestion}`, `result` (RFC:337-356) | Not implemented. Validator JSON entries have `level`, `message`, `scd_id`, `file_path`; no `severity` (split into `errors`/`warnings` arrays), no `code`, no `suggestion` (`reporter.py:139-181`) |
| `--dry-run` | Same `changes` without writing (RFC:359-361) | Not implemented anywhere |
| `changes` coverage | "every file the command created, modified, or deleted" (RFC:359) | n/a. Git commits and tags made by `bundle version` (`_create_git_version`, `bundle.py:706`) are not files; RFC does not say whether they appear in `changes` (G6) |
| Diagnostic codes | Example `VERSION_APPROVER_REQUIRED` (RFC:349) | No code registry exists in RFC or engine (G7) |
| `scs bundle diff` | MUST, deterministic, `--json` (RFC §7) | Not built (ISS-052 open) |
| Repo-root validation | SHOULD validate all workspaces; error on 0 or >1 `domain/` (RFC:733-735) | Not built (ISS-048 open) |
| Compile to `dist/` | SHOULD `<bundle-name>-<version>.yaml` (RFC:595-597) | Default output stdout (`compile.py:15-19`) |
| Digest verification | validate + compile verify; compile refuses, no override | **[UNCOMMITTED]** implemented (ISSUES.md:911-918; `tools/scd-validator/src/scs_validator/digest.py` untracked) |
| Validator-in-compile | Compile runs validator unless `--no-validate` (`compile.py:47-73`) | Exists; skills must not pass `--no-validate` unprompted (§6.3) |
| MCP layer | Thin stdio adapter over the same operations (RFC:319-322) | Not built (ISS-054, lowest priority) |

## RFC 0002 vs as-built (table: requirement with section ref | status | evidence file:line)

| Requirement | Status | Evidence |
|---|---|---|
| §1 Scope limits; out-of-scope refusals | Not in spec; not in skills (no skills) | `overview.md:303-318` still 0.6 list |
| §2 Three layers; skills primary, in open Agent Skills format | Not started | No SKILL.md outside `plugins/` (find) |
| §3 Machine mode envelope, no prompts, `--dry-run` | Not started (ISS-049 open) | `bundle.py:329, 355`; `add.py:78, 200`; `new.py:210-252` |
| §3 Approver never inferred | Done (prompt instead of git config) | `bundle.py:325-333`; ISSUES.md ISS-047 done; `docs/MIGRATION-0.7.0.md:20` |
| §4 Intake fields + `intake.yaml` + `schema/intake.schema.json` | Not started (ISS-050 open) | `ls schema/` has no intake schema |
| §5 `derived_from` on items | Not started | Absent from `schema/scd/*`, `runtime-artifact.md:66-70, 97-104, 124-128` |
| §6 Human confirmation rules 1-8 | Not in spec; no conforming skills | `governance-and-compliance.md:259-275` is the only agent-behavior text |
| §7 `scs bundle diff` | Not started (ISS-052) | `bundle.py` commands: list, info, validate, version |
| §8 Drafting from sources, `sources/` dir | Not started | No `sources/` in scaffold (`new.py:638-690`) |
| §9 Domain repository, `AGENTS.md`, CI, `--profile personal` | Not started (ISS-048) | `bundle-format.md:602-635` still two-repo layout; scaffold writes `.scs/config` with `project_name`/`ontology_model` keys (`new.py:672-682`) vs RFC "`.scs/config` (bundle_type, name, ontology, scs_version)" (RFC:555) |
| §9 Workspace-qualified tags/manifests | Partial: name-qualified only | `bundle.py:337-338` tag `<bundle-name>-v<version>`; `docs/MIGRATION-0.7.0.md:28-30`; `bundle-format.md:563-564` **[UNCOMMITTED]** |
| §9 Reserved dirs/bundle names | RFC amended; not in spec or validator | RFC:575-577, 592-593, 736-738 **[UNCOMMITTED]** |
| §10 Placement guide (non-normative docs) | Not started (ISS-053) | grep of `docs/` for placement: none |
| §10 Tools MUST NOT place renderings | Engine complies (compile writes only `-o` or stdout); plugins violate | `compile.py:15-19`; `scs-team/skills/version/SKILL.md:86`, `scs-vibe/skills/init/SKILL.md:231` |
| §11 `content_digest`, verification, `source_digest`, truthful `validation_passed` | Done **[UNCOMMITTED]** | `bundle-format.md:536-600, 675-678`; `runtime-artifact.md:172, 201, 257-266, 284-295`; ISSUES.md:911-918 |
| §11 Version manifest non-empty `approved_by` | Engine enforces at prompt; spec rule absent | `bundle.py:331-333`; no rule in `bundle-format.md` §9 |
| §12 Advisory review + `review_findings` record | Not started | No schema; scs-vibe CONSIDERATIONS is the nearest prior art |
| Impl. note 5 Skills (ISS-051) | Not started; open questions unresolved | ISSUES.md ISS-051 "Open questions ... to settle first" |
| Impl. note 7 Placement guide | Not started | — |
| Impl. note 8 MCP | Not started (deferred by design) | ROADMAP workstream 9 |
| Acceptance test (ISS-055) | Not started | ISSUES.md ISS-055 |
| Release engineering for skills (PyPI) | Open | ROADMAP workstream 8: PyPI holds `scs-tools` 0.1.0 and no `scs-validator` |

## Gaps and ambiguities in the RFC (esp. anything a skill author couldn't build from the RFC alone)

- **G1. No normative home for agent-interface text.** RFC sections 1-6, 9-10, 12 are written as
  MUST/SHOULD but no `spec/0.7/` file is named to carry them, and `overview.md` §11 lists no
  such document. A skill author cannot cite a spec section for confirmation rules.
- **G2. Conformance target unclear.** "A conforming agent interface" (RFC:491) — is conformance
  claimed by a skill set, by a client running it, or by the MCP server? Matters for tests (see
  Tests).
- **G3. Intake schema is under-specified.** The YAML example (RFC:421-460) covers the
  organization profile only. Not specified: personal-profile field shapes (`owner`, `practices`),
  project-profile shapes (`risk`, `data`), where `regulated` frameworks go vs `certifications`,
  `domain` routing value persistence, answer id convention (`q-boundaries-1`), `answered_by`
  when the agent inferred and the user confirmed (RFC:368-369), `intake_version` semantics,
  `review_findings` id uniqueness, and whether `answers[]` covers every routing/profile field or
  only free-text boundary questions. The organization profile is triggered by
  `audience: organization` **or** `regulated: yes` (RFC:396), so an individual with a regulated
  project gets the organization profile; unclear whether that applies to a personal Domain.
- **G4. Who writes `intake.yaml`.** No engine command is named for creating/updating it or
  appending `review_findings`. If skills write it directly, that write is outside the
  "engine is the only behavior" layering and outside `--dry-run` `changes`; if the engine
  writes it, the command is missing from ISS-049's list.
- **G5. Maintain operations lack engine commands.** RFC:285 lists edit, retire, re-scope SCDs and
  RFC:287 "pin imports"; the engine has `add scd|bundle` only. Retirement has no defined
  representation in SCD or bundle schema (RFC §7 diff mentions "retired" SCDs, RFC:513).
- **G6. Git side effects in `changes`.** `bundle version` commits and tags by default. RFC §3
  `changes` lists files only; §6.1 confirmation covers files. Whether tags/commits must be shown
  and confirmed is unstated. The scaffold's `git init` for the Domain repository has the same issue.
- **G7. Diagnostic `code` vocabulary.** Envelope requires `code` but no registry, naming rule,
  or stability guarantee is given; skills that branch on codes need one.
- **G8. Workspace-qualified manifest naming.** RFC:591-592 "Version manifests MUST be named the
  same way" as `<workspace>/<bundle-name>-v<version>` tags; a `/` cannot be in a filename, and
  **[UNCOMMITTED]** `bundle-format.md` §7.6 uses `<bundle-name>-v<version>-MANIFEST.yaml`. A
  per-workspace directory may be the intended qualifier (inference); not stated.
- **G9. Meta bundle version for 0.7.** RFC is silent; `meta/` and scaffold pin
  `bundle:meta:0.6.0` (`new.py:30`). Skills explaining context need to know which applies.
- **G10. Placement-guide location and shape.** "Maintained outside the spec text" (RFC:614-615)
  but no path, format, or machine-readable structure is given, so a skill cannot reliably load
  it (e.g. as a `references/` file vs a URL). The guide "MUST be checked against each service's
  current documentation" — no recorded check date or owner field.
- **G11. Skill split and naming.** RFC names seven skills (Impl. note 5) but not their
  boundaries: where placement advice lives (compile vs explain), whether review is invoked by
  draft and version or stands alone, whether "maintain" belongs to draft. No skill names
  (Agent Skills `name` must be lowercase-hyphen and match the directory; generic names like
  `validate` will collide with other installed skills — inference).
- **G12. Engine discovery and installation from skills.** Unresolved Q3 (RFC:838-840): no
  fallback is defined if `pip install` fails; no minimum engine version check; no statement of
  how a skill detects `--json` support. `compatibility` frontmatter could carry requirements
  (Agent Skills spec), not mentioned.
- **G13. "Current conversation" evidence.** §6.2/6.3 depend on what the user said in the
  current conversation; no record requirement for the approver confirmation itself (only the
  manifest's `approved_by`). Auditors cannot tell whether the approver was named or accepted
  from a suggestion.
- **G14. Writes outside the repo.** §6.8 MUST NOT write outside the Domain repository, but
  creating a new Domain repository necessarily writes a new directory (parent location
  unspecified), and source documents shared from elsewhere must be copied into `sources/`.
- **G15. Existing workspaces.** Unresolved Q7 (no `intake.yaml` for pre-0.7 workspaces) and the
  Migration Guide layout move (RFC:910-914) leave the intake skill without a defined onboarding
  path for 0.6 workspaces such as the CDMO trial workspace.
- **G16. Finding target syntax.** `target: scd:project:design-history#DC-004` (RFC:453) uses a
  `#item` fragment not defined elsewhere; artifact rule ids use `<bundle>/<scd>/<id>`
  (`runtime-artifact.md` §2.5 :142-148).
- **G17. Unresolved Questions in this area.** Q1 (skills location: in-repo `agent/skills/` vs
  separate repo), Q2 (fate of scs-vibe/scs-team), Q3 (sandbox install), Q8 (`AGENTS.md` +
  pointer vs per-client files) are all open; ISS-051 says Q1-Q3 must be settled first. Q8 also
  affects whether the scaffold writes `CLAUDE.md` (RFC:583-585 says SHOULD, so partly decided).
- **G18. RFC links.** RFC links point to `spec/0.6/` (RFC:288, 524, 620, 930-931); 0.7 text now
  lives in `spec/0.7/`.

## Dependencies

- Skills (ISS-051) depend on: machine mode (ISS-049) for every engine call; Domain
  repositories (ISS-048) for intake step 1 and scaffold; intake schema + `derived_from`
  (ISS-050) for intake, draft, review; `scs bundle diff` (ISS-052) for version §6.6; placement
  guide (ISS-053) for compile/explain advice; PyPI publish of `scs-tools` and `scs-validator`
  at 0.7.0 (ROADMAP workstream 8) for hosted sandboxes.
- Digest work (ISS-045, **[UNCOMMITTED]**) is a prerequisite for compile/version skills to
  report truthful results; needs committing before skills are built against it.
- Spec text updates depend on decisions in G1, G8, G9 and Unresolved Q5 (workspace-level
  versioning, RFC:844-847), which changes the version skill's flow and manifest naming.
- MCP server (ISS-054) depends on the same envelope; RFC orders it last.
- Acceptance test (ISS-055) depends on all of the above plus a chosen chat client and a
  baseline run with 0.6 tools.
- RFC 0003 (stub) is not a dependency for 0.7; review runs on agent judgment.

## Risks

- **Spec/RFC divergence.** `spec/0.7` currently contradicts the RFC in several places
  (`bundle-format.md` §8 two-repo layout and §14 Project-scoped-to-Domain extension;
  `terminology.md` §2.11/§3.4 and `core-model.md` §5.4 on Personal; `governance-and-compliance.md`
  §8-9 agent role). Skills that "use the spec" as reference material would inherit these.
- **Layering erosion.** If `intake.yaml`, SCD edits, and `review_findings` are written by skills
  directly (G4, G5), behavior moves into the non-deterministic layer the RFC says must not
  carry it, and `--dry-run` cannot show those changes.
- **Client variance.** Agent Skills portability is not guaranteed (RFC:757-759); `allowed-tools`
  is experimental and space-separated per the open spec, while the existing plugins use a
  comma-separated Claude Code form. Script execution and network access differ by client.
- **Installation in hosted sandboxes.** PyPI currently lacks a working toolchain (ROADMAP
  workstream 8); a bundled engine (Unresolved Q3) would duplicate the engine.
- **Stale prior art.** The plugins are discoverable in the repo and in `docs/resources.md:40-70`
  as current; a user or agent may follow them (11-concept layout, `scd:standards` copying,
  writing into app repos) instead of 0.7 skills (inference).
- **Approval integrity rests on conversation behavior.** Engine prevents environment
  inference, but an agent-supplied `--approved-by` is indistinguishable from a user-named one
  (G13).
- **Advisory review fatigue / inconsistency** acknowledged by RFC (RFC:760-763); no profiles
  until RFC 0003.
- **Uncommitted digest work.** Spec and tooling for §11 are uncommitted; a lost or reworked
  change set would reopen ISS-045 and the spec text with it.

## Tests (how skills/agent behavior could be tested; what exists)

- **Exists.** Engine tests: `tools/cli/tests/test_compile.py` (**[UNCOMMITTED]** +118 lines for
  digest), `tools/cli/tests/test_scs_tools.py`, `tools/scd-validator/tests/{test_digest.py
  (untracked), test_governance_060.py, test_packaging.py, test_regression_050.py}`; CI
  `.github/workflows/tools-ci.yml` runs `scs-validate` over scaffolds. Plugins have no tests;
  only manual demo scripts (`plugins/scs-team/demo/DEMO-SCRIPT.md`, `plugins/scs-vibe/demo/`)
  and an ad hoc `plugins/temp-test.md` (local `--plugin-dir` note).
- **Deterministic layer (testable now once built).** Envelope schema tests per command;
  `--dry-run` `changes` equals actual writes; no stdout besides one JSON object; no prompt when
  stdin is closed; exit-code mapping; no approver without `--approved-by`; validator findings
  mapped into `diagnostics` with `code`.
- **Skill structure.** `skills-ref validate <skill-dir>` from the Agent Skills project checks
  frontmatter and naming (agentskills.io/specification, "Validation").
- **Skill behavior (inference).** Scripted-conversation tests against RFC §6 rules, as the RFC
  itself proposes under Future Possibilities (RFC:867-868): assert that the transcript shows a
  dry-run before each write, the approver came from a user turn, no `--force`/`--no-validate`/
  `--allow-draft` without a user request, no success claim after `ok: false`, findings recorded
  in `intake.yaml`, no writes outside the repo (filesystem diff), and placement advice given but
  no file placed. A shim `scs` on PATH that logs arguments can check flag use without a model
  judge. Claude Code has a client-specific plugin eval runner (`claude plugin eval`); other
  clients would need their own harness.
- **Acceptance.** ISS-055 (Omarchy, one Domain + two Projects, no CLI, no spec reading, friction
  log, baseline vs 0.6 tools). No success criteria beyond "validated, versioned, compiled, with
  placement advice" are defined; friction log format unspecified.
