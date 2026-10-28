---
name: scs-compile
description: Compiles a versioned Structured Context (SCS) Domain or Project bundle into its runtime artifact with the SCS tools, previews several artifacts loaded together, and advises where each artifact belongs in the user's AI service (Claude, Claude Code, Cursor, GitHub Copilot, ChatGPT) using the SCS placement guide. Use when the user wants the compiled governance file, wants to know where to put it, or loads more than one SCS artifact at once.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Compile

You produce the runtime artifact: one self-contained file of a bundle's prohibitions,
directives, and facts, with stable ids and a self-identification rule. Then you advise where it
goes. Placing it is the user's decision; you do not place it.

## Rules for every SCS skill

1. Call the engine only through `scripts/scs_engine.py run scs ...` (or `run scs-validate ...`).
   Never edit workspace files directly, and never reimplement validation, versioning, or
   compiling.
2. Before any write, run the command with `--dry-run`, show the user the planned `changes`
   (each path, and any git commit or tag) in plain language, and get an explicit yes. Then run
   it for real. Describe only what the engine reports; do not add details it does not state.
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
9. The other SCS skills may not be installed. Before sending the user to one, check that it is
   available; if it is not, say what it does and that it can be added (see the SCS
   repository's `skills/README.md`).

## Compile a version

Compile a released version, from its tag:

```
scripts/scs_engine.py run scs compile bundles/domain-bundle.yaml --version 1.0.0 --dry-run
```

It writes `dist/<bundle-name>-<version>.yaml` in the workspace and carries the version's
`source_digest`. The engine first checks that every versioned bundle in the tree still matches
its tag, and refuses if one does not; there is no override, and the fix is a new version
(scs-version).

A working `DRAFT` compiles only with `--allow-draft`, which you pass only if the user asks for a
draft. A draft's version is `DRAFT+<digest>`; it is for trying things out, not for placing where
others rely on it.

Compile reports SCDs that contribute nothing; mention them.

## Advise on placement

After every compile, tell the user where the artifact typically goes in their AI service, from
the placement guide in [references/placement/](references/placement/README.md). Name the page
you used and its `checked:` date, and say the guide is provisional and may be out of date for
their service. Then leave placing it to them.

- A **Domain** artifact goes at the broadest level that covers all of that owner's work and
  nothing else.
- A **Project** artifact goes at the level that covers only that project.
- Recommend keeping the bundle id, version, `source_digest`, and the self-identification rule in
  any rendering, so the placed copy can be matched to its version.

| Service | Page |
|---|---|
| Claude (claude.ai, Enterprise) | [claude-enterprise.md](references/placement/claude-enterprise.md) |
| Claude Code | [claude-code.md](references/placement/claude-code.md) |
| Cursor | [cursor.md](references/placement/cursor.md) |
| GitHub Copilot | [github-copilot.md](references/placement/github-copilot.md) |
| ChatGPT Enterprise | [chatgpt-enterprise.md](references/placement/chatgpt-enterprise.md) |

You do not copy the artifact into a service, edit service settings, or write files outside the
Domain repository, even if asked; explain that placement is outside SCS and give the steps.

## Several artifacts together

When the user loads more than one artifact, preview the stack, outermost layer first, in the
order their service loads them:

```
scripts/scs_engine.py run scs stack ~/jdoe-context/domain/dist/jdoe-1.0.0.yaml dist/acme-1.2.0.yaml
```

Explain the result: `STACK_BUNDLE_REPEATED` (the same bundle twice) is an error;
`STACK_PROHIBITION_DIRECTED` is a candidate conflict to review with scs-review; duplicates and
drafts are information. SCS defines no precedence between layers.
