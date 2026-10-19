# Migration Guide: Upgrading to SCS 0.6.0

**Last Updated:** 2026-10-19

---

## Overview

SCS 0.6.0 changes how governance context is organized. There are two independent governance
bundles:

- **Domain bundle**: an organization's governance, applied everywhere in its scope.
  Deployments often call it the **Global** context.
- **Project bundle**: one project's governance, and nothing else.

Neither imports the other. A runtime applies them side by side, Domain first.

0.6.0 also deprecates **Standards bundles** and the **standards tier**. Standards are now
referenced by **citation** (`std:iso-13485:2016#7.3.9`), never reproduced.

This is a breaking change, expected pre-1.0. No automated `scs migrate` helper ships with
0.6.0; the steps below are the full migration path.

---

## What Changed

| | 0.5.0 | 0.6.0 |
|---|---|---|
| Project bundle imports | MUST import meta, standards, and domain bundles | MAY import concept bundles; MUST NOT import meta, standards, domain, or project bundles |
| Project bundle SCDs | Typically empty | Project-tier SCDs directly, or via concept bundles |
| Domain bundle | An industry vertical, imported by projects | An organization's governance; independent of projects |
| Domain bundle imports | Concept bundles | One pinned meta bundle plus concept bundles |
| Meta bundle | Copied into every project | Published with the spec; pinned by the Domain bundle |
| Standards bundle | 1+ per project | Deprecated (warning) |
| `scd:standards:` SCDs | Standards tier | Deprecated (warning); use citations |
| `satisfies` targets | `scd:standards:` ids | `std:` citations (`scd:standards:` deprecated) |
| Domain manifest `schemas.standards` | Required | Optional, deprecated |

The validator now resolves the whole import tree for any bundle type, so it checks import
types, unresolved imports, version mismatches, and import cycles that 0.5.0 did not. An import
that resolves to no bundle is an **error**; an SCD listed in a bundle but not found is a
warning (an ontology template may list SCD slots not yet written).

`bundle:meta:<version>` resolves to the meta bundle published with the spec (`meta/`), which
`scs-validator` ships; you do not need a copy of it in your workspace.

### Tooling

| | 0.5.0 | 0.6.0 |
|---|---|---|
| `scs new project` | Project, meta, standards, and domain bundles | Project bundle importing concept bundles |
| `scs new domain` | — | Domain bundle importing `bundle:meta:0.6.0` and concept bundles |
| `scs add bundle <domain>` | Added a domain bundle to a project | Rejected; use `scs new domain` |
| `scs bundle validate` / `version` | `bundles/project-bundle.yaml` | `bundles/domain-bundle.yaml` or `bundles/project-bundle.yaml` |
| `scs compile` | — | Compiles a Domain or Project bundle into a runtime artifact |

---

## Steps

### 1. Split organization rules from project context

Look at each project's concept bundles and SCDs:

- Rules that apply to the whole organization (AI usage policy, data boundaries, QMS rules)
  move to the organization's **Domain bundle**, in concept bundles.
- Context specific to one project stays in its **Project bundle**.

If you have no organization rules yet, you can skip the Domain bundle; a Project bundle is
valid on its own.

### 2. Rewrite the Project bundle

Remove meta, standards, and domain imports. Either import the project's concept bundles:

```yaml
id: bundle:patient-portal
type: project
version: "DRAFT"
imports:
  - bundle:portal-architecture:1.0.0
  - bundle:portal-security:1.0.0
scds: []
```

or list its SCDs directly (not both):

```yaml
imports: []
scds:
  - scd:project:portal-data-boundaries
  - scd:project:portal-release-rules
```

### 3. Create or update the Domain bundle

Pin the published meta bundle and import the organization's concept bundles:

```yaml
id: bundle:acme-health
type: domain
version: "DRAFT"
imports:
  - bundle:meta:0.6.0
  - bundle:ai-governance:1.0.0
  - bundle:data-protection:1.0.0
scds: []
```

If your 0.5.0 Domain bundle was an industry template (for example the MCA or CDMO
reference ontology), fill in its skeleton SCDs with your organization's decisions; the
filled-in, approved version is your Domain bundle.

### 4. Replace standards with citations

For each standards-tier SCD:

1. Find the SCDs whose rules implement it, and add a citation to their `cites` list:
   ```yaml
   cites:
     - std:hipaa#164.312
   ```
2. If it contains genuine organization rules rather than paraphrased standard text, move
   those rules into a project-tier SCD in a Domain concept bundle.
3. Remove the Standards bundle from all imports.

Citation format and examples: `spec/0.6/citations.md`.

### 5. Update domain manifests

Replace `satisfies` targets:

```yaml
# 0.5.0
satisfies:
  - scd:standards:iso-13485-clause-7.4
# 0.6.0
satisfies:
  - std:iso-13485:2016#7.4
```

Remove `schemas.standards` if present.

### 6. Validate

```bash
scs-validate --bundle path/to/domain-bundle.yaml
scs-validate --bundle path/to/project-bundle.yaml
```

Deprecation warnings point at any remaining standards bundles, `scd:standards:` references,
and `satisfies` targets.

### 7. Write directives and compile (optional)

To deliver governance to an AI runtime, add `content.directives` to the SCDs whose rules
agents should follow, then compile each bundle:

```bash
scs compile path/to/domain-bundle.yaml -o compiled/global.yaml
scs compile path/to/project-bundle.yaml -o compiled/projects/my-app.yaml
```

See `spec/0.6/runtime-artifact.md`.

---

## Reference

- `spec/0.6/bundle-format.md` — bundle types and rules
- `spec/0.6/citations.md` — standard citations
- `spec/0.6/standards-tier.md` — the deprecation
- `spec/0.6/runtime-artifact.md` — compiled runtime artifacts
- `examples/two-tier-governance/` — a Domain and a Project bundle, compiled
- `examples/med-adherence/` — a Project bundle organized by concept
