# Survey: CLI engine

Surveyed 2026-10-25 on worktree `structured-context-spec-0.7`, branch `0.7-dev`, HEAD `f1c9d11`.
Paths are relative to the repo root; CLI paths to `tools/cli/` unless they start with `tools/`.

**Uncommitted state (marked `[U]` below).** The hardening batch commit `43bc0dd` covers ISS-042,
043, 044, 047. ISS-045 (content digest, truthful `validation_passed`, `source_digest`) is
**uncommitted**: diffs in `scs_tools/commands/bundle.py`, `scs_tools/compiler.py`,
`tests/test_compile.py`, plus untracked `tools/scd-validator/src/scs_validator/digest.py` and its
test. `ISSUES.md` marks ISS-045 done only in the working tree. The RFC's reserved-names amendment
(section 9, Validation Rules, Implementation step 2) is also uncommitted.

## Scope read (dirs/files you read)

- `rfcs/RFC-0002-agent-mediated-scs.md` (full), `ROADMAP.md`, `ISSUES.md` 845-985
- `tools/cli/pyproject.toml`; `scs_tools/__init__.py`, `cli.py`, `compiler.py`
- `scs_tools/commands/{bundle,compile,new,init,add,validate}.py`
- `scs_tools/utils/files.py`; `utils/project_types.py` (grep only)
- `scs_tools/templates/bundles/{domain,project}-bundle.yaml`, `templates/project.gitignore`, template dir listing
- `tests/test_scs_tools.py`, `tests/test_compile.py` (test inventory, versioning helpers)
- Validator touch points (read only where the CLI depends on them): `tools/scd-validator/src/scs_validator/commands/validate.py`, `resolver.py` 23-24, 71-161, `digest.py` 130-218 `[U]`
- `git diff` of CLI files; `git show --stat 43bc0dd`
- Probes run in a scratchpad copy of the worktree (not in the repo): test suite, `scs new domain`, `scs bundle version`, `scs compile`, exit codes

## Components

| Component | Responsibility | Key files | Key functions |
|---|---|---|---|
| Entry point | Click group, `--version`, registers 6 commands | `scs_tools/cli.py:16-58`; `__init__.py:8-12` | `cli()`; `__version__` from package metadata (ISS-042) |
| `scs new` | Scaffold a Domain or Project **workspace** (not a repo) | `commands/new.py:64-364` | `domain` 118-149, `project` 152-189, `_scaffold` 192-364, `_create_bundles` 392-415, `_create_scds` 418-460, `_create_domain_manifest` 367-389, `_create_supporting_files` 638-680 |
| Profile selection | Which concepts/SCDs a Domain vs Project gets, per ontology | `new.py:35-46` (`DOMAIN_COMMON_CONCEPTS` company/prohibited), `new.py:290-306`, `new.py:584-609` (sdlc Global profile); `utils/project_types.py:475-505` (`ONTOLOGY_MODELS`, cdmo `domain_scds`) | `_sdlc_domain_scd_mapping`, `get_concepts_for_project_type` |
| `scs init` | Add SCS dirs + `.scs/config` to cwd | `commands/init.py:45-126` | `init` |
| `scs add` | Add one SCD or concept bundle from templates | `commands/add.py:31-236` | `scd` 43-121, `bundle` 136-236, `_read_ontology_model` 268-280 |
| `scs bundle` | list / info / validate / version | `commands/bundle.py:19-785` | `_root_bundle` 34-46, `list` 56-121, `info` 126-220, `validate` 224-241, `version` 283-458 |
| Versioning internals | Snapshot, checksum, digest `[U]`, manifest, git commit+tag | `bundle.py:461-785` | `_validate_bundle` 461-492, `_bundle_name` 495-500, `_git_tag_exists` 503-509, `_create_versioned_bundle` 537-584, `_create_version_manifest` 600-703, `_create_git_version` 706-785 |
| `scs compile` | Optional validator pre-check, compile, write artifact | `commands/compile.py:13-104` | `compile` |
| Compiler | Resolved tree -> deterministic runtime artifact; digest verification `[U]` | `compiler.py:49-228` | `compile_tree` 49-185, `render` 205-215, `compile_bundle` 218-228 |
| `scs validate` | Re-export of the validator's click command (no CLI-side logic) | `commands/validate.py:13-30` | imports `scs_validator.commands.validate.validate` |
| File utils | dir layout, Jinja rendering, writes | `utils/files.py:26-68` | `create_directory_structure` 26-38, `copy_template` 55-63, `write_file` 48-52 |

