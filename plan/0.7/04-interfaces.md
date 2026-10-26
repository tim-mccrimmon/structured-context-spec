# 4. Interfaces

## Machine mode (RFC §3)

Every command a skill uses accepts `--json`. In machine mode:

- stdout carries exactly one JSON object, the envelope; human text goes to stderr or nowhere.
- No prompts. A missing required value fails with a diagnostic and, where one exists, a
  `suggestion` (for example the git email for the approver).
- No human value is inferred from the environment (approver, author, email) (D-13).

### Envelope

Schema: `schema/cli/envelope-schema.json` (WP-05). A successful run:

```json
{
  "scs_version": "0.7.0",
  "tools_version": "0.7.0",
  "command": "bundle version",
  "ok": true,
  "exit_code": 0,
  "changes": [
    {"action": "create", "path": "domain/bundles/concepts/company-v1.0.0.yaml"},
    {"action": "create", "path": "domain/bundles/concepts/company-v1.0.0-MANIFEST.yaml"},
    {"action": "git-commit", "ref": "HEAD", "paths": [
      {"path": "domain/bundles/concepts/company-v1.0.0.yaml", "status": "A"},
      {"path": "domain/bundles/concepts/company-v1.0.0-MANIFEST.yaml", "status": "A"},
      {"path": "domain/context/project/company-profile.yaml", "status": "M"}]},
    {"action": "git-tag", "ref": "domain/company-v1.0.0"}
  ],
  "diagnostics": [],
  "result": {"tag": "domain/company-v1.0.0", "content_digest": "sha256:..."}
}
```

A failed run, rolled back:

```json
{
  "scs_version": "0.7.0", "tools_version": "0.7.0", "command": "bundle version",
  "ok": false, "exit_code": 1, "changes": [],
  "diagnostics": [
    {"severity": "error", "code": "VERSION_APPROVER_REQUIRED",
     "message": "An approver is required.", "path": null,
     "suggestion": {"approved_by": "Jane Doe <jane@example.com>"}}
  ],
  "result": {}
}
```

- `scs_version` is the spec version; `tools_version` the package version (D-06).
- `changes[].action`: `create`, `modify`, `delete` (with `path`); `git-init`, `git-commit`,
  `git-tag` (with `ref`) (D-09). `create`/`modify`/`delete` list only files the run itself wrote;
  a `git-commit` entry lists every path it commits, including edits made earlier and swept in by
  the whole-workspace commit (D-40). On `ok: true` it lists every effect of the run; on `ok: false`,
  what remains after rollback (normally nothing). A `--dry-run` lists what the real run would do
  and changes nothing.
- `diagnostics[].severity`: `error`, `warning`, `info` (D-10).
- `suggestion` is an object keyed by the field it would fill (RFC §3 form).
- All paths are POSIX, relative to the Domain repository root (D-42).

### Machine-mode conformance

Required of every command in the table below:

1. stdout parses as exactly one envelope that validates against the envelope schema;
2. with stdin closed (apart from documented stdin input), it never blocks on a prompt;
3. for commands that take `--dry-run`: its `changes` equals the effects of the real run (files and
   git), and the dry run changes nothing;
4. the exit code matches the table below and the envelope's `exit_code`;
5. every diagnostic `code` is registered.

## Workspace selection

Workspace-scoped commands take `--workspace <domain|name>`. Without it, the workspace is the
nearest `.scs/config` above the current directory. At the repository root without
`--workspace`, they fail with `WORKSPACE_REQUIRED` (D-42).

## Commands

| Command | `--dry-run` | Notes |
|---|---|---|
| `scs --version` | n/a | `--json` returns `scs_version`, `tools_version` (D-45) |
| `scs new domain NAME [--ontology sdlc\|cdmo\|mca\|personal]` | yes | Creates `NAME-context/`; machine mode requires `--author` (D-13) |
| `scs new project NAME` | yes | Inside a Domain repo only (`DOMAIN_WORKSPACE_MISSING`) |
| `scs add scd\|bundle` | yes | Overwrite requires `--force`; no prompt; reserved bundle names refused (D-33) |
| `scs scd write PATH --from-file -` | yes | D-08 option 1: SCD content from stdin; validated before writing |
| `scs bundle add-scd` / `remove-scd` / `add-import` / `pin` | yes | D-08 option 1 (`pin` in either option) |
| `scs bundle version BUNDLE --version V --approved-by P` | yes | `--approved-by` required in every mode; no `--force`, no `--no-git`; refuses unpinned or DRAFT imports (D-14); commits the workspace (D-40) with the D-55 identity |
| `scs bundle diff BUNDLE [--from V] [--to V\|working]` | n/a | Default `--from` = latest version (D-41 for none or legacy), `--to` = `working`; old content from the tag |
| `scs intake set` / `scs intake record-finding` | yes | The only writers of `intake.yaml` (D-07) |
| `scs compile BUNDLE [--version V \| --allow-draft]` | yes | `--version V` compiles the released snapshot with `source_digest` (D-57); without it, the working DRAFT needs `--allow-draft`. Writes `dist/<bundle-name>-<version>.yaml`; `--stdout` in human mode only (D-11); no flag bypasses a failed D-39 check |
| `scs validate` / `scs-validate` | n/a | See below |

