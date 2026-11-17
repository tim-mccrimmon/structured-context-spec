# Survey: Validator and schemas

Surveyed 2026-10-25 on branch `0.7-dev` (HEAD `f1c9d11`). Paths are relative to the worktree
root. **[U]** marks content that exists only as uncommitted working-tree changes (the ISS-045
hardening batch); everything else is committed. "Inference" marks conclusions not stated in
code or docs.

## Scope read

- `rfcs/RFC-0002-agent-mediated-scs.md` in full (itself modified **[U]**: §9 reserved dirs and
  names, Validation Rules lines 736-738 were added uncommitted).
- `ISSUES.md` ISS-042..055 (lines ~845-990; ISS-045 "done" text is **[U]**). `ROADMAP.md`.
- `tools/scd-validator/`: all of `src/scs_validator/` (`commands/validate.py`, `bundle_validator.py`,
  `resolver.py`, `digest.py` **[U]**, `schema_validator.py`, `semantic_validator.py`,
  `parser.py`, `reporter.py`, `rules_loader.py`, `utils.py`, rules YAML), `scripts/sync_schemas.py`,
  `pyproject.toml`, all tests.
- `schema/` (all 7 JSON schemas plus `domain/examples/`).
- Compiler use of digest/artifact schema: `tools/cli/scs_tools/compiler.py` **[U]**,
  `commands/compile.py`, `commands/bundle.py` (version path) **[U]**, `tests/test_compile.py` **[U]**.
- `spec/0.7/bundle-format.md` §7.6, §8, §9 **[U]**; `spec/0.7/runtime-artifact.md` diff **[U]**;
  `docs/MIGRATION-0.7.0.md` diff **[U]**; `.github/workflows/tools-ci.yml`.
- Ran tests read-only (ephemeral `uv run --no-project`, no bytecode, no pytest cache):
  validator 204 passed; `tools/cli/tests/test_compile.py` 31 passed.

## Components

| Component | Responsibility | Key files |
|---|---|---|
| CLI entry (`scs-validate`, also re-exported as `scs validate`) | Option parsing, mode dispatch (bundle / domain manifest / checkpoint / files), exit codes | `tools/scd-validator/src/scs_validator/commands/validate.py:23-209`; entry point `pyproject.toml` `[project.scripts]`; re-export `tools/cli/scs_tools/commands/validate.py:14` |
| Bundle pipeline | Levels 1-6 for one root bundle: parse, bundle schema, type rules, tree, digests, per-SCD semantic, relationships, completeness | `commands/validate.py:325-435` (digest hook **[U]** at 378-385) |
| Resolver | Index every YAML with an `id` under the workspace root (plus packaged meta); resolve imports/SCDs by id; build `BundleTree` | `resolver.py:79-83` (`find_project_root`), `:23-24` (`LAYOUT_DIRS`, `SKIP_DIRS`), `:95-141` (`Index`), `:144-200` (`resolve`); `BundleTree.index` field **[U]** `:61,171` |
| Content digest **[U]** | Canonical JSON, per-document SHA-256, recursive bundle digest, `content_inputs`, version-manifest lookup, verification | `digest.py:43-49` (canonical/digest), `:95-135` (`content_digest`), `:138-160` (manifest names/lookup), `:198-230` (`verify`, `verify_tree`) |
| Bundle validator (Level 5) | XOR, per-type import rules, meta pinning, unresolved imports/SCDs, cycles; digest verification **[U]** | `bundle_validator.py:23-88`, `:90-231` (`validate_tree`), `:233-262` (`validate_digests`) **[U]** |
| Schema validator (Level 2) | Draft 2020-12 validation; schema picked by SCD tier from id | `schema_validator.py:25-82`, `:259-308`; finders `utils.py:103-173` |
| Schema dir discovery | `--schema-dir` > `$SCS_SCHEMA_DIR` > `schema/` upward from cwd > source checkout > packaged copy | `utils.py:176-241` |
| Semantic validator (Level 3) | type/tier, version, provenance, id format, item-id uniqueness across directives/prohibitions/facts, binary prohibitions | `semantic_validator.py:25-122` |
| Relationship / completeness / ontology validators | Level 4, Level 6 (opt-in), domain manifest rules (RFC 0001) | `relationship_validator.py`, `completeness_validator.py`, `ontology_validator.py` |
| Rules loader | Loads `rules/v0.6.0/*.yaml` (fixed default), message templates | `rules_loader.py:21-28`, `:150-170` |
| Reporter | Text and JSON reports | `reporter.py:25-109`, `:111-184` |
| Schema vendoring | Mirror `schema/**/*.json` and `meta/**/*.yaml` into the package; `--check` for drift | `tools/scd-validator/scripts/sync_schemas.py:24-27,34-65`; enforced by `tests/test_packaging.py:61,110,128` |
| Compiler (consumer, tools/cli) | Verifies digests, emits `source_digest` **[U]**; builds artifact by whitelist | `tools/cli/scs_tools/compiler.py:75-96`, `:106-128`, `:174-182` |
| `scs bundle version` (consumer, tools/cli) | Computes and records `content_digest`/`content_inputs` **[U]**; records truthful `validation_passed` **[U]** | `tools/cli/scs_tools/commands/bundle.py:343-420`, `:553-560`, `:646-647`, `:697` |

