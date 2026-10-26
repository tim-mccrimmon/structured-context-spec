# RFC 0002: Agent-Mediated SCS

- **Start Date**: 2026-10-25
- **RFC PR**: #25
- **Tracking Issue**: `ISSUES.md` ISS-042 – ISS-055
- **Author(s)**: Tim McCrimmon (@tim-mccrimmon)
- **Status**: Accepted (2026-10-25; comment period waived by the maintainer)
- **Amended**: 2026-10-25: workspaces reserve directory and bundle names for a later release
  (section 9). 2026-10-25: build plan decisions (`plan/0.7/07-decisions-and-gaps.md`): engine
  commands for maintenance, git effects in the envelope, intake writers, layout corrections,
  whole-workspace version commits, the tag as the record of a version, and resolved questions
  (sections 1, 3, 4, 6, 7, 9, 11, Schema Changes, Validation Rules, Unresolved Questions,
  Migration Guide). 2026-10-26: layered context: `scs stack` previews and checks an ordered
  stack of compiled artifacts, and the advisory review covers conflicts between layers
  (sections 1, 12, 13, Validation Rules, Implementation Notes). 2026-10-26: ontologies,
  templates, and identity (`plan/0.7/07-decisions-and-gaps.md` D-60 to D-73): `personal` is an
  ontology, identity is provenance only, templates are chosen by ontology and workspace kind,
  provenance is corrected at validation and versioning (Motivation, Guide-level Explanation,
  sections 4, 5, 9, Implementation Notes, Migration Guide, Unresolved Questions). 2026-10-26:
  empty SCDs are reported as `SCD_EMPTY` (info) and listed before versioning; stub detection is
  removed (plan D-70; Validation Rules, Unresolved Questions)
- **Target**: SCS 0.7.0 (additive; no breaking changes to SCDs or bundles)

---

## Summary

SCS's value is immutable, versioned context that serves as the source of truth for AI: a
small bundle recording what a named person approved for AI to know and obey. Whatever a
vendor or runtime needs downstream (a compiled artifact, a rules file, a system prompt) is a
rendering of that truth, and can always be traced back to the exact version it came from.

Through 0.5.0, producing good structured context required someone who knew the
specification: its tiers, bundle types, import rules, and the versioning steps. SCS 0.6.0
showed that an AI assistant, given the spec and the tooling, can do most of that work for a
person through conversation. This RFC makes that the intended way to use SCS. It defines an
**agent interface** to the SCS lifecycle (create, maintain, validate, version, compile) so
that a person can produce validated, versioned bundles entirely through a chat window,
without learning the format. It specifies the interface's scope, its three layers (a
machine-readable CLI, a set of Agent Skills, and an optional local MCP server), an adaptive
**intake** for individual and organizational users, and the points at which a human MUST
confirm. It also defines where context lives, which SCS has so far left to the adopter: one
**Domain repository** per Domain, managed like code, holding the Domain workspace and the
workspaces of the Projects that run under it. Every Project has a Domain, an individual
developer's included. SCS's output ends at a validated, versioned bundle and its compiled
artifact; placing that artifact where an AI service reads it is the user's decision, supported
by a non-normative placement guide. Finally, it makes immutability verifiable: a versioned
bundle carries a digest over its full resolved content, the tools check it, and compiled
artifacts carry it, so a rendering can be checked against its source. And the agent reviews
drafts for problems a careful reviewer would raise, leaving every decision, and its record, to
the human. The spec remains the
authority; the agent is a client of it, and the validator is the gate.

---

## Motivation

**What SCS is for.** The point of SCS is a versioned bundle that serves as the source of
truth for AI context. "Truth" here means authoritative: SCS makes context accountable. The
bundle records what was approved for AI to know and obey, who approved it, what was flagged
along the way, and what the approver decided, which is what an auditor or a regulated buyer
needs. As with any quality system, the organization remains responsible for the rules
themselves; SCS does not certify them. The agent interface helps by reviewing drafts and
raising problems for a human to decide on (section 12). Every downstream form, whether vendor-specific, runtime-specific, or pasted by hand, is a rendering
of that record and can take whatever shape its destination needs, as long as it traces back to
the version it came from. Everything in this RFC serves that: making the bundle easy to
produce, easy to keep current, and verifiably unchanged once versioned.

**The expert requirement limits adoption.** Every SCS workspace through 0.5.0 was built by
someone who understood the spec. That is a reasonable bar for the people writing the
standard, and a high one for everyone else. The people SCS is meant to serve, such as a quality
engineer at a medical-device CDMO or a solo developer handling patient data, generally know
their domain well and have no reason to learn SCS's object model.

**0.6.0 showed the alternative works.** In 0.6.0 work, an assistant with the spec in context
interviewed a user, scaffolded workspaces, drafted SCDs, and ran the validator. Creating
context this way was markedly faster than doing it by hand, and the resulting SCDs
validated. The user described what their organization does and does not allow; the assistant
handled the format.

**The lifecycle, not authoring, is where it breaks.** A CDMO governance trial (2026-10-20)
drove the 0.6.0 tooling through a full cdmo Domain workspace and found that the failures
were in lifecycle operations an expert would catch and an agent might not:

- ISS-043: versioning several concept bundles at the same version overwrites each other's
  manifests, losing checksums and approval records without an error.
- ISS-042: `scs --version` reports the wrong version.
- ISS-044: templates carry a profile note that contradicts the workspace they are in.

An agent that reports "versioned successfully" on top of ISS-043 is worse than no agent. If
the agent is going to hide the spec, the tooling it calls has to be dependable and explicit
about failure.

**Immutability is promised but not enforced.** `bundle-format.md` §7.3 says a versioned
bundle MUST remain immutable. In 0.6.0 the tooling cannot show that it is (ISS-045).
`scs bundle version` snapshots and checksums only the bundle manifest; the SCDs it includes
are read from the working tree every time, so editing an SCD after `1.0.0` silently changes
what `1.0.0` compiles to. Nothing verifies the checksum, the snapshot records
`validation_passed: true` even when validation was skipped, and git tags can be moved. If the
versioned bundle is the source of truth, anyone holding it, or a rendering of it, needs to be
able to check that it is what was approved.

**The current tooling speaks to people, not agents.** The `scs` CLI prints prose, prompts
interactively, and in places fills in defaults that matter (for example, `scs bundle version`
takes the approver from `git config user.email` when `--approved-by` is omitted). Those are
reasonable choices for a person at a terminal. For an agent they mean parsing human output and
silently recording an approver no one named.

**Prior art in this repo is client-specific and predates 0.6.** The `scs-vibe` and
`scs-team` plugins already guide users conversationally, but they are Claude Code plugins
built on the 0.3/0.5 model (concern bundles, the 11-concern layout). They show the idea has
value; they are not a basis for a portable interface.

