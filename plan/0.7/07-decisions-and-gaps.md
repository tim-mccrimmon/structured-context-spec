# 7. Decisions and gaps

Every item here is the maintainer's call. "Rec." is the drafting recommendation, not a decision.
**Blocks** names the work packages that cannot start until the item is decided; this column is
the single source for each WP's decision dependencies in section 6. "RFC" means the outcome
amends RFC 0002. The Decision column records outcomes; **Decided** entries are final.

Two batches, so engine work can start before the rest is settled: **WP-01a** (sections A to D)
and **WP-01b** (section E, except D-27, which WP-11a settles).

Sources: `survey/*.md`, `review/plan-review-1.md`, `review/plan-review-2.md`.

## A. Integrity model and versioning (WP-01a)

The integrity model (D-39, D-40, D-53, D-54) was decided by the maintainer on 2026-10-25 after
review 2. Summary: **the git tag is the record of a version.** It points at a commit holding the
whole workspace; verification reads the tagged content and the tagged manifest, and working-tree
copies must match them. Section 5 states the model in full.

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-39 | Where does trust in a version come from, and what does validation verify? | The tag. Verification set: (1) every version tag in the repository: the digest recomputed from the tagged content equals the `content_digest` in the tagged manifest, and each pinned import's manifest at that commit equals the import's own tagged manifest; (2) for versions still in use (pinned by a working bundle, or the latest version of a bundle whose working file exists), the working manifest and snapshot equal their tagged copies by git blob id (`MANIFEST_ALTERED`); (3) every pinned import of a working bundle matches its tagged content (drift, `CONTENT_DIGEST_MISMATCH`). A version tag without a manifest at the tag is an error; so is a manifest carrying `content_digest` with no qualified tag (`VERSION_TAG_MISSING`), and repository mode on a shallow clone (`GIT_HISTORY_INCOMPLETE`). Signing is out of 0.7; the spec states that protecting tags on the remote is the adopter's job. RFC (Validation Rules). | WP-14 | **Decided** 2026-10-25: tag is the record; signing out of 0.7. Check 2 narrowed to versions in use (review 3, decided 2026-10-25). |
| D-40 | What does a version commit contain? | Everything under the workspace directory except `dist/`, including deletions, listed in the dry run. "Rebuild from its tag" holds by construction. Consequence: uncommitted edits elsewhere in the same workspace go into the commit; the dry run shows them. Implementation: `git commit --only -- <workspace>/ ':!<workspace>/dist/'`, so nothing staged elsewhere enters; files ignored by `.gitignore` are not added; `bundle version` refuses with `VERSION_INPUT_UNTRACKED` if any digest or compiler input is ignored or untracked. | WP-14 | **Decided** 2026-10-25: whole workspace except `dist/`. |
| D-53 | What may `--no-validate` skip? | Content validation only (schemas, rules). Integrity checks always run: pinned imports match their tags. The manifest records `validation_passed: false`. | WP-14 | **Decided** 2026-10-25: content only. |
| D-54 | Pre-0.7 versions under strict CI | Migration versions each bundle once under 0.7. Versions without a workspace-qualified tag are history: not verified, not reported. Strict CI is green once each bundle has a 0.7 version. RFC (Validation Rules, Migration Guide). | WP-14 | **Decided** 2026-10-25: re-version once. |
| D-52 | What does the working bundle file hold after `bundle version`? | `DRAFT`, as built. The released copy is the snapshot, and the record is the tag. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-01 | UQ5: version per bundle or per workspace? | Per bundle. Already in ISS-043 code, ISS-045 code, and spec §7.6. Cost: a cascade of `bundle version` calls (D-44). | WP-03, WP-06, WP-14 || **Decided** 2026-10-25: per bundle. |
| D-02 | Manifest file name, given `/` in `<workspace>/` tags | `<bundle-name>-v<version>-MANIFEST.yaml` in the bundle's directory; location supplies the workspace. RFC (§9 wording). | WP-04, WP-14 || **Decided** 2026-10-25: as recommended. |
| D-03 | Which name is `<workspace>`? | `domain` or the directory name under `projects/`; `.scs/config name` must match (validator, `CONFIG_NAME_MISMATCH`). | WP-03, WP-04, WP-14 || **Decided** 2026-10-25: as recommended. |
| D-04 | Every workspace already has `domain/` for the ontology manifest, so the layout yields `domain/domain/` | Move it to `ontology/domain-manifest.yaml`; the 0.6 location is still read, with `ONTOLOGY_LEGACY_LOCATION` (info). RFC (§9 layout). | WP-03, WP-04 || **Decided** 2026-10-25: move to `ontology/`. |
| D-05 | RFC shows `context/`; as-built is `context/project/` | Keep `context/project/` for 0.7; amend the diagram. RFC. | WP-03 || **Decided** 2026-10-25: as recommended. |
| D-06 | `.scs/config` keys and meaning of `scs_version` | RFC keys (`bundle_type`, `name`, `ontology`, `scs_version` = spec version) plus `tools_version`; old keys still read. | WP-03 || **Decided** 2026-10-25: as recommended. |
| D-38 | Does `bundle version --no-git` survive? | Removed. A version is a tag. Missing git fails with `GIT_REQUIRED`. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-41 | Where does `bundle diff --from` get old content? Defaults? | From the tagged commit. No prior version: diff from empty (everything added). A bundle whose only versions are pre-0.7: diff from its stem-named snapshot, with `DIFF_LEGACY_BASELINE` (info). Explicit `--from` with no tag: `DIFF_VERSION_NOT_FOUND`. | WP-08 || **Decided** 2026-10-25: as recommended. |
| D-43 | Snapshot file name | `<bundle-dir>/<bundle-name>-v<version>.yaml`, beside the manifest; stem-named 0.6 snapshots still resolve. Snapshots are indexed by (id, version), not as working documents. | WP-04, WP-14 || **Decided** 2026-10-25: as recommended. |
| D-55 | Git identity for version commits (sandboxes usually have none) | Author = the `--approved-by` person; committer = fixed `scs-tools <noreply@scs.invalid>`; both passed with `git -c`, never read from the environment. Commit and tag listed in `changes`. Tag details in D-58. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-57 | How is a released version compiled? (review 3) | `scs compile BUNDLE --version V` compiles the snapshot for V after the D-39 checks for that version, with `source_digest`. Without `--version`, it compiles the working DRAFT and needs `--allow-draft`. | WP-14 | **Decided** 2026-10-25: `compile --version V`. |
| D-58 | Tag type and git settings (review 3) | Annotated tag; tagger is the fixed `scs-tools <noreply@scs.invalid>` identity. The engine overrides `commit.gpgsign`, `tag.gpgSign`, `core.hooksPath` (no hooks), and `core.autocrlf` with `git -c` for its commit and tag. | WP-14 | **Decided** 2026-10-25: annotated, fixed tagger, settings overridden. |
| D-59 | Are `sources/` documents committed? (review 3) | No by default: the scaffold `.gitignore` ignores `sources/`; `derived_from` still names the document; the user may opt in to tracking. Keeps source documents local (RFC §8). Rebuild is unaffected; the compiler never reads `sources/`. | WP-03 | **Decided** 2026-10-25: ignored by default. |

