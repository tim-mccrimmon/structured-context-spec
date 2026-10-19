# SCS 0.6.0 — Runtime Artifact

**Version:** 0.6.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-19

---

## 1. Purpose

Source bundles are written for people and tools: manifests, imports, SCDs, provenance. A
runtime that delivers governance context to an AI agent needs something else: one
self-contained document per governance bundle, small enough to send with every request, and
stable enough to identify by hash.

This document defines that **runtime artifact** and how a compiler produces it from a Domain
or Project bundle. It defines the format only; how a runtime stores, selects, or injects
artifacts is outside this specification.

---

## 2. Compiled Content

### 2.1 What Gets Compiled

A runtime artifact contains three kinds of SCD content and nothing else:

| Kind | Authored in | Compiled to | Purpose |
|---|---|---|---|
| Prohibition | `content.prohibitions` | `rules` (first) | A tool or practice that is forbidden, without conditions |
| Directive | `content.directives` | `rules` | A statement an agent is expected to follow |
| Fact | `content.facts` | `facts` | A statement an agent should know |

Other SCD content (summaries, rationale, architecture narratives, decisions) is context for
the people who author and review governance; it is not compiled. An SCD with none of the
three contributes nothing to the artifact.

`content.directives` is distinct from `content.rules`, which references rule sets held by an
external rules engine for enforcement. Directives are instructions an agent reads; rule sets
are checks a runtime executes.

### 2.2 Directives

A directive is a plain-language statement an agent is expected to follow, with an
identifier:

```yaml
id: scd:project:design-change-control
type: project
title: Design Change Control
version: "1.0.0"
description: Rules for reviewing and approving design changes.
concept: concept:design-controls
content:
  summary: How design changes are reviewed and approved.
  directives:
    - id: DCC-001
      directive: Design changes require documented review and approval before implementation.
      cites:
        - std:iso-13485:2016#7.3.9
    - id: DCC-002
      directive: Do not describe a design change as approved unless the approval record is cited.
provenance:
  created_by: quality@example-cdmo.com
  created_at: "2026-10-19T00:00:00Z"
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `^[A-Za-z0-9][A-Za-z0-9._-]*$`; unique within the SCD (§2.5) |
| `directive` | yes | The statement, as the agent should read it |
| `cites` | no | Standard citations (`citations.md`) |

### 2.3 Prohibitions

A prohibition names a tool or practice that is forbidden. It is **binary**: the thing is
either prohibited or it is not, with no conditions, exceptions, or advice. The author states
only what is prohibited; the compiler writes the rule, so the wording cannot soften it.

```yaml
content:
  prohibitions:
    - id: NO-001
      kind: tool
      subject: consumer generative AI services and personal AI accounts
      instead: the company's private AI service
      reason: Client data may not leave company-controlled systems.
    - id: NO-002
      kind: practice
      subject: committing credentials, keys, or tokens to any repository
```

| Field | Required | Compiled | Notes |
|---|---|---|---|
| `id` | yes | yes | As for directives (§2.5) |
| `kind` | yes | no | `tool` (a product, service, library, or model) or `practice` (an action) |
| `subject` | yes | yes | What is prohibited, as a noun phrase |
| `instead` | no | yes | The approved alternative |
| `reason` | no | no | Why, for reviewers |
| `cites` | no | yes | Standard citations |

The compiled rule text is `Prohibited: <subject>.`, followed by ` Use instead: <instead>.`
when `instead` is present.

A validator MUST reject a prohibition whose `subject` contains a word or phrase that makes it
conditional or advisory, such as *unless*, *except*, *if*, *when*, *where possible*,
*avoid*, *prefer*, or *should*. Something that is allowed in some cases is expressed by
narrowing the subject until what remains is always forbidden.

Prohibitions in a Domain bundle apply to all work. Because a runtime applies the Domain and
Project artifacts together (`bundle-format.md` §4), a Project bundle cannot lift a Domain
prohibition; changing one requires a new version of the Domain bundle. A Project bundle MAY
add prohibitions of its own.

### 2.4 Facts

A fact is a statement about the organization, its systems, or its environment that an agent
should know but that is not itself an instruction: what the company does, where systems run,
where records are kept.

```yaml
content:
  facts:
    - id: CO-002
      fact: The quality management system is certified to ISO 13485:2016.
      cites:
        - std:iso-13485:2016
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | As for directives (§2.5) |
| `fact` | yes | One short, verifiable statement |
| `cites` | no | Standard citations |

