---
name: scs-explain
description: Explains Structured Context (SCS) in plain language. Summarizes what an SCS Domain repository or compiled artifact contains, what a rule means and why it exists (tracing it to intake answers, source documents, and citations), what a validator or engine message means, and what SCS does and does not do. Use when the user asks what their governance context says, why a rule exists, which bundles are active, or what SCS is.
license: Apache-2.0
compatibility: Needs Python 3.11+ and the SCS tools (scs-tools 0.7.0 or later) for workspace summaries; scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Explain

You explain context the user already has. You read; you do not write.

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

## What SCS is

SCS is versioned context for generative AI: the guidance, guardrails, and supporting facts an
organization or a person stands behind, authored deliberately and changed only by a new
version. That distinguishes it from retrieved context, which changes with every query.

- A **Domain** holds the governance for all of one owner's work; a **Project** holds one
  project's. Both live in one git repository, the Domain repository, and each compiles to its
  own artifact.
- Content is **prohibitions** (absolute), **directives** (instructions), and **facts**.
- A **version** is a git tag with an approver and a content digest; changing it is detectable.
- SCS ends at the validated, versioned bundle and its compiled artifact. Placing artifacts in
  AI services, review workflows, registries, and runtime serving are outside it.

## Summarize a workspace

```
scripts/scs_engine.py run scs bundle list --workspace <ws>
scripts/scs_engine.py run scs bundle info <name> --workspace <ws>
```

Describe what the root bundle imports, what each concept covers, and how many rules and facts it
has, in the user's terms rather than file names. Read SCD files for their content.

## Why a rule exists

Trace an item through its `derived_from`: an intake answer (`answers[]` in `intake.yaml`, with
who answered and when) or a source document (`source_documents[]`, with the locator), and its
`cites`. Name a citation as a clause reference; never present remembered wording as the
standard's text. If an item has no `derived_from`, say its origin is not recorded.

## Which bundles are active

A compiled artifact names itself: its first rule is the self-identification rule
(`<bundle-name>/identity`), and its header gives `id`, `version`, and `source_digest`. Rule ids
are `<bundle-name>/<scd-name>/<id>`, so any rule can be traced to its bundle and SCD.

## Engine messages

Every diagnostic has a registered code. Explain what it means, which file it concerns, and what
the user can do. For validation results, the scs-validate skill has the common codes.
