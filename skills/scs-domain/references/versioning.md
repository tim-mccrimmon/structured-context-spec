# Versioning

A version is a git tag, `<workspace>/<bundle-name>-v<version>`, on a commit holding the whole
workspace, with a manifest recording the approver and a content digest. It cannot be changed
without detection. A named person approves it, never you. Validate before versioning.

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

List the review findings still `deferred` (`scs status`, `intake.deferred`) and raise each
again. They never block the version.

## 3. Get the approver and the version

Ask the user who approves this version, as `Name <email>`. The approver is recorded as the
commit's author. If the engine's diagnostics suggest a value (`suggestion.approved_by`), you may
offer it, but only the user's answer counts. Ask for optional version notes.

Ask which version to release; never choose it. Show the latest version (`scs status`,
`latest_version`) and suggest the next one: patch for wording fixes, minor for added rules,
major for removed or changed rules. For a first release, offer `0.1.0` (still being shaped) or
`1.0.0` (ready to rely on). Explain that the working copy stays `DRAFT` and is not a release.

## 4. Plan the order

Every import must be pinned to a released version before the root can be versioned
(`VERSION_IMPORT_NOT_PINNED`). So versioning a root usually means a **cascade**: version each
changed concept bundle first, pin it in the root, then version the root.

Before asking for confirmation, show the cascade plan. For each step, list:

- the bundle and the new version the user chose;
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
