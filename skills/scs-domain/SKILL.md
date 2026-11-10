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
   commit. Versions are committed by `scs bundle release` or `scs bundle version`.
10. Where the work stands comes from `scs status`, run at the start of every session and before
    each stage, not from memory, notes, or an earlier conversation.
11. Ask at most three questions in one message. A request to confirm a set of proposed answers
    counts as one; a person's name, email, and role count as one.
12. There are four SCS skills: scs-domain, scs-project, scs-validate, and scs-explain. They may
    not all be installed. Before sending the user to one, check that it is available; if it is
    not, say what it does and that it can be added (see the SCS repository's
    `skills/README.md`).

## 0. Where things stand

If this session has already run the scs-project skill, say first, before the check, that
the Domain is best done in a new session, and why: the Project conversation is still in
context, so its answers can carry over into the Domain's rules, and a long session gets
compacted, which loses detail. A new session picks up from `scs status`. Offer to stop here;
go on in this session only if the user asks to.

Run `scripts/scs_engine.py check`. If `ok` is false, run `scripts/scs_engine.py install-plan`
and handle what `missing` names; install nothing the user has not agreed to, or let them run it.

- **The SCS tools**: show the user the command and where the package comes from. Recommend the
  plan the result marks `recommended`; when wheels are bundled, that is the wheels. If the user
  uploaded wheel files, run `stage-wheels` on them first and pass the staged paths to
  `install-plan`.
- **git**: show the `git` command from the same result, before running it, with its reason: SCS
  keeps each change and version in a local git repository; no GitHub account or git setup is
  needed. If the result has no command, say git is needed and stop.

Then find the Domain repository. If the user names one, or the current directory is inside
one, run `scs status --workspace domain` there and choose the mode:

| `scs status` shows | Mode |
|---|---|
| No repository yet | **Set up**: start at step 1 |
| No intake record, or SCDs with placeholders, or no version | **Resume**: say what is done and what is left, then continue at that stage |
| A released version | **Update**: step 9 |

Tell the user which mode you chose and why, from the status, before going on.

## 1. Welcome

Before any question, tell the user in a short message:

- what happens: setting up the Domain, gathering documents, a few questions at a time,
  drafting all the rules from the documents in one pass, naming who owns each section, a draft
  review package they can read and share with those owners, reviewing and fixing until the rules
  settle, then naming who releases, releasing a version, and compiling it for their AI tools;
- what is needed on the computer: git, which SCS uses to keep each change and version (no
  GitHub account or git setup is needed), and the SCS tools; step 0 has already checked both;
- what helps to have ready: the organization's AI usage policy and any related policies or
  SOPs, and the people involved and their roles; who owns each section is asked once the draft
  shows which sections there are, and who releases a version at the end;
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
repository `<name>-context/`, so pass the name without `-context`. Propose a display name too,
the name as people write it (for example `NexTern` for `nextern`): it goes in the titles and
descriptions, and changing it later takes a new version. Ask which directory it goes in; do not
assume the current directory. Ask for the author's name and email, and say what they are for:
they are recorded as `created_by` in the provenance of what is created, and as the author of
each checkpoint commit (the committer is `scs-tools`). They are not taken from git config, and
git config is not changed. These are the first message. Once they are answered, ask the routing
questions (audience, regulated, and the ontology) from
[references/intake.md](references/intake.md) in a message of their own.

```
scripts/scs_engine.py run scs new domain <name> --title "<Display name>" --ontology <ontology> \
    --dir <directory> --author "<Name>" --email "<email>" --no-interactive --dry-run
```

Show the planned changes, get a yes, then run it without `--dry-run`. The engine makes the
initial commit itself. Record the routing answers with `scs intake set` (see the reference).

## 3. Documents

Before the profile questions, ask for the source documents, and whether there is a website to
read, as [references/intake.md](references/intake.md) describes: give the full,
absolute path of `domain/sources/`, wait for the user, then record each document and read it. Propose the answers the documents
support.

## 4. Profile

Ask the profile questions that apply, then who is involved and in which role (the people
answer, `q-people-1`), from [references/intake.md](references/intake.md). Pace them, record
each group of answers, and confirm proposals before recording them. Section owners are asked
after drafting (step 6) and who releases versions at release (step 8), not here.

**Checkpoint:** commit the intake.

```
scripts/scs_engine.py run scs commit --workspace domain -m "Record the Domain intake" \
    --author "<Name> <email>" --dry-run
```

## 5. Draft

Follow [references/drafting.md](references/drafting.md) and
[references/authoring.md](references/authoring.md). Draft from the sources outward, in one
pass: work out the topics the documents and answers cover, place each in its concept, and
draft every SCD that has material, giving each item its `derived_from` as you write it. Then
use the ontology's templates as a coverage check: for the templates with no material, propose
which to retire and which to keep as gaps, as one list to confirm. Show each concept's drafts as one batch, with their dry
runs, and get one yes per batch. Then validate (`scs-validate --strict` at the repository root)
and explain the result.

**Checkpoint:** `scs commit --workspace domain`, as above, with a message naming what was
drafted.

## 6. Section owners and draft review package

The section owners are the primary reviewers, so settle them before the package, as
[references/intake.md](references/intake.md) describes ("Section owners"): read the people
recorded in the intake, propose a person for each section owner role yourself as one table,
never asking who holds a role, and record the confirmed owners. Commit the intake
(`scs commit`).

Then offer the user a review package of the draft: one HTML file with every prohibition, rule,
and fact, its source, the line the AI receives, and each section's owner, marked as not for
approval. It is the first time they see the whole Domain in one place, and they can share it
with the section owners, each reviewing their own sections. If they want it, that is their request for `--allow-draft`:

```
scripts/scs_engine.py run scs view bundles/domain-bundle.yaml --allow-draft --dry-run
```

Show the path, get a yes, write it (it goes to `domain/dist/`), and tell the user where it is.
Ask them to read it and bring back what they or others want changed. If they decline, go on to
the review.

## 7. Review

Review the whole Domain with the user, as [references/review.md](references/review.md)
describes, together with any comments from the package, and record each finding and decision.
Make the changes the user confirms, validate again, and repeat until nothing more changes; a
new draft package can be written after a round of changes. Commit the decisions and changes
(`scs commit`).

## 8. Release and compile

Check that every section still has its owner, including any section added in review (`scs
status`, `owners.unmapped_roles`), and propose one for each that does not. Then ask who releases
versions and record them, as [references/intake.md](references/intake.md) describes ("Who
releases versions"). Commit the intake (`scs commit`). The engine refuses a version until every
section's owner is mapped.

In an update, the owners and releasers are already recorded: show them and ask only whether
they have changed.

Release a version as [references/versioning.md](references/versioning.md) describes: the
person who releases it and the version numbers come from the user. Then compile it and advise
on placement, as [references/compiling.md](references/compiling.md) describes.

Finish with `scs status --workspace domain`, and tell the user what they have: the version, its
tag, the compiled artifact. Their Projects can start now, each in a new session with the
scs-project skill.

## 9. Update

For a Domain with a released version, start from what changed: `scs status` (changes since the
version, deferred findings, unrecorded sources) and `scs bundle diff <bundle-file>`. Ask what
the user wants to change and why, for example a new or revised policy, or a question a Project
recorded for the Domain owner. Then go through steps 3 to 8 for only what changes: record any
new document, draft, review, validate, commit, version, and compile. A new Domain version does
not change any Project; tell the user each Project can review against it in its own session.