**Context has no defined home.** The spec defines what a workspace contains, not where it
lives or how it is managed. Adopters improvise: a folder inside an application repo, a shared
drive, a directory on one person's laptop. Context that governs AI behavior deserves the
same discipline as code: history, review, tagged releases, and CI. A defined home also keeps
an AI agent focused. An agent working in a repo whose only purpose is managing one Domain's
context does not mix that work with the goals of the applications it governs.

**Every Project has a Domain, but the spec does not say so.** In 0.6.0 a Project bundle is
independent of the Domain bundle, and a runtime applies the two side by side. That
independence is right for compilation, but nothing ties a Project to its Domain, and a
Project without one is possible, which leaves an individual developer's projects with no
common rules at all. A Domain is the capacity someone works in, not the person: the same
developer works under a personal Domain on their own projects and under their company's
Domain on company work. For a single developer, the personal Domain may hold only a few rules
they want everywhere.

**Domain and Project context are placed differently.** The reason to keep Domain and Project
context apart at all is that AI services read them from different places. Claude Enterprise,
for example, applies organization-level context separately from project-level context. Users
need to know where each compiled artifact belongs for the service they use. SCS can tell
them, without taking on the job of putting it there.

Expected outcome: anyone with a capable AI assistant can go from "here is what my organization
or project is" to a validated, versioned, compiled workspace in one conversation, and the
result is the same kind of workspace an expert would produce by hand.

---

## Guide-level Explanation

### What changes for users

Nothing about SCDs or bundles changes. What changes is how you get them. Instead of learning
the spec, you install the SCS skills (or connect the SCS MCP server) in your AI assistant and
start a conversation. The assistant asks what it needs, drafts the context, shows you what it
plans to write, validates it, and asks you to approve before anything is versioned.

You can still use the CLI directly. Everything the agent does goes through the same
commands.

### Two kinds of users, one intake

The intake starts with a few routing questions and goes deeper only where the answers call
for it.

A solo developer:

> **User:** I want guardrails for a side project. It's a FastAPI app that stores patient
> appointment reminders.
>
> **Agent:** That's a Project, just for you. Every Project runs under a Domain. Do you have
> a personal one already?
>
> **User:** No.
>
> **Agent:** Then I'll set one up first, in a new repo, `jdoe-context`, with the personal
> ontology: the rules you want on every project. Anything you never want an AI tool to do, on
> any of your work?
>
> **User:** Never commit secrets or API keys.
>
> **Agent:** Got it. Now the Project, under `projects/reminders` in the same repo. Since it
> stores appointment data, it likely holds PHI. Is it used by a covered entity, or is it a
> personal or demo project?
>
> **User:** Demo only, no real patient data.
>
> **Agent:** Then I'll use the sdlc ontology without HIPAA citations, and add one
> prohibition: no real patient data in the repository or test fixtures. Here's what I'll
> create... *(lists the Domain and Project workspaces and their SCDs)* ...okay to write these?

A handful of questions, a personal Domain and one Project, validated in a few minutes. The
next project goes into the same repo, under the same Domain, and starts with one question
fewer.

A quality engineer at a CDMO:

> **User:** I need to set up our organization's AI governance context. We're an ISO
> 13485-certified contract manufacturer for catheters and implantable leads.
>
> **Agent:** That's a Domain (organization-wide) workspace, and probably Projects later.
> From what you've said I'd propose the cdmo ontology with ISO 13485:2016, IEC 62304, and
> 21 CFR 820 citations. Does that match your certification scope?
>
> **User:** Yes, plus ISO 14971.
>
> **Agent:** Added. Do you have documents I can draft from, such as a quality manual, SOPs, or
> your design-control procedure? Drafting from what you already have keeps the context
> faithful to how you actually work.
>
> *(...user shares documents; the agent asks about scope boundaries, who approves context
> versions, and which software is safety-class C...)*

The conversation is longer because the result has to stand up to an audit. Every
prohibition traces back to either a source document or an answer, and to the person who
gave it.

### One repository per Domain

The first thing the tool does is create a git repository for your Domain, if it does not
exist yet. That *Domain repository* holds one Domain workspace and one workspace for each
Project that runs under it:

```
jdoe-context/
├── domain/
└── projects/
    ├── reminders/
    └── trail-map/
```

A person can have more than one Domain. A developer might have `jdoe-context` for personal
work and `acme-context` for work done as Acme's lead developer; switching between them changes
who the AI understands you to be. Which Domain a project belongs to is your call.

Below a Project are the applications it covers, each with whatever user context its own repo
carries. SCS does not manage that.

Because it is a repo, context is managed like code. Changes have history, versions are git
tags, a generated CI workflow runs the validator on every push, and teams that want review
can use pull requests on their own infrastructure. The repo also carries an agent
instructions file that tells any AI working there what the repo is for, so context work stays
separate from application work.

### Where the output goes

SCS's output is a validated, versioned bundle and its compiled artifact. Putting the artifact
where your AI service reads it is up to you. Domain and Project artifacts usually go to
different places: in Claude Enterprise, for example, Domain context belongs at the
organization level and Project context at the project level. The SCS docs include a placement
guide for common services, and the agent uses it to tell you where each artifact belongs:

> **Agent:** `reminders` 1.0.0 is versioned and compiled to
> `projects/reminders/dist/reminders-1.0.0.yaml`. For Claude Code, the placement guide
> suggests adding it to the app repo's `.claude/rules/`. Your Domain artifact belongs
> wherever it will cover all your personal projects and nothing else.

Every compiled artifact names its bundle and version, so you can always tell which version is
in place.

### The agent points out problems, and you decide

While drafting, the agent reviews what it is about to write and raises anything that looks
wrong: a rule that conflicts with a standard you cite, an obvious protection that is missing
given what you told it, a rule that would weaken security or auditability, or one that could
cause harm or unfair treatment.

> **Agent:** One thing before I write this. You cite 21 CFR 820, but directive DC-004 lets
> the assistant mark DHR records as approved. Approval of records is normally a human
> sign-off. Do you want to change it to "draft for approval", or keep it as written?
>
> **User:** Change it.

The agent never blocks you and never changes a rule without asking. Whatever you decide is
recorded, so the record shows the question was raised and who answered it.

### What the agent will not do on its own

- Write files without showing you what it will write.
- Write anywhere outside the Domain repository.
- Version a bundle without an approver you name.
- Report success when validation failed, or skip validation unless you tell it to.

### Where SCS stops

SCS covers one person working in one Domain repository at a time: creating, maintaining,
validating, versioning, and compiling bundles. It stops at the versioned bundle and its
compiled artifact. It can also show what several compiled artifacts look like together, the
way an AI client loads them in layers, and point out where they conflict; it reads those
artifacts and changes nothing. Placing artifacts, review by several people, approval workflows, shared
registries, hosting, and runtime serving of context are outside SCS. If a user asks for
those, the agent says they are outside what SCS does.

---

## Reference-level Explanation

### 1. Scope

The agent interface MUST be limited to these operations on a local Domain repository
(section 9):

