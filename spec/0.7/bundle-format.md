# SCS 0.7.0 — Bundle Format

**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-28

---

## 1. Purpose

The **SCS Bundle** is a manifest document that organizes and references Structured Context Documents (SCDs). Bundles are NOT SCDs themselves—they are container documents similar to Docker manifests or Kubernetes pod specifications.

The Bundle Format defines:

- how SCDs are grouped into logical units
- how bundles reference other bundles (imports)
- how bundle types differ (domain, project, meta, concept; standards is deprecated)
- how versions are managed
- how a bundle version gets approved, once it leaves `DRAFT`
- how tools load, validate, and reason over bundles

A real (non-`DRAFT`) bundle version serves as an **immutable, approved contract** for
structured context. It is recorded as a git tag in the owner's Domain repository (§7.3, §8).

### What changed in 0.6.0

- **Domain and Project bundles are independent governance bundles.** A Domain bundle holds an
  organization's governance; a Project bundle holds one project's governance. Neither imports
  the other, and either may exist without the other (§3.1, §3.5, §4).
- **Project bundles no longer import meta, standards, or domain bundles.** They carry only
  project-specific context.
- **Domain bundles import the meta bundle** alongside their concept bundles.
- **Standards bundles are deprecated.** Standards are referenced by citation instead
  (`citations.md`).

See `docs/MIGRATION-0.6.0.md`.

### What changed in 0.7.0

- **Versioned bundles are verifiably immutable.** Versioning records a content digest over
  the bundle's full resolved content; validators and compilers verify it, and a mismatch is
  an error (§7.3, §7.6, §9.6).
- **The git tag is the record of a version.** A version is the tag
  `<workspace>/<bundle-name>-v<version>` on a commit holding the whole workspace. Verification
  reads the tagged content, not only the working tree (§7.3, §7.7).
- **One Domain repository per Domain.** A Domain's context lives in its own git repository,
  holding one Domain workspace and its Project workspaces (§8). A Domain can belong to an
  organization or to one person.

See `docs/MIGRATION-0.7.0.md`.

---

## 2. What Is an SCS Bundle?

An **SCS Bundle** is:

- A YAML manifest file that lists SCDs and imports other bundles
- A container/organizer (NOT content itself)
- Versioned as an immutable set once locked
- Used by tools as the "active context" for evaluation
- The foundation for AI-assisted development and autonomic governance

**Key Principle**: Bundles are manifests. SCDs are content. They are separate document types.

### Container Analogy

Think of SCS bundles like Docker/Kubernetes containers:

| Docker/K8s | SCS Bundle |
|------------|------------|
| Container manifest (`Dockerfile`, K8s Pod spec) | Bundle YAML file |
| Container image | Versioned bundle |
| Base image (`FROM python:3.11`) | Bundle import (`bundle:meta:0.6.0`) |
| Layers | SCDs |
| Container registry | SCS Registry (future) |
| Image tags (`:latest`, `:1.0.0`) | Bundle versions (`DRAFT`, `1.0.0`) |

Just as Docker manifests organize layers without being layers themselves, SCS bundles organize SCDs without being SCDs.

---

## 3. Bundle Types

SCS 0.7.0 defines **four bundle types**, plus one deprecated type:

| Type | Holds | Authored by |
|---|---|---|
| `domain` | An organization's governance | The organization (governance or quality team) |
| `project` | One project's governance | The project team |
| `meta` | Shared vocabulary | SCS specification maintainers |
| `concept` | The SCDs for one Domain Ontology concept | Whoever owns the Domain or Project bundle that imports it |
| `standards` | *Deprecated in 0.6.0* | — |

Domain and Project bundles are the two **governance bundles**: the context an AI agent is
expected to observe and follow. Meta and Concept bundles are building blocks for them.

### 3.1 Project Bundle

**Type**: `project`
**Purpose**: Governance context for a single project
**Cardinality**: 1 per project
**Imports**: MAY import concept bundles; MUST NOT import meta, domain, project, or standards bundles
**SCDs**: Project-tier SCDs, directly or through imported concept bundles (XOR rule, §9.3)

A Project bundle contains only what is specific to its project: its constraints, decisions,
and conventions. The project inherits the organization's Domain rules at runtime, so the
Project bundle does not restate them, and it does not import the Domain bundle. Where both
exist, a consuming tool applies the two together (§4.2).

**Example (SCDs directly):**
```yaml
id: bundle:patient-portal
type: project
version: "1.2.0"
title: "Patient Portal"
description: "Project governance for the patient portal."

imports: []

scds:
  - scd:project:portal-data-boundaries
  - scd:project:portal-release-rules

provenance:
  created_by: "portal-lead@medtech.com"
  created_at: "2026-10-01T09:00:00Z"
  version_approved_by: "portal-lead@medtech.com"
  version_approved_at: "2026-10-15T09:00:00Z"
```

