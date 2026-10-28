# SCS 0.7.0 — Agent Interface

**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-28

---

## 1. Purpose

Most people who adopt SCS will not run its tools directly. They will ask an AI agent to build
and maintain their context for them. This document defines how an agent that operates SCS on a
user's behalf behaves: what it may do, how it calls the SCS tools, and where it stops for the
user.

It applies to agents that **operate** SCS. Agents that **consume** compiled context are
described in [governance-and-compliance.md](governance-and-compliance.md) §9.

An **agent interface** is the set of skills, scripts, or tools through which an agent operates
SCS. A **conforming agent interface** meets the requirements of this document. The **engine**
is the SCS tools: `scs` (`scs-tools`) and `scs-validate` (`scs-validator`).

---

## 2. Scope

An agent interface MUST be limited to these operations on a local Domain repository
([bundle-format.md](bundle-format.md) §8):

| Area | Operations |
|---|---|
| Create | Intake (§5); create the Domain repository; scaffold Domain and Project workspaces; draft SCDs from conversation or source documents (§9) |
| Maintain | Add, edit, retire, and re-scope SCDs; add concept bundles; explain existing context in plain language |
| Validate | Run the validator; explain results; propose fixes |
| Version | Pin imports; version bundles; record approver and notes |
| Compile | Produce the runtime artifact defined in [runtime-artifact.md](runtime-artifact.md); preview and check a stack of compiled artifacts ([runtime-artifact.md](runtime-artifact.md) §5) |

Each write is an engine command: `scs scd write` (content on stdin), `scs bundle add-scd`,
`remove-scd`, `add-import`, and `pin`. Retiring an SCD is removing it from its bundle.

Placing artifacts where AI services read them, multi-user review, approval workflows, shared or
hosted registries, and runtime serving are out of scope for SCS ([overview.md](overview.md)
§1.1). An agent interface MUST NOT present itself as providing them.

---

## 3. Architecture

An agent interface has up to three layers:

```
  chat client (Claude, Cursor, Codex, Copilot, ...)
        |                         |
   Agent Skills              MCP server (local, stdio; optional)
   (workflow know-how)       (operations as tools)
        \                        /
         scs / scs-validate  --json
         (deterministic engine)
```

1. **Engine.** The SCS tools in machine mode (§4). The engine is the single source of truth for
   behaviour.
2. **Agent Skills.** Skills in the open Agent Skills format (`SKILL.md`) carry the parts that
   are not deterministic: running the intake, turning intent into prohibitions, directives, and
   facts, explaining validator output, and stopping for confirmation. Skills call the engine
   through scripts. This is the primary interface.
3. **MCP server.** An optional adapter exposing the engine's operations as MCP tools, for
   clients without skill support or shell access. It MUST run locally, over the stdio
   transport. A hosted server is out of scope (§2).

Each layer above the engine MUST go through the engine. No layer reimplements validation,
versioning, or compilation.

---

## 4. Machine Mode

Every `scs` command an agent uses MUST accept `--json`. In machine mode a command:

- MUST NOT prompt. Missing required input is an error, not a prompt.
- MUST NOT infer human-attributable values (approver, author) from the environment. Values such
  as `git config user.email` MAY be offered as suggestions in the result, never applied.
- MUST write a single JSON object, the **envelope**, to stdout, and nothing else to stdout.
- MUST keep the exit codes `0` (ok), `1` (errors), `2` (warnings under `--strict`), `3` (bad
  arguments or no input), `4` (file error: missing, unreadable, or unwritable), and `5`
  (internal error).

### 4.1 Workspace Selection

Workspace-scoped commands take `--workspace <domain|name>`. Without it, the workspace is the
nearest `.scs/config` above the current directory. At the repository root without it, the
command fails with `WORKSPACE_REQUIRED`.

### 4.2 Envelope

```json
{
  "scs_version": "0.7.0",
  "tools_version": "0.7.0",
  "command": "bundle version",
  "ok": false,
  "exit_code": 1,
  "changes": [],
  "diagnostics": [
    {
      "severity": "error",
      "code": "VERSION_APPROVER_REQUIRED",
      "message": "An approver is required to version a bundle.",
      "path": "domain/bundles/concepts/design-controls.yaml",
      "suggestion": {"approved_by": "Jane Doe <jane@medtech-cdmo.example>"}
    }
  ],
  "result": {}
}
```

The envelope validates against `schema/cli/envelope-schema.json`.

- `scs_version` is the spec version; `tools_version` is the engine package version.
- `ok` is true exactly when `exit_code` is `0`.
- Paths are POSIX, relative to the Domain repository root.
- `diagnostics[].severity` is `error`, `warning`, or `info`; `info` never changes the exit code.
  Every `code` MUST be registered in `schema/diagnostics/codes.yaml`.
- `result` holds the command's own output. `scs-validate`'s JSON report SHOULD be carried in
  `result` unchanged, with its findings mapped into `diagnostics`.

### 4.3 Changes

