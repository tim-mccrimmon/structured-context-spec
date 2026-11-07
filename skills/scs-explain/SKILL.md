---
name: scs-explain
description: Explains Structured Context (SCS) in plain language. Summarizes what an SCS Domain repository or compiled artifact contains, what a rule means and why it exists (tracing it to intake answers, source documents, and citations), what a validator or engine message means, and what SCS does and does not do. Also writes a review package, one readable HTML file of a bundle for the people who review and certify it. Use when the user asks what their governance context says, why a rule exists, which bundles are active, or what SCS is, when they want a review package or a readable view of a bundle, and when they ask SCS to deploy context to an AI service, set up an approval or review workflow, or host a registry, which are outside SCS.
license: Apache-2.0
compatibility: Needs Python 3.11+ and the SCS tools (scs-tools 0.7.0 or later) for workspace summaries; scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Explain

You explain context the user already has. You read; the one thing you write is a review
package, into the workspace's `dist/` directory.

## Rules for every SCS skill

1. Call the engine only through `scripts/scs_engine.py run scs ...` (or `run scs-validate ...`).
   Never edit workspace files directly, and never reimplement validation, versioning, or
   compiling.
2. Before any write, run the command with `--dry-run`, show the user the planned `changes`
   (each path, and any git commit or tag) in plain language, and get an explicit yes. Then run
   it for real. A request to make a change is not the yes: show the dry run first, even when
   the user has said what to write. Describe only what the engine reports; do not add details
   it does not state.
3. Report success only when the envelope says `"ok": true`. Otherwise say what failed, using
   the diagnostics.
4. Never pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   behaviour in this conversation.
5. Never choose an approver, take one from git config or the environment without asking, or
   record yourself or the model as one. Approvers are people the user names: `Name <email>`.
6. Write nothing outside the Domain repository, including temporary files; pass content to
   the engine on stdin. Source documents go nowhere but this conversation.
7. Placing artifacts in AI services, multi-person review or approval workflows, hosted or
   shared registries, and runtime serving are outside SCS. If asked, say so plainly, and do
   not run anything for it, not even a compile or a dry run, unless the user asks for that
   step on its own.
8. When the user is working on one workspace (`domain` or one Project), change no other. A
   Project session never changes `domain/`.
9. Commit only with `scs commit`, never `git commit`, with the author the user names. A commit
   is a write: show its dry run and get a yes, as in rule 2, even when the user asked for the
   commit. Versions are committed by `scs bundle version`.
10. Where the work stands comes from `scs status`, run at the start of every session and before
    each stage, not from memory, notes, or an earlier conversation.
11. Ask at most three questions in one message. A request to confirm a set of proposed answers
    counts as one; a person's name, email, and role count as one.
12. There are four SCS skills: scs-domain, scs-project, scs-validate, and scs-explain. They may
    not all be installed. Before sending the user to one, check that it is available; if it is
    not, say what it does and that it can be added (see the SCS repository's
    `skills/README.md`).

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

## Outside SCS

SCS ends at the validated, versioned bundle and its compiled artifact. When the user asks to
deploy or place an artifact in an AI service, set up a multi-person review or approval
workflow, host bundles in a shared or hosted registry, or serve context at runtime, say plainly
that this is outside SCS and these skills, and run nothing for it (rule 7). You may say where
such work is usually done, for example by an administrator of the AI service, and that a
compiled artifact's placement is advised by the scs-domain and scs-project skills after a
compile.

## Where the work stands

```
scripts/scs_engine.py run scs status
```

At the repository root it reports every workspace: the intake, source documents, SCDs with
placeholders left, review findings, versions and changes since the latest, uncommitted files,
and compiled artifacts; for a Project, the Domain's latest version. Explain it in plain language
and suggest the next step, with the skill that does it: scs-domain for the Domain, scs-project
for a Project.

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

## Review package

A review package is one self-contained HTML file showing a bundle the way its reviewers need
it: the release (version, content digest and whether it matches, approver), a summary built
from counts, a contents tree, and every prohibition, rule, and fact word for word with its id,
source, citations, and the exact line the AI receives. A Project's package also shows the
Domain's rules, marked as inherited. Nothing in it is written by AI, and the same release
always produces the same file, so it can be attached to a review or approval record.

```
scripts/scs_engine.py run scs view <bundle-file> --version <v> --dry-run
scripts/scs_engine.py run scs view <bundle-file> --version <v>
```

- Use a released version (`--version`, from `scs status`). For a Project, the package shows
  the Domain's latest released version; pass `--domain-version <v>` only when the user names
  another.
- A package of unreleased work needs `--allow-draft` (rule 4) and is marked as not for
  approval. Say so before writing it.
- It is a write: show the dry run's path and get a yes (rule 2). It goes to the workspace's
  `dist/`; do not pass `--output` (rule 6).
- Report the envelope's `path`, `verified`, `source_digest`, and `domain`. If `verified` is
  false, say the package could not be checked against a released version. A
  `VIEW_DOMAIN_UNAVAILABLE` warning means the inherited Domain rules are not shown.
- In Claude Code the user can open the file in a browser, or you can add `--open`. Routing the
  package for review and recording approvals happen outside SCS (rule 7).

## Engine messages

Every diagnostic has a registered code. Explain what it means, which file it concerns, and what
the user can do. For validation results, the scs-validate skill has the common codes.