| Area | Operations |
|---|---|
| Create | Intake; create the Domain repository; scaffold Domain and Project workspaces; draft SCDs from conversation or source documents |
| Maintain | Add, edit, retire, and re-scope SCDs; add concept bundles; explain existing context in plain language. Each write is an engine command: `scs scd write` (content on stdin), `scs bundle add-scd`, `remove-scd`, `add-import`, `pin`. Retiring an SCD is removing it from its bundle. |
| Validate | Run the validator; explain results; propose fixes |
| Version | Pin imports; version bundles; record approver and notes |
| Compile | Produce the runtime artifact defined in [runtime-artifact.md](../spec/0.6/runtime-artifact.md); preview and check a stack of compiled artifacts (section 13) |

SCS's output ends at a validated, versioned bundle and its compiled artifact. Placing
artifacts where AI services read them (section 10), multi-user review, approval workflows,
shared or hosted registries, and runtime serving (selecting or streaming context to agents at
request time) are out of scope for SCS. An agent interface MUST NOT present itself as
providing them.

### 2. Architecture

The interface has three layers. Each layer above the first MUST go through the first; no
layer reimplements validation, versioning, or compilation.

```
  chat client (Claude, Cursor, Codex, Copilot, ...)
        |                         |
   Agent Skills              MCP server (local, stdio; optional)
   (workflow know-how)       (operations as tools)
        \                        /
         scs / scs-validate  --json
         (deterministic engine)
```

**Layer 1: engine.** The existing `scs-tools` and `scs-validator` packages, extended with a
machine mode (section 3). This is the single source of truth for behavior.

**Layer 2: Agent Skills.** A set of skills in the open Agent Skills format (`SKILL.md`)
carrying the parts that are not deterministic: running the intake, turning intent into
prohibitions, directives, and facts, explaining validator output, and stopping for
confirmation. Skills call the engine through scripts. This is the primary interface.

**Layer 3: MCP server.** A thin adapter exposing the engine's operations as MCP tools, for
clients without skill support or shell access, and for environments that disable code
execution. It MUST run locally (stdio transport). A hosted remote server is out of scope
(section 1).

### 3. Engine machine mode

Every `scs` command an agent uses MUST accept `--json`. In machine mode a command:

- MUST NOT prompt. Missing required input is an error, not a prompt.
- MUST NOT infer human-attributable values (approver, author) from the environment. Values
  such as `git config user.email` MAY be offered as suggestions in the result, never applied.
- MUST write a single JSON object to stdout, and nothing else to stdout.
- MUST keep the existing exit codes (`0` ok, `1` errors, `2` warnings in strict mode, `3` bad
  arguments or no input, `4` file error (missing, unreadable, or unwritable file), `5` internal
  error).

Workspace-scoped commands take `--workspace <domain|name>`. Without it, the workspace is the
nearest `.scs/config` above the current directory; at the repository root without it, the
command fails with `WORKSPACE_REQUIRED`.

Result envelope:

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

`scs_version` is the spec version; `tools_version` is the engine package version. Paths are
POSIX, relative to the Domain repository root. `diagnostics[].severity` is `error`, `warning`,
or `info`; `info` never changes the exit code. Every `code` is registered in
`schema/diagnostics/codes.yaml`.

`changes` lists every effect of the command. File effects are `create`, `modify`, and `delete`,
each with a `path`, and list only files the command itself wrote. Git effects are `git-init`,
`git-commit`, and `git-tag`, each with a `ref`; a `git-commit` entry also carries
`paths: [{path, status}]` (status `A`, `M`, or `D`) for everything the commit contains,
including edits made earlier and committed with it (section 9). On `ok: false`, `changes`
lists what remains after rollback, normally nothing. A command run with `--dry-run` MUST return
the same `changes` the real run would, and change nothing, so the agent can show the user what
will happen before it happens. `scs-validate --output json` already exists; its report SHOULD
be carried in `result` unchanged, with its findings mapped into `diagnostics`.

### 4. Intake

The intake is the conversation that gathers what scaffolding and drafting need. It is
adaptive: routing questions are always asked, and profile questions only when the routing
answers call for them. An agent SHOULD infer what it can and ask the user to confirm, rather
than asking each question separately.

The first step of every intake MUST be to establish the Domain repository (section 9): either
an existing one the user names, or a new one. A new Domain repository's Domain workspace MUST
be built before any Project workspace in it.

**Routing (always asked)**

| Field | Values |
|---|---|
| `audience` | `individual` or `organization` |
| `domain` | The existing Domain repository to work in, or `new` |
| `workspace` | `domain`, or the name of a Project (new or existing) |
| `regulated` | yes/no; if yes, which frameworks |
| `ontology` | `sdlc`, `cdmo`, `mca`, or `personal` (proposed from the above, confirmed by the user) |

**Personal Domain profile** (`audience: individual`, `workspace: domain`, usually with the
`personal` ontology)

| Field | Purpose |
|---|---|
| `owner` | The developer's person identifier, `Name <email>`. Provenance only (section 5): it attributes the workspace's records and is never compiled |
| `boundaries` | What no AI tool should do on any of their work; the source of personal prohibitions |
| `practices` | Habits they want applied everywhere (languages, testing, commit style) |

A personal Domain is deliberately small. It MAY consist of only a few prohibitions. The
`personal` ontology has one fixed concept, boundaries; everything else in a person's context is
particular to them, so the agent defines those concepts with the user rather than starting from
templates (section 9).

**Organization profile** (`audience: organization`, or `regulated: yes`)

| Field | Purpose |
|---|---|
| `organization` | Name, products or services, sites |
| `certifications` | Standards and editions in scope; drives `cites` |
| `source_documents` | Quality manual, SOPs, standards the agent may draft from |
| `approvers` | People and roles who approve context versions |
| `boundaries` | What is explicitly out of bounds; the main source of prohibitions |

**Project profile** (each Project)

| Field | Purpose |
|---|---|
| `project` | Name, purpose, technology |
| `risk` | Risk or safety classification where applicable (e.g. IEC 62304 software safety class) |
| `data` | Categories of data handled (PHI, PCI, PII) |
| `boundaries` | Project-specific prohibitions |

**Intake record.** The agent MUST save the answers to `intake.yaml` at the root of the
workspace they apply to (`domain/intake.yaml`, `projects/<name>/intake.yaml`), so
the intake can be resumed, revisited when circumstances change, and audited. The record is
not an SCD and is not compiled. It is validated against a new schema,
`schema/intake/intake-schema.json`. The engine commands `scs intake set` and
`scs intake record-finding` (both with `--dry-run`) are its only writers; the agent does not
edit the file directly.

People in the record are identified as `Name <email>`. For a repository that will be shared
publicly, the record MAY use role-only attribution instead, written `role:<name>` (for example
`role:quality-manager`). Role-only attribution is allowed in `intake.yaml` only; a version
manifest's approver is always a person.