**Example (organized by concept):**
```yaml
id: bundle:patient-portal
type: project
version: "DRAFT"
title: "Patient Portal"
description: "Project governance for the patient portal, organized by concept."

imports:
  - bundle:portal-architecture:1.0.0
  - bundle:portal-security:1.1.0

scds: []

provenance:
  created_by: "portal-lead@medtech.com"
  created_at: "2026-10-01T09:00:00Z"
```

---

### 3.2 Meta Bundle

**Type**: `meta`
**Purpose**: Standard vocabulary and semantic foundations
**Cardinality**: Published once per SCS release; pinned by Domain bundles
**Imports**: None (meta is the foundation)
**SCDs**: Meta-tier SCDs (roles, capabilities, domains, concepts)

The meta bundle is **published and versioned with the SCS specification**. Adopters pin a
version of it from their Domain bundle (e.g. `bundle:meta:0.6.0`); they do not author or
edit it. Tools SHOULD supply the published meta bundle read-only rather than copying it
into adopters' repositories.

**Example**:
```yaml
id: bundle:meta
type: meta
version: "0.6.0"
title: "SCS Meta-Tier Standard Bundle"
description: "Shared SCS vocabulary: roles, capabilities, domains, concepts."

imports: []

scds:
  - scd:meta:roles
  - scd:meta:capabilities
  - scd:meta:domains
  - scd:meta:concepts

provenance:
  created_by: "scs-spec"
  created_at: "2026-10-19T00:00:00Z"
  version_approved_by: "scs-spec"
  version_approved_at: "2026-10-19T00:00:00Z"
```

---

### 3.3 Standards Bundle (Deprecated)

**Type**: `standards`
**Status**: Deprecated in 0.6.0; scheduled for removal in a later release

Standards bundles are no longer part of the bundle model. Tools MUST continue to accept
`type: standards` in 0.7.0 and SHOULD warn when they encounter one. Domain and Project
bundles SHOULD NOT import them.

Standards are referenced by **citation** instead: an SCD's `cites` list, or a `satisfies`
target, names a standard, edition, and clause (e.g. `std:iso-13485:2016#7.3.9`) without
reproducing its text. The organization's own rules, which interpret the standard, belong in
the Domain bundle. See `citations.md` and `standards-tier.md`.

---

### 3.4 Concept Bundle

**Type**: `concept`
**Purpose**: Context for a Domain Ontology concept — a functional area or cross-cutting aspect
**Cardinality**: Variable (depends on the ontology)
**Imports**: MUST NOT import other bundles
**SCDs**: MUST contain at least 1 project-tier SCD

Concept bundles organize context by functional area (architecture, security, risk
management, etc.). The concept itself — its id, taxonomy position, and relationships to
other concepts — is defined once, in the domain manifest's `ontology` block
(`domain-ontology.md`); the concept bundle is where that concept's SCDs live. A Domain
bundle uses concept bundles to hold the organization's rules; a Project bundle MAY use them
to organize project rules the same way. Concepts are **domain-scoped, not reusable across
domains** (RFC-0001, parked indefinitely) — see `terminology.md` §2.12.

**Example (DRAFT — no approval needed yet):**
```yaml
id: bundle:architecture
type: concept
version: "DRAFT"
title: "Architecture Concept Bundle"
description: "System architecture, components, and technical design."

imports: []

scds:
  - scd:project:system-context
  - scd:project:tech-stack
  - scd:project:integration-map
  - scd:project:component-model

provenance:
  created_by: "architecture-team@medtech.com"
  created_at: "2026-09-22T10:00:00Z"
```

**Example (versioned — approval required):**
```yaml
id: bundle:risk-management
type: concept
version: "0.1.0"
title: "Risk Management Concept Bundle"
description: "Risk register, risk-to-requirement traceability, and risk-acceptability criteria per ISO 14971."

imports: []

scds:
  - scd:project:risk-register
  - scd:project:risk-traceability

provenance:
  created_by: "info@ohana-tech.com"
  created_at: "2026-06-04T00:00:00Z"
  version_approved_by: "info@ohana-tech.com"
  version_approved_at: "2026-09-21T00:00:00Z"
  rationale: "Risk management concept bundle for the CDMO reference domain"
```

---

### 3.5 Domain Bundle

**Type**: `domain`
**Purpose**: Governance context for an organization
**Cardinality**: 1 per organization or deployment
**Imports**: MUST import at least one concept bundle; SHOULD import exactly one meta bundle, pinned to a version; MUST NOT import project or domain bundles
**SCDs**: MUST be empty (the organization's rules live in its concept bundles)

A Domain bundle is the organization's governance: the rules that apply to every user,
project, and agent in its scope. Deployments often call it the **Global** context. It is
self-contained: it pins the meta bundle and imports the concept bundles that hold the
organization's rules.

**Industry and organization.** An industry's **Ontology Model** (SDLC, CDMO, MCA —
`domain-ontology.md` §4) is the template for a Domain bundle: a set of concepts with
skeleton SCDs and open decisions. An organization's Domain bundle is that template filled
in with the organization's decisions and approved. It is the same bundle type at a greater
level of detail; only the organization's version is governance. An organization adopts a
model by starting from its template, not by importing an industry bundle.