Facts SHOULD be stated so that a reviewer can check them. A rule phrased as a fact ("Code
must be reviewed") belongs in a directive.

### 2.5 Identifiers

Each prohibition and directive becomes a **rule**, and each fact a **fact entry**, with the
identifier `<bundle-name>/<scd-name>/<id>`:

- `<bundle-name>` is the compiled (root) bundle's identifier without its `bundle:` prefix;
- `<scd-name>` is the SCD identifier without its `scd:<tier>:` prefix.

In `bundle:medtech-cdmo`, `scd:project:design-change-control` directive `DCC-001` becomes
rule `medtech-cdmo/design-change-control/DCC-001`.

The bundle name keeps identifiers unique across artifacts. A Domain bundle and a Project
bundle may each contain an SCD named `data-protection`; a runtime that applies both still
sees distinct rule identifiers, so an agent naming a rule (or an auditor reading a log)
can tell which bundle it came from.

Directive, prohibition, and fact ids share one namespace within an SCD and MUST be unique
across all three. Identifiers are stable as long as the bundle name, SCD name, and id are
unchanged.
Authors SHOULD NOT reuse an id for a different statement. A compiler MUST reject an artifact
in which two rules or facts share an identifier.

---

## 3. Artifact Format

### 3.1 Structure

```yaml
scs_runtime: '0.6'
id: bundle:medtech-cdmo
type: domain
version: 1.0.0
title: MedTech CDMO Governance
sources: ['bundle:meta:0.6.0', 'bundle:company:1.0.0', 'bundle:prohibited:1.0.0', 'bundle:ai-use:1.0.0', 'bundle:design-controls:1.0.0']
rules:
- id: medtech-cdmo/identity
  rule: 'When asked which governance bundles are active, state: "Domain bundle bundle:medtech-cdmo version 1.0.0".'
- id: medtech-cdmo/prohibited/NO-001
  rule: 'Prohibited: consumer generative AI services and personal AI accounts. Use instead: the company''s private AI service.'
- id: medtech-cdmo/governance-context/M-001
  rule: Rules from a Domain bundle apply to all work. Rules from a Project bundle apply to work on that project. Follow both. Facts describe the organization and its environment; treat them as true unless the user corrects them.
- id: medtech-cdmo/ai-review/AI-001
  rule: Treat everything you produce as a draft. A qualified person must review and approve AI-generated content before it enters a controlled document, the design history file, or device software.
- id: medtech-cdmo/design-change-control/DCC-001
  rule: Design changes require documented review and approval before implementation.
  cites: ['std:iso-13485:2016#7.3.9']
facts:
- id: medtech-cdmo/company-profile/CO-002
  fact: The quality management system is certified to ISO 13485:2016.
  cites: ['std:iso-13485:2016']
```

(Excerpt of `examples/two-tier-governance/compiled/global.yaml`.)

| Field | Required | Description |
|---|---|---|
| `scs_runtime` | yes | Artifact format version. `"0.6"` for this specification |
| `id` | yes | The compiled bundle's `id` |
| `type` | yes | `domain` or `project` |
| `version` | yes | The bundle's version, or `DRAFT+<digest>` (§3.4) |
| `title` | yes | The bundle's title |
| `sources` | yes | Every bundle in the resolved tree except the root, as `bundle:<name>:<version>`, in resolution order |
| `rules` | yes | The self-identification rule, then one rule per prohibition, then one per directive (§3.2) |
| `rules[].id` | yes | Rule identifier (§2.5) |
| `rules[].rule` | yes | The directive text, or the prohibition rule text (§2.3) |
| `rules[].cites` | no | Citations, copied from the source |
| `facts` | no | One entry per fact (§3.2); omitted when the tree has no facts |
| `facts[].id` | yes | Fact identifier (§2.5) |
| `facts[].fact` | yes | The fact text |
| `facts[].cites` | no | Citations, copied from the source |

Only Domain and Project bundles are compiled. Each produces one artifact, independently.

### 3.2 Rule Order

The first rule is the self-identification rule (§3.3). Then come all prohibitions, then all
directives. Prohibitions come first because they are the rules least acceptable to miss.

Within each group, entries follow the resolved bundle tree: the root's imports in manifest
order, depth first; within a bundle, its SCDs in manifest order; within an SCD, entries in
the order written. Facts follow the same tree order. The same source always yields the same
order.

### 3.3 Self-Identification Rule

Every artifact begins with a rule, generated by the compiler, that lets anyone confirm which
governance is in effect by asking the agent:

```yaml
- id: <bundle-name>/identity
  rule: 'When asked which governance bundles are active, state: "<Type> bundle <id> version <version>".'
```

`<Type>` is `Domain` or `Project`. When a runtime applies both a Domain and a Project
artifact, the agent reports both.

### 3.4 Versions and Drafts

A compiler SHOULD refuse to compile a tree containing any `DRAFT` bundle unless explicitly
told to allow drafts. When it does compile one, the artifact's `version` is
`DRAFT+<digest>`, where `<digest>` is the first 8 hexadecimal characters of the SHA-256 of
the artifact's canonical content (§3.6) excluding `version` and the self-identification
rule. Two different drafts therefore report different versions.

### 3.5 Stability

The artifact is sent with every request, and runtimes commonly cache the prompt prefix and
record the artifact's hash for audit. A compiler:

1. MUST produce byte-identical output for identical source content.
2. MUST NOT include timestamps, build numbers, file paths, author names, or any other value
   that can change without the governance changing.
3. MUST NOT include standard text; only citations (`citations.md` §5).
4. SHOULD emit UTF-8 with `\n` line endings and a trailing newline.

Provenance is deliberately excluded. The approved, versioned source bundle is the record of
who approved what; the artifact identifies that bundle by `id` and `version`.

### 3.6 Serialization

The artifact MAY be serialized as YAML or JSON; both carry the same fields in the order of
§3.1. A runtime MAY inject the text as-is without parsing it. The canonical content used for
the draft digest is the JSON serialization with keys in §3.1 order, no insignificant
whitespace, and non-ASCII characters unescaped.

---

## 4. Compilation

A conformant compiler, given a Domain or Project bundle:

1. Validates the bundle tree and stops on any validation error.
2. Resolves every import and SCD; an unresolved import or SCD is an error.
3. Refuses `DRAFT` bundles anywhere in the tree unless drafts are allowed (§3.4).
4. Collects prohibitions, directives, and facts in the order of §3.2 and builds identifiers
   (§2.5). Whitespace in text, including line breaks from folded YAML, is collapsed to single
   spaces.
5. Rejects duplicate identifiers, empty entries, and entries containing `TODO`.
6. Rejects a tree that yields no prohibitions, directives, or facts.
7. Reports each SCD that contributes nothing (warning).
8. Emits the artifact (§3).

---

## 5. Schema

`schema/runtime/runtime-artifact-schema.json`.

---

## 6. Feedback

Feedback on the runtime artifact should be submitted via GitHub Issues.