```yaml
intake_version: "1.0"
scs_version: "0.7.0"
audience: organization
workspace: domain
regulated: true
ontology: cdmo
organization:
  name: Medtech CDMO
  products: [catheters, implantable leads]
certifications:
  - std:iso-13485:2016
  - std:iec-62304:2006+A1:2015
  - std:21-cfr-820
  - std:iso-14971:2019
approvers:
  - name: Jane Doe
    role: Quality Manager
    email: jane@medtech-cdmo.example
answers:
  - id: q-boundaries-1
    question: "Is there anything AI tools must never do with design history files?"
    answer: "Never edit a released DHF record; drafts only."
    answered_by: Jane Doe <jane@medtech-cdmo.example>
    answered_at: 2026-10-20T14:12:00Z
source_documents:
  - id: doc-qm
    title: Quality Manual rev F
    path: sources/quality-manual-rev-f.pdf
review_findings:
  - id: rf-1
    kind: framework-conflict
    target: scd:project:design-history#DC-004
    finding: "Directive lets the assistant mark DHR records approved; 21 CFR 820 is cited and record approval is normally a human sign-off."
    cites: [std:21-cfr-820]
    decision: changed
    rationale: "Changed to draft-for-approval."
    decided_by: Jane Doe <jane@medtech-cdmo.example>
    decided_at: 2026-10-20T14:40:00Z
```

### 5. Provenance

Every SCD item the agent drafts SHOULD record where it came from: an intake answer or a
source document. This RFC adds an optional `derived_from` list to prohibitions, directives,
and facts:

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

**Identity.** A person's identity in SCS is provenance only: a person identifier,
`Name <email>`, in provenance fields (`provenance.created_by`, `approval.approved_by`, and the
intake record). It is not a concept or an SCD, and it is never compiled.

**When provenance must be right.** Provenance is read at validation and versioning, so that is
where it MUST be correct. A scaffold or draft need not be final; the tools report provenance that
is not a person identifier, and the agent corrects it with the user before a version is made. A
value that was never true, such as a placeholder, is corrected; a true value is never replaced
(the person who created an SCD is not necessarily the person who approves a version).

The name `derived_from` avoids colliding with the existing SCD-level `provenance` object
(`created_by`, `created_at`, `rationale`), which records who created the SCD. `derived_from`
records where an individual item came from. It is not compiled into the runtime artifact. It
exists so an organization can answer "why does this rule exist" from the workspace.

### 6. Human confirmation

A conforming agent interface:

1. MUST show the user the planned `changes` (from `--dry-run`) and get explicit confirmation
   before writing files.
2. MUST obtain the approver for `scs bundle version` from the user in the current
   conversation. It MUST NOT supply one itself, take one from the environment without
   confirmation, or record the agent or model as approver.
3. MUST NOT pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   specific behavior in the current conversation.
4. MUST NOT report an operation as successful unless the engine returned `ok: true`.
5. MUST present validation errors to the user, in plain language, before proposing fixes.
6. SHOULD present a plain-language change summary (section 7) before versioning.
7. MUST record the user's decision on every advisory review finding it raises, and SHOULD
   show any findings still open before versioning (section 12).
8. MUST NOT write outside the Domain repository. After compiling, it SHOULD tell the user
   where the artifact belongs for their AI service, using the placement guide (section 10),
   and leave placing it to the user.

Versioning a root bundle usually means versioning its concept bundles first, bottom-up,
re-pinning as each is versioned. One confirmation MAY cover that cascade (items 1 and 2) if,
before asking, the agent shows a cascade plan listing every snapshot, manifest, pin, commit,
and tag, and the confirmation names the approver. The agent then runs each step's `--dry-run`
and stops if a result differs from the plan.

### 7. Change summary

A new command, `scs bundle diff <bundle> [--from <version>] [--to <version|working>]`, MUST
produce a deterministic summary of what changed between two versions of a bundle, or between
a version and the working tree: SCDs added or removed (a retired SCD is a removed one);
prohibitions, directives, and facts added, removed, or changed; citations added or removed;
imports re-pinned. With `--json` it returns the structured diff. The agent uses it to show the
user what they are approving. Because it is deterministic, the summary of a change does not
depend on the model.

The content of a version is read from its tag (section 11). By default `--from` is the latest
version and `--to` is `working`. A bundle with no version diffs from empty, so everything is
added. A `--from` version with no tag is an error (`DIFF_VERSION_NOT_FOUND`).

### 8. Drafting from source documents

When the user provides source documents, the agent MAY draft SCD items from them. Each item
drafted from a document MUST carry a `derived_from` entry naming the document, and SHOULD carry
a locator. The agent MUST NOT copy standard text into SCDs; citations remain `std:`
references (see [citations.md](../spec/0.6/citations.md)). Source documents stay in the
user's workspace; the interface MUST NOT send them anywhere other than the user's own AI
client.

### 9. Domain repositories

Every Domain MUST have its own git repository, called a *Domain repository*. A Domain
repository holds exactly one Domain workspace, under `domain/`, and zero or more Project
workspaces, each under `projects/<name>/`. A Project belongs to the Domain whose repository it
is in; no field records the relationship, because the layout does. Application repositories
that consume the context are separate and MUST NOT be used to author it.

The Domain and Project bundles keep the 0.6.0 model: a Project bundle does not import the
Domain bundle, each is validated, versioned, and compiled on its own, and rule ids are already
namespaced by bundle so their artifacts cannot collide. They sit in separate directories
because their artifacts are placed separately (section 10), not because either depends on the
other.

The agent interface MUST create the Domain repository (or confirm an existing one) before
writing any workspace content, and MUST NOT write outside it.

Domain repository names SHOULD follow `<domain-name>-context` (for example
`medtech-cdmo-context`, `jdoe-context`).

Layout, building on what `scs new` scaffolds in 0.6.0:

```
medtech-cdmo-context/
├── AGENTS.md                      # agent instructions: purpose and boundaries of this repo
├── CLAUDE.md                      # pointer to AGENTS.md
├── .gitignore                     # ignores sources/ by default
├── .gitattributes                 # * text eol=lf
├── .github/workflows/scs-validate.yml
├── domain/
│   ├── .scs/config                # workspace marker (bundle_type, name, ontology, scs_version, tools_version)
│   ├── intake.yaml                # intake record (section 4)
│   ├── ontology/
│   │   └── domain-manifest.yaml   # ontology manifest (0.6: domain/domain-manifest.yaml)
│   ├── bundles/
│   │   ├── domain-bundle.yaml
│   │   └── concepts/
│   ├── context/
│   │   └── project/               # SCDs
│   ├── sources/                   # optional source documents (section 8)
│   └── dist/                      # compiled artifacts
└── projects/
    └── infusion-pump-fw/
        ├── .scs/config
        ├── intake.yaml
        ├── ontology/
        ├── bundles/
        │   ├── project-bundle.yaml
        │   └── concepts/
        ├── context/
        │   └── project/
        ├── sources/
        └── dist/
```

A workspace's name is `domain` for the Domain workspace and the directory name under
`projects/` for a Project; the `name` in its `.scs/config` MUST match. The ontology manifest
moves from `domain/domain-manifest.yaml` to `ontology/domain-manifest.yaml`, since a Domain
workspace already lives in `domain/`; the 0.6 location is still read, with an info diagnostic.
`scs new domain` initializes git and makes an initial commit.

