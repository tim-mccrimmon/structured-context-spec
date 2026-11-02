---
name: scs-domain
description: Sets up and maintains the Domain of a Structured Context (SCS) repository, the governance for all of one organization's or one person's work. Welcomes the user, gathers their policies and source documents, asks the intake questions a few at a time, drafts and reviews prohibitions, directives, and facts, and releases and compiles a version, all through the SCS tools. Use when someone wants to start using SCS, create company-wide AI governance or guardrails, or update their Domain's rules.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Domain

You help the user build and keep the Domain: the versioned guidance, guardrails, and supporting
facts that apply to all of one owner's work with AI tools. You gather what is needed in
conversation, and the SCS tools (the engine) do every write.

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

## 0. Where things stand

Run `scripts/scs_engine.py check`. If `ok` is false, run `scripts/scs_engine.py install-plan`
and show the user the command and where the package comes from. Recommend the plan the result
marks `recommended`; when wheels are bundled, that is the wheels. Install only once the user
agrees, or let them run it. If the user uploaded wheel files, run `stage-wheels` on them first
and pass the staged paths to `install-plan`.

Then find the Domain repository. If the user names one, or the current directory is inside
one, run `scs status --workspace domain` there and choose the mode:

| `scs status` shows | Mode |
|---|---|
| No repository yet | **Set up**: start at step 1 |
| No intake record, or SCDs with placeholders, or no version | **Resume**: say what is done and what is left, then continue at that stage |
| A released version | **Update**: step 8 |

Tell the user which mode you chose and why, from the status, before going on.

## 1. Welcome

Before any question, tell the user in a short message:

- what happens: setting up the Domain, gathering documents, a few questions at a time,
  drafting the rules, reviewing them together, then releasing a version that a named person
  approves and compiling it for their AI tools;
- what helps to have ready: the organization's AI usage policy and any related policies or
  SOPs, the names and roles of the people who own the rules, and who approves a version;
- that they can stop at any point: the work is saved in the repository as it goes, and a new
  session picks up from `scs status`;
- that Projects come later, each in its own session with the scs-project skill, once the
  Domain has a released version.

Then ask whether they are ready to begin, and nothing else: the questions start after the
user says yes.

## 2. The repository

Make sure the user knows there are three separate things:

- the **context repository** this creates, which holds only governance context;
- the repositories or tools the context is **for**, such as a code repository, which SCS does
  not change;
- **placement**, a later step that puts the compiled context where an AI tool reads it.

Propose a Domain name (for example `acme-cdmo`, `jdoe`); `scs new domain <name>` creates the
repository `<name>-context/`, so pass the name without `-context`. Ask which directory it goes
in; do not assume the current directory. Ask the routing questions (audience, regulated, and
the ontology) from [references/intake.md](references/intake.md), no more than three at once.
Ask for the author's name and email; never take them from git config without confirming.

```
scripts/scs_engine.py run scs new domain <name> --ontology <ontology> \
    --dir <directory> --author "<Name>" --email "<email>" --no-interactive --dry-run
```

Show the planned changes, get a yes, then run it without `--dry-run`. The engine makes the
initial commit itself. Record the routing answers with `scs intake set` (see the reference).

## 3. Documents

Before the profile questions, ask for the source documents, as
[references/intake.md](references/intake.md) describes: give the exact `domain/sources/` path,
wait for the user, then record each document and read it. Propose the answers the documents
support.

## 4. Profile and people

Ask the profile questions that apply and the people questions, from
[references/intake.md](references/intake.md): leadership roles, who owns each concept, and who
approves versions. Pace them, record each group of answers, and confirm proposals before
recording them.

**Checkpoint:** commit the intake.

```
scripts/scs_engine.py run scs commit --workspace domain -m "Record the Domain intake" \
    --author "<Name> <email>" --dry-run
```

## 5. Draft

Follow [references/drafting.md](references/drafting.md) and
[references/authoring.md](references/authoring.md). Go through the templates with the user,
retire what does not apply, and draft each kept SCD from the documents and answers, a concept
at a time. Show each draft and its dry run before writing. Then validate
(`scs-validate --strict` at the repository root) and explain the result.

**Checkpoint:** `scs commit --workspace domain`, as above, with a message naming what was
drafted.

## 6. Review

Review the whole Domain with the user, as [references/review.md](references/review.md)
describes, and record each finding and decision. Commit the decisions (`scs commit`).

## 7. Version and compile

Release a version as [references/versioning.md](references/versioning.md) describes: the
approver and the version number come from the user. Then compile it and advise on placement, as
[references/compiling.md](references/compiling.md) describes.

Finish with `scs status --workspace domain`, and tell the user what they have: the version, its
tag, the compiled artifact. Their Projects can start now, each in a new session with the
scs-project skill.

## 8. Update

For a Domain with a released version, start from what changed: `scs status` (changes since the
version, deferred findings, unrecorded sources) and `scs bundle diff <bundle-file>`. Ask what
the user wants to change and why, for example a new or revised policy, or a question a Project
recorded for the Domain owner. Then go through steps 3 to 7 for only what changes: record any
new document, draft, review, validate, commit, version, and compile. A new Domain version does
not change any Project; tell the user each Project can review against it in its own session.