`changes` lists every effect of the command:

| `action` | Fields | Meaning |
|---|---|---|
| `create`, `modify`, `delete` | `path` | A file the command itself wrote |
| `git-init` | `ref` | A repository was initialized |
| `git-commit` | `ref`, `paths: [{path, status}]` | A commit, with everything it contains (status `A`, `M`, or `D`), including edits made earlier and committed with it |
| `git-tag` | `ref` | A tag was created |

On `ok: false`, `changes` lists what remains after rollback, normally nothing.

A command run with `--dry-run` MUST return the same `changes` the real run would, and change
nothing, so the agent can show the user what will happen before it happens.

---

## 5. Intake

The **intake** is the conversation that gathers what scaffolding and drafting need. It is
adaptive: routing questions are always asked, and profile questions only when the routing
answers call for them. An agent SHOULD infer what it can and ask the user to confirm, rather
than asking each question separately.

The first step of every intake MUST be to establish the Domain repository: either an existing
one the user names, or a new one. In a new Domain repository, the Domain workspace MUST be built
before any Project workspace.

### 5.1 Routing (always asked)

| Field | Values |
|---|---|
| `audience` | `individual` or `organization` |
| `domain` | The existing Domain repository to work in, or `new` |
| `workspace` | `domain`, or the name of a Project (new or existing) |
| `regulated` | Yes or no; if yes, which frameworks |
| `ontology` | `sdlc`, `cdmo`, `mca`, or `personal`, proposed from the above and confirmed by the user |

### 5.2 Profiles

**Personal Domain** (`audience: individual`, `workspace: domain`, usually with the `personal`
ontology):

| Field | Purpose |
|---|---|
| `owner` | The person's identifier, `Name <email>`. Provenance only (§6); never compiled |
| `boundaries` | What no AI tool should do on any of their work; the source of personal prohibitions |
| `practices` | Habits they want applied everywhere (languages, testing, commit style) |

A personal Domain is deliberately small and MAY consist of only a few prohibitions. The
`personal` ontology has one fixed concept, boundaries; the agent defines the person's other
concepts with them rather than starting from templates.

**Organization** (`audience: organization`, or `regulated: yes`):

| Field | Purpose |
|---|---|
| `organization` | Name, products or services, sites |
| `certifications` | Standards and editions in scope; drives `cites` |
| `source_documents` | Quality manual, SOPs, and other documents the agent may draft from |
| `approvers` | People and roles who approve context versions |
| `boundaries` | What is explicitly out of bounds; the main source of prohibitions |

**Project** (each Project):

| Field | Purpose |
|---|---|
| `project` | Name, purpose, technology |
| `risk` | Risk or safety classification where applicable (for example, IEC 62304 software safety class) |
| `data` | Categories of data handled (PHI, PCI, PII) |
| `boundaries` | Project-specific prohibitions |

### 5.3 Intake Record

The agent MUST save the answers to the workspace's intake record, `intake.yaml`
([bundle-format.md](bundle-format.md) §8.4), so the intake can be resumed, revisited when
circumstances change, and audited.

The engine commands `scs intake set` and `scs intake record-finding` (both with `--dry-run`)
are the record's only writers; the agent MUST NOT edit the file directly. `scs intake set FIELD
VALUE` sets one field. An object given for `answers`, `source_documents`, or `approvers`
replaces the entry with the same `id` (`person` for approvers), or is appended.
`review_findings` is written only by `scs intake record-finding` (§11).

---

## 6. Provenance

### 6.1 Item Provenance

Every SCD item the agent drafts SHOULD record where it came from, in the item's `derived_from`
list ([core-model.md](core-model.md) §4.1): an intake answer or a source document.

```yaml
content:
  prohibitions:
    - id: PU-003
      kind: practice
      subject: editing a released DHF record
      derived_from:
        - intake: q-boundaries-1
  directives:
    - id: DC-007
      directive: "Draft DHF changes as redlines for human review."
      derived_from:
        - source: doc-qm
          locator: "section 4.2.5"