**Example (an organization built on the MCA ontology):**
```yaml
id: bundle:acme-funding
type: domain
version: "1.0.0"
title: "Acme Funding Governance"
description: "Organization-wide AI governance for Acme Funding."

imports:
  - bundle:meta:0.6.0
  - bundle:governance:1.0.0
  - bundle:ai-accountability:1.0.0
  - bundle:data-security:1.0.0
  - bundle:underwriting-decisioning:1.0.0

scds: []

provenance:
  created_by: "governance@acme-funding.com"
  created_at: "2026-10-01T00:00:00Z"
  version_approved_by: "cco@acme-funding.com"
  version_approved_at: "2026-10-15T00:00:00Z"
  rationale: "First approved organization governance bundle"
```

---

### 3.6 Scope of a Domain Bundle

The validator enforces only structural rules for Domain bundles (§9.3). It does not
enforce what organizational unit a Domain bundle represents. Most deployments have one
Domain bundle for the whole organization. A large organization MAY scope Domain bundles to
a business unit or division with its own governance authority; in that case each such
deployment uses one Domain bundle, not several stacked together.

When deciding scope:

1. **Align with governance authority.** A Domain bundle should be owned by the people
   accountable for the rules in it.
2. **Don't share concept bundles across domains.** Concepts are domain-scoped (RFC-0001).
   If two Domain bundles need the same shape, start both from the same **Ontology Model**
   (`terminology.md` §2.14).
3. **Keep project rules in Project bundles.** A rule that applies to one project belongs
   in that project's bundle, not in the Domain bundle.

---

## 4. Bundle Structure

### 4.1 Two Trees, Applied Together

Governance context is organized as two bundle trees, versioned and compiled separately. At
runtime both apply to a project: the Domain bundle's rules govern every project, and the
Project bundle adds that project's rules (§4.2).

```
Domain Bundle (organization governance, "Global")
├── Meta Bundle (pinned; published with the SCS spec)
└── Concept Bundles (the organization's rules, by ontology concept)
    ├── Governance → SCDs
    ├── Data Security → SCDs
    └── ...

Project Bundle (one project's governance)
├── Project-tier SCDs (directly), or
└── Concept Bundles → SCDs
```

**Key Rules**:
- Domain bundles import one meta bundle and one or more concept bundles (no direct SCDs)
- Project bundles contain project-tier SCDs or import concept bundles (not both)
- Project bundles do not import meta, domain, or other project bundles
- Meta bundles import nothing
- Concept bundles contain SCDs and import nothing
- A deployment MAY have a Domain bundle, Project bundles, or both

### 4.2 Applying Both

When both a Domain bundle and a Project bundle apply to a request, a consuming tool presents
them as separate, ordered context: Domain first, then Project. The bundles do not merge,
and neither overrides the other by import. How a runtime resolves a conflict between a
Domain rule and a Project rule is outside this specification; a common policy is to follow
the stricter rule.

---

## 5. Bundle Manifest Format

### 5.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique bundle identifier (`bundle:name`) |
| `type` | enum | Bundle type: `domain`, `project`, `meta`, `concept` (`standards` deprecated) |
| `version` | string | Semantic version (`1.0.0`) or `DRAFT` |
| `title` | string | Human-readable bundle title |
| `description` | string | Summary of what this bundle represents |
| `imports` | array | List of bundle references with versions |
| `scds` | array | List of SCD references included in this bundle |
| `provenance` | object | Authorship and change history |

### 5.2 Version Format

Versions MUST follow one of these patterns:
- **Semantic version**: `1.0.0`, `2.1.3` (immutable, locked)
- **Draft**: `DRAFT` (mutable, working state)

Once a bundle is versioned (e.g., `1.0.0`), it becomes immutable.

### 5.3 Bundle References

Bundle imports use this format:
```
bundle:<name>:<version>
```

Examples:
- `bundle:meta:0.6.0` - Versioned meta bundle
- `bundle:architecture:1.0.0` - Versioned concept bundle

### 5.4 SCD References

SCD references use this format:
```
scd:<tier>:<name>
```

Examples:
- `scd:meta:roles` - Meta-tier SCD
- `scd:project:system-context` - Project-tier SCD

`scd:standards:` references remain valid and have been deprecated since 0.6.0 (`citations.md` §6).

---

## 6. Complete Example

An organization with one Domain bundle and one Project bundle. The two are authored and
versioned separately.

**Domain Bundle** (`governance/bundles/domain-bundle.yaml`):
```yaml
id: bundle:medtech-cdmo
type: domain
version: "1.0.0"
title: "MedTech CDMO Governance"
description: >
  Organization-wide governance for MedTech CDMO, built on the CDMO ontology.

imports:
  - bundle:meta:0.6.0
  - bundle:design-controls:1.0.0
  - bundle:risk-management:1.0.0
  - bundle:document-control:1.0.0

scds: []

provenance:
  created_by: "quality@medtech.com"
  created_at: "2026-10-01T09:00:00Z"
  version_approved_by: "qa-director@medtech.com"
  version_approved_at: "2026-10-10T14:00:00Z"
  rationale: "Organization governance v1.0.0"
```