## B. Lifecycle integrity (WP-01a)

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-14 | Root versions while imports are DRAFT or unpinned | Refuse: `VERSION_IMPORT_NOT_PINNED`. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-15 | `--force` can rewrite a released version | Remove `--force` from `bundle version`; failed runs roll back (WP-06). `VERSION_EXISTS`. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-16 | Compile skips verification when any bundle is DRAFT | Always run D-39 checks for the compiled tree. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-17 | Unpinned import resolves to a versioned snapshot | Unpinned refs resolve to working files; pinned refs to snapshots. | WP-14, WP-08 || **Decided** 2026-10-25: as recommended. |
| D-18 | Versioned bundle with no manifest | Under D-39, a workspace-qualified version tag without a manifest at the tag is an error; a working manifest missing while its tag has one is `MANIFEST_ALTERED`. No `source_digest` without a verified digest. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-19 | Editing an SCD under a pinned concept fails validation until re-versioned | Keep. The diagnostic names the changed files and the bundles to version again, bottom-up; the version skill runs the cascade. Snapshotting SCDs is a 0.8 question. | WP-14, WP-10 || **Decided** 2026-10-25: as recommended. |
| D-44 | Does one approver confirmation cover a cascade? | Yes. Before the single confirmation, the skill shows a cascade plan listing every snapshot, manifest, pin, commit, and tag (all determined by names and versions). It then runs each step's `--dry-run` and stops if a result differs from the plan. RFC (§6.1/§6.2 reading). | WP-10 || **Decided** 2026-10-25: as recommended. |