## Data structures

**Workspace layout (as scaffolded, `files.py:28-34`, `new.py:309-356`; confirmed by probe):**
```
<cwd>/<name>/
  .scs/config  .gitignore  README.md  VERSION ("1.0.0", new.py:661)
  bundles/{domain|project}-bundle.yaml  bundles/concepts/<concept>.yaml
  context/project/<scd>.yaml          # all SCDs, Domain workspaces included
  domain/domain-manifest.yaml         # Domain Ontology manifest (RFC 0001)
  docs/GETTING_STARTED.md  docs/<concept>/...   (sdlc only)
```
No `intake.yaml`, `sources/`, `dist/`, `AGENTS.md`, CI workflow, or git init.

**`.scs/config`** (line-oriented YAML-ish, written by f-string, read by prefix match `add.py:255-280`):
- `new` (`new.py:673-679`): `bundle_type`, `project_name`, `project_type`, `ontology_model`, `scs_version` (= scs-tools package version, e.g. `0.6.0`, not spec version).
- `init` (`init.py:97-103`): `project_name`, `project_type`, `scs_version`, `author`, `email`; no `bundle_type`/`ontology_model`.

**Root bundle templates** (`templates/bundles/domain-bundle.yaml:1-19`, `project-bundle.yaml:1-19`): `id: bundle:<name>`, `version: "DRAFT"`, unpinned `imports` (`bundle:<concept>`; Domain also `bundle:meta:0.6.0`, `new.py:30`), `scds: []`, `provenance.created_by` = `--email` or `$USER@example.com`.