All rows take `--json` and must meet machine-mode conformance. Rows marked D-08 option 1 drop out
if option 2 is chosen.

## Validator output

- `scs-validate --output json` keeps the report format, now with `code` and `severity` per
  finding. Schema: `schema/validator/report-schema.json` (WP-04).
- `scs validate --json` and `scs-validate --json` emit the envelope with that report unchanged in
  `result` and its findings mapped to `diagnostics`.
- Repository mode: at a Domain repository root, validates every workspace and runs the D-39 checks
  over every version tag; reports per workspace; returns the worst exit code. Zero, or more than
  one, workspace whose `.scs/config bundle_type` is `domain` is an error.
- `--verify-version <tag>` verifies one version against its tagged content.
- Under `--strict`, warnings exit 2; `info` never changes the exit code.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Errors |
| 2 | Warnings under `--strict` |
| 3 | Bad arguments or no input (click usage errors remapped from 2, D-12) |
| 4 | File error: missing, unreadable, or unwritable file, including the schema directory |
| 5 | Internal error |

## Diagnostic codes

Registry: `schema/diagnostics/codes.yaml`, merged from per-WP fragments in
`schema/diagnostics/codes.d/` (D-10). Seed list from this plan:

| Code | Severity | Raised by |
|---|---|---|
| `VERSION_APPROVER_REQUIRED` | error | `bundle version` without `--approved-by` |
| `VERSION_IMPORT_NOT_PINNED` | error | D-14 |
| `VERSION_EXISTS` | error | D-15 |
| `VERSION_MANIFEST_MISSING` | error | A workspace-qualified tag with no manifest at the tag (D-39) |
| `CONTENT_DIGEST_MISMATCH` | error | Tagged content or drift (D-39); names changed files and bundles to version again |
| `MANIFEST_ALTERED` | error | Working manifest or snapshot of a version in use differs from its tagged copy (D-39) |
| `VERSION_TAG_MISSING` | error | A manifest with `content_digest` has no qualified tag (D-39) |
| `GIT_HISTORY_INCOMPLETE` | error | Repository mode on a shallow clone (D-39) |
| `VERSION_INPUT_UNTRACKED` | error | A digest or compiler input is ignored or untracked at versioning (D-40) |
| `GIT_REQUIRED` | error | D-38; also `new domain` without git (WP-03) |
| `GIT_COMMAND_FAILED` | error | A git command the engine ran failed; the run's writes are removed (WP-03) |
| `WORKSPACE_REQUIRED` | error | D-42 |
| `DOMAIN_WORKSPACE_MISSING` | error | `new project` outside a Domain repo |
| `WORKSPACE_EXISTS` | error | `new domain` or `new project` target exists (WP-03) |
| `WORKSPACE_NAME_INVALID` | error | A name that cannot be a directory, bundle id, and tag prefix; a concept bundle's name; a Project named `domain` (WP-03) |
| `CONFIG_NAME_MISMATCH` | error | D-03 |
| `DUPLICATE_ID` | error | Two documents with one id in a workspace |
| `RESERVED_BUNDLE_NAME` | error | D-33 |
| `OUTPUT_OUTSIDE_REPO` | error | Any output path outside the repository root |
| `DIFF_VERSION_NOT_FOUND` | error | D-41 |
| `DERIVED_FROM_UNRESOLVED` | warning | D-20 |
| `ONTOLOGY_LEGACY_LOCATION` | info | D-04 |
| `PROVENANCE_PLACEHOLDER` | warning | D-71: a placeholder `created_by` |
| `VERSION_PROVENANCE_PLACEHOLDER` | error | D-71: `bundle version` over a placeholder `created_by` |
| `SCD_EMPTY` | info | D-70; replaces `COMPLETENESS_STUB_SCD`, which is removed |
| `DIFF_LEGACY_BASELINE` | info | D-41 |

## Skill-to-engine contract

- Skills call the engine only through machine mode and check `ok` before reporting success.
- Every write goes through a `--dry-run`, then confirmation, then the real run (RFC §6.1). A
  versioning cascade uses the D-44 plan.
- Before the first engine call, a skill checks `scs --version --json` against its
  `compatibility` minimum (D-45, D-56).
- No engine command writes outside the repository root or opens a network connection.