## C. Interface contract (WP-01a)

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-07 | Who writes `intake.yaml` and review findings? | Engine: `scs intake set`, `scs intake record-finding`, with `--dry-run`. RFC. | WP-07 || **Decided** 2026-10-25: as recommended. |
| D-08 | Edit, retire, re-scope SCDs and pin imports | Option 1 (rec.): engine commands `scs scd write PATH --from-file -` (stdin, so nothing is written outside the repo), `scs bundle add-scd`, `scs bundle remove-scd`, `scs bundle add-import`, `scs bundle pin`. Retire = `remove-scd`; diff reports it as removed. RFC (§1, §7 drop "retired"). Option 2: skills edit SCD files directly, shown and confirmed; retire = removal from `scds`; MCP cannot edit content in 0.7. RFC (§1, §2, §7). | WP-05, WP-06, WP-10 || **Decided** 2026-10-25: option 1, engine commands. |
| D-09 | Git effects in `changes` | `{"action": "git-init|git-commit|git-tag", "ref": ...}`; a `git-commit` entry carries `paths: [{path, status: A|M|D}]` for everything it commits, while `create`/`modify`/`delete` list only files the run itself wrote. On `ok: false`, `changes` lists what remains after rollback (normally empty). RFC. | WP-05 || **Decided** 2026-10-25: as recommended. |
| D-10 | Diagnostic code registry | Codes with severity (`error`, `warning`, `info`) and meaning. Each WP adds its codes as a fragment `schema/diagnostics/codes.d/WP-nn.yaml`; WP-04's build step merges them into `codes.yaml`. CI fails on an unregistered code. `info` never changes the exit code, under `--strict` either. | WP-04, WP-05 || **Decided** 2026-10-25: as recommended. |
| D-11 | Compile output target | `dist/<bundle-name>-<version>.yaml` in every mode; `--stdout` in human mode only; with `--json`, `result` holds the path and `source_digest`. | WP-05 || **Decided** 2026-10-25: as recommended. |
| D-12 | Exit codes | Map to RFC codes; click usage errors become 3; file errors 4. | WP-05 || **Decided** 2026-10-25: as recommended. |
| D-13 | Author, email, approver | `--approved-by` required in every mode. Machine mode requires `--author` for `new`/`add`. Git identity only as a `suggestion`. | WP-06 || **Decided** 2026-10-25: as recommended. |
| D-33 | Reserved directories and names | Workspace root only; names matched on the bundle id's name part and the file stem; refused at `scs add` and `scs new` (`RESERVED_BUNDLE_NAME`) and by the validator. | WP-03, WP-04, WP-05 || **Decided** 2026-10-25: as recommended. |
| D-37 | `bundle version` and `compile` shell out to the validator | Call it in-process through a structured API. | WP-05 || **Decided** 2026-10-25: as recommended. |
| D-42 | Workspace selection and envelope path base | `--workspace <domain|name>`, else the nearest `.scs/config` above cwd; at repo root without it, `WORKSPACE_REQUIRED`. Paths are POSIX, relative to the repo root. | WP-05 || **Decided** 2026-10-25: as recommended. |
| D-45 | Minimum engine version for skills | `scs --version --json`; each skill's `compatibility` names a minimum `tools_version`, compared per D-56. | WP-05, WP-10 || **Decided** 2026-10-25: as recommended. |
| D-47 | `content_inputs` in manifests; `scs_runtime: "0.7"` | Keep both; §3.5 stability applies to 0.7 artifacts from here on. RFC (Schema Changes). | WP-04, WP-05 || **Decided** 2026-10-25: as recommended. |
| D-49 | How a manifest's format is recognized | By its tag form, not a field value: a manifest whose version has a workspace-qualified tag is a 0.7 manifest and must carry `content_digest` and `tools_version`. Checked by WP-14's check module, since it needs tags; WP-04's schema keeps both fields optional. | WP-14 || **Decided** 2026-10-25: as recommended. |
| D-56 | Version comparison | PEP 440, with a pre-release counted as meeting its base version (`0.7.0rc1` meets a minimum of `0.7.0`). | WP-05, WP-10 || **Decided** 2026-10-25: as recommended. |