**Templates.** The scaffold chooses concept bundles and SCD templates by two things only: the
ontology (`sdlc`, `cdmo`, `mca`, `personal`, and others added later) and the workspace kind
(Domain or Project). Each ontology provides one set for a Domain workspace and one for a Project
workspace; there are no further variants by user type. The scaffold cannot know which of them a
user needs, so it supplies the set and the agent removes, with the user, what does not apply,
through engine commands (section 1). The `personal` ontology supplies only its fixed concept,
boundaries; the agent creates the user's other concepts with the user.

**Source documents.** The scaffold's `.gitignore` ignores `sources/`, so source documents stay
local (section 8) unless the user chooses to track them. `derived_from` still names the
document. The compiler never reads `sources/`, so ignoring it does not affect rebuilding a
version.

**Reserved directories.** `plan/`, `test-plan/`, and `qa/` are reserved in every workspace
for use by a later release. 0.7 defines no content for them, the scaffold does not create
them, and the validator and compiler do not read them.

**Agent instructions.** The scaffold MUST generate an agent instructions file stating that the
repository manages SCS context for one named Domain and its Projects, that work in it is
limited to creating, maintaining, validating, versioning, and compiling that context, and that
application work belongs elsewhere. When the user is working on one workspace, the agent
SHOULD confine its changes to that workspace. `AGENTS.md` is the default; the scaffold SHOULD
also generate a client-specific file (for example `CLAUDE.md`) that points to it, for clients
that read only their own file.

**Versioning.** Each bundle is versioned on its own. Bundle versions MUST be recorded as git
tags in the Domain repository. Because several workspaces, and their concept bundles, are
versioned in one repository, tags MUST be qualified by workspace and bundle name:
`<workspace>/<bundle-name>-v<version>`, where `<workspace>` is `domain` or the Project name
(for example `domain/company-v1.0.0`, `infusion-pump-fw/design-controls-v1.0.0`). Version
manifests MUST be named `<bundle-name>-v<version>-MANIFEST.yaml`, and snapshots
`<bundle-name>-v<version>.yaml`, in the bundle's directory; the location supplies the
workspace, so no two bundles share a manifest file (ISS-043). The bundle names `plan`,
`test-plan`, and `qa` are reserved for a later release, so its tags cannot collide with a
bundle's.

`scs bundle version`:

- commits everything under the workspace directory except `dist/`, including deletions, and
  nothing outside it, then creates an annotated tag on that commit. Edits made earlier in the
  same workspace are committed with the version; the dry run lists them. Because the tagged
  commit holds every compiler input, any version can be rebuilt from its tag;
- refuses if a file the digest or the compiler reads is ignored or untracked
  (`VERSION_INPUT_UNTRACKED`), or if git is not available (`GIT_REQUIRED`). There is no
  `--no-git` and no `--force`; an existing version is never rewritten (`VERSION_EXISTS`);
- refuses if an import is unpinned or `DRAFT` (`VERSION_IMPORT_NOT_PINNED`);
- records the approver as the commit's author. The committer and the tagger are the fixed
  identity `scs-tools <noreply@scs.invalid>`. Neither identity is read from the environment,
  and the engine overrides the user's commit and tag signing, hooks, and line-ending settings
  for its own commit and tag;
- on failure at any step, undoes what that run wrote, leaving the working tree, index, and refs
  as they were.

The working bundle file stays `DRAFT` after versioning; the released copy is the snapshot.

**Compiled output.** `scs compile` SHOULD write to the workspace's `dist/` directory, named
`<bundle-name>-<version>.yaml`. `scs compile BUNDLE --version V` compiles the released version
V; without `--version`, it compiles the working `DRAFT` and requires `--allow-draft`. Whether
`dist/` is committed is the user's choice; every artifact can be rebuilt from its tag.

**CI.** The scaffold SHOULD generate a CI workflow that validates the Domain workspace and every
Project workspace with `scs-validate --strict` on every push. Validation reads tags (section
11), so the workflow MUST fetch full history and tags (for GitHub Actions, `fetch-depth: 0`).
GitHub Actions is the default; the workflow is a convenience, not a requirement of
conformance.

### 10. Placement

SCS's output ends at a validated, versioned bundle and its compiled artifact. The versioned
bundle is the source of truth; the compiled artifact, and anything a user derives from it for a
particular vendor or runtime, is a rendering. Placing or transforming renderings is the user's
decision, and SCS tools MUST NOT do it.
Where a Domain artifact goes depends on how the user works: an organization may place it at
an organization-wide level (for example, organization-level context in Claude Enterprise),
while an individual with several Domains places each where it covers only that Domain's work.

The SCS documentation SHOULD include a **placement guide**: for common AI services, where
Domain and Project artifacts are typically placed and in what form. The guide is
non-normative, is maintained outside the spec text, and MUST be checked against each service's
current documentation when written or updated, since these conventions change. Skills SHOULD
use it to advise the user after compiling.

Every compiled artifact already identifies its bundle and version, and carries a
self-identification rule (see [runtime-artifact.md](../spec/0.6/runtime-artifact.md) §3), so
a user or an agent can always tell which version is in place. With section 11 it also carries
the source digest, so a rendering can be checked against the exact content it came from. The
placement guide SHOULD recommend that renderings keep the bundle id, version, and digest.

### 11. Verifiable immutability

A versioned bundle MUST be verifiably unchanged after it is versioned.

**The tag is the record.** A version of a bundle is its tag,
`<workspace>/<bundle-name>-v<version>`, on a commit that holds the whole workspace except
`dist/` (section 9). The version manifest at that tag records the approver, the validation
result, and the `content_digest`. Verification reads the tagged content and the tagged
manifest, never only the working tree, so editing a manifest in place cannot vouch for changed
content.

**Content digest.** `scs bundle version` MUST compute a `content_digest` over the bundle's
full resolved content and record it in the version manifest:

- the bundle manifest as versioned (with its released `version`);
- every SCD the bundle includes;
- for each pinned import, that bundle's own `content_digest`.

Each file is parsed and serialized canonically before hashing: JSON with sorted keys, no
insignificant whitespace, and non-ASCII characters unescaped, as
[runtime-artifact.md](../spec/0.6/runtime-artifact.md) §3.6 does for artifacts. Inputs are
hashed in a fixed order (the manifest, then SCDs by id, then imports by id). The digest is
SHA-256, written `sha256:<hex>`. Because files are parsed first, edits to comments or
formatting do not change the digest; edits to content do.

**Verification.** Run at the root of a Domain repository, `scs-validate` MUST make three
checks, each an error in every mode:

1. **Every version tag.** The digest recomputed from the tagged content equals the tagged
   manifest's `content_digest`, and each pinned import's manifest at that commit equals the
   import's own tagged manifest. A workspace-qualified tag with no manifest at the tag
   (`VERSION_MANIFEST_MISSING`), and a manifest carrying `content_digest` with no qualified tag
   (`VERSION_TAG_MISSING`), are errors.