## Data model

| Schema (repo path) | `$id` | Required / key fields | 0.7 status |
|---|---|---|---|
| SCD project tier `schema/scd/project-scd-template.json` | `.../scd.project.schema.json` | `id,type,title,version,description,content,provenance` (`:7`); `content.directives[]` `{id,directive,cites}` (`:272-298`), `prohibitions[]` `{id,kind,subject,instead,reason,cites}` (`:299-340`), `facts[]` `{id,fact,cites}` (`:341-367`) | Unchanged. Items are `additionalProperties: false` (`:296,338,365`), so `derived_from` is a **schema error today**. |
| SCD meta tier `schema/scd/meta-scd-template.json` | `.../scd.meta.schema.json` | same top level; `content.directives[]` only (`:153-178`, closed at `:177`) | Unchanged. No prohibitions/facts in meta tier. |
| SCD standards tier `schema/scd/standards-scd-template.json` | `.../scd.standards.schema.json` | same top level; no directives/prohibitions/facts | Unchanged (tier deprecated since 0.6). |
| Bundle `schema/bundles/scd-bundle-schema.json` | `.../bundle.schema.json` | `id,type,version,title,description,imports,scds,provenance`; id `^bundle:[a-zA-Z0-9._-]+$` (`:11`); non-DRAFT requires `provenance.version_approved_by/_at` (`:166-183`) | Unchanged (RFC: "No bundle manifest fields change"). `version_approved_by` is a plain string, no `minLength` (`:74-77`). Reserved names not expressible here today. |
| Version manifest | none | Written ad hoc by `bundle.py:620-697`: `version, release_date, status, project, bundle{id,type,file,sha256,size_bytes}, content_digest`**[U]**`, content_inputs`**[U]**`, validation{...}, components, approval{approved_by,approved_at,approval_notes}, phases, release_notes, distribution` | **No schema exists.** RFC "Schema Changes" (line 713) adds a required field to a document with no schema. `approved_by` lives at `approval.approved_by`, not top level. |
| Runtime artifact `schema/runtime/runtime-artifact-schema.json` | `.../runtime-artifact.schema.json` | `scs_runtime,id,type,version,title,sources,rules` | **[U]** `scs_runtime` `const "0.6"` -> `enum ["0.6","0.7"]`; new optional `source_digest` `^sha256:[0-9a-f]{64}$` (`:29-33`). Not conditionally required for non-DRAFT 0.7 artifacts. Rule/fact items closed (`additionalProperties: false`), so `derived_from` would fail artifact validation. |
| Domain manifest `schema/domain/domain-manifest-schema.json` | `.../domain-manifest.schema.json` | `domain{id,name,version,description,ontology,schemas}` | Unchanged; no 0.7 impact found. |
| Checkpoint record `schema/checkpoint/checkpoint-record-schema.json` | `.../checkpoint-record.schema.json` | `checkpoint{bundle,agent,intent,timestamp}` | Unchanged; no 0.7 impact found. |
| Intake record `schema/intake.schema.json` | n/a | RFC §4 example (lines 421-460) | **Does not exist.** No code references `intake`. |
| Bundle `provenance` (snapshot) | via bundle schema `additionalProperties: true` | `bundle.py:553-561` writes `version_approved_by/_at, approval_status, validation_passed, validation_date, version_notes` | **[U]** `validation_passed`/`approval_status` now truthful; not schema-typed. |