**Versioning outputs** (`bundle version`, all in the bundle's own directory):

| Output | Name | Source |
|---|---|---|
| Snapshot | `<file-stem>-v<ver>.yaml` (e.g. `domain-bundle-v1.0.0.yaml`) | `bundle.py:566-569` (uses file stem, not bundle name) |
| Manifest | `<bundle-name>-v<ver>-MANIFEST.yaml` | `bundle.py:697`; name from id via `_bundle_name` 495-500 |
| Git tag | `<bundle-name>-v<ver>` (annotated) | `bundle.py:338`, 777-780 |
| Snapshot provenance | `version_approved_by/_at`, `approval_status` (`validated`/`approved`) `[U]`, `validation_passed` `[U]`, `validation_date` (only if validated) `[U]`, `version_notes` | `bundle.py:553-563` |
| Manifest fields | `version, release_date, status [U], project, bundle{id,type,file,sha256,size_bytes}, content_digest [U], content_inputs [U], validation{...} (only if validated), components, approval{approved_by,approved_at,approval_notes}, phases, release_notes, distribution{repository?,branch?,tag?,immutable,authoritative}` | `bundle.py:634-694` |

- `content_inputs` `[U]` maps `bundle:<id>:<ver>` and SCD ids to per-file digests (probe: imported unpinned concepts recorded as `bundle:<c>:DRAFT`).
- `components.total_scds` / `validation.scd_count` count `context/project/*.yaml` on disk, not the bundle's SCDs (`bundle.py:624-627`; ISS-027).
- Validator finds manifests by `version_manifest_names` (`tools/scd-validator/.../digest.py:139-142` `[U]`): `<name>-v<ver>-MANIFEST.yaml`, then legacy `VERSION-<ver>-MANIFEST.yaml`, next to the bundle. CLI and validator name derivation differ slightly (`_bundle_name` takes `split(":")[1]`; validator takes everything after the first colon).

**Compiled artifact** (`compiler.py:174-184`): `scs_runtime: "0.7"` `[U]` (was 0.6), `id`, `type`, `version` (`DRAFT+<8hex>` for drafts, 157-164), `source_digest` `[U]` (versioned only), `title`, `sources`, `rules` (identity rule first, ids `<bundle>/<scd>/<item>`, 117), optional `facts`. Output path: stdout by default, or `-o` (`compile.py:98-104`). No `dist/` default, no naming convention.

**Resolution scope** (validator, used by compile/version): workspace root = bundle dir walked up past `bundles|domains|concepts` (`resolver.py:23,79-83`); index scans the whole workspace recursively, skipping `.git, .venv, venv, node_modules, __pycache__, build, dist` (`resolver.py:24,86-92`). `plan/`, `test-plan/`, `qa/` are not skipped.

## Interfaces

None of the `scs-tools` commands has `--json` or `--dry-run`. Only `scs validate` (the validator's command) has machine output (`--output json`).

| Command | Flags relevant to RFC 0002 | Current behavior | Machine-readable? | Prompts / env inference |
|---|---|---|---|---|
| `scs --version` | | package metadata version (`__init__.py:9-12`) | text | - |
| `scs new domain\|project [NAME]` | `--type`, `--ontology {sdlc,mca,cdmo}`, `--dir`, `--author`, `--email`, `-i`, `--no-interactive` (`new.py:83-115`) | creates `<dir or cwd>/<NAME>/` workspace; refuses if dir exists (280-282) | prose to stdout | **interactive by default** (199): name, project type, author, email, directory confirm (202-258). Non-interactive: author defaults to `$USER`, email to `<author>@example.com` (268-271) and are written into provenance. No `--profile`. |
| `scs init` | `--type`, `--author`, `--email`, `--force` | adds dirs/config to cwd | prose | none; author/email from `$USER` (84-85) |
| `scs add scd NAME` / `add bundle NAME` | `--author`, `--email` | copies template into `context/project/` or `bundles/concepts/` | prose | `click.confirm` on overwrite (`add.py:78`, 200); author/email from `$USER` (84-85, 206-207) |
| `scs bundle list [-a]` | | lists root + concept bundles in cwd | prose | - |
| `scs bundle info NAME` | | workspace bundle or template fallback | prose | - |
| `scs bundle validate` | none (no `--strict`, `--output`) | invokes validator on root bundle (`bundle.py:235-241`) | text only | - |
| `scs bundle version` | `-b/--bundle`, `-v/--version` (required), `--approved-by`, `--notes`, `--no-git`, `--no-validate`, `-f/--force` (`bundle.py:245-282`) | validate (subprocess, text parsed by regex 479-483) -> snapshot -> checksum + digest `[U]` -> manifest -> git add/commit/tag | prose to stdout, errors to stderr | **prompts** for approver if `--approved-by` omitted (329; never git config, ISS-047) and for notes if `--notes` omitted (354-359, default text). Commit/tag use git's own identity. |
| `scs compile BUNDLE` | `-o`, `--format {yaml,json}`, `--allow-draft`, `--no-cites`, `--no-validate` (`compile.py:14-35`) | validator subprocess unless `--no-validate` (accepts rc 0 or 2, 74); compile; write | artifact to stdout when no `-o` (summary to stderr); with `-o`, summary line to stdout | - |
| `scs validate` | validator's full option set incl. `--output json`, `--strict` | validator | JSON report with `--output json` | - |
| `scs bundle diff` | - | **does not exist** | - | - |

**Exit codes as built (probed):** validator uses 0/1/2(strict warnings)/3(no input)/4(schema dir)/5(internal) (`tools/scd-validator/.../commands/validate.py:142,186,198,202,209,438-447`). `scs-tools` commands exit **1** on every handled failure (`click.Abort`, `ClickException`), including bad semver and missing name; click usage errors (e.g. missing `--version`) exit **2**, which collides with RFC "2 = warnings in strict mode"; nothing emits 3 or 4.

## State and lifecycle

States are implicit in file content; there is no state field or state machine in the CLI.

| State | How represented | Entered by | Guards |
|---|---|---|---|
| draft | `version: "DRAFT"` in bundle file | `scs new` / `scs add` templates | none |
| validated | not persisted for drafts; recorded only inside a version's snapshot/manifest | `scs bundle validate` / `scs validate` (no record) | - |
| versioned | snapshot `<stem>-v<ver>.yaml` (version set, approval provenance) + manifest + optional git tag | `scs bundle version` | semver x.y.z (316-324); non-empty approver (328-333); tag must not exist unless `--no-git` (339-341); validator rc must be 0 unless `--no-validate` (364-374); snapshot must not exist unless `--force` (572-578); digest must compute (`DigestError` deletes snapshot, 394-399) `[U]` |
| compiled | artifact file or stdout | `scs compile` | type domain/project (`compiler.py:54-58`); no unresolved imports/SCDs/cycles (60-65); no DRAFT in tree unless `--allow-draft` (67-71); digest verification of every versioned bundle with a manifest, no override (75-96) `[U]`; no TODO text, no duplicate ids, non-empty (106-150); validator pass unless `--no-validate` |

Observed (probe, scratchpad copy):
- A freshly scaffolded Domain skeleton versions successfully (`scs bundle version --no-git ...` exit 0) while its imports are unpinned DRAFT concept bundles; `content_inputs` records them as `:DRAFT`. Nothing requires imports to be pinned or versioned before the root is versioned. Compiling that version then fails on the DRAFT imports.
- After a concept bundle is versioned in place, an **unpinned** import `bundle:company` resolves to the snapshot `company-v1.0.0.yaml`, not the working `company.yaml` (`resolver.py:127-136` returns `candidates[0]`; paths sort `-` before `.`). Inference: "working tree" vs "version" is not cleanly separable by the resolver once snapshots sit beside sources.
- `--force` with `--no-git` rewrites an existing snapshot and manifest at the same version, with a fresh digest (`bundle.py:572-584`, 697-701). The migration guide line "an existing version is not rewritten" is not enforced by the tool.
- Compile skips digest verification for the whole tree when any bundle is DRAFT (`compiler.py:78`, `if not drafts`), so `--allow-draft` on a draft root importing versioned concepts does not verify those concepts (inference from code; the validator pre-check may still catch it via `bundle_validator.py:233-247`).
- Versioning is not transactional: snapshot (384), manifest (409), commit/tag (426) are written in sequence; a git failure leaves both files on disk (782-785).

## RFC 0002 vs as-built

| RFC requirement | Status | Evidence |
|---|---|---|
| §1 Engine limited to create/maintain/validate/version/compile; no placement | done (no placement code) | no deliver/placement command in `cli.py:53-58` |
| §2 Layer 1 = `scs-tools` + `scs-validator`, single source of behavior | partial | compile and version shell out to `python -m scs_validator` and parse text (`bundle.py:472-483`, `compile.py:61-78`); digest/resolver imported in-process `[U]` (`bundle.py:344-351`, `compiler.py:79`) |
| §3 `--json` on every agent-used command | not started | no `--json` in `scs_tools/` (grep); only validator `--output json` |
| §3 No prompts in machine mode | not started | prompts at `new.py:202-258`, `add.py:78,200`, `bundle.py:329,355` |
| §3 No inferred human values | partial | approver: done (`bundle.py:326-333`, ISS-047). author/email still from `$USER` (`new.py:229,269-271`; `init.py:84-85`; `add.py:84-85,206-207`) |
| §3 git email offered as `suggestion` | not started | ISS-047 defers to ISS-049 (`ISSUES.md:936-937`) |
| §3 Single JSON object on stdout | not started | prose on stdout throughout; compile mixes artifact/summary across streams (`compile.py:98-104`) |
| §3 Keep exit codes 0/1/2/3/4/5 | conflicts | scs-tools uses 1 for all failures, click usage errors give 2 (probe) |
| §3 `--dry-run` returns same `changes` without writing | not started | no change list; writes interleaved with computation (`bundle.py:384-428`, `new.py:309-356`) |
| §3 validator report in `result`, findings in `diagnostics` | not started | `_validate_bundle` keeps only rc + regex counts (`bundle.py:479-488`) |
| §6.2 approver from user, never from env | done (interactive) | `bundle.py:261,326-333`; test `test_scs_tools.py:340` |
| §6.3 `--force`, `--no-validate`, `--allow-draft` exist as explicit flags | done | `bundle.py:272-282`, `compile.py:29-35` |
| §7 `scs bundle diff [--from] [--to version\|working]`, `--json` | not started | no `diff` command in `bundle.py` |
| §9 `scs new domain` creates a git repo with `domain/`, `projects/` | not started | `_scaffold` creates a single workspace at `<cwd>/<name>` (`new.py:274-282`); no `git init` |
| §9 `scs new project` adds `projects/<name>/` in an existing Domain repo | not started | `new project` is independent of any Domain (`new.py:152-189`) |
| §9 Workspace layout (`context/`, `intake.yaml`, `sources/`, `dist/`) | partial / conflicts | SCDs in `context/project/` (`files.py:31`); `domain/` subdir already used for the ontology manifest (`files.py:30`, `new.py:387`) |
| §9 `.scs/config` fields `bundle_type, name, ontology, scs_version` | partial | field names differ: `project_name`, `ontology_model` (`new.py:673-679`); `scs_version` is the tools version; `init` omits `bundle_type`/`ontology_model` |
| §9 `AGENTS.md` + client pointer file | not started | no template |
| §9 CI workflow `scs-validate --strict` | not started | no template |
| §9 Reserved dirs `plan/ test-plan/ qa/` not created, not read | partial | scaffold does not create them (`files.py:28-34`); resolver indexes them (not in `SKIP_DIRS`, `resolver.py:24`) `[U amendment]` |
| §9 Reserved bundle names `plan`, `test-plan`, `qa` rejected | not started | no check in `new.py`, `add.py`, `bundle.py` |
| §9 Tags `<workspace>/<bundle-name>-v<version>` | partial | name-qualified only: `<bundle-name>-v<ver>` (`bundle.py:338`); workspace qualifier is ISS-048 (`ISSUES.md:876-877`) |
| §9 Manifests named the same way (ISS-043) | partial | `<bundle-name>-v<ver>-MANIFEST.yaml` (`bundle.py:697`); no workspace qualifier |
| §9 Compile to `dist/<bundle-name>-<version>.yaml` | not started | default stdout (`compile.py:19`, 102-104); template `.gitignore` ignores `dist/` (`templates/project.gitignore:23`) |
| §9 / Impl step 2 personal Domain profile (`company` + `prohibited` only), `--profile personal` | not started | no `--profile` option (`new.py:83-115`); company/prohibited are always added to Domains plus ontology concepts (`new.py:299-306`) |
| §11 `content_digest` in manifest | done `[U]` | `bundle.py:392-405,646` |
| §11 compile verifies, refuses on mismatch, no override | done `[U]` (with draft caveat) | `compiler.py:75-96`; skipped when any DRAFT in tree (78) |
| §11 truthful `validation_passed`/`approval_status` | done `[U]` | `bundle.py:558-562,637,675` |
| §11 `source_digest` in artifact, absent for DRAFT | done `[U]` | `compiler.py:96,180-181` |
| Validation rule: manifest has non-empty `approved_by` | done (writer side) | `bundle.py:331-333,667-671` |
| Impl step 1: ISS-042 | done | `__init__.py:8-12`; test `test_scs_tools.py:253` |
| Impl step 1: ISS-043 | done (name-qualified) | `bundle.py:335-341,697`; tests `test_scs_tools.py:272,297` |
| Impl step 1: ISS-044 | done | commit `43bc0dd`; test `test_scs_tools.py:1022` |
| Impl step 1: ISS-047 | done | `bundle.py:259-262,326-333` |
| Impl step 1: ISS-045 | done `[U]` | see §11 rows |
| Impl step 6 `scs bundle diff` | not started | - |

## Gaps and ambiguities in the RFC

- **Tag vs manifest naming.** §9 says manifests "MUST be named the same way" as `<workspace>/<bundle-name>-v<version>`. A `/` in a filename is a directory; the RFC does not say whether that means `<workspace>-<name>-v...-MANIFEST.yaml`, a subdirectory, or that the workspace qualifier is implied by the manifest living in the workspace. The validator's lookup (`digest.py:139-161` `[U]`) must change in step with whatever is chosen.
- **Workspace name for tags.** `<workspace>` is `domain` or "the Project name". Unstated whether that is the directory name under `projects/`, `.scs/config` `project_name`, or the root bundle id; they can differ (bundle id comes from the scaffold name, `templates/bundles/project-bundle.yaml:1`).
- **Unresolved Question 5 (workspace-level versioning)** is explicitly "decide before the engine work" and blocks the shape of ISS-048/049 versioning (one manifest per bundle vs per workspace).
- **`domain/` collision.** Each workspace already has a `domain/` subdir for the Domain Ontology manifest; §9's repo layout uses `domain/` as the Domain workspace, producing `domain/domain/domain-manifest.yaml`. The layout diagram omits `domain-manifest.yaml`, `docs/`, `README.md`, `VERSION` entirely; unclear whether they stay.
- **`context/` vs `context/project/`.** RFC diagram shows `context/`; as-built uses `context/project/` for both Domain and Project SCDs (`files.py:31`). Not stated whether this changes (affects ids `scd:project:*` and the "Project-tier" naming question in ISS-041).
- **`.scs/config` schema.** RFC lists `bundle_type, name, ontology, scs_version`; as-built keys differ and `scs_version` holds the tools version. Not stated whether keys are renamed, which version `scs_version` means, or whether a repo-level marker exists for "this is a Domain repository".
- **`changes` semantics for git.** Envelope `changes` lists files; `bundle version` also creates a commit and tag. Not stated whether tags/commits appear in `changes` or `result`, or how `--dry-run` reports them.
- **`--dry-run` for `new domain` git init** and for repo-external effects: unspecified.
- **Machine-mode exit codes vs click.** RFC requires 3 for bad arguments; click's usage errors exit 2. Not addressed.
- **`--json` + `compile` without `-o`.** Artifact-to-stdout conflicts with "single JSON object on stdout"; RFC does not say whether `--json` implies writing to `dist/` or embedding the artifact in `result`.
- **`scs bundle diff --to working`** after in-place versioning: the resolver resolves unpinned imports to snapshots (see State). RFC does not define "working tree" content for imported bundles, nor how `--from` locates a version (tag, snapshot file, or manifest `content_inputs`; only digests, not content, are in the manifest).
- **Diff of "retired" SCDs.** RFC lists "SCDs ... retired"; no retirement field is referenced in the CLI; source of that state is unspecified here.
- **Personal profile vs ontology.** Step 2 says personal scaffolds "only company and prohibited"; unstated whether `--ontology` is ignored, required, or `none` (§4 intake lists `ontology: none`, which `ONTOLOGY_MODELS` does not support).
- **Author/`created_by` in machine mode.** §3 forbids inferring "author" from env; RFC does not say whether `--author/--email` become required for `new`/`add` or provenance is left blank.
- **Pinned-import requirement before versioning** is not stated in RFC 0002; the tool currently versions roots with DRAFT imports.
- **`--force` vs immutability.** §11 says a changed bundle needs a new version, §6.3 restricts agents passing `--force`, but the RFC does not say whether `--force` re-versioning at an existing version remains legal.
- **Repository-level operations.** Validator gets repo-root validation; the RFC does not say whether `scs compile` / `scs bundle version` gain repo-root modes or remain per-workspace (cwd-based `_root_bundle`, `bundle.py:34-46`).

## Dependencies

**CLI needs from validator (`tools/scd-validator`):**
- `resolver.resolve`, `Index.find_bundle` (tree, import resolution, workspace root heuristic `resolver.py:79-83`).
- `digest.content_digest`, `verify_tree`, `tree_index`, `DigestError` `[U]`; manifest naming (`version_manifest_names`) must match `bundle.py:697`.
- Validator command object for `scs validate` (`commands/validate.py:14`); `python -m scs_validator` subprocess and its text summary format (regex at `bundle.py:480-481` breaks if the text report changes).
- For machine mode: a structured validation API or the `--output json` report to carry in `result` (`reporter.report_json`, validator `reporter.py:111`).
- Repo-level validation, reserved-dir skipping, reserved-name rule: validator side of §9; resolver `SKIP_DIRS` affects what compile/version index.
- Packaged meta bundle (`bundle:meta:0.6.0`, `new.py:30`) resolved via validator's `PACKAGED_META`.

**CLI needs from schemas:** runtime artifact schema (`schema/runtime/runtime-artifact-schema.json` `[U]`, `source_digest`, `scs_runtime 0.7`); bundle schema for snapshot provenance fields; future `intake.schema.json` if `new` scaffolds `intake.yaml`; any schema for the version manifest (none found in this survey; inference: manifests are unschema'd).

**Skills / MCP need from CLI:** the §3 envelope on every command; `--dry-run` change lists; no prompts; `suggestion` for approver; stable diagnostic `code`s (none exist; errors are free text, e.g. `compiler.py:55-150`); `scs bundle diff --json`; `dist/` output paths to drive placement advice; Domain-repo scaffolding (`new domain`/`new project`).

## Risks

- **Machine mode is a cross-cutting rewrite.** Every command prints prose inline with work (`click.echo` throughout), aborts via `click.Abort`, and writes as it goes. `--dry-run` and a `changes` list need the writes separated from planning in `new`, `add`, and `bundle version`.
- **Exit-code mismatch.** Existing scs-tools behavior (1 for everything, click 2 for usage) differs from the RFC table; aligning may change behavior seen by current scripts/tests.
- **Text-parsing coupling.** `bundle version` decides pass/fail from validator rc and counts from regex over text (`bundle.py:472-488`); `compile` accepts rc 2 (`compile.py:74`) though it never passes `--strict`.
- **Resolver ambiguity with in-place snapshots.** Unpinned imports silently resolve to a versioned snapshot after versioning (probe); affects diff semantics, and a Domain repo will hold many snapshots.
- **Draft compile skips verification** of versioned imports (`compiler.py:78`).
- **`--force` can rewrite a released version** with a new digest (`bundle.py:572-584`), undermining §11 if passed.
- **Partial-write states** on git failure (`bundle.py:782-785`) or exceptions between steps; an agent must not report success, and cleanup is manual.
- **Layout migration.** Moving to `domain/` + `projects/<name>/` collides with the existing `domain/` subdir and `context/project/`; the resolver's workspace-root heuristic and `_root_bundle` (cwd-based) assume one workspace per cwd.
- **Version string drift.** `pyproject.toml:7` is still `0.6.0`; `.scs/config scs_version` and `__version__` will report 0.6.0 until bumped; meta ref hardcoded `bundle:meta:0.6.0` (`new.py:30`).
- **`.gitignore` template ignores `dist/`** (`templates/project.gitignore:23`), which decides the RFC's "user's choice" by default.
- **Uncommitted ISS-045 work** spans CLI, validator, spec, schema, examples; the survey treats it as as-built but it has no commit yet.

## Tests

- Files: `tools/cli/tests/test_scs_tools.py` (scaffold, validate shortcut, versioning, add, list/info, mca/cdmo profiles), `tools/cli/tests/test_compile.py` (artifact determinism, schema conformance, rule ids, drafts, digest/verification `[U]` 371-442).
- Run (needs both packages installed): `pip install -e tools/scd-validator -e tools/cli pytest`, then `cd tools/cli && python -m pytest -q`. No env with the packages exists on the host Python; run here from a scratchpad copy of the worktree (including uncommitted changes): **152 passed in 17s**.
- Versioning tests use `--no-git` except `test_concept_bundles_at_the_same_version_get_their_own_tags` (`test_scs_tools.py:297`, real `git init` in tmp).
- Covered RFC-relevant behavior: ISS-042 (`:253`), ISS-043 manifests/tags (`:272`, `:297`), ISS-044 (`:1022`), ISS-047 approver prompt and blank approver (`:340`, `:363`), digest record/verify/format-insensitivity/no-validate/legacy manifest (`test_compile.py:371-442`) `[U]`.
- Obvious holes:
  - No tests of exit codes beyond 0/non-zero; nothing asserts 3/4/5 or the click-usage 2.
  - No tests that `new`/`add` avoid prompts or env-derived author/email.
  - No test that versioning a root with DRAFT/unpinned imports is refused or allowed deliberately.
  - No test for unpinned import resolving to a snapshot; none for `--force` overwriting a released version; none for `--allow-draft` skipping verification of versioned imports.
  - No tests for `--json`, `--dry-run`, `bundle diff`, Domain repository scaffold, `AGENTS.md`/CI generation, personal profile, reserved dirs/names, `dist/` output (all unbuilt).
  - Git commit/tag path is tested only for tag naming, not for failure cleanup.