2. **Working copies of versions in use.** For each version pinned by a working bundle, and the
   latest version of each bundle whose working file exists, the working manifest and snapshot
   equal their tagged copies, compared by git blob id (`MANIFEST_ALTERED`). Versions of a
   removed bundle are history, still covered by check 1.
3. **Drift.** Each pinned import of a working bundle matches its tagged content
   (`CONTENT_DIGEST_MISMATCH`). The diagnostic SHOULD name the files whose content changed and
   the bundles to version again.

Because all three read tags, repository mode on a shallow clone is an error
(`GIT_HISTORY_INCOMPLETE`). `scs-validate --verify-version <tag>` checks one version on
request.

- `scs compile` MUST run these checks for the tree it compiles, including when the root is
  `DRAFT`, and MUST refuse on a failure. There is no override; a changed bundle needs a new
  version. `scs compile --version V` compiles V's tagged snapshot.
- `scs bundle version` MUST record `validation_passed` and `approval_status` from what actually
  happened. `--no-validate` skips content validation (schemas and rules) only; the integrity
  checks above always run, and the manifest records `validation_passed: false`.

**Boundary.** Git allows anyone with write access to delete and recreate a tag. These checks
detect change that was not recorded as a new version; they do not defend against someone who
rewrites both the content and the tag. Signed tags are out of scope for 0.7. Protecting
version tags on the shared remote (for example with tag protection rules) is the adopter's
responsibility.

**In the artifact.** The compiled artifact gains a `source_digest` field holding the root
bundle's `content_digest`. It is derived from content, so it does not conflict with the
stability rules in `runtime-artifact.md` §3.5. A `DRAFT` compile has no `content_digest` and
omits the field; its `DRAFT+<digest>` version already distinguishes drafts.

Compiling at a checkout of a version's tag, with the `tools_version` its manifest records,
gives an artifact with the same `source_digest` and the same content as the original, apart
from the fields `runtime-artifact.md` §3.5 declares variable.

### 12. Advisory review

The validator checks structure, completeness, and conflicts. It cannot judge whether a rule
is sound. The agent interface adds an advisory review: while drafting and before versioning,
the agent SHOULD review the workspace for problems a careful reviewer would raise, in these
categories:

| `kind` | Examples |
|---|---|
| `framework-conflict` | A rule that contradicts a framework the workspace cites |
| `missing-protection` | No prohibition or directive covering something the intake says is present (PHI, payment data, safety-class C software) |
| `technical-risk` | A rule that weakens security, auditability, or traceability (disabling logging, sharing credentials) |
| `ethical-risk` | A rule that could cause harm, deception, or unfair treatment of people |
| `layer-conflict` | A rule that contradicts a rule in another layer of the stack the user loads it with (section 13) |

Rules for findings:

- The review is advisory. The agent MUST NOT block an operation because of a finding, and MUST
  NOT change content to resolve a finding without the user's confirmation.
- Each finding MUST be presented in plain language, naming the SCD item it concerns and, where
  relevant, the citation it rests on.
- The user's decision MUST be recorded in the workspace's `intake.yaml` under
  `review_findings`, with one of `changed`, `kept` (with a rationale), or `deferred`, plus who
  decided and when.
- Findings are not compiled into the runtime artifact. They belong to the record of how the
  context was made, not to the context.
- A finding left `deferred` SHOULD be raised again before the next version.

In this RFC the review is driven by the agent's own judgment, guided by the skills. RFC 0003
proposes *review profiles*: declarative, citable checks per framework (for example CHAI, HIPAA,
ISO 13485) that make the review consistent across clients and auditable in its own right.

### 13. Layered context

Domain and Project bundles are independent: neither imports the other, and each compiles to
its own artifact (section 9). AI clients, however, often load several artifacts at once, in
layers. A developer with several Domains might place one artifact where every session reads it,
an area's Domain artifact where sessions in that area read it, and a Project artifact in the
project's repository; the client loads all three, outermost first. Each artifact validates on
its own, but nothing in SCS so far shows what a session receives when they are combined, or
whether they disagree.

A **stack** is an ordered list of compiled artifacts, outermost layer first. SCS does not know
where artifacts are placed (section 10), so the user or the agent supplies the stack.

`scs stack ARTIFACT...` reads the artifacts in the order given and reports:

- each layer: its bundle `id`, `type`, `version`, and `source_digest` when present;
- the combined context: every rule and fact of every layer, in stack order, each with its
  identifier and the layer it came from;
- the findings of the checks below, as diagnostics.

The command:

- MUST only read. It MUST NOT write, compile, or place anything, and it MAY read artifacts from
  any path, since the layers of a stack usually come from different Domain repositories.
- MUST accept only runtime artifacts as defined in
  [runtime-artifact.md](../spec/0.6/runtime-artifact.md); any other input is an error
  (`STACK_ARTIFACT_INVALID`).
- MUST NOT merge, reorder, or drop rules. SCS defines no precedence between layers: a rule in an
  inner layer does not override one in an outer layer. How a client weighs layers is the
  client's behaviour, outside SCS.
- MUST support machine mode (section 3). Its `changes` is always empty.

The engine checks a stack for what can be decided exactly:

| Code | Severity | Condition |
|---|---|---|
| `STACK_BUNDLE_REPEATED` | error | The same bundle `id` appears in two layers, for example two versions of one bundle |
| `STACK_PROHIBITION_DIRECTED` | warning | A directive in one layer contains, ignoring case, the `subject` of a prohibition in another layer (taken from the rule text `Prohibited: <subject>.`, runtime-artifact §2.3) |
| `STACK_RULE_DUPLICATE` | info | Two layers carry a rule or fact with identical text, for example the meta bundle's rules in two Domain artifacts |
| `STACK_LAYER_DRAFT` | info | A layer is a DRAFT artifact (`version` of the form `DRAFT+<digest>`) |

`STACK_PROHIBITION_DIRECTED` is a textual match: it finds candidates and can miss
contradictions phrased differently. Whether two rules actually contradict is a judgment, which
the agent makes in the advisory review (section 12) under the kind `layer-conflict`, with the
same rules as any other finding. The user's decision is recorded in the `intake.yaml` of the
workspace the user is working in.

Whether a client actually loads the layers of a stack, and in what order, is the client's
behaviour. SCS does not test it; the placement guide (section 10) SHOULD describe how each
service loads layered context.

### Schema Changes

- New `schema/intake/intake-schema.json` for the intake record (section 4).
- New `schema/manifest/version-manifest-schema.json` for version manifests.
  `approval.approved_by` MUST be a person identifier, `Name <email>`; the schema rejects empty
  and `role:` values.
- New `schema/cli/envelope-schema.json` for the machine-mode envelope (section 3), and the
  diagnostic code registry `schema/diagnostics/codes.yaml`.