## D. Intake and provenance (WP-01a)

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-20 | Unresolved `derived_from` under strict | Warning; exit 2 under `--strict`. RFC (wording). | WP-07 || **Decided** 2026-10-25: as recommended. |
| D-28 | UQ4: personal data; what counts as a person | Role-only attribution allowed in `intake.yaml` only, written `role:<name>`. A person identifier is `Name <email>`. The manifest's `approval.approved_by` must be a person identifier; the schema rejects `role:` and empty values. | WP-07, WP-04 || **Decided** 2026-10-25: as recommended. |
| D-29 | UQ6: provenance granularity | Item-level `derived_from` only. | WP-07 || **Decided** 2026-10-25: as recommended. |
| D-30 | UQ7: intake for pre-0.7 workspaces | Optional; the intake skill offers to reconstruct one. | WP-07, WP-10 || **Decided** 2026-10-25: as recommended. |
| D-32 | Link from a version to the review record | `intake.yaml` is in the version commit (D-40), so the tag already holds the record in force at approval. No separate `intake_digest`. | none || **Decided** 2026-10-25: as recommended. |
| D-34 | Intake schema shapes | Designed in WP-07; approval is milestone M-07. | WP-07 || **Decided** 2026-10-25: as recommended. |
| D-35 | Intake schema location | `schema/intake/intake-schema.json`. RFC. | WP-07 || **Decided** 2026-10-25: as recommended. |
| D-36 | Manifest schema; `approved_by` path | `schema/manifest/version-manifest-schema.json`; RFC means `approval.approved_by`. RFC (wording). | WP-04 || **Decided** 2026-10-25: as recommended. |

## E. Skills, spec, docs (WP-01b)

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-21 | Meta bundle version for 0.7 | Keep `bundle:meta:0.6.0` unless meta content changes. | WP-03 || **Decided** 2026-10-25: as recommended. |
| D-22 | Spec home for agent-interface rules | New `spec/0.7/agent-interface.md`; layout in `bundle-format.md`. | WP-02a || **Decided** 2026-10-25: as recommended. |
| D-23 | Personal profile and ontologies | Personal ignores ontology unless one is given; `ontology: none` supported. | WP-03 || **Decided** 2026-10-25: as recommended. **Superseded** 2026-10-26 by D-61 and D-62: Personal is an ontology; no `--profile personal`, no `ontology: none`. |
| D-24 | Placement guide | `docs/placement/<service>.md` with `checked:` dates and sources, for Claude Enterprise, Claude Code, Cursor, GitHub Copilot, ChatGPT Enterprise. Skills ship a copy and state its `checked:` date when advising. | WP-09 || **Decided** 2026-10-25: as recommended. |
| D-25 | UQ1: where skills live | `skills/` in this repo, versioned with the spec. | WP-10 || **Decided** 2026-10-25: as recommended. |
| D-26 | UQ2: legacy plugins | Deprecated in 0.7, removed in 0.8. | WP-10 || **Decided** 2026-10-25: as recommended. |
| D-27 | UQ3: installing in chat sandboxes | Fallback order recorded now: PyPI; GitHub tag; a wheel bundled with the skill. The choice per client is an output of WP-11a, not part of WP-01b. | WP-10 (via WP-11a) | |
| D-31 | UQ8: agent instructions file | `AGENTS.md` plus a `CLAUDE.md` pointer. | WP-03 || **Decided** 2026-10-25: as recommended. |
| D-50 | Target chat clients | WP-11a: Claude.ai, Claude Code, Cursor, Codex, GitHub Copilot. WP-13 runs in Claude.ai. | WP-11a, WP-13 || **Decided** 2026-10-25: as recommended. |
| D-51 | Skill behavior test harness | Claude Agent SDK with the skills loaded from `skills/`, model pinned in the harness config (`claude-sonnet-5-5` at the start; changes recorded). Each scripted conversation runs 5 times with a filesystem snapshot per turn. MUST assertions pass in 5 of 5 runs, SHOULD assertions in 4 of 5. | WP-10 || **Decided** 2026-10-25: as recommended. |

