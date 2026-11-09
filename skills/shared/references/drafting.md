# Drafting

How to turn intent and source documents into SCS content: **prohibitions** (absolute),
**directives** (instructions), and **facts** (statements to know). Only these three are
compiled. The field-level rules are in [authoring.md](authoring.md).

## Start from the sources

Draft from the sources outward, in one pass. Read the documents and answers, list the topics
they cover, and place each topic in a concept: an existing template SCD where one fits, a new
SCD or concept where none does (`scs add scd`, `scs add bundle <name> --new`). Draft every SCD
that has material, giving each item its `derived_from` as you write it, not afterwards.

Then use the ontology's templates as a coverage check. Templates hold placeholders (`TODO`, or
`"[...]"` hints); `scs status` lists the SCDs that still have them (`scds.placeholders`). For
the templates with no material, propose the outcome yourself, as one list to confirm or
correct: for each, retire it or keep it as a gap, with a short reason from the sources and
answers. That is one question; never ask the user to sort the templates themselves. A kept gap
is filled with an answer; a retired template is removed with `scs bundle remove-scd`. Retiring
a template never removes a topic the sources raise. A `personal` Domain gets only
boundaries; define the person's other concepts with them using `scs add bundle <name> --new`.

Removing the last SCD of a concept bundle also removes the bundle, its import in the root
bundle, and its entry in the ontology manifest. Relationships in other SCDs that point at a
retired SCD are removed too (`result.relationships_removed`), so none is left dangling. Retire several SCDs in one call
(`scs bundle remove-scd <id> <id> ... --dry-run`), so one dry run shows everything that goes;
dry runs made one at a time against the same files miss it. Show that dry run's `changes` and
name each concept bundle in `result.removed[].bundle_removed`, then get the yes. Afterwards,
report what the real run's envelope says, not what you expected.

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

## Writing for the assistant

Everything compiled is read by an AI assistant in the middle of a task. A policy is usually
written for people, so drafting it faithfully can produce rules the assistant cannot act on.
For each item, ask: could the assistant do this, or know this, while helping someone?

- **A directive says what the assistant does when it meets the case.** "Check content before
  it is sent outside the company" is a control someone else runs; the assistant cannot
  intercept anything. Write what it does itself: "When drafting content for an external
  recipient, leave out customer names and internal project codes, and point out any you were
  given."
- **Administration is not the assistant's.** Which model version is approved, how accounts are
  provisioned, who grants access, how vendors are qualified, how long records are kept: these
  inform people. Leave them out of prohibitions, directives, and facts. If the user wants them
  kept, put them in the SCD's `summary`, which is not compiled, and say so. Keep a fact only
  when the assistant needs it to answer or act correctly, such as which tool is approved for a
  task.
- **A detection pattern is not a rule.** A list of what a monitoring tool looks for (card
  number formats, keyword lists) tells the assistant nothing to do. Draft the behaviour behind
  it instead, usually a prohibition on the data itself, or leave it out.
- **Facts state what is true now.** When a source describes a process that is planned or not
  yet in operation, say so in the fact ("A review board is planned; until it meets, the CTO
  approves new AI tools"), and keep the same tense for every such process. Never state a
  planned process as current. Ask the user when the source does not say which it is.

When you leave something out or move it to `summary`, tell the user what and why, so the
decision is theirs.

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
| Retire SCDs | `scs bundle remove-scd <scd-id> [<scd-id> ...]` |
| Import a concept bundle | `scs bundle add-import <ref>` |
| See what is there | `scs bundle list`, `scs bundle info <name>` |

Every one takes `--dry-run`; use it, show the changes, and confirm before the real run.
Work through a group of SCDs as one batch: show every planned change in the group, get one
yes, then run them, stopping to ask again if a dry run differs from what you showed.
`scs scd write` validates the SCD before writing and refuses an invalid one; explain its
diagnostics in plain language.

`provenance.created_by` is the person who created the SCD, `Name <email>`. Correct a
placeholder (`PROVENANCE_PLACEHOLDER`) with the user; never replace a true value.

## Drafting in a Project

A Project inherits its Domain's rules. Before drafting a Project rule, check the Domain's
(see [review.md](review.md), "The Domain in a Project review"): do not repeat a Domain rule in
the Project, and never draft a Project rule that lifts or loosens one. If the user needs a
Domain rule changed, record it as a question for the Domain owner; do not change `domain/`.