- Optional `derived_from` array on items in `content.prohibitions`, `content.directives`, and
  `content.facts`. Each entry has exactly one of `intake` (an answer id) or `source` (a
  document id), plus an optional `locator` string.

```yaml
derived_from:
  type: array
  items:
    type: object
    oneOf:
      - required: [intake]
      - required: [source]
    properties:
      intake: {type: string}
      source: {type: string}
      locator: {type: string}
    additionalProperties: false
```

- New `content_digest` field (`^sha256:[0-9a-f]{64}$`) in version manifests written by 0.7
  tools (section 11), with `content_inputs` listing the files and imports it covers, and
  `tools_version`. A manifest is recognized as 0.7 by its workspace-qualified tag, not by a
  field value: such a manifest MUST carry `content_digest` and `tools_version`. The schema
  keeps both optional so pre-0.7 manifests still validate; the requirement is checked with the
  tags (section 11).
- New `source_digest` field in the runtime artifact schema (`schema/runtime/`), present for
  versioned bundles and absent for `DRAFT` compiles (section 11). Added in `runtime-artifact.md`
  §3.1. Artifacts compiled by 0.7 tools carry `scs_runtime: "0.7"`; the §3.5 stability rules
  apply to them from 0.7 on.

No bundle manifest fields change. The Domain repository layout (section 9) is a convention the
tools create and check, not a schema.

### Validation Rules

- `intake.yaml`, when present, MUST validate against `intake-schema.json`.
- A `derived_from.intake` id MUST resolve to an `answers[].id` in the workspace's `intake.yaml`;
  a `derived_from.source` id MUST resolve to a `source_documents[].id`. An unresolved id is a
  warning (`DERIVED_FROM_UNRESOLVED`), so it fails under `--strict` with exit code 2.
- A version manifest MUST have an `approval.approved_by` that is a person identifier
  (`Name <email>`).
- `scs compile` MUST NOT emit `derived_from`.
- The three checks in section 11 MUST pass; a failure is an error in every mode.
- A version without a workspace-qualified tag (made before 0.7) is history: it is neither
  verified nor reported. Strict CI is green once each bundle has a 0.7 version (Migration
  Guide).
- A workspace's `.scs/config` `name` MUST match its workspace name (`CONFIG_NAME_MISMATCH`).
- Run at the root of a Domain repository, the validator SHOULD validate the Domain workspace
  and every Project workspace, and report a Domain repository with no workspace whose
  `.scs/config` `bundle_type` is `domain`, or with more than one, as an error.
- The validator MUST NOT report a workspace's reserved directories (`plan/`, `test-plan/`,
  `qa/`) as errors or warnings in any mode, and MUST NOT validate their content.
- A bundle named `plan`, `test-plan`, or `qa` is an error.
- An SCD with no `prohibitions`, `directives`, or `facts` contributes nothing to a compiled
  artifact. The validator MUST report it as `SCD_EMPTY` (info), so a fresh scaffold still passes
  `--strict`, and `scs bundle version --dry-run` MUST list the bundle's empty SCDs, so they are
  removed or kept knowingly before a release. The 0.6 stub detection (`COMPLETENESS_STUB_SCD`)
  is removed.
- `scs stack` MUST report the checks of section 13 with the codes and severities given there.
  Under `--strict`, its warnings give exit code 2.

---

## Drawbacks

- **More surface to maintain.** Skills, an MCP server, a JSON mode, and a diff command are
  each something to keep in step with the spec. The layering limits this, since only the engine
  carries behavior, but it does not eliminate it.
- **Agent quality varies.** Two clients running the same skills may run noticeably different
  intakes. The required intake fields and the deterministic engine bound the variation; they
  do not remove it.
- **It can produce plausible but wrong context.** An agent can draft a well-formed
  prohibition that does not reflect the organization's practice. Validation catches format
  errors, not judgment errors. Item-level `derived_from` and human confirmation are the
  mitigations.
- **Less incentive to learn the spec.** As fewer people read the spec, its quality, along with
  the meta bundle, ontologies, and validator rules, becomes what keeps an agent-driven process
  honest. That raises the bar on those artifacts.
- **Skill portability is not guaranteed.** The Agent Skills format is an open standard with
  broad reported adoption, but client behavior (script execution, network access, package
  installation) varies and changes.
- **Advisory review can be wrong or tiresome.** An agent may raise findings that are not real
  problems, or apply its own preferences. Keeping the review advisory, limiting it to four
  categories, and recording the user's decision keeps the user in charge; review profiles
  (RFC 0003) would make it more consistent.
- **An agent in the repo can see every Project.** One repository per Domain means an agent
  working on one Project has the others in view. The agent instructions and the intake scope
  its work to the named workspace; nothing in the layout enforces that.
- **Placement stays a manual step.** Users copy compiled artifacts into place themselves. The
  placement guide and the agent's advice reduce the guesswork, but a user can still place an
  artifact wrongly or leave an old version in place.

---

## Alternatives

### Alternative 1: MCP server only

Exposes the operations cleanly and works across clients. But the intake, drafting guidance,
and confirmation behavior would have to live in tool descriptions or MCP prompts, and client
support for prompts is uneven. The result would validate well and guide poorly. Kept as a
secondary layer.

### Alternative 2: Skills only

Covers most clients and carries the guidance well, but excludes clients without skill support
and organizations that disable code execution in their AI tools, a meaningful share of
regulated buyers. Kept as the primary layer, with MCP for the rest.

### Alternative 3: A hosted service

A hosted agent or remote MCP server would remove installation entirely. It would also move
SCS from a local, single-user format into hosting and multi-user operation, which is outside
SCS's scope (section 1).

### Alternative 4: Update the existing plugins

`scs-vibe` and `scs-team` could be brought forward to 0.6. They are Claude Code plugins,
though, and would remain client-specific. Their useful content (intake patterns, the
considerations approach in `scs-vibe`) should be carried into the new skills.

### Alternative 5: One repository per workspace

A separate repository for the Domain and for each Project would isolate them completely. The
only reason to separate Domain and Project context is that their artifacts are placed
differently, and directories already serve that. Separate repositories would multiply repos
(eleven for an organization with ten Projects), require each Project to record which Domain it
belongs to, and add a cross-repo lookup to validation. Rejected in favor of one repository per
Domain.

### Alternative 6: Projects declare or import their Domain

A Project bundle could name its Domain in a pinned field, or import it. A field duplicates
what the repository layout already says; an import reverses the 0.6.0 decision to keep the
trees independent and couples every Project's versioning to every Domain release. Rejected.

### Alternative 7: Delivery tooling in SCS

SCS could ship a `deliver` command with adapters that write compiled artifacts into each AI
service's expected location. That would extend SCS past the versioned bundle into placement,
which differs between organizations and individuals, and into conventions that change with
each service. Rejected in favor of a placement guide, so SCS ends at the versioned bundle.

### Do Nothing

SCS stays usable mainly by experts. Users keep improvising with general-purpose assistants
and the spec, with no shared intake, no confirmation rules, no defined home for context, and
tooling that silently records approvers and fails quietly on lifecycle operations. Workspaces
produced that way will vary in quality, and the variation will reflect on the standard.

