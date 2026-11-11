# Understanding SCDs

**Version**: 0.7

A Structured Context Document (SCD) is one YAML file about one topic: the prohibitions,
directives, and facts an AI assistant should follow and know about it. This page covers what
an SCD holds and how to write content an assistant can act on. The normative definitions are
in [Core Model](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/core-model.md) §4 and [Runtime Artifact](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/runtime-artifact.md) §2.

---

## An SCD

```yaml
id: scd:project:document-control
type: project
title: "Document Control"
version: "DRAFT"
description: "How design changes, design reviews, and controlled documents are handled"
concept: concept:qms-records
content:
  summary: "Design changes and reviews follow the QMS procedures."
  prohibitions:
    - id: DOC-P01
      kind: practice
      subject: "marking a design change approved without a recorded human approval"
  directives:
    - id: DOC-001
      directive: "Design changes require documented review and approval before implementation."
      cites:
        - std:iso-13485:2016#7.3.9
      derived_from:
        - source: qm-manual
          locator: "section 7.3.9"
  facts:
    - id: DOC-F01
      fact: "Controlled documents are kept in the eQMS, not in shared drives or repositories."
relationships: []
provenance:
  created_by: "Jane Doe <jane@acme-medical.com>"
  created_at: "2026-10-01T09:00:00Z"
  rationale: "Design control rules from the quality manual"
```

- `id` is `scd:<tier>:<name>`. Organizations write `project`-tier SCDs; the `meta` tier is
  published with the spec. (The `standards` tier is deprecated; standards are cited.)
- `concept` names the Domain Ontology concept the SCD belongs to. Its concept bundle lists it.
- `version` stays `DRAFT` in the working copy. Versions belong to bundles, not to SCDs.
- `provenance.created_by` is a real person, `Name <email>`. Placeholders block a release.

**Only `prohibitions`, `directives`, and `facts` are compiled.** `summary` and any other
content are for the people who review the SCD. An SCD with none of the three contributes
nothing; fill it or retire it before a release.

---

## The three kinds

### Prohibitions

Binary: something the assistant itself must never do, use, or recommend.

| Field | Required | Compiled | Notes |
|---|---|---|---|
| `id` | yes | yes | Unique within the SCD |
| `kind` | yes | no | `tool` (a product, service, library, or model) or `practice` (an action) |
| `subject` | yes | yes | A noun phrase, compiled as `Prohibited: <subject>.` |
| `instead` | no | yes | The approved alternative, compiled as `Use instead: <instead>.` |
| `reason` | no | no | Why, for reviewers |
| `cites` | no | yes | Citations |

The validator rejects a subject with a condition or a hedge in it: *unless*, *except*, *if*,
*when*, *where possible*, *avoid*, *prefer*, *should*. If something is allowed in some cases,
narrow the subject until what remains is always forbidden, or make it a directive.

A rule only a person can break (which account they sign in with, whether they share
credentials, which tools they install) is not the assistant's to obey. Write it as a directive
that says when to remind the user. A Project cannot lift a Domain prohibition.

### Directives

One instruction: what the assistant does when it meets the case. `directive` is required;
`cites` and `derived_from` are optional.

### Facts

One short, checkable statement the assistant needs to answer or act correctly. A rule phrased
as a fact is a directive. A fact states what is true now; a planned process says so.

Ids are unique within an SCD across all three lists (`DOC-001`, `DOC-P01`, `DOC-F01`).

---

## Writing content that works

Everything compiled is read by an assistant in the middle of someone's task. For each item,
ask: could the assistant do this, or know this, while helping someone?

- **Say what the assistant does.** "Check content before it is sent outside the company" is a
  control someone else runs. "When drafting content for an external recipient, leave out
  customer names and internal project codes" is something the assistant can do.
- **Leave administration out.** Which model version is approved, who grants access, how long
  records are kept: these inform people. Put them in `summary` if they should stay in the SCD.
- **One statement per item.** Two rules in one directive are two directives.
- **Don't repeat across sections.** A shared rule (who decides, how to report) belongs once,
  in the section that owns it.
- **Keep what prevents over-caution.** A fact saying what AI may help with keeps the assistant
  useful.
- **Include a rule against invented content** in regulated work: presenting invented
  citations, clauses, requirements, data, or numbers as fact.

---

## Citations and sources

**Citations** name a standard or regulation, never its text:
`std:<standard>[:<edition>][#<clause>]`.

- `std:` is the only prefix, for laws and regulations too: `std:21-cfr-820`,
  `std:eu-ai-act-2024-1689`, `std:hipaa`.
- Lowercase, with hyphens: IEC 62304:2006+A1:2015 is `std:iec-62304:2006-a1`.

See [Citations](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/citations.md).

**`derived_from`** records where an item came from: `intake: <answer id>` from the intake
record, or `source: <document id>` (with an optional `locator`) from its source documents.
It is never compiled. Reviewers use it to check each rule against its source.

---

## Relationships

`relationships` are typed edges to other SCDs (`depends-on`, `constrains`, `refines`,
`conflicts-with`, and others), or to a citation for `satisfies`, for tools that traverse
context as a graph. They are optional and are not compiled. See
[Core Model](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/core-model.md) §6.

---

## Creating and changing SCDs

- The ontology's templates supply most SCDs; each says what goes in it. Fill the ones that
  apply and retire the rest: `scs bundle remove-scd <id> ...`.
- A topic the templates lack: `scs add bundle <concept> --new` creates a concept bundle with
  a first SCD; `scs bundle add-scd` lists another SCD in an existing bundle.
- `scs scd write <path> --from-file <file>` validates an SCD before writing it; an invalid
  SCD is not written.
- A released version keeps the SCD as it was at its tag. Editing it changes the working copy
  only, until the next release.

The Agent Skills do all of this with you; see the [Quick Start](quick-start-guide.md).