**Concept Bundle** (`governance/bundles/concepts/design-controls.yaml`):
```yaml
id: bundle:design-controls
type: concept
version: "1.0.0"
title: "Design Controls"
description: >
  Organization rules for design planning, review, verification, and change control.

imports: []

scds:
  - scd:project:design-review-rules
  - scd:project:design-change-control

provenance:
  created_by: "quality@medtech.com"
  created_at: "2026-10-01T09:00:00Z"
  version_approved_by: "qa-director@medtech.com"
  version_approved_at: "2026-10-10T14:00:00Z"
```

**Project Bundle** (`infusion-pump-fw/bundles/project-bundle.yaml`):
```yaml
id: bundle:infusion-pump-fw
type: project
version: "0.3.0"
title: "Infusion Pump Firmware"
description: >
  Project governance for the infusion pump firmware program.

imports: []

scds:
  - scd:project:pump-software-safety-class
  - scd:project:pump-release-gates

provenance:
  created_by: "fw-lead@medtech.com"
  created_at: "2026-10-05T09:00:00Z"
  version_approved_by: "fw-lead@medtech.com"
  version_approved_at: "2026-10-12T11:30:00Z"
  rationale: "Project rules for the 0.3 milestone"
```

---

## 7. Bundle Semantics

### 7.1 Independence of Governance Bundles

Domain and Project bundles are independent. Neither imports the other, neither is required
for the other to be valid, and each follows its own version lifecycle. A Project bundle is
complete when it holds its project's governance; it does not need to contain the
organization's.

### 7.2 Roots

Each governance bundle is the root of its own tree. Tools that load, validate, or compile
context start from a Domain bundle or a Project bundle and resolve its imports. There is no
single root that combines both.

### 7.3 Immutability

Once versioned (e.g., `1.0.0`), a bundle MUST remain immutable. Changes require a new version.

**Lifecycle**:
1. Create bundle in `DRAFT` state
2. Iterate and refine in `DRAFT` mode
3. Lock and version (e.g., `1.0.0`)
4. Bundle becomes immutable contract
5. Future changes create new versions (e.g., `1.1.0`)

Immutability covers the bundle's full resolved content: its manifest, every SCD it lists, and
every bundle it imports. Editing an SCD after `1.0.0` changes what `1.0.0` means, so it is a
change to the bundle. A versioned bundle MUST be verifiably unchanged after it is versioned.

**The tag is the record.** A version of a bundle is the git tag
`<workspace>/<bundle-name>-v<version>` (§8.5) on a commit that holds the whole workspace
directory except `dist/`. The version manifest at that tag records the approver, the
validation result, and the content digest (§7.6). Verification reads the tagged content and the
tagged manifest, never only the working tree, so editing a manifest in place cannot vouch for
changed content (§7.7). Because the tagged commit holds every compiler input, any version can be
rebuilt from its tag.

The working bundle file stays `DRAFT` after versioning; the released copy is the snapshot
beside it, and the record is the tag.

### 7.4 Independent Versioning

Concept bundles MAY version independently of the bundle that imports them:
- The quality team locks `bundle:design-controls:1.0.0` in week 3
- The security team locks `bundle:data-security:1.0.0` in week 5
- The Domain bundle references specific versions of each

### 7.5 Tiers

A Domain bundle binds meta-tier SCDs (through the pinned meta bundle) and the organization's
project-tier SCDs (through its concept bundles). A Project bundle binds project-tier SCDs
only.

### 7.6 Content Digest

A versioned bundle's **content digest** identifies its full resolved content. Tools that
version a bundle MUST record it; tools that read a versioned bundle verify against it.

**Canonical form.** Each document (a bundle manifest or an SCD) is parsed and serialized as
JSON with keys sorted, no insignificant whitespace, and non-ASCII characters unescaped,
encoded as UTF-8. Mapping keys are serialized as strings. A YAML date is serialized as
`YYYY-MM-DD`; a YAML timestamp as ISO 8601 (`YYYY-MM-DDTHH:MM:SS`, with fractional seconds
when present and a `+HH:MM` offset when it has a time zone). Because documents are parsed
first, edits to comments, key order, quoting, or layout do not change a digest; edits to
content do. A document's digest is `sha256:` followed by the lowercase hexadecimal SHA-256 of
its canonical form.

**Content digest.** The content digest of a bundle is the digest of the JSON array

```
[ <digest of the bundle manifest>,
  [[<SCD id>, <digest of the SCD>], ...],              // SCDs it lists, sorted by id
  [[<import reference>, <content digest of import>], ...] ]  // its imports, sorted by reference
```

serialized in canonical form. Import references are taken as written
(`bundle:design-controls:1.0.0`). An SCD that cannot be found, or an import that does not
resolve to a bundle of the pinned version, contributes `null`, so adding it later changes
the digest. Imports are digested recursively, so the root's digest covers the whole tree.