---

## Unresolved Questions

1. **Where the skills live.** *Resolved 2026-10-25:* `skills/` in this repository, versioned
   with the spec.
2. **What happens to `scs-vibe` and `scs-team`.** *Resolved 2026-10-25:* deprecated in 0.7,
   removed in 0.8.
3. **Installation inside chat clients.** Whether code-execution sandboxes in hosted chat
   clients can reliably install `scs-tools` from PyPI needs testing per client. Fallback order:
   PyPI, then a GitHub tag, then a wheel bundled with the skill. The choice per client is
   settled by testing in Claude.ai, Claude Code, Cursor, Codex, and GitHub Copilot before
   release. Open.
4. **Personal data in the intake record.** *Resolved 2026-10-25:* role-only attribution
   (`role:<name>`) is allowed in `intake.yaml` only; approvers in version manifests are always
   people (section 4).
5. **Workspace-level versioning.** *Resolved 2026-10-25:* per bundle, with workspace- and
   name-qualified tags and manifests (section 9). Versioning several bundles is a cascade
   covered by one confirmation (section 6).
6. **Provenance granularity.** *Resolved 2026-10-25:* item-level `derived_from` only.
7. **Intake for existing workspaces.** *Resolved 2026-10-25:* the intake record stays optional;
   the intake skill offers to reconstruct one by asking.
8. **Name of the agent instructions file.** *Resolved 2026-10-25:* `AGENTS.md` plus a
   `CLAUDE.md` that points to it.
9. **Creating a concept with no template.** The `personal` ontology's concepts are defined with
   the user, so the engine needs a command that creates a concept bundle, its first SCD, and its
   ontology manifest entry. Open (plan D-68).
10. **Removing what the scaffold supplied.** When removing an SCD leaves its concept bundle
    empty, the same command should remove the concept bundle, the root bundle's import, and the
    manifest entry. Open (plan D-69).
11. **Reporting provenance to correct.** Which check reports a `created_by` that is not a person
    identifier (section 5) is open (plan D-71). Unused SCDs are resolved (Validation Rules; plan
    D-70).
12. **Projects under the `personal` ontology.** Rec.: the same fixed concept, boundaries, and
    nothing else. Open (plan D-72).
13. **The ontology manifest's naming.** It still uses "domain" (`domain-manifest.yaml`, the
    `domain:` key), while "Domain" now names only the global tier. Kept for 0.7; a rename needs
    its own RFC (plan D-73).

---

## Future Possibilities

- **Coverage questions.** With the ontology's framework mappings (RFC 0001) and
  `derived_from`, an agent could answer "which ISO 13485 clauses does our context not yet
  address?"
- **Re-intake on change.** When a certification or product line changes, re-run the affected
  intake questions and propose the resulting SCD changes as a diff.
- **Intake profiles per ontology.** Ontologies could declare their own profile questions, so
  the cdmo intake asks about DHF and design controls without hardcoding that in the skills.
- **Conformance tests for agent interfaces.** A scripted conversation suite that any client
  or skill set can run to show it meets section 6.

---

## Appendix

### Implementation Notes

Proposed order. Each step is usable on its own.

1. **Harden the lifecycle.** Fix ISS-042, ISS-043 (with workspace- and name-qualified tags and
   manifests), and ISS-044. Remove the silent `git config` approver default, `--force`, and
   `--no-git` from `scs bundle version`. Fix ISS-045: `content_digest` in version manifests,
   whole-workspace version commits and annotated tags (section 9), the three tag-based checks
   in `scs-validate` and `scs compile` (section 11), `compile --version`, `source_digest` in
   the artifact, and truthful `validation_passed`.
2. **Domain repositories.** `scs new domain` creates the repository with `domain/`,
   `projects/`, `AGENTS.md`, and the CI workflow; `scs new project` adds a workspace under
   `projects/` of an existing Domain repository; templates chosen by ontology and workspace kind
   only, including the `personal` ontology (boundaries only); repository-level validation
   that tolerates the reserved plan directories and rejects the reserved bundle names; compile
   output to `dist/`.
3. **Machine mode.** `--json` and `--dry-run` across `new`, `add`, `scd`, `bundle`, `intake`,
   `validate`, and `compile`; the result envelope and its schema; the diagnostic code registry;
   no prompts in machine mode.
4. **Intake schema and `derived_from`.** `intake-schema.json`, `scs intake`, the
   `derived_from` field, validator rules, and `scripts/sync_schemas.py`.
5. **Skills.** Intake, draft, review, validate, version, compile, and explain, including
   placement advice from the guide.
6. **`scs bundle diff`.**
7. **Placement guide.** Docs for the most widely used AI services, checked against each
   service's current documentation.
8. **MCP server.** Local stdio adapter over the engine, once there is demand.
9. **Layered context.** `scs stack` with its exact checks (section 13), the `layer-conflict`
   review kind in the review skill, and load-order notes in the placement guide.

**Acceptance test:** onboard Omarchy entirely through a chat client using the skills, with no
direct CLI use and no reading of the spec: one Domain repository holding the Domain and two
Projects, all validated, versioned, and compiled, with the agent advising where each artifact
belongs. Record every point of friction.

### Migration Guide

None required for SCDs or bundles; they remain valid. `derived_from` and `intake.yaml` are
optional.

- **Layout.** Workspaces created by 0.6.0 tools move into a Domain repository: the Domain
  workspace under `domain/`, each Project under `projects/<name>/`. A Project with no Domain
  needs one; an individual developer creates a personal Domain
  (`scs new domain NAME --ontology personal`). Git history can be carried over with `git filter-repo`
  or a similar tool, or the move can start a fresh history.
- **Tags.** Existing tags of the form `v<version>` stay in history; new versions use
  `<workspace>/<bundle-name>-v<version>`.
- **`scs bundle version`** no longer takes the approver from `git config`; pass
  `--approved-by` explicitly. `--force` and `--no-git` are removed.
- **Ontology manifest.** Move `domain/domain-manifest.yaml` to `ontology/domain-manifest.yaml`.
  The old location is still read, with an info diagnostic.
- **Versions made before 0.7** have no workspace-qualified tag and no `content_digest`. They
  are history: not verified and not reported. After moving into the layout, version each
  bundle once with 0.7 tools, at a new version number, bottom-up; strict CI is green once
  every bundle has a 0.7 version. An existing version is not rewritten.

### Related RFCs

- RFC 0001: Domain Ontology. The intake proposes an ontology, and ontology framework mappings
  enable future coverage questions.
- RFC 0003: Review Profiles (stub). Declarative, citable checks that structure the advisory
  review in section 12.
- Related issues: ISS-014, ISS-027, ISS-042, ISS-043, ISS-044, ISS-045.
- Related spec: [bundle-format.md](../spec/0.6/bundle-format.md) (Domain and Project
  independence; §7.3 immutability), [runtime-artifact.md](../spec/0.6/runtime-artifact.md).
