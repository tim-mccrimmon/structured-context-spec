# Versioning

A version is a git tag, `<workspace>/<bundle-name>-v<version>`, on a commit holding the whole
workspace, with a manifest recording who released it and a content digest. It cannot be
changed without detection. A person the user names releases it, never you. Validate before
versioning.

Releasing is not certifying. The person who releases a version authorizes it into the
repository; the engine records them as the approver (`--approved-by`, `version_approved_by`).
Where an organization formally approves its AI context, in a review or quality system, that
happens afterwards and outside SCS. Say "released by", not "approved by", so the two are not
confused.

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

## 3. Get who releases it and the version

Ask the user who releases this version, as `Name <email>`. They are recorded as the approver
(`--approved-by`) and as the commit's author. If the engine's diagnostics suggest a value
(`suggestion.approved_by`), you may offer it, but only the user's answer counts. Ask for optional version notes.

Ask which version to release; never choose it. Show the latest version (`scs status`,
`latest_version`) and suggest the next one: patch for wording fixes, minor for added rules,
major for removed or changed rules. For a first release, offer `0.1.0` (still being shaped) or
`1.0.0` (ready to rely on). Explain that the working copy stays `DRAFT` and is not a release.

## 4. Release

Every import must be pinned to a released version before the root can be versioned
(`VERSION_IMPORT_NOT_PINNED`). So releasing a root usually means a **cascade**: version each
changed concept bundle, pin it in the root, then version the root. `scs bundle release` does
the whole cascade in one command.

Commit any other pending changes first, such as recorded review decisions, with `scs commit`
as a step of its own, shown and confirmed before the release.

Find which concept bundles need a version: run the release without them. The engine refuses
with `RELEASE_VERSION_REQUIRED`, and `suggestion.concepts` lists each one with its latest
version and why (`not pinned`, `changed since <version>`). Ask the user for a version for each,
as in step 3; never choose one.

```
scripts/scs_engine.py run scs bundle release --version 1.2.0 \
    --approved-by "Jane Doe <jane@acme.example>" --dry-run
```

Then run the dry run with every version. It rehearses the whole release on a copy of the
repository, so its `changes` list every snapshot, manifest, root bundle pin, commit, and tag,
the root's included:

```
scripts/scs_engine.py run scs bundle release --version 1.2.0 \
    --concept security=1.0.0 --concept privacy=1.1.0 \
    --approved-by "Jane Doe <jane@acme.example>" --notes "..." --dry-run
```

Show that as the release plan: for each bundle, its new version, its snapshot
`<bundle-name>-v<version>.yaml` and manifest `<bundle-name>-v<version>-MANIFEST.yaml`, the pin
it changes in the root bundle file, and its commit and tag `<workspace>/<bundle-name>-v<version>`.
Write out every file by its name; never "its manifest" or "the root". One confirmation, naming
who releases it, covers the whole plan. Then run the same command without `--dry-run`. It
covers versioning and pinning only: compiling comes after the versions are reported, with its
own dry run and yes.

The dry run also lists empty SCDs (`SCD_EMPTY`); ask whether to remove or keep each before
the release.

The `content_digest` in a dry run is provisional: the digest covers the approval time, so the
real run reports a different value. That is expected; report the real run's digest, and do not
compare it with the dry run's.

To version a single bundle on its own, `scs bundle version --bundle <file> --version <v>` and
`scs bundle pin <name> --version <v>` remain; show each one's dry run and confirm it.

## 5. Report

Report each version only after its envelope says `ok: true`, with the tag it created
(`result.steps`). If a release fails, the engine has undone every step, so nothing was
released; say what failed, using the diagnostics.

Refusals you may see: `VERSION_EXISTS` (versions are never overwritten; choose a new number),
`VERSION_INPUT_UNTRACKED` (a file the digest reads is ignored or untracked),
`VERSION_PROVENANCE_PLACEHOLDER` (correct `created_by` first), `VERSION_OWNER_MISSING` or
`VERSION_OWNER_UNMAPPED` (the section has no owner role, or no one holds it: settle it as the
people step in [intake.md](intake.md) describes), `GIT_REQUIRED`.
`--no-validate` skips content validation only, and is used only if the user asks for it.
