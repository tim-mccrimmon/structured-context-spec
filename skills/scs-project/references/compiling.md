# Compiling and placement

Compiling produces the runtime artifact: one self-contained file of a bundle's prohibitions,
directives, and facts, with stable ids and a self-identification rule. Then you advise where it
goes. Placing it is the user's decision; you do not place it.

## Compile a version

Compile a released version, from its tag:

```
scripts/scs_engine.py run scs compile bundles/domain-bundle.yaml --version 1.0.0 --dry-run
```

It writes `dist/<bundle-name>-<version>.yaml` in the workspace and carries the version's
`source_digest`. The engine first checks that every versioned bundle in the tree still matches
its tag, and refuses if one does not; there is no override, and the fix is a new version.

A working `DRAFT` compiles only with `--allow-draft`, which you pass only if the user asks for a
draft. A draft's version is `DRAFT+<digest>`; it is for trying things out, not for placing where
others rely on it.

Compile reports SCDs that contribute nothing; mention them.

## Advise on placement

After every compile, tell the user where the artifact typically goes in their AI service, from
the placement guide in [placement/](placement/README.md). Name the page you used and its
`checked:` date, and say the guide is provisional and may be out of date for their service.
Then leave placing it to them.

- A **Domain** artifact goes at the broadest level that covers all of that owner's work and
  nothing else.
- A **Project** artifact goes at the level that covers only that project, with the Domain's
  artifact loaded too.
- Recommend keeping the bundle id, version, `source_digest`, and the self-identification rule in
  any rendering, so the placed copy can be matched to its version.

| Service | Page |
|---|---|
| Claude (claude.ai, Enterprise) | [claude-enterprise.md](placement/claude-enterprise.md) |
| Claude Code | [claude-code.md](placement/claude-code.md) |
| Cursor | [cursor.md](placement/cursor.md) |
| GitHub Copilot | [github-copilot.md](placement/github-copilot.md) |
| ChatGPT Enterprise | [chatgpt-enterprise.md](placement/chatgpt-enterprise.md) |

You do not copy the artifact into a service, edit service settings, or write files outside the
Domain repository, even if asked; explain that placement is outside SCS and give the steps.

## Several artifacts together

When the user loads more than one artifact, preview the stack, outermost layer first, in the
order their service loads them:

```
scripts/scs_engine.py run scs stack ../../domain/dist/acme-1.0.0.yaml dist/timekeeping-0.1.0.yaml
```

Explain the result: `STACK_BUNDLE_REPEATED` (the same bundle twice) is an error;
`STACK_PROHIBITION_DIRECTED` is a candidate conflict to review (see [review.md](review.md));
duplicates and drafts are information. SCS defines no precedence between layers.
