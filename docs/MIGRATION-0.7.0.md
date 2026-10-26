# Migration Guide: Upgrading to SCS 0.7.0

**Last Updated:** 2026-10-25

---

## Overview

SCS 0.7.0 implements RFC 0002 (agent-mediated SCS). No changes are required to SCDs or
bundles; they remain valid. This guide is filled in as 0.7.0 work lands on `0.7-dev`.

---

## What Changed

### Tooling

| | 0.6.0 | 0.7.0 |
|---|---|---|
| `scs bundle version` approver | `git config user.email` when `--approved-by` is omitted | Prompted for when `--approved-by` is omitted; never taken from git config (ISS-047) |
| Version manifest file | `VERSION-<version>-MANIFEST.yaml` | `<bundle-name>-v<version>-MANIFEST.yaml` (ISS-043) |
| Version git tag | `v<version>` | `<bundle-name>-v<version>` (ISS-043) |
| Manifest `distribution` | `repository` was the bundle name, `branch` always `main` | `repository` and `branch` read from git; omitted with `--no-git` (ISS-043) |
| `scs --version` | Reported 0.5.0 in 0.6.0 | Reports the installed package version (ISS-042) |
| cdmo SCD templates | Header line `# Profile: Project only.` | Line removed; the bundle that includes an SCD sets its scope (ISS-044) |
| Version manifest digest | SHA-256 of the snapshot file only, never checked | Also `content_digest` over the bundle's full resolved content, plus `content_inputs` (ISS-045) |
| `scs-validate` / `scs compile` on a versioned bundle | Not checked | Verified against `content_digest`; a mismatch is an error, and compile refuses with no override (ISS-045) |
| `scs bundle version --no-validate` | Recorded `validation_passed: true`, `approval_status: validated` | Records `validation_passed: false`, `approval_status: approved` (ISS-045) |
| Runtime artifact | `scs_runtime: '0.6'` | `scs_runtime: '0.7'`, with `source_digest` for versioned bundles (ISS-045) |
| `scs bundle version` | Ran without scs-validator installed | Needs scs-validator (`pip install 'scs-tools[validator]'`) to compute the digest (ISS-045) |

The name in manifests and tags is the bundle's name from its id (`bundle:<name>`). RFC 0002
also qualifies tags by workspace (`<workspace>/<bundle-name>-v<version>`); that arrives with
Domain repositories (ISS-048).

---

## Steps

1. **Scripts that call `scs bundle version`** without `--approved-by` now stop at a prompt.
   Pass `--approved-by` explicitly.
2. **Tooling that looks for `VERSION-<version>-MANIFEST.yaml` or `v<version>` tags** should
   look for `<bundle-name>-v<version>-MANIFEST.yaml` and `<bundle-name>-v<version>`.
   Existing manifests and tags are not renamed and keep working.
3. **Versions made before 0.7** have no `content_digest`. Validating or compiling one warns
   that it cannot be verified (a failure under `--strict`). To make one verifiable, version it
   again at a new version number with 0.7 tools; an existing version is not rewritten.
4. **Committed compiled artifacts** change when recompiled: `scs_runtime` becomes `'0.7'` and
   versioned bundles gain `source_digest`. Runtimes that check `scs_runtime` should accept
   `'0.7'`. Rules and facts are unchanged.
5. **Editing an SCD after versioning is now visible.** SCDs are not snapshotted: a bundle's
   versions and its working copy read the same SCD files. Once an SCD changes for the next
   version, earlier versions in the working tree no longer verify, and neither does any bundle
   that still pins them. Version the changed bundle, update the pins that import it, and
   validate or compile older versions from their git tag. Comment and formatting edits don't
   change the digest.
