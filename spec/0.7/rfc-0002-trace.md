# RFC 0002 Trace

**Version:** 0.7.0 (Draft)
**Last Updated:** 2026-10-28

This file maps every MUST and SHOULD in [RFC 0002](../../rfcs/RFC-0002-agent-mediated-scs.md)
to the section of the 0.7 specification that states it. It is a working record for the 0.7
release, not part of the normative text.

Statements are numbered by RFC section, in the order they appear. Where one sentence holds two
requirements, they are numbered separately (a, b).

Status:

- **Stated**: the spec section states the requirement at the RFC's level.
- **Outside the spec**: the RFC places it outside the spec text.

Sections 1, 4, 9, 10, and 11 were traced in WP-02a; sections 2, 3, 5, 6, 7, 8, 12, Schema
Changes, and Validation Rules in WP-02b, which also wrote `agent-interface.md` (D-22) and, for
section 13, `runtime-artifact.md` §5. The engine command for section 13 is WP-16.

## Section 1. Scope

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 1.1 | The agent interface is limited to the create, maintain, validate, version, and compile operations on a local Domain repository | MUST | `agent-interface.md` §2; `overview.md` §1.1 | Stated |
| 1.2 | An agent interface does not present itself as providing placement, review workflows, registries, or runtime serving | MUST NOT | `agent-interface.md` §2; `overview.md` §1.1; `governance-and-compliance.md` §9 | Stated |

## Section 2. Architecture

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 2.1 | Each layer above the engine goes through the engine; no layer reimplements validation, versioning, or compilation | MUST | `agent-interface.md` §3 | Stated |
| 2.2 | The MCP server runs locally (stdio transport) | MUST | `agent-interface.md` §3 | Stated |

## Section 3. Engine machine mode

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 3.1 | Every `scs` command an agent uses accepts `--json` | MUST | `agent-interface.md` §4 | Stated |
| 3.2 | In machine mode a command does not prompt | MUST NOT | `agent-interface.md` §4 | Stated |
| 3.3 | In machine mode a command does not infer human-attributable values from the environment (it MAY suggest them) | MUST NOT | `agent-interface.md` §4 | Stated |
| 3.4 | In machine mode a command writes a single JSON object to stdout, and nothing else | MUST | `agent-interface.md` §4 | Stated |
| 3.5 | In machine mode a command keeps the exit codes 0-5 | MUST | `agent-interface.md` §4 | Stated |
| 3.6 | A command run with `--dry-run` returns the same `changes` the real run would, and changes nothing | MUST | `agent-interface.md` §4.3 | Stated |
| 3.7 | `scs-validate`'s JSON report is carried in `result` unchanged, with findings mapped into `diagnostics` | SHOULD | `agent-interface.md` §4.2 | Stated |

`agent-interface.md` §4.2 states "every `code` MUST be registered in `codes.yaml`" as a MUST;
the RFC states it as a fact ("Every `code` is registered"). The conftest check that emitted
codes match the registry enforces it.

## Section 4. Intake

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 4.1 | An agent infers what it can and asks the user to confirm, rather than asking each question separately | SHOULD | `agent-interface.md` §5 | Stated |
| 4.2 | The first step of every intake establishes the Domain repository, existing or new | MUST | `agent-interface.md` §5 | Stated |
| 4.3 | A new Domain repository's Domain workspace is built before any Project workspace in it | MUST | `agent-interface.md` §5 | Stated |
| 4.4 | The agent saves the answers to `intake.yaml` at the workspace root; the record is not an SCD, is not compiled, is validated against `schema/intake/intake-schema.json`, and is written only by the engine's intake commands | MUST | `agent-interface.md` §5.3 (saving, the only writers); `bundle-format.md` §8.4 (location, not an SCD, never compiled, schema, person identifiers) | Stated |

## Section 5. Provenance

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 5.1 | Every SCD item the agent drafts records where it came from | SHOULD | `agent-interface.md` §6.1; `core-model.md` §4.1 (the field) | Stated |
| 5.2 | `approval.approved_by` is a person identifier | MUST | `agent-interface.md` §6.2; `bundle-format.md` §9.8 | Stated |
| 5.3 | Provenance is correct at validation and versioning | MUST | `agent-interface.md` §6.3 | Stated |
| 5.4 | The tools do not invent provenance | MUST NOT | `agent-interface.md` §6.3 | Stated |

