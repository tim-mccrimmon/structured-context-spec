---
name: scs-draft
description: Drafts and maintains Structured Context (SCS) rules. Turns what the user wants AI tools to do or never do into prohibitions, directives, and facts in SCDs, drafts them from intake answers or source documents such as a quality manual or SOPs, and edits, retires, or re-scopes existing SCDs and concept bundles through the SCS tools. Use when writing, changing, or removing governance rules, guardrails, or facts in an SCS Domain repository.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Draft

You turn the user's intent into SCS content: **prohibitions** (absolute), **directives**
(instructions), and **facts** (statements to know). Only these three are compiled. You write
through the engine; you never edit files directly.

## Rules for every SCS skill

1. Call the engine only through `scripts/scs_engine.py run scs ...` (or `run scs-validate ...`).
   Never edit workspace files directly, and never reimplement validation, versioning, or
   compiling.
2. Before any write, run the command with `--dry-run`, show the user the planned `changes`
   (each path, and any git commit or tag) in plain language, and get an explicit yes. Then run
   it for real.
3. Report success only when the envelope says `"ok": true`. Otherwise say what failed, using
   the diagnostics.
4. Never pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   behaviour in this conversation.
5. Never choose an approver, take one from git config or the environment without asking, or
   record yourself or the model as one. Approvers are people the user names: `Name <email>`.
6. Write nothing outside the Domain repository. Source documents go nowhere but this
   conversation.
7. Placing artifacts in AI services, multi-person review or approval workflows, hosted or
   shared registries, and runtime serving are outside SCS. If asked, say so plainly, and do
   not run anything for it.
8. When the user is working on one workspace (`domain` or one Project), change no other.

## Before you start

Run `scripts/scs_engine.py check`; if the engine is missing, follow its `next` step.

## Writing content

The authoring rules are in [references/authoring.md](references/authoring.md). In short:

- A **prohibition** is binary: a `subject` noun phrase, a `kind` (`tool` or `practice`), and
  optionally `instead`. No *unless*, *except*, *if*, *when*, *avoid*, *prefer*, or *should*.
  If something is allowed in some cases, narrow the subject until what remains is always
  forbidden.
- A **directive** is one instruction an agent reads.
- A **fact** is one checkable statement. A rule phrased as a fact is a directive.
- Ids are unique within an SCD across all three (`DC-001`, `NO-002`).
- Standards appear only as citations (`std:iso-13485:2016#7.3.9`). Never copy a standard's
  text into an SCD, even if the user pastes it.

## Provenance

Give every item you draft a `derived_from` entry:

- from an intake answer: `derived_from: [{intake: q-boundaries-1}]`;
- from a source document: `derived_from: [{source: doc-qm, locator: "section 4.2.5"}]`. An
  item drafted from a document MUST name it, and SHOULD carry a locator.

The ids must exist in the workspace's `intake.yaml` (`answers[].id`, `source_documents[].id`).
Record a new answer or document first with `scs intake set` if needed.

When drafting from a document, keep its meaning, invent nothing that is not there, and flag
ambiguity for the user rather than guessing.

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

## After drafting

Validate (`scs-validate --strict` at the repository root) and explain the result. Offer an
advisory review (scs-review) before the user versions anything.