**Version manifest.** `scs bundle version` writes a version manifest beside the versioned
bundle, named `<bundle-name>-v<version>-MANIFEST.yaml`, which validates against
`schema/manifest/version-manifest-schema.json`. It MUST contain `content_digest`
(`sha256:<64 hex digits>`) and `tools_version`, and SHOULD contain `content_inputs`: the digest
of every bundle manifest and SCD in the tree, used only to name what changed on a mismatch. A
manifest is recognized as 0.7 by its workspace-qualified tag (§8.5), not by a field value; the
schema keeps `content_digest` and `tools_version` optional so manifests written before 0.7
still validate, and the requirement is checked with the tags (§7.7).

```yaml
content_digest: sha256:ec9de04bb0bb4cb2768d91ce4e9011cfaf77ebb72c614266e008f4f6e7cf9ff3
content_inputs:
  bundles:
    bundle:design-controls:1.0.0: sha256:0c3c13b0ade13d2c1fc9faecdab0afd7d83f4adfd4c5b508b9355d496297260a
    bundle:medtech-cdmo:1.1.0: sha256:134cbd2fb451d3c4d801e589c0bac7162e8912eb918a3b517367979d4619c62b
    # ... every other bundle in the tree
  scds:
    scd:project:design-change-control: sha256:58ec9b92125a111a1e35037d32b51d78a2b245e783950e1eaeac8d7b3e62991f
    # ... every other SCD in the tree
```

The versioned bundle's `provenance` records `validation_passed` and `approval_status` from
what happened: a bundle versioned without validation records `validation_passed: false` and
`approval_status: approved` rather than `validated`.

**Digest checks.** A validator or compiler given a versioned bundle recomputes its content
digest and compares it with its version manifest's `content_digest`:

- A mismatch is an error in every mode. The diagnostic SHOULD name the bundles and SCDs whose
  content changed. A compiler MUST refuse to compile, with no override; a changed bundle needs
  a new version.
- A version manifest with no `content_digest` (written before 0.7) produces a warning that
  the bundle cannot be verified. Versioning it again at a new version makes it verifiable.
- A versioned bundle with no version manifest (for example, one published with the
  specification, such as the meta bundle) has nothing to verify against and is not reported.

Every versioned bundle in a tree that has a version manifest is verified, not only the root.
In a Domain repository these checks read the tags (§7.7).

A compiled artifact carries the root's content digest as `source_digest`
([runtime-artifact.md](runtime-artifact.md) §3.1), so a rendering can be checked against the
exact content it came from. Compiling at a checkout of a version's tag, with the
`tools_version` its manifest records, gives an artifact with the same `source_digest` and the
same content as the original, apart from the fields
[runtime-artifact.md](runtime-artifact.md) §3.5 declares variable.

### 7.7 Verification of Versions

Run at the root of a Domain repository, a validator MUST make three checks, each an error in
every mode:

1. **Every version tag.** The digest recomputed from the tagged content equals the tagged
   manifest's `content_digest`, and each pinned import's manifest at that commit equals the
   import's own tagged manifest. A workspace-qualified tag with no manifest at the tag
   (`VERSION_MANIFEST_MISSING`), and a manifest carrying `content_digest` with no qualified tag
   (`VERSION_TAG_MISSING`), are errors.
2. **Working copies of versions in use.** For each version pinned by a working bundle, and the
   latest version of each bundle whose working file exists, the working manifest and snapshot
   equal their tagged copies, compared by git blob id (`MANIFEST_ALTERED`). Versions of a
   removed bundle are history, still covered by check 1.
3. **Drift.** Each pinned import of a working bundle matches its tagged content
   (`CONTENT_DIGEST_MISMATCH`). The diagnostic SHOULD name the files whose content changed and
   the bundles to version again.

All three read tags, so validating a Domain repository from a shallow clone is an error
(`GIT_HISTORY_INCOMPLETE`). A single version can be checked on request
(`scs-validate --verify-version <tag>`). Versions recorded without a workspace-qualified tag
(before 0.7) are history: they are not verified and not reported. Migrating a bundle means
versioning it once under 0.7.

A compiler MUST run these checks for the tree it compiles, including when the root is `DRAFT`,
and MUST refuse on a failure. There is no override; a changed bundle needs a new version.

A tool that versions a bundle MUST record `validation_passed` and `approval_status` in the
version from what actually happened. Skipping content validation (schemas and rules) does not
skip these integrity checks, and the version records `validation_passed: false`.

### 7.8 Boundary of the Integrity Model

Git allows anyone with write access to delete and recreate a tag. The checks in §7.6 and §7.7
detect change that was not recorded as a new version. They do not defend against someone who
rewrites both the content and the tag. Signed tags are out of scope for 0.7. Protecting version
tags on a shared remote, for example with tag protection rules, is the adopter's
responsibility.

---

## 8. Domain Repositories

### 8.1 One Repository per Domain

Every Domain MUST have its own git repository, called a **Domain repository**. A Domain
repository holds exactly one Domain workspace, under `domain/`, and zero or more Project
workspaces, each under `projects/<name>/`. A Project belongs to the Domain whose repository it
is in. No field records the relationship, because the layout does.

