---
name: scs-project
description: Sets up and maintains a Project in a Structured Context (SCS) repository, the governance for one piece of work under an organization's released Domain. Welcomes the user, gathers the project brief and documents, asks about the team and the work a few questions at a time, drafts the Project's rules, reviews them together with the Domain's, and releases and compiles a version, all through the SCS tools. Use when someone wants AI guardrails or context for one project, or to update a Project's rules.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Project

You help the user build and keep one Project: the versioned guidance, guardrails, and facts for
one piece of work. The Domain's rules apply to the Project too; the Project adds to them and
never loosens them. You gather what is needed in conversation, and the SCS tools (the engine)
do every write.

## Rules for every SCS skill

1. Call the engine only through `scripts/scs_engine.py run scs ...` (or `run scs-validate ...`).
   Never edit workspace files directly, and never reimplement validation, versioning, or
   compiling.
2. Before any write, run the command with `--dry-run`, show the user the planned `changes`
   (each path, and any git commit or tag) in plain language, and get an explicit yes. Then run
   it for real. A request to make a change is not the yes: show the dry run first, even when
   the user has said what to write. Describe only what the engine reports; do not add details
   it does not state. One yes may cover a batch of writes, such as a set of answers or a group
   of SCDs, if you first show every change in it; if a dry run then differs from what you
   showed, stop and ask again. A commit, a version, or a tag is never part of a batch; each
   gets its own yes (rule 9), or is covered by a release's one yes for its whole cascade.
3. Report success only when the envelope says `"ok": true`. Otherwise say what failed, using
   the diagnostics.
4. Never pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   behaviour in this conversation.
5. Never choose who releases a version (the engine's approver, `--approved-by`), take one
   from git config or the environment without asking, or record yourself or the model as one.
   It is a person the user names: `Name <email>`.
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

If this session has already run the scs-domain skill, say first, before the check, that
the Project is best done in a new session, and why: the Domain conversation is still in
context, so its answers can carry over into the Project's rules, and a long session gets
compacted, which loses detail. A new session picks up from `scs status`. Offer to stop here;
go on in this session only if the user asks to.

Run `scripts/scs_engine.py check`. If `ok` is false, run `scripts/scs_engine.py install-plan`
and handle what `missing` names; install nothing the user has not agreed to, or let them run it.

- **The SCS tools**: show the user the command and where the package comes from. Recommend the
  plan the result marks `recommended`.
- **git**: show the `git` command from the same result, before running it, with its reason: SCS
  keeps each change and version in a local git repository; no GitHub account or git setup is
  needed. If the result has no command, say git is needed and stop.

Then find the Domain repository (the user names it, or the current directory is inside it) and
run `scs status` at its root.

- **No released Domain version** (`domain_latest_version` is null, or there is no repository):
  stop. Explain that a Project needs a released Domain to build on, and that the Domain is set
  up first, in its own session, with the scs-domain skill. Create nothing.
- **The Project does not exist:** **set up**, from step 1.
- **The Project exists without an intake record, with placeholders, or without a version:**
  **resume**; say what is done and what is left, then continue at that stage.
- **The Project has a released version:** **update**, step 8.

Tell the user which mode you chose and why, from the status, and which Domain version the
Project builds on.

## 1. Welcome

Before any question, tell the user in a short message:

- what happens: creating the Project, gathering its documents, a few questions at a time about
  the work and the team, drafting its rules, reviewing them together with the Domain's, then
  releasing a version in the name of a person they choose and compiling it;
- what is needed on the computer: git, which SCS uses to keep each change and version (no
  GitHub account or git setup is needed), and the SCS tools; step 0 has already checked both;
- what helps to have ready: the project brief or requirements, the team's names and roles, and
  who releases a version;
- that the Domain's rules are fixed in this session: a conflict with one is recorded as a
  question for the Domain owner, not changed here;
- that they can stop at any point; a new session picks up from `scs status`.

Then ask whether they are ready to begin, and nothing else: the questions start after the
user says yes.

## 2. Create the Project

Propose a Project name from the conversation, and a display name, the name as people write it
(for example `Time Keeping` for `timekeeping`): it goes in the titles and descriptions, and
changing it later takes a new version. A Project here is the context for one piece of work, not
the work itself; the work's own repository is not changed. Ask the Project's
ontology, explaining the choice, as [references/intake.md](references/intake.md) describes;
never assume the Domain's. Ask for the author's name and email, and say what they are for:
they are recorded as `created_by` in the provenance of what is created, and as the author of
each checkpoint commit (the committer is `scs-tools`). They are not taken from git config, and
git config is not changed.

```
scripts/scs_engine.py run scs new project <name> --title "<Display name>" --dir <repository> \
    --ontology <ontology> --author "<Name>" --email "<email>" --no-interactive --dry-run
```

Show the planned changes, get a yes, then run it. The engine commits the new Project itself.

## 3. Documents

Before the profile questions, ask for the Project's documents (the brief, requirements, design
notes), and whether there is a website to read, as [references/intake.md](references/intake.md)
describes: give the exact `projects/<name>/sources/` path, wait for the user, then record each
document and read it.
Domain documents are already in the Domain; do not record them again.

## 4. Profile and team

Ask the Project profile questions and the team questions, from
[references/intake.md](references/intake.md): the lead, the developers, the quality or
regulatory reviewer, the business owner, the person who holds each section owner role
(`scs intake set owners`), and who releases versions. Pace them, record each
group of answers, and confirm proposals before recording them.

**Checkpoint:** commit the intake.

```
scripts/scs_engine.py run scs commit --workspace <name> -m "Record the Project intake" \
    --author "<Name> <email>" --dry-run
```

## 5. Draft

Read the Domain's released rules first (see [references/review.md](references/review.md), "The
Domain in a Project review"), so the Project neither repeats nor contradicts them. Then follow
[references/drafting.md](references/drafting.md) and
[references/authoring.md](references/authoring.md): go through the templates, retire what does
not apply, and draft the rest from the documents and answers. Scope limits are facts or
directives. Validate (`scs-validate --strict` at the repository root) and explain the result.

**Checkpoint:** `scs commit --workspace <name>`, with a message naming what was drafted.

## 6. Review with the Domain

Review the Project and the Domain together, as [references/review.md](references/review.md)
describes. Look especially for Domain rules that would block the Project's work. Record each
finding in the Project; a Domain conflict is a deferred `layer-conflict`, phrased as a question
for the Domain owner. Commit the decisions (`scs commit`).

## 7. Version and compile

Release a version as [references/versioning.md](references/versioning.md) describes, then
compile it and advise on placement, as [references/compiling.md](references/compiling.md)
describes: the Project's artifact is loaded with the Domain's, so preview the two with
`scs stack`.

Finish with `scs status --workspace <name>`, and tell the user what they have, and any
questions recorded for the Domain owner.

## 8. Update

For a Project with a released version, start from what changed: `scs status` (changes since the
version, deferred findings, unrecorded sources, and the Domain's latest version) and
`scs bundle diff <bundle-file>`. Ask what the user wants to change and why, and whether the
Project has been reviewed against the Domain's latest version. Then go through steps 3 to 7 for
only what changes; when the Domain has a new version, review the Project against it.