## F. Housekeeping (no decision needed; fold into the named WP)

- Validator `__version__` hardcoded to 0.6.0 (WP-00).
- ISS-048 text and ROADMAP WS2 do not mention the reserved names (WP-01a).
- Rules added under `rules/v0.6.0/`; no 0.7 rule set (WP-04).
- Rule YAML declares severities and modes no code reads (WP-04).
- mypy not run on scs-tools (WP-05).
- `spec/`, `docs/`, `rfcs/` changes trigger no CI (WP-11rc).
- CONTRIBUTING.md describes feature branches; practice is `0.x-dev` (WP-15).
- RFC links point at `spec/0.6/` (WP-02a).
- `scs-validator` URL in its pyproject differs from the repo (WP-11rc).

## G. Ontologies, templates, and provenance (2026-10-26)

Decided by the maintainer in a design conversation on 2026-10-26, while WP-03 was being built.
The goal is to simplify: fewer scaffold modes and flags, with the agent and the user deciding
what a workspace needs instead of the scaffold guessing. D-68 to D-73 are the open items those
decisions depend on.

| ID | Question | Rec. | Blocks | Decision |
|---|---|---|---|---|
| D-60 | What does "Domain" name? | The global tier only: the Domain workspace, bundle, and repository. `sdlc`, `cdmo`, `mca`, and `personal` are ontologies. | none | **Decided** 2026-10-26: as recommended. The ontology manifest keeps its 0.6 naming in 0.7 (D-73). |
| D-61 | Is "personal" a profile or an ontology? | An ontology, alongside `sdlc`, `cdmo`, and `mca`, with more added as needed. `--profile personal` and `ontology: none` are removed. Supersedes D-23. RFC (§4, §9, Implementation Notes, Migration Guide). | WP-03, WP-07 | **Decided** 2026-10-26: as recommended. |
| D-62 | What does the personal ontology contain? | One fixed concept, boundaries (the `prohibited` concept bundle). Every other concept is personal, so it is defined with the user in conversation, not shipped. Personal means one person. RFC (§4, §9). | WP-03, WP-07, WP-10 | **Decided** 2026-10-26: as recommended. |
| D-63 | What is identity? | Provenance only: a person identifier, `Name <email>`, used in provenance fields. Not a concept, not an SCD, not compiled. The same in all of a person's Domains. The intake `owner` field narrows to this. RFC (§4, §5). | WP-03, WP-07 | **Decided** 2026-10-26: as recommended. |
| D-64 | What selects the scaffold's templates? | The ontology and the workspace kind (Domain or Project), nothing else. The `--type` variants (`healthcare`, `fintech`, `saas`, `government`, `minimal`, `standard`) are removed. Each ontology ships one Domain set and one Project set; the agent and the user remove what does not apply, through engine commands. The Domain/Project split stays. RFC (§9, Implementation Notes). | WP-03, WP-06, WP-10 | **Decided** 2026-10-26: as recommended. |
| D-65 | A person's Domains share nothing; is duplication between them a problem? | No. Each Domain stays self-contained and rebuildable from its own tags. A hierarchy across Domains comes from where the user places the artifacts (the client loads them in layers), and `scs stack` checks such a stack (D-67). | none | **Decided** 2026-10-26: as recommended. |
| D-66 | When does provenance have to be right? | At validation and versioning, which are the only times it is read. The scaffold need not be final; inconsistencies are corrected then, by the tool with the user. A value that was never true (a placeholder) is corrected; a true value is never overwritten (`created_by` is not the approver). RFC (§5). | WP-06, WP-14 | **Decided** 2026-10-26: as recommended. |
| D-67 | How does a user test layered context? | `scs stack ARTIFACT...`: a read-only preview of an ordered stack of compiled artifacts, with exact checks in the engine and a `layer-conflict` kind in the advisory review. Whether a client loads the layers is the client's behaviour, described in the placement guide. RFC (§1, §12, §13). | new WP (none assigned) | **Decided** 2026-10-26: RFC 0002 §13. |
| D-68 | How is a concept with no shipped template created? | Needed for D-62. An engine command that creates a concept bundle, its first SCD, and the ontology manifest entry, with `--dry-run`, for example `scs add bundle NAME --new`. | WP-06, WP-10 | |
| D-69 | What does removing an SCD clean up? | Needed for D-64. When `scs bundle remove-scd` leaves a concept bundle with no SCDs, the same run removes the concept bundle, the root bundle's import of it, and its ontology manifest entry, all listed in `changes`. | WP-06 | |
| D-70 | How are unused (empty) SCDs made visible? | Needed for D-64. Today `scs-validate --strict` passes a scaffold of empty SCDs, and only `scs compile` warns. A warning would make every fresh scaffold fail `--strict`, which WP-03's acceptance requires to pass. Rec.: an `info` diagnostic in validation (`SCD_EMPTY`: an SCD with no prohibitions, directives, or facts, the compiler's test), and `bundle version` lists empty SCDs in its dry run so they are removed or kept knowingly. `info` is enough because the agent reads every diagnostic in the envelope. The validator check is a check module (WP-04's registry). The 0.6 stub detection is retired: it is opt-in, skips DRAFT SCDs, has no tests, and guesses from heuristics; its rule blocks (`scd-rules.yaml`, `completeness-rules.yaml`), `_detect_stubs`, and `COMPLETENESS_STUB_SCD` are removed, with a migration note. | WP-14 | **Decided** 2026-10-26: as recommended, including retiring stub detection. |
| D-71 | What flags provenance to correct (D-66)? | The validator warns on a `created_by` that is not a person identifier (`Name <email>`); the scaffold stops writing placeholders (`$USER@example.com`) in every mode (D-13 already forbids inference in machine mode). | WP-03, WP-06, WP-14 | |
| D-72 | What does a Project under the personal ontology get? | The same fixed concept as a personal Domain, boundaries (Project-specific prohibitions), and nothing else; other concepts are defined with the user. | WP-03 | |
| D-73 | The ontology manifest still says "domain" (`domain-manifest.yaml`, the `domain:` key, `scs validate --domain`, RFC 0001's "Domain Ontology"). | Keep for 0.7; a rename is a schema change for a later RFC. | none | |

## RFC amendments implied

Applied to RFC 0002 on 2026-10-25 as one amendment covering WP-01a and WP-01b: §1 (D-08), §3
(D-09, D-12, D-42), §4 (D-07, D-28, D-35), §6 (D-44), §7 (D-08, D-41), §9 (D-01, D-02, D-03,
D-04, D-05, D-15, D-38, D-40, D-52, D-55, D-57, D-58, D-59), §11 (D-16, D-39, D-53, D-57),
Schema Changes (D-28, D-36, D-47, D-49), Validation Rules (D-03, D-20, D-36, D-39, D-54),
Unresolved Questions (D-01, D-25, D-26, D-27, D-28, D-29, D-30, D-31), Implementation Notes,
and Migration Guide (D-04, D-54). §2 is unchanged (D-08 option 2 was not chosen).

Applied to RFC 0002 on 2026-10-26: §1, §12, §13, Validation Rules, Implementation Notes (D-67);
Motivation, Guide-level Explanation, §4, §5, §9, Implementation Notes, Migration Guide, and
Unresolved Questions (D-61 to D-64, D-66, D-68 to D-73).