A Domain can belong to an organization or to one person (`terminology.md` §2.11). A person can
have several Domains, for example one for personal work and one for work done for an employer;
each has its own repository.

The Domain and Project bundles keep the model of §7.1: a Project bundle does not import the
Domain bundle, and each is validated, versioned, and compiled on its own. They sit in separate
directories because their artifacts are placed separately, not because either depends on the
other.

Application repositories that consume the context are separate and MUST NOT be used to author
it. Domain repository names SHOULD follow `<domain-name>-context` (for example
`medtech-cdmo-context`, `jdoe-context`).

### 8.2 Layout

```
medtech-cdmo-context/
├── AGENTS.md                      # agent instructions: purpose and boundaries of this repo
├── CLAUDE.md                      # pointer to AGENTS.md
├── .gitignore                     # ignores sources/ by default
├── .gitattributes                 # * text eol=lf
├── .github/workflows/scs-validate.yml
├── domain/                        # the Domain workspace
│   ├── .scs/config                # workspace marker: bundle_type, name, ontology, scs_version, tools_version
│   ├── intake.yaml                # intake record (§8.4)
│   ├── ontology/
│   │   └── domain-manifest.yaml   # ontology manifest (domain-ontology.md)
│   ├── bundles/
│   │   ├── domain-bundle.yaml
│   │   └── concepts/
│   ├── context/
│   │   └── project/               # SCDs
│   ├── sources/                   # optional source documents (§8.6)
│   └── dist/                      # compiled artifacts (§8.7)
└── projects/
    └── infusion-pump-fw/          # a Project workspace
        ├── .scs/config
        ├── intake.yaml
        ├── ontology/
        ├── bundles/
        │   ├── project-bundle.yaml
        │   └── concepts/
        ├── context/
        │   └── project/
        ├── sources/
        └── dist/
```

The meta bundle is not copied into the repository; tools supply the published version.

### 8.3 Workspaces

A **workspace** is a directory with a `.scs/config` file: the Domain workspace or one Project
workspace. A workspace's name is `domain` for the Domain workspace and the directory name under
`projects/` for a Project. The `name` in its `.scs/config` MUST match.

The ontology manifest lives at `ontology/domain-manifest.yaml` in each workspace. SCS 0.6
placed it at `domain/domain-manifest.yaml`, which would become `domain/domain/` in a Domain
workspace; tools still read the 0.6 location and report it as information.

A workspace's starting set of concept bundles and SCD templates depends on two things only: its
ontology (`sdlc`, `cdmo`, `mca`, `personal`, and others added later) and its kind (Domain or
Project). Each ontology provides one set for a Domain workspace and one for a Project workspace.
The `personal` ontology provides one fixed concept, boundaries (the `prohibited` concept
bundle); a person's other concepts are defined with them. What does not apply is removed.

### 8.4 Intake Record

A workspace MAY hold an **intake record**, `intake.yaml` at the workspace root
(`domain/intake.yaml`, `projects/<name>/intake.yaml`). It records the answers that scaffolding
and drafting were based on, the approvers, source documents, and review findings, so an intake
can be resumed, revisited, and audited. It is not an SCD and is never compiled. When present,
it MUST validate against `schema/intake/intake-schema.json` (`INTAKE_SCHEMA_INVALID`). The
engine's intake commands are its only writers (`agent-interface.md` §5.3).

People in the record are identified as `Name <email>`. For a repository that will be shared
publicly, the record MAY use role-only attribution instead, written `role:<name>` (for example
`role:quality-manager`). Role-only attribution is allowed in the intake record only; a version
manifest's approver is always a person.

### 8.5 Versions in the Repository

Each bundle is versioned on its own. Bundle versions MUST be recorded as git tags in the Domain
repository. Because several workspaces, and their concept bundles, are versioned in one
repository, tags MUST be qualified by workspace and bundle name:
`<workspace>/<bundle-name>-v<version>`, where `<workspace>` is `domain` or the Project name (for
example `domain/company-v1.0.0`, `infusion-pump-fw/design-controls-v1.0.0`).

Version manifests MUST be named `<bundle-name>-v<version>-MANIFEST.yaml`, and snapshots
`<bundle-name>-v<version>.yaml`, in the bundle's directory. The location supplies the
workspace, so no two bundles share a manifest file. The bundle names `plan`, `test-plan`, and
`qa` are reserved for a later release, so its tags cannot collide with a bundle's.

A tool that versions a bundle:

- commits everything under the workspace directory except `dist/`, including deletions, and
  nothing outside it, then creates an annotated tag on that commit;
- refuses if a file the digest or the compiler reads is ignored or untracked, or if git is not
  available. An existing version is never rewritten;
- refuses if an import is unpinned or `DRAFT`;
- records the approver as the commit's author. The committer and the tagger are the fixed
  identity `scs-tools <noreply@scs.invalid>`. Neither identity is read from the environment;
- on failure at any step, undoes what that run wrote, leaving the working tree, index, and refs
  as they were.

