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