Duplication between `schema/` and the package:

- `tools/scd-validator/src/scs_validator/schemas/` mirrors all 7 `schema/**/*.json` byte-for-byte;
  `diff -rq` shows only `schema/domain/examples/` (YAML, not synced by design, `sync_schemas.py:25`).
  The runtime schema change is applied in both copies **[U]**, so `--check` passes.
- Packaged `meta/` mirrors repo `meta/` (`sync_schemas.py:26`).
- `tools/cli/tests/test_compile.py:21` reads the repo-root runtime schema directly, not the packaged copy.
- `CITATION_RE` is duplicated in `utils.py:11` and as `pattern` strings in each SCD and runtime schema.
- A new root-level `schema/intake.schema.json` would be picked up by `sync_schemas.py` (`rglob("*.json")`) without script changes (inference).

## Validation rules

Where rules live:

- `src/scs_validator/rules/v0.6.0/{scd,bundle,relationship,completeness,domain-ontology}-rules.yaml`;
  directory hardcoded at `rules_loader.py:21-23`. No `v0.7.0/` set. The two 0.7 messages
  (`content_digest_mismatch`, `content_digest_unrecorded`) were added to `v0.6.0/bundle-rules.yaml:345-349` **[U]**.
- Rule YAML is partly declarative only: `severity` keys exist throughout but `get_severity`
  (`rules_loader.py:183`) has no callers; severities are decided in Python (`add_error`/`add_warning`).
  `validation_modes` DRAFT/VERSIONED (`scd-rules.yaml:129-147`) and `scd_uniqueness`
  (`bundle-rules.yaml:216-221`) have no implementing code (grep finds no references).
- `rules/README.md:15-28` still documents `v0.5.0/` as current (stale).

What is checked (bundle mode):

| Level | Check | Location |
|---|---|---|
| 1 | YAML/JSON parse | `parser.py:101-131` |
| 2 | Bundle schema; pipeline stops on failure | `commands/validate.py:358-370` |
| 3 | Per-SCD semantic incl. item id uniqueness and binary prohibitions (SCD schema is **not** run in bundle mode; only in file mode, `validate.py:302`) | `semantic_validator.py:76-122` |
| 5 | XOR, type import rules, meta pinning, unresolved imports (error), unresolved SCDs (warning), cycles | `bundle_validator.py:23-231` |
| 5 **[U]** | Digest: every versioned bundle in tree with a manifest; mismatch = error in all modes; manifest without `content_digest` = warning; no manifest = silent | `bundle_validator.py:233-262`, `digest.py:198-230` |
| 4 | Relationships | `relationship_validator.py` |
| 6 | Completeness (opt-in, `enabled: false` default) | `completeness-rules.yaml:18-20` |

Not checked: SCD-id uniqueness across the tree (resolver silently takes the first match,
`resolver.py:189-196`; `digest.py:113` likewise); version-manifest `approved_by`; `intake.yaml`;
`derived_from`; reserved directories or bundle names; repository layout.

Loose vs strict: one flag. `--strict` does not upgrade warnings to errors; it changes the exit
code to 2 when there are warnings and no errors (`validate.py:438-448`) and the JSON status to
`valid_with_warnings` (`reporter.py:132-137`). There is no "loose" flag; loose is the default.

## Interfaces

`scs-validate` (`commands/validate.py:23-97`):

| Input | Flag |
|---|---|
| SCD files | positional `FILES...` (must exist; directories accepted by click but then fail to parse as SCDs, inference from `validate.py:298`) |
| Bundle | `--bundle/-b PATH` |
| Domain manifest | `--domain/-d PATH` |
| Checkpoint record | `--checkpoint/-c PATH` |
| Options | `--schema-dir/-s`, `--output/-o text\|json`, `--strict`, `--no-color`, `--verbose/-v`, `--skip-completeness`, `--completeness-rules PATH` |

