---
name: scs-version
description: Releases a version of a Structured Context (SCS) bundle with the SCS tools. Shows what changed since the last version, raises open review findings, gets the approver from the user, pins imports, and versions concept bundles bottom-up before the root bundle, each as a git commit and tag. Use when the user wants to approve, release, publish a version of, or tag their SCS governance context, or when validation says a bundle must be versioned again.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Version

A version is a git tag, `<workspace>/<bundle-name>-v<version>`, on a commit holding the whole
workspace, with a manifest recording the approver and a content digest. It cannot be changed
without detection. A named person approves it, never you.

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
8. When the user is working on one workspace (`domain` or one Project), change no other.
9. The other SCS skills may not be installed. Before sending the user to one, check that it is
   available; if it is not, say what it does and that it can be added (see the SCS
   repository's `skills/README.md`).

## 1. Show what changes

For each bundle to version, run the diff and summarize it in plain language:

```
scripts/scs_engine.py run scs bundle diff <bundle-file>
```

It compares the latest version with the working tree: SCDs added and removed; prohibitions,
directives, and facts added, removed, or changed; citations; imports. A bundle with no version
yet shows everything as added. Use the diff's own result; do not describe changes it does not
report.

## 2. Raise open findings

List advisory review findings still `deferred` in `intake.yaml` and raise each again (see
scs-review). They never block the version.

## 3. Get the approver

Ask the user who approves this version, as `Name <email>`. The approver is recorded as the
commit's author. If the engine's diagnostics suggest a value (`suggestion.approved_by`), you may
offer it, but only the user's answer counts. Ask for optional version notes.

## 4. Plan the order

Every import must be pinned to a released version before the root can be versioned
(`VERSION_IMPORT_NOT_PINNED`). So versioning a root usually means a **cascade**: version each
changed concept bundle first, pin it in the root, then version the root.

Before asking for confirmation, show the cascade plan. For each step, list:

- the bundle and its new version (semver: patch for wording fixes, minor for added rules, major
  for removed or changed rules);
- the snapshot `<bundle-name>-v<version>.yaml` and manifest
  `<bundle-name>-v<version>-MANIFEST.yaml` it writes;
- the pin it changes in the root (`scs bundle pin <name> --version <v>`);
- the commit and the tag `<workspace>/<bundle-name>-v<version>`.

One confirmation, naming the approver, may cover the whole plan. Then run each step's
`--dry-run` first; if its `changes` differ from the plan, stop and show the user.

```
scripts/scs_engine.py run scs bundle version --bundle bundles/concepts/security.yaml \
    --version 1.0.0 --approved-by "Jane Doe <jane@acme.example>" --dry-run
scripts/scs_engine.py run scs bundle pin security --version 1.0.0 --dry-run
scripts/scs_engine.py run scs bundle version --version 1.2.0 \
    --approved-by "Jane Doe <jane@acme.example>" --notes "..." --dry-run
```

The dry run also lists empty SCDs (`SCD_EMPTY`); ask whether to remove or keep each before
the release.

The `content_digest` in a dry run is provisional: the digest covers the approval time, so the
real run reports a different value. That is expected; report the real run's digest, and do not
compare it with the dry run's.

## 5. Report

Report each version only after its envelope says `ok: true`, with the tag it created. If a step
fails, the engine has undone that step; say which steps completed and which did not.

Refusals you may see: `VERSION_EXISTS` (versions are never overwritten; choose a new number),
`VERSION_INPUT_UNTRACKED` (a file the digest reads is ignored or untracked),
`VERSION_PROVENANCE_PLACEHOLDER` (correct `created_by` first), `GIT_REQUIRED`.
`--no-validate` skips content validation only, and is used only if the user asks for it.
