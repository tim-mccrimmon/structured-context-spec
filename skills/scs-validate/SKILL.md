---
name: scs-validate
description: Validates a Structured Context (SCS) Domain repository with the SCS validator and explains the results in plain language. Covers schemas, rules, intake records, provenance, and the integrity of versioned bundles (tags, manifests, digests), then proposes fixes. Use when the user asks whether their SCS context is valid, when a validation or CI check fails, or after any change to SCDs or bundles.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Validate

You run the validator, explain what it found, and propose fixes. The validator is the only
judge of validity; never decide it yourself.

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

## Run it

At the repository root, so every workspace and every version tag is checked:

```
scripts/scs_engine.py check
scripts/scs_engine.py run scs-validate --strict
```

`--strict` makes warnings fail (exit code 2), as CI does. Exit codes: `0` valid, `1` errors,
`2` warnings under `--strict`, `3` bad arguments, `4` file error, `5` internal error.

To check one bundle: `scs-validate --bundle <file> --strict`. To check one version:
`scs-validate --verify-version <workspace>/<bundle>-v<version>`.

## Explain before fixing

When validation fails, your next message names each error first, in plain language: what is
wrong, in which file, and why it matters. Only then propose fixes. Group repeated findings,
but do not drop any. `info` findings (such as `SCD_EMPTY`) never fail validation; mention them
briefly.

Common findings, by code (see [references/diagnostics.md](references/diagnostics.md)):

- `CONTENT_DIGEST_MISMATCH`, `MANIFEST_ALTERED`: a versioned bundle changed after it was
  versioned. The fix is a new version, bottom-up, re-pinning each in the next (scs-version);
  never edit the manifest or tag.
- `GIT_HISTORY_INCOMPLETE`: a shallow clone. Fetch full history and tags.
- `PROVENANCE_PLACEHOLDER`: a placeholder `created_by`. Correct it with the user.
- `DERIVED_FROM_UNRESOLVED`: an item names an intake answer or document that is not recorded.
- `WORKSPACE_FILE_UNREADABLE`: a YAML file could not be read and was skipped. Offer to fix or
  delete it.

## Fixing

Each fix is a write: use the scs-draft commands with `--dry-run`, show the change, and confirm.
Validate again afterwards and report the new result, not the expected one.
