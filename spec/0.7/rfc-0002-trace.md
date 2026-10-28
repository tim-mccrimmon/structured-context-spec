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
- **Pending (agent-interface.md)**: a rule for agents that operate SCS. Its home is
  `spec/0.7/agent-interface.md` (D-22), written in WP-02b. Where part of the requirement is
  about a format, that part is already stated where shown.
- **Outside the spec**: the RFC places it outside the spec text.

Sections 2, 3, 5, 6, 7, 8, 12, Schema Changes, and Validation Rules are traced in WP-02b.

## Section 1. Scope

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 1.1 | The agent interface is limited to the create, maintain, validate, version, and compile operations on a local Domain repository | MUST | `overview.md` §1.1 (the scope); `agent-interface.md` (the agent rule) | Pending (agent-interface.md) |
| 1.2 | An agent interface does not present itself as providing placement, review workflows, registries, or runtime serving | MUST NOT | `overview.md` §1.1 (out of scope); `governance-and-compliance.md` §9 | Pending (agent-interface.md) |

## Section 4. Intake

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 4.1 | An agent infers what it can and asks the user to confirm, rather than asking each question separately | SHOULD | `agent-interface.md` | Pending (agent-interface.md) |
| 4.2 | The first step of every intake establishes the Domain repository, existing or new | MUST | `agent-interface.md` | Pending (agent-interface.md) |
| 4.3 | A new Domain repository's Domain workspace is built before any Project workspace in it | MUST | `agent-interface.md` | Pending (agent-interface.md) |
| 4.4 | The agent saves the answers to `intake.yaml` at the workspace root; the record is not an SCD, is not compiled, is validated against `schema/intake/intake-schema.json`, and is written only by the engine's intake commands | MUST | `bundle-format.md` §8.4 (location, not an SCD, never compiled, schema, person identifiers); `agent-interface.md` (saving, the only writers) | Pending (agent-interface.md) |

## Section 9. Domain repositories

| # | Requirement | Level | Spec | Status |
|---|---|---|---|---|
| 9.1 | Every Domain has its own git repository, the Domain repository | MUST | `bundle-format.md` §8.1 | Stated |
| 9.2 | Application repositories that consume the context are not used to author it | MUST NOT | `bundle-format.md` §8.1 | Stated |
| 9.3a | The agent interface creates the Domain repository, or confirms an existing one, before writing any workspace content | MUST | `agent-interface.md` | Pending (agent-interface.md) |
| 9.3b | The agent interface does not write outside the Domain repository | MUST NOT | `agent-interface.md` | Pending (agent-interface.md) |
| 9.4 | Domain repository names follow `<domain-name>-context` | SHOULD | `bundle-format.md` §8.1 | Stated |
| 9.5 | The `name` in a workspace's `.scs/config` matches the workspace name | MUST | `bundle-format.md` §8.3 | Stated |
| 9.6 | The scaffold generates an agent instructions file stating the repository's purpose and limits | MUST | `bundle-format.md` §8.8 | Stated |
| 9.7 | When the user is working on one workspace, the agent confines its changes to that workspace | SHOULD | `agent-interface.md` | Pending (agent-interface.md) |
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
| 10.4 | Skills use the placement guide to advise the user after compiling | SHOULD | `agent-interface.md` | Pending (agent-interface.md) |
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

## Remaining references to 0.6

`grep -rE 'spec/0\.6|0\.6\.0' spec/0.7 rfcs/RFC-0002*` returns only the references below. Each
is historical or a literal identifier. No reference to `spec/0.6/` remains.

**The meta bundle's identifier.** The meta bundle published with the spec is still
`bundle:meta:0.6.0`; these name it.

- `bundle-format.md` §2 (container analogy), §3.2 (text and example `version: "0.6.0"`), §3.5
  (example), §5.3, §6 (example), §9.4
- `meta-tier.md` §1 (ownership)
- `runtime-artifact.md` §3.1 (example `sources`)

**When something was introduced or deprecated.**

- `bundle-format.md` "What changed in 0.6.0" (and its migration guide link), §3 (bundle type
  table), §3.3 (standards status), §5.4, §12 (examples), §15 (migration guide link)
- `citations.md` §1, §6
- `core-model.md` §3.1 (`type` table), §5.2, §8.3 (SCDs written for 0.6.0 stay readable)
- `domain-ontology.md` §3.1, §5, §9
- `governance-and-compliance.md` §5
- `meta-tier.md` §1 (ownership), §10
- `overview.md` §4.2, §5.1, §6 (what 0.7.0 keeps from 0.6.0, and what 0.6.0 introduced)
- `project-tier.md` §1 (naming note), §6.2
- `standards-tier.md` status line and §1
- `terminology.md` §2.4, §2.5, the Standards Bundle entry, §3.2

**RFC 0002's own history.** The RFC describes what 0.6.0 showed and what 0.7 changes from it:
the Summary, Motivation, section 9 ("keep the 0.6.0 model", "building on what `scs new`
scaffolds in 0.6.0"), Alternative 6, and the Migration Guide.
