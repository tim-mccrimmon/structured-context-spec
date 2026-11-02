# Drafting

How to turn intent and source documents into SCS content: **prohibitions** (absolute),
**directives** (instructions), and **facts** (statements to know). Only these three are
compiled. The field-level rules are in [authoring.md](authoring.md).

## Start from the templates

The scaffold supplies every template for the ontology. Templates hold placeholders (`TODO`, or
`"[...]"` hints); `scs status` lists the SCDs that still have them (`scds.placeholders`). Go
through the templates with the user: fill the ones that apply, and retire the rest with
`scs bundle remove-scd`. A `personal` Domain gets only boundaries; define the person's other
concepts with them using `scs add bundle <name> --new`.

## Choosing the kind

- A **prohibition** is binary: a `subject` noun phrase, a `kind` (`tool` or `practice`), and
  optionally `instead`. If something is allowed in some cases, narrow the subject until what
  remains is always forbidden.
- A **directive** is one instruction an agent reads.
- A **fact** is one checkable statement. A rule phrased as a fact is a directive.
- A **scope limit**, such as "this Project covers time entry only" or "the first release does
  not include reporting", is a fact or a directive, not a prohibition. A prohibition is for
  something that must never happen; a scope limit changes with the next release.

Ids are unique within an SCD across all three (`DC-001`, `NO-002`). Standards appear only as
citations (`std:iso-13485:2016#7.3.9`); never copy a standard's text into an SCD, even if the
user pastes it.

## Provenance

Give every item a `derived_from` entry:

- from an intake answer: `derived_from: [{intake: q-boundaries-1}]`;
- from a source document: `derived_from: [{source: doc-qm, locator: "section 4.2.5"}]`. An
  item drafted from a document MUST name it, and SHOULD carry a locator.

The ids must exist in the workspace's `intake.yaml`. Record a new answer or document first
with `scs intake set` if needed.

When drafting from a document, keep its meaning, invent nothing that is not there, and flag
ambiguity for the user rather than guessing. When a rule comes from the organization's
document, say so; when it is your suggestion, say that instead, so the user can tell the
organization's rules from yours.

## Engine commands

| Task | Command |
|---|---|
| Write or replace an SCD | `scs scd write <path> --from-file -` (YAML on stdin) |
| Add a concept from a template | `scs add bundle <concept> --author ... --email ...` |
| Create a concept with no template | `scs add bundle <name> --new --title "..." --author ... --email ...` |
| Add a template SCD | `scs add scd <name>` |
| List an existing SCD in a bundle (re-scope) | `scs bundle add-scd <scd-id> --bundle <file>` |
| Retire an SCD | `scs bundle remove-scd <scd-id>` |
| Import a concept bundle | `scs bundle add-import <ref>` |
| See what is there | `scs bundle list`, `scs bundle info <name>` |

Every one takes `--dry-run`; use it, show the changes, and confirm before the real run.
`scs scd write` validates the SCD before writing and refuses an invalid one; explain its
diagnostics in plain language.

`provenance.created_by` is the person who created the SCD, `Name <email>`. Correct a
placeholder (`PROVENANCE_PLACEHOLDER`) with the user; never replace a true value.

## Drafting in a Project

A Project inherits its Domain's rules. Before drafting a Project rule, check the Domain's
(see [review.md](review.md), "The Domain in a Project review"): do not repeat a Domain rule in
the Project, and never draft a Project rule that lifts or loosens one. If the user needs a
Domain rule changed, record it as a question for the Domain owner; do not change `domain/`.
