# SCS 0.7.0 — Bundle Format

**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-25

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

In SCS 0.6.0, a real (non-`DRAFT`) bundle version serves as an **immutable, approved
contract** for structured context.

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

SCS 0.6.0 defines **four bundle types**, plus one deprecated type:

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
and conventions. It does not import or repeat the organization's Domain bundle. Where both
exist, a consuming tool applies the Domain bundle and the Project bundle side by side
(§4.2); the Project bundle never needs to restate organization-wide rules.

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
`type: standards` in 0.6.0 and SHOULD warn when they encounter one. Domain and Project
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

### 4.1 Two Independent Trees

Governance context is organized as two independent bundle trees:

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

`scd:standards:` references remain valid in 0.6.0 and are deprecated (`citations.md` §6).

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

### 7.4 Independent Versioning

Concept bundles MAY version independently of the bundle that imports them:
- The quality team locks `bundle:design-controls:1.0.0` in week 3
- The security team locks `bundle:data-security:1.0.0` in week 5
- The Domain bundle references specific versions of each

### 7.5 Tiers

A Domain bundle binds meta-tier SCDs (through the pinned meta bundle) and the organization's
project-tier SCDs (through its concept bundles). A Project bundle binds project-tier SCDs
only.

---

## 8. Directory Structure

Domain and Project bundles normally live in separate repositories, owned by the teams that
approve them.

```
org-governance/                      # Domain bundle repository
├── bundles/
│   ├── domain-bundle.yaml           # The Domain bundle
│   └── concepts/
│       ├── design-controls.yaml
│       └── ...
├── context/
│   └── project/                     # Project-tier SCDs holding the org's rules
│       ├── design-change-control.yaml
│       └── ...
├── domain.yaml                      # Domain manifest (ontology)
└── .scs/
    └── config.yaml

project-name/                        # Project bundle repository
├── bundles/
│   └── project-bundle.yaml
├── context/
│   └── project/
│       ├── pump-release-gates.yaml
│       └── ...
└── .scs/
    └── config.yaml
```

The meta bundle is not copied into either repository; tools supply the published version.

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
6. The Domain or Project bundle is approved and locked (e.g., `1.0.0`)
7. The locked bundle is compiled and published for runtime use

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
- Bundle signatures for attestation
- Registry-based bundle resolution
- Scoping a Project bundle to a named Domain bundle
- Bundle dependency graph visualization

---

## 15. Related Documentation

- [Standard Citations](citations.md) - How standards are referenced
- [Runtime Artifact](runtime-artifact.md) - Compiling Domain and Project bundles for runtime delivery
- [Domain Ontology](domain-ontology.md) - Concepts and Ontology Models
- [Bundle Lifecycle](../../docs/bundle-lifecycle.md) - How bundles evolve through development
- [Migration to 0.6.0](../../docs/MIGRATION-0.6.0.md)

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