### 8.6 Source Documents and Reserved Directories

`sources/` holds documents that SCDs were drafted from. The generated `.gitignore` ignores it,
so source documents stay local unless the owner chooses to track them. An SCD item's
`derived_from` still names the document. Compilers never read `sources/`, so ignoring it does
not affect rebuilding a version.

`plan/`, `test-plan/`, and `qa/` are reserved in every workspace for a later release. SCS 0.7
defines no content for them, and validators and compilers do not read them.

### 8.7 Compiled Output

A compiler SHOULD write to the workspace's `dist/` directory, named
`<bundle-name>-<version>.yaml`. Compiling a released version reads it from its tag; compiling the
working `DRAFT` is an explicit choice. Whether `dist/` is committed is the owner's choice; every
artifact can be rebuilt from its tag. Placing an artifact where an AI service reads it is the
owner's decision, outside SCS (`overview.md` §1.1).

### 8.8 Agent Instructions and CI

A tool that creates a Domain repository MUST generate an agent instructions file stating that
the repository manages SCS context for one named Domain and its Projects, that work in it is
limited to creating, maintaining, validating, versioning, and compiling that context, and that
application work belongs elsewhere. `AGENTS.md` is the default; the tool SHOULD also generate a
client-specific file (for example `CLAUDE.md`) that points to it, for clients that read only
their own file.

The tool SHOULD also generate a CI workflow that validates the Domain workspace and every
Project workspace with `scs-validate --strict` on every push. Validation reads tags (§7.7), so
the workflow MUST fetch full history and tags (for GitHub Actions, `fetch-depth: 0`). The
workflow is a convenience, not a requirement of conformance.

---

## 9. Validation Requirements

Tools MUST validate that:

### 9.1 Schema Validation
- Bundle conforms to JSON schema (`schema/bundles/scd-bundle-schema.json`)
- All required fields present
- Field types and patterns correct
- Conditional rules satisfied (e.g., concept bundles have no imports)

### 9.2 Reference Resolution
- All SCD references resolve to actual SCD files
- All bundle imports resolve to actual bundle files (the meta bundle MAY resolve to the
  copy published with the SCS tooling)
- No circular imports
- SCD identifiers are unique within the resolved bundle tree

### 9.3 Type Consistency
- Every bundle contains imports or SCDs, not both and not neither (XOR rule)
- Concept bundles MUST NOT import other bundles and MUST contain at least one SCD
- Domain bundles MUST import at least one concept bundle, SHOULD import exactly one meta
  bundle, MUST NOT import project or domain bundles, and MUST NOT directly contain SCDs
- Project bundles MAY import concept bundles and MUST NOT import meta, domain, project, or
  standards bundles
- Meta bundles contain only meta-tier SCDs and import nothing
- `type: standards` bundles and `scd:standards:` references produce a deprecation warning

### 9.4 Version Consistency
- Version follows semantic versioning or `DRAFT`
- Imported bundle versions exist
- No conflicting version requirements
- The meta bundle import SHOULD pin a version (`bundle:meta:0.6.0`)

### 9.5 Approval (non-`DRAFT` versions only)
- `provenance.version_approved_by` and `version_approved_at` are present once `version` is
  a real semantic version — not required while `version: "DRAFT"` (RFC-0001, Provenance and
  approval)

### 9.6 Content Digest (versioned bundles with a version manifest)
- The recomputed content digest matches the version manifest's `content_digest` (§7.6); a
  mismatch is an error in every mode
- A version manifest with no `content_digest` is a warning
- In a Domain repository, the three checks of §7.7 pass

### 9.7 Domain Repository and Workspaces
- A workspace's `.scs/config` `name` MUST match its workspace name (`CONFIG_NAME_MISMATCH`, §8.3)
- Run at the root of a Domain repository, the validator SHOULD validate the Domain workspace
  and every Project workspace, and report a repository with no workspace whose
  `.scs/config` `bundle_type` is `domain`, or with more than one, as an error
  (`DOMAIN_WORKSPACE_MISSING`, `DOMAIN_WORKSPACE_MULTIPLE`)
- The validator MUST NOT report a workspace's reserved directories (`plan/`, `test-plan/`,
  `qa/`) as errors or warnings in any mode, and MUST NOT validate their content (§8.6)
- A bundle named `plan`, `test-plan`, or `qa` is an error (`RESERVED_BUNDLE_NAME`, §8.5)

### 9.8 Provenance
- A version manifest's `approval.approved_by` MUST be a person identifier, `Name <email>`; the
  version manifest schema rejects empty and `role:` values
- A placeholder `created_by` (an empty name, `developer`, or an address at `example.com`,
  `example.org`, `example.net`, or a `.example` or `.invalid` domain) is a warning
  (`PROVENANCE_PLACEHOLDER`), and a tool that versions a bundle MUST refuse to version over one
  (`VERSION_PROVENANCE_PLACEHOLDER`). Any other `created_by` value passes