## Section 6. Human confirmation

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 6.1 | Show the planned `changes` (from `--dry-run`) and get explicit confirmation before writing files | MUST | `agent-interface.md` §7 item 1 | Stated |
| 6.2a | Obtain the approver for `scs bundle version` from the user in the current conversation | MUST | `agent-interface.md` §7 item 2 | Stated |
| 6.2b | Do not supply an approver, take one from the environment without confirmation, or record the agent or model as approver | MUST NOT | `agent-interface.md` §7 item 2 | Stated |
| 6.3 | Do not pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for it in the current conversation | MUST NOT | `agent-interface.md` §7 item 3 | Stated |
| 6.4 | Do not report an operation as successful unless the engine returned `ok: true` | MUST NOT | `agent-interface.md` §7 item 4 | Stated |
| 6.5 | Present validation errors in plain language before proposing fixes | MUST | `agent-interface.md` §7 item 5 | Stated |
| 6.6 | Present a plain-language change summary before versioning | SHOULD | `agent-interface.md` §7 item 6 | Stated |
| 6.7a | Record the user's decision on every advisory review finding raised | MUST | `agent-interface.md` §7 item 7, §11 | Stated |
| 6.7b | Show findings still open before versioning | SHOULD | `agent-interface.md` §7 item 7 | Stated |
| 6.8a | Do not write outside the Domain repository | MUST NOT | `agent-interface.md` §7 item 8, §10 | Stated |
| 6.8b | After compiling, tell the user where the artifact belongs, using the placement guide, and leave placing it to the user | SHOULD | `agent-interface.md` §10 | Stated |

The cascade confirmation (one confirmation MAY cover a bottom-up versioning cascade) is stated
in `agent-interface.md` §7.

## Section 7. Change summary

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 7.1 | `scs bundle diff` produces a deterministic summary of what changed between two versions, or a version and the working tree | MUST | `agent-interface.md` §8 | Stated |

## Section 8. Drafting from source documents

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 8.1 | Each item drafted from a document carries a `derived_from` entry naming it | MUST | `agent-interface.md` §9 | Stated |
| 8.2 | Such an item carries a locator | SHOULD | `agent-interface.md` §9 | Stated |
| 8.3 | The agent does not copy standard text into SCDs | MUST NOT | `agent-interface.md` §9; `citations.md` | Stated |
| 8.4 | The interface does not send source documents anywhere other than the user's own AI client | MUST NOT | `agent-interface.md` §9 | Stated |

## Section 9. Domain repositories

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 9.1 | Every Domain has its own git repository, the Domain repository | MUST | `bundle-format.md` §8.1 | Stated |
| 9.2 | Application repositories that consume the context are not used to author it | MUST NOT | `bundle-format.md` §8.1 | Stated |
| 9.3a | The agent interface creates the Domain repository, or confirms an existing one, before writing any workspace content | MUST | `agent-interface.md` §10 | Stated |
| 9.3b | The agent interface does not write outside the Domain repository | MUST NOT | `agent-interface.md` §10, §7 item 8 | Stated |
| 9.4 | Domain repository names follow `<domain-name>-context` | SHOULD | `bundle-format.md` §8.1 | Stated |
| 9.5 | The `name` in a workspace's `.scs/config` matches the workspace name | MUST | `bundle-format.md` §8.3 | Stated |
| 9.6 | The scaffold generates an agent instructions file stating the repository's purpose and limits | MUST | `bundle-format.md` §8.8 | Stated |
| 9.7 | When the user is working on one workspace, the agent confines its changes to that workspace | SHOULD | `agent-interface.md` §10 | Stated |
| 9.8 | The scaffold also generates a client-specific file that points to `AGENTS.md` | SHOULD | `bundle-format.md` §8.8 | Stated |
| 9.9 | Bundle versions are recorded as git tags in the Domain repository | MUST | `bundle-format.md` §8.5, §7.3 | Stated |
| 9.10 | Tags are qualified by workspace and bundle name, `<workspace>/<bundle-name>-v<version>` | MUST | `bundle-format.md` §8.5 | Stated |
| 9.11 | Version manifests are named `<bundle-name>-v<version>-MANIFEST.yaml`, and snapshots `<bundle-name>-v<version>.yaml`, in the bundle's directory | MUST | `bundle-format.md` §8.5 | Stated |
| 9.12 | `scs compile` writes to the workspace's `dist/`, named `<bundle-name>-<version>.yaml` | SHOULD | `bundle-format.md` §8.7 | Stated |
| 9.13 | The scaffold generates a CI workflow that runs `scs-validate --strict` on every workspace on every push | SHOULD | `bundle-format.md` §8.8 | Stated |
| 9.14 | The CI workflow fetches full history and tags | MUST | `bundle-format.md` §8.8 | Stated |