Modes are mutually exclusive by `if/elif` precedence (`validate.py:161-186`); there is no
directory, workspace, or repository mode, and no `--intake`.

Exit codes: 0 ok; 1 errors; 2 warnings under `--strict`; 3 no input (`:186`); 4 schema dir not
found (`:142`); 5 `ValidationError` or unexpected exception (`:200-209`). These match RFC §3's list.

Machine-readable output: `--output json` (`reporter.py:111-184`): `validator_version`,
`strict_mode`, `validation_levels{level:{status,error_count,warning_count,...details}}`,
`errors[]`/`warnings[]` of `{level,message,scd_id,file_path}`, `summary{total_errors,total_warnings,status}`.
No stable diagnostic `code`, no `severity` field per item, no `suggestion`; digest mismatch
file lists are embedded in the message text (`bundle_validator.py:243`). `validator_version` comes
from a hardcoded `__version__ = "0.6.0"` (`src/scs_validator/__init__.py:3`; `pyproject.toml` version
also 0.6.0), the same staleness pattern ISS-042 fixed for scs-tools.

Python API used by tools/cli: `scs_validator.resolver.resolve`, `scs_validator.digest.{content_digest,
verify_tree, tree_index, DigestError}` **[U]** (`compiler.py:79`, `bundle.py:345-346`). `scs bundle
version` and `scs compile` also shell out to `python -m scs_validator --bundle ... --no-color`
(`bundle.py:461-488`, `compile.py:60-78`); `bundle.py:480-481` scrapes error/warning counts from
text output with regexes.

## RFC 0002 vs as-built

| Requirement (RFC line) | Status | Evidence |
|---|---|---|
| §4 `intake.yaml` validated against `schema/intake.schema.json` (415-419; VR 724) | not started | no schema file; no `intake` reference in `tools/scd-validator/src` |
| §4/§12 `review_findings` with `kind` enum, `decision` `changed\|kept\|deferred`, `decided_by/_at` (450-459, 680-682) | not started | (schema absent) |
| §5 optional `derived_from` on prohibitions, directives, facts; `oneOf intake\|source`, optional `locator` (464-487, 694-711) | not started; currently **conflicts** | items closed: `project-scd-template.json:296,338,365`, `meta-scd-template.json:177`; any `derived_from` is a schema error today |
| VR: `derived_from.intake` resolves to `answers[].id`, `.source` to `source_documents[].id`; warning loose / error strict (725-727) | not started | no workspace-to-intake lookup exists |
| VR/§5: compile never emits `derived_from` (486, 729) | done by construction | compiler copies only `id`, rule/fact text, `cites` (`compiler.py:124-128`); runtime schema items closed |
| §12: findings not compiled (683) | done by construction | intake is never read by compiler; not indexed (no `id`) by `resolver.py:111` |
| §11 `content_digest` over manifest + SCDs + imports, canonical JSON, SHA-256 (629-641) | done **[U]** | `digest.py:43-49,95-135`; spec `spec/0.7/bundle-format.md` §7.6 **[U]**; tests `test_digest.py:92-131` |
| §11 order "imports by id" (639-640) | done, slightly different | code sorts by import reference string (`digest.py:119`); spec 0.7 §7.6 says "sorted by reference" |
| §11 imports contribute "that bundle's own `content_digest`" (634) | done, differently | recomputed recursively from content (`digest.py:120-126`), not read from the import's manifest; unpinned imports also recurse |
| §11 validator recomputes and reports mismatch as error in every mode, naming changed files (645-646; VR 730-732) | done **[U]** | `bundle_validator.py:233-262`; `test_digest.py:174-185` |
| VR: manifest without `content_digest` warns (731-732) | done **[U]** | `digest.py:204-206`; `test_digest.py:186-192` |
| §11 compile verifies, refuses on mismatch, no override (647-648) | done **[U]**, partial | `compiler.py:75-95`; skipped when any bundle in the tree is `DRAFT` (`compiler.py:78`), so a DRAFT root compiled with `--allow-draft` does not verify its pinned versioned imports (validator does) |
| §11 `validation_passed`/`approval_status` truthful (649-650) | done **[U]** (CLI) | `bundle.py:557-560` (recorded in snapshot provenance, not in the version manifest, which has `status` and `validation.passed`) |
| §11 / Schema Changes: `source_digest` in artifact, absent for DRAFT (652-655, 715-717) | done **[U]** | `runtime-artifact-schema.json:29-33`; `compiler.py:96,180-181`; `test_compile.py` ISS-045 block (~340-460) |
| Schema Changes: required `content_digest` in version manifests (713-714) | partial | written by `bundle.py:646`; no version manifest schema exists to require it |
| VR: version manifest MUST have non-empty `approved_by` (728) | not started (validator) | CLI refuses blank at version time (`bundle.py:328-333`); validator never checks manifests' approval; bundle schema `version_approved_by` lacks `minLength` |
| §9 VR: at Domain repo root, validate `domain/` and every `projects/*`; error on zero or several `domain/` (733-735) | not started | no directory/repo mode in `validate.py:161-186` |
| §9 VR: reserved `plan/`, `test-plan/`, `qa/` never reported, content not validated (575-577, 736-737) | not started; latent **conflict** | `resolver.py:24` `SKIP_DIRS` lacks them; `Index._scan` indexes any YAML with an `id` under the workspace root, so a reserved-dir YAML can shadow or duplicate an SCD/bundle id (inference) |
| §9 VR: bundle named `plan`/`test-plan`/`qa` is an error (592-593, 738) | not started | no rule in `bundle-rules.yaml`; id pattern `:28` admits them |
| §9 manifests and tags qualified `<workspace>/<bundle-name>-v<version>` (587-592) | partial (ISS-048) | name-qualified only: `digest.py:138-142` (`<name>-v<version>-MANIFEST.yaml`, legacy `VERSION-<v>-MANIFEST.yaml`), `bundle.py:337,697` |
| §9 compiled output in `dist/` | n/a here; compatible | `dist` already in `SKIP_DIRS` (`resolver.py:24`), so compiled artifacts are not indexed |
| §3 validator JSON carried in envelope `result`, findings mapped to `diagnostics` with `code` (359-362) | not started (ISS-049) | report has no codes (`reporter.py:162-182`) |
| Appendix step 4: run `scripts/sync_schemas.py` (891-892) | ready | script exists; picks up new files automatically |