- A `derived_from.intake` id MUST resolve to an `answers[].id` in the workspace's intake record,
  and a `derived_from.source` id to a `source_documents[].id`; an unresolved id is a warning
  (`DERIVED_FROM_UNRESOLVED`), so it fails under `--strict` with exit code 2 (`core-model.md`
  §4.1)

### 9.9 Empty SCDs
- An SCD with no `prohibitions`, `directives`, or `facts` contributes nothing to a compiled
  artifact. The validator MUST report it as `SCD_EMPTY` (info), so a fresh scaffold still passes
  `--strict`
- A tool that versions a bundle MUST list the bundle's empty SCDs in its dry run, so they are
  removed or kept knowingly before a release
- The 0.6 stub detection (`COMPLETENESS_STUB_SCD`) is removed

Tools MAY also perform:
- Compliance completeness checks
- Dependency cycle analysis
- Minimum SCD requirements validation

---

## 10. Bundle Lifecycle

### 10.1 DRAFT State

During development, bundles use `version: "DRAFT"`:
- Mutable (can be changed)
- No strict validation (warnings instead of errors)
- Used for active development

### 10.2 VERSIONED State

When ready to lock, bundles receive semantic versions (e.g., `1.0.0`):
- Immutable (cannot be changed)
- Strict validation (all errors must be fixed)
- Requires `provenance.version_approved_by` / `version_approved_at` — a real version is
  approved, not just authored (RFC-0001). A `DRAFT` bundle has no approval fields because
  there's nothing to approve yet.
- Serves as binding contract

### 10.3 Versioning Workflow

Domain and Project bundles follow the same workflow, independently:

1. Owners create concept bundles and SCDs in `DRAFT` state
2. Owners iterate, add SCDs, refine content
3. Owners validate the bundle tree
4. Owners lock concept bundles with versions (e.g., `bundle:design-controls:1.0.0`)
5. The Domain or Project bundle imports the versioned concept bundles (or lists its SCDs)
6. The Domain or Project bundle is approved and locked (e.g., `1.0.0`), recorded as its tag
   (§8.5)
7. The locked bundle is compiled; where its artifact is placed is the owner's decision (§8.7)

---

## 11. Choosing Bundles

**An organization** typically maintains:
- **1 Domain bundle**, started from the Ontology Model for its industry and pinning the
  published meta bundle

**Each project** typically maintains:
- **1 Project bundle** with its project-specific rules

**There are no universally prescribed concepts** — the appropriate concepts depend on the
Ontology Model the organization starts from (SDLC, CDMO, MCA, or one adapted from them).

---

## 12. Examples

Working examples are available in `examples/`:
- `examples/merchant-cash-advance/` - MCA Ontology Model template: concept bundles and
  skeleton SCDs
- `examples/medical-device-cdmo/` - CDMO Ontology Model with taxonomy and `satisfies`
  citations
- `examples/med-adherence/` - A Project bundle organized by concept, with standard
  citations
- `examples/chai-standards-bundle/` - A standards bundle (deprecated in 0.6.0; kept for
  reference)

---

## 13. Schema Reference

**Bundle Schema**: `schema/bundles/scd-bundle-schema.json`
**Domain Manifest Schema**: `schema/domain/domain-manifest-schema.json` (the `ontology`
block — see `domain-ontology.md`)
**SCD Schemas**:
- Meta-tier: `schema/scd/meta-scd-template.json`
- Project-tier: `schema/scd/project-scd-template.json`
- Standards-tier (deprecated): `schema/scd/standards-scd-template.json`

---

## 14. Future Extensions

Future versions may introduce:
- Bundle signatures for attestation (signed tags, §7.8)
- Bundle dependency graph visualization

---

## 15. Related Documentation

- [Standard Citations](citations.md) - How standards are referenced
- [Runtime Artifact](runtime-artifact.md) - Compiling Domain and Project bundles for runtime delivery
- [Domain Ontology](domain-ontology.md) - Concepts and Ontology Models
- [Bundle Lifecycle](../../docs/bundle-lifecycle.md) - How bundles evolve through development
- [Migration to 0.6.0](../../docs/MIGRATION-0.6.0.md)
- [Migration to 0.7.0](../../docs/MIGRATION-0.7.0.md)

---

## 16. Key Takeaways

1. **Bundles are manifests, not content** - They organize and reference SCDs
2. **Two governance bundles** - Domain (the organization) and Project (one project)
3. **Independent** - Neither imports the other; either can exist alone
4. **Meta comes from the spec** - Domain bundles pin it; adopters don't author it
5. **Standards are cited, not bundled** - `std:iso-13485:2016#7.3.9`
6. **Approved contracts** - A real (non-`DRAFT`) version requires
   `version_approved_by`/`version_approved_at`, then it's locked
7. **Industry → organization** - An Ontology Model is the template; the organization's
   Domain bundle is that template filled in and approved

---

## 17. Feedback

Comments and refinements for the Bundle Format should be submitted through:
- [GitHub Issues](https://github.com/tim-mccrimmon/scs-spec/issues)
- [GitHub Discussions](https://github.com/tim-mccrimmon/scs-spec/discussions)