The `scs bundle version` behaviour in RFC section 9 (what it commits, when it refuses, the
fixed committer identity, rollback) is stated without RFC 2119 keywords in the RFC and in
`bundle-format.md` §8.5.

## Section 10. Placement

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 10.1 | SCS tools do not place or transform renderings | MUST NOT | `overview.md` §1.1 | Stated |
| 10.2 | The SCS documentation includes a placement guide for common AI services | SHOULD | `overview.md` §1.1 names it; the guide is `docs/placement/` (WP-09, provisional) | Outside the spec |
| 10.3 | The placement guide is checked against each service's current documentation when written or updated | MUST | `docs/placement/README.md` and each page's `checked:` date | Outside the spec |
| 10.4 | Skills use the placement guide to advise the user after compiling | SHOULD | `agent-interface.md` §10 | Stated |
| 10.5 | The placement guide recommends that renderings keep the bundle id, version, and digest | SHOULD | `docs/placement/README.md` | Outside the spec |

## Section 11. Verifiable immutability

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 11.1 | A versioned bundle is verifiably unchanged after it is versioned | MUST | `bundle-format.md` §7.3 | Stated |
| 11.2 | `scs bundle version` computes a `content_digest` over the bundle's full resolved content and records it in the version manifest | MUST | `bundle-format.md` §7.6 | Stated |
| 11.3 | Run at a Domain repository root, `scs-validate` makes the three checks (every tag, working copies, drift), each an error in every mode | MUST | `bundle-format.md` §7.7 | Stated |
| 11.4 | The drift diagnostic names the files whose content changed and the bundles to version again | SHOULD | `bundle-format.md` §7.7 (check 3), §7.6 | Stated |
| 11.5a | `scs compile` runs the checks for the tree it compiles, including when the root is `DRAFT` | MUST | `bundle-format.md` §7.7 | Stated |
| 11.5b | `scs compile` refuses on a failed check, with no override | MUST | `bundle-format.md` §7.7, §7.6 | Stated |
| 11.6 | `scs bundle version` records `validation_passed` and `approval_status` from what actually happened | MUST | `bundle-format.md` §7.7, §7.6 | Stated |

The integrity model's boundary (RFC section 11, "Boundary") is stated in `bundle-format.md`
§7.8.

## Section 12. Advisory review

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 12.1 | While drafting and before versioning, the agent reviews the workspace in the five categories | SHOULD | `agent-interface.md` §11 | Stated |
| 12.2 | The agent does not block an operation because of a finding | MUST NOT | `agent-interface.md` §11 | Stated |
| 12.3 | The agent does not change content to resolve a finding without the user's confirmation | MUST NOT | `agent-interface.md` §11 | Stated |
| 12.4 | Each finding is presented in plain language, naming the SCD item and, where relevant, the citation | MUST | `agent-interface.md` §11 | Stated |
| 12.5 | The user's decision is recorded in `intake.yaml` under `review_findings` (`changed`, `kept` with rationale, or `deferred`; who and when) | MUST | `agent-interface.md` §11 | Stated |
| 12.6 | A finding left `deferred` is raised again before the next version | SHOULD | `agent-interface.md` §11 | Stated |

That findings are not compiled is stated in `runtime-artifact.md` §2.1.