## Gaps and ambiguities in the RFC

- **Intake schema shape is unspecified.** Only an example (421-460). Not stated: required
  fields per `audience`/`workspace` combination; whether the profile tables (385-413:
  `owner`, `boundaries`, `practices`, `project`, `risk`, `data`) are top-level keys (the example
  puts `organization`, `certifications`, `approvers` at top level but `boundaries` only appear as
  `answers`); `additionalProperties` policy; enum for `review_findings[].kind` beyond the four in §12;
  whether `rationale` is required only for `kept` (681 says "kept (with a rationale)"); format of
  `target` (`scd:project:design-history#DC-004` is a new id#item syntax not defined elsewhere).
- **`intake_version` vs `scs_version`.** Two version fields with no stated semantics or allowed values.
- **Timestamps.** The example's `answered_at: 2026-10-20T14:12:00Z` is unquoted; PyYAML loads it as
  a `datetime`, which fails JSON Schema `type: string` (repo examples quote timestamps, e.g.
  `examples/two-tier-governance/org/context/project/company-profile.yaml:24`). The RFC does not say
  which is canonical (inference from `parser.py:115`).
- **Schema file location.** `schema/intake.schema.json` (419, 693) breaks the existing
  `schema/<kind>/<kind>-schema.json` convention that `utils.py:103-173` finders follow.
- **Version manifest has no schema.** "New required `content_digest` field" (713) and "MUST have a
  non-empty `approved_by`" (728) presuppose one. The manifest stores the approver at
  `approval.approved_by`; the RFC names a bare `approved_by`.
- **"Errors in strict mode."** VR 725-727 makes unresolved `derived_from` ids errors under strict;
  the validator's strict mode does not reclassify warnings, it only changes the exit code to 2.
  Whether "error" means exit 1 or exit 2 is open.
- **Which `intake.yaml`.** Resolution is against "the workspace's" intake; for an SCD in a concept
  bundle, or a file validated outside bundle mode, the workspace root has to be discovered
  (`.scs/config` marker vs `find_project_root`, `resolver.py:79-83`). Not specified. Also unstated:
  SCD imported across workspaces (not possible today since project/domain trees are independent).
- **Reserved directories: depth.** "in every workspace" — at workspace root only, or any depth?
  `SKIP_DIRS` matching is by any path component (`resolver.py:90`), so a naive add of `plan`
  would also skip e.g. `context/plan/`.
- **Reserved bundle names: by what.** "A bundle named `plan`" — by id (`bundle:plan`), file stem, or
  both? The CLI derives the name from the id, falling back to the stem (`bundle.py:495-500`).
  Whether `plan` etc. as an SCD name or concept-bundle name is also reserved is not stated.
- **Workspace-qualified manifest naming.** 590-592 say manifests are named "the same way" as
  `<workspace>/<bundle-name>-v<version>` tags; a `/` cannot be in a file name, and manifests already
  sit inside the workspace directory. Unclear whether the workspace prefix belongs in the file name.
- **Repository-level validation output.** No shape given for aggregating several workspaces into
  one report/exit code, or for how a CI run on repo root names failing workspaces.
- **Digest and the intake record.** `intake.yaml` (including `review_findings` decisions and
  `answers` that `derived_from` cites) is outside the content digest, so the audit record behind a
  version is not covered by immutability. The RFC does not say whether it should be.
- **Digest scope for unversioned imports and missing manifests.** RFC 645 says the validator,
  "given a versioned bundle", MUST verify; spec 0.7 §7.6 **[U]** narrows this to bundles that have a
  manifest and stays silent otherwise. A versioned bundle whose manifest is deleted is not reported.
- **Unresolved Q6 (provenance granularity)** and **Q4 (personal data in intake)** both affect the
  intake schema (role-only attribution would change `approvers`/`answered_by`).

## Dependencies

What this area needs from others:

- `tools/cli` (`scs bundle version`) is the only writer of version manifests and `content_digest`;
  the validator's checks depend on its file naming (`bundle.py:697` vs `digest.py:138-142`).
- ISS-048 (CLI scaffold) defines the Domain repository layout and `.scs/config` marker that
  repository-level validation would detect.

What others need from this area:

| Consumer | Needs |
|---|---|
| CLI engine (ISS-049 machine mode) | Stable diagnostic codes, per-item severity, structured fields (e.g. changed files on digest mismatch) instead of message text; JSON report to wrap in `result`. `bundle.py:480-481` and `compile.py:60-78` currently parse text or exit codes. |
| CLI `scs compile`, `scs bundle version` | `scs_validator.resolver` and `scs_validator.digest` as an importable API (already coupled **[U]**); `scs bundle version` now hard-requires scs-validator (`bundle.py:344-350`). |
| CLI `scs bundle diff` (ISS-052, inference) | `content_inputs` per-document digests and the resolver tree are the natural basis for "what changed". |
| Skills (ISS-051) | `intake.schema.json` to write valid intake records; `derived_from` accepted by SCD schemas; resolution diagnostics naming the unresolved id; repo-root validation for CI (§9) and for "validate everything" in chat; deterministic error text to explain in plain language. |
| CI workflow generated by scaffold (ISS-048) | A single command that validates the whole Domain repository with `--strict` (RFC 599-601). Today it would need one `--bundle` call per workspace. |
| MCP server (ISS-054) | Same JSON/diagnostic contract as skills. |

## Risks

- **Edit-in-progress breaks validation hard (high, inference).** SCDs are not snapshotted; the
  working tree is the content of every version (`docs/MIGRATION-0.7.0.md` item 5 **[U]**). Editing an
  SCD in a versioned concept bundle makes the DRAFT Domain/Project bundle that pins it fail
  validation with an error "in every mode" until the concept bundle is re-versioned and re-pinned.
  An agent loop of edit-then-validate will hit this on the first edit to existing content.
- **Silent escape from verification.** A versioned bundle with no version manifest is not reported
  (`digest.py:200-202`); deleting or renaming the manifest removes the check. `compiler.py:96` still
  emits a `source_digest` for such a root, which looks like a verified digest but was never recorded.
- **Compile with DRAFT root skips verification** of pinned imports (`compiler.py:78`), while the
  validator verifies them; `scs compile --no-validate --allow-draft` compiles tampered imports.
- **Ambiguous id resolution.** Duplicate SCD or bundle ids are resolved by sorted path order
  (`resolver.py:137,196`; `digest.py:113`), unchecked despite spec §9.2 and the declared
  `scd_uniqueness` rule. Reserved dirs (`plan/` etc.) holding YAML with ids would feed this.
- **Schema strictness vs additive claim.** Adding `derived_from` requires opening item schemas;
  anyone running a 0.6 validator (or a cwd `schema/` from an older checkout, `utils.py:225-230`)
  against 0.7 SCDs gets hard schema errors. Discovery prefers a cwd/checkout `schema/` over the
  packaged copy, so version skew between schema and code is possible.
- **Digest stability depends on PyYAML parsing.** Dates/timestamps canonicalized via `isoformat`
  (`digest.py:38-39`); a YAML loader change or another implementation (MCP, another language)
  could diverge. Spec 0.7 §7.6 pins the forms, mitigating this.
- **Rule YAML drift.** Declared-but-unimplemented rules (`validation_modes`, `scd_uniqueness`,
  severities) can mislead contributors or skills reading the rules as truth.
- **Version reporting.** Validator `__version__` and package version are 0.6.0; manifests record
  `validator_version` (`bundle.py` `_validator_version`) and reports carry it.
- **Rules directory naming.** 0.7 rules are being added under `rules/v0.6.0/` **[U]**; no versioned rule set for 0.7.

## Tests

Existing (`tools/scd-validator/tests/`, 204 passing):

| File | Covers |
|---|---|
| `test_digest.py` **[U]** (`:92-192`) | canonical JSON, dates, digest format, formatting vs content edits, missing SCD, import change propagation, verify statuses, DRAFT not verified, validator exit 1 on mismatch without strict, warning and strict exit 2 on unrecorded |
| `test_governance_060.py` | bundle type/import rules, resolver, cycles, citations, directive/prohibition/fact validation |
| `test_regression_050.py` | examples validate, ontologies, checkpoint records, schema-dir discovery, strict exit 2 |
| `test_packaging.py` | packaged rules/schemas/meta present and in sync (`:61`, `:110` runs `sync_schemas.py --check`) |
| `tools/cli/tests/test_compile.py` **[U]** | artifact validates against repo runtime schema (`:21,62-64`); versioning records digest, edited SCD refused, formatting edits keep digest, unrecorded manifest warns |

How to run (read-only, no repo writes):

```
cd tools/scd-validator
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src uv run --no-project \
  --with pyyaml --with jsonschema --with click --with colorama --with tabulate --with semver --with pytest \
  python -m pytest -q -p no:cacheprovider -o addopts="" tests
```

For `tools/cli/tests/test_compile.py`, `PYTHONPATH` must be absolute (`$PWD:$PWD/../scd-validator/src`)
because `scs bundle version` re-invokes `python -m scs_validator` after `chdir`; with a relative path
four ISS-045 tests fail spuriously. CI: `.github/workflows/tools-ci.yml:40-46` (editable installs).

Holes:

- No tests for: intake schema, `derived_from` (accept, resolve, unresolved warning/strict), reserved
  dirs ignored, reserved bundle names, repository-level validation, version manifest `approved_by`.
- Digest: no test for an import cycle during digest (`DigestError` path, `digest.py:106-107`,
  `verify_tree` skip `:226-227`); legacy `VERSION-<v>-MANIFEST.yaml` lookup; manifest whose
  `bundle.id`/`version` disagree (`digest.py:157-159`); duplicate-id shadowing; non-root versioned
  import mismatch reported via a DRAFT root; JSON output of digest diagnostics.
- No test that the packaged runtime schema (rather than repo root) validates compiled artifacts.
- No test that compile never emits `derived_from` (true by construction today).
- No test of `--output json` shape stability, which ISS-049 will depend on.