```

`derived_from` is never compiled. It exists so an organization can answer "why does this rule
exist" from the workspace.

### 6.2 Identity

A person's identity in SCS is provenance only: a person identifier, `Name <email>`, in
`provenance.created_by`, a version manifest's `approval.approved_by`, and the intake record. It
is not a concept or an SCD, and it is never compiled. `approval.approved_by` MUST be a person
identifier; `created_by` MAY instead name a team or organization.

### 6.3 When Provenance Must Be Right

Provenance is read at validation and versioning, so that is where it MUST be correct. A
scaffold or draft need not be final: the tools report placeholder provenance
(`PROVENANCE_PLACEHOLDER`), and the agent corrects it with the user before a version is made.

The tools MUST NOT invent provenance. `scs new` offers the git identity only as a suggestion and
otherwise requires `--author` and `--email`. A value that was never true, such as a
placeholder, is corrected. A true value is never replaced: the person who created an SCD is not
necessarily the person who approves a version.

---

## 7. Human Confirmation

A conforming agent interface:

1. MUST show the user the planned `changes` (from `--dry-run`) and get explicit confirmation
   before writing files.
2. MUST obtain the approver for `scs bundle version` from the user in the current
   conversation. It MUST NOT supply one itself, take one from the environment without
   confirmation, or record the agent or model as approver.
3. MUST NOT pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   specific behaviour in the current conversation.
4. MUST NOT report an operation as successful unless the engine returned `ok: true`.
5. MUST present validation errors to the user, in plain language, before proposing fixes.
6. SHOULD present a plain-language change summary (§8) before versioning.
7. MUST record the user's decision on every advisory review finding it raises, and SHOULD show
   any findings still open before versioning (§11).
8. MUST NOT write outside the Domain repository (§10).

**Cascades.** Versioning a root bundle usually means versioning its concept bundles first,
bottom-up, re-pinning each as it is versioned. One confirmation MAY cover that cascade (items 1
and 2) if, before asking, the agent shows a cascade plan listing every snapshot, manifest, pin,
commit, and tag, and the confirmation names the approver. The agent then runs each step's
`--dry-run` and stops if a result differs from the plan.

---

## 8. Change Summary

`scs bundle diff [BUNDLE] [--from VERSION] [--to VERSION|working]` MUST produce a deterministic
summary of what changed between two versions of a bundle, or between a version and the working
tree, across the bundle's whole tree:

- SCDs added or removed (a retired SCD is a removed one);
- prohibitions, directives, and facts added, removed, or changed;
- citations added or removed;
- imports added, removed, or re-pinned.

With `--json` it returns the structured diff in `result`. The agent uses it to show the user
what they are approving. Because the diff is deterministic, the summary of a change does not
depend on the model.

The content of a version is read from its tag ([bundle-format.md](bundle-format.md) §7.3). By
default `--from` is the latest version and `--to` is `working`. A bundle with no version diffs
from empty, so everything is added. A version with no tag is an error
(`DIFF_VERSION_NOT_FOUND`).

---

## 9. Drafting From Source Documents

When the user provides source documents, the agent MAY draft SCD items from them.

- Each item drafted from a document MUST carry a `derived_from` entry naming the document, and
  SHOULD carry a locator.
- The agent MUST NOT copy standard text into SCDs. Standards are cited with `std:` references
  ([citations.md](citations.md)).
- Source documents stay in the user's workspace (`sources/`, [bundle-format.md](bundle-format.md)
  §8.6). The interface MUST NOT send them anywhere other than the user's own AI client.

---

## 10. Working in the Domain Repository

The agent interface MUST create the Domain repository, or confirm an existing one, before
writing any workspace content, and MUST NOT write outside it.

When the user is working on one workspace, the agent SHOULD confine its changes to that
workspace. The repository's agent instructions file ([bundle-format.md](bundle-format.md) §8.8)
states the repository's purpose and limits for clients that read it.

**Placement.** Placing a compiled artifact where an AI service reads it is the user's decision
([overview.md](overview.md) §1.1). After compiling, the agent SHOULD tell the user where the
artifact belongs for their AI service, using the placement guide (`docs/placement/`), and leave
placing it to the user.

---

## 11. Advisory Review

The validator checks structure, completeness, and conflicts. It cannot judge whether a rule is
sound. While drafting and before versioning, the agent SHOULD review the workspace for problems
a careful reviewer would raise:

| `kind` | Examples |
|---|---|
| `framework-conflict` | A rule that contradicts a framework the workspace cites |
| `missing-protection` | No prohibition or directive covering something the intake says is present (PHI, payment data, safety-class C software) |
| `technical-risk` | A rule that weakens security, auditability, or traceability (disabling logging, sharing credentials) |
| `ethical-risk` | A rule that could cause harm, deception, or unfair treatment of people |
| `layer-conflict` | A rule that contradicts a rule in another layer of the stack the user loads it with ([runtime-artifact.md](runtime-artifact.md) §5) |

Rules for findings:

- The review is advisory. The agent MUST NOT block an operation because of a finding, and MUST
  NOT change content to resolve a finding without the user's confirmation.
- Each finding MUST be presented in plain language, naming the SCD item it concerns and, where
  relevant, the citation it rests on.
- The user's decision MUST be recorded in the workspace's intake record under
  `review_findings`, with one of `changed`, `kept` (with a rationale), or `deferred`, plus who
  decided and when. `scs intake record-finding` writes it.
- Findings are not compiled. They belong to the record of how the context was made, not to the
  context.
- A finding left `deferred` SHOULD be raised again before the next version.

A `layer-conflict` finding can come from `STACK_PROHIBITION_DIRECTED` or from the agent's own
reading of a stack. The decision is recorded in the intake record of the workspace the user is
working in.

In 0.7 the review is driven by the agent's own judgment, guided by its skills.

---

## 12. Feedback

Feedback on the agent interface should be submitted via GitHub Issues.