## Section 13. Layered context

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 13.1 | `scs stack` only reads; it does not write, compile, or place anything (it MAY read any path) | MUST, MUST NOT | `runtime-artifact.md` §5.1 | Stated |
| 13.2 | `scs stack` accepts only runtime artifacts; any other input is `STACK_ARTIFACT_INVALID` | MUST | `runtime-artifact.md` §5.1 | Stated |
| 13.3 | `scs stack` does not merge, reorder, or drop rules | MUST NOT | `runtime-artifact.md` §5.1 | Stated |
| 13.4 | `scs stack` supports machine mode; its `changes` is always empty | MUST | `runtime-artifact.md` §5.1 | Stated |
| 13.5 | The placement guide describes how each service loads layered context | SHOULD | `runtime-artifact.md` §5.2 names it; the guide is `docs/placement/` (WP-16) | Outside the spec |

The check table (codes and severities) is in `runtime-artifact.md` §5.2. The `layer-conflict`
review kind, and where its decision is recorded, are in `agent-interface.md` §11.

## Schema Changes

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| S.1 | A version manifest's `approval.approved_by` is a person identifier; the schema rejects empty and `role:` values | MUST | `bundle-format.md` §9.8 | Stated |
| S.2 | A manifest recognized as 0.7 by its workspace-qualified tag carries `content_digest` and `tools_version` | MUST | `bundle-format.md` §7.6 | Stated |

The other schema changes carry no RFC 2119 keyword. Where each is documented:

- `schema/intake/intake-schema.json`: `bundle-format.md` §8.4
- `schema/manifest/version-manifest-schema.json`: `bundle-format.md` §7.6
- `schema/cli/envelope-schema.json` and `schema/diagnostics/codes.yaml`: `agent-interface.md` §4.2
- `derived_from` on items: `core-model.md` §4.1, `project-tier.md` §4.2, `meta-tier.md` §4.1
- `content_digest`, `content_inputs`, `tools_version` in manifests: `bundle-format.md` §7.6
- `source_digest` and `scs_runtime: "0.7"` in the runtime artifact: `runtime-artifact.md` §3.1,
  §3.5

## Validation Rules

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| V.1 | `intake.yaml`, when present, validates against `intake-schema.json` | MUST | `bundle-format.md` §8.4 | Stated |
| V.2 | `derived_from` ids resolve in the workspace's `intake.yaml`; an unresolved id is a warning (`DERIVED_FROM_UNRESOLVED`) | MUST | `bundle-format.md` §9.8; `core-model.md` §4.1 | Stated |
| V.3 | A version manifest has an `approval.approved_by` that is a person identifier | MUST | `bundle-format.md` §9.8 | Stated |
| V.4 | `scs compile` does not emit `derived_from` | MUST NOT | `runtime-artifact.md` §2.1 | Stated |
| V.5 | The three checks in section 11 pass; a failure is an error in every mode | MUST | `bundle-format.md` §7.7, §9.6 | Stated |
| V.6 | A workspace's `.scs/config` `name` matches its workspace name (`CONFIG_NAME_MISMATCH`) | MUST | `bundle-format.md` §8.3, §9.7 | Stated |
| V.7 | At a Domain repository root, the validator validates every workspace and reports no Domain workspace, or more than one, as an error | SHOULD | `bundle-format.md` §9.7 | Stated |
| V.8 | The validator does not report reserved directories, or validate their content | MUST NOT | `bundle-format.md` §9.7 | Stated |
| V.9a | The validator reports an SCD with no prohibitions, directives, or facts as `SCD_EMPTY` (info) | MUST | `bundle-format.md` §9.9 | Stated |
| V.9b | `scs bundle version --dry-run` lists the bundle's empty SCDs | MUST | `bundle-format.md` §9.9 | Stated |
| V.10 | `scs bundle version` refuses to version over a placeholder `created_by` | MUST | `bundle-format.md` §9.8 | Stated |
| V.11 | `scs stack` reports the section 13 checks with their codes and severities; under `--strict` its warnings give exit 2 | MUST | `runtime-artifact.md` §5.2 | Stated |

Rules without an RFC 2119 keyword are also stated: a reserved bundle name is an error
(`bundle-format.md` §9.7); a version without a workspace-qualified tag is history
(`bundle-format.md` §7.7); `COMPLETENESS_STUB_SCD` is removed (`bundle-format.md` §9.9).

