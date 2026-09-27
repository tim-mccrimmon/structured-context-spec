# SCS 0.5.0 — Bundle Format

**Version:** 0.5.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-09-22

---

## 1. Purpose

The **SCS Bundle** is a manifest document that organizes and references Structured Context Documents (SCDs). Bundles are NOT SCDs themselves—they are container documents similar to Docker manifests or Kubernetes pod specifications.

The Bundle Format defines:

- how SCDs are grouped into logical units
- how bundles reference other bundles (imports)
- how bundle types differ (project, meta, standards, concept, domain)
- how versions and tier boundaries are managed
- how a bundle version gets approved, once it leaves `DRAFT`
- how tools load, validate, and reason over context hierarchies

In SCS 0.5.0, a real (non-`DRAFT`) bundle version serves as an **immutable, approved
contract** for structured context.

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
| Base image (`FROM python:3.11`) | Bundle import (`bundle:meta:1.0.0`) |
| Layers | SCDs |
| `docker-compose.yml` | Project bundle |
| Container registry | SCS Registry (future) |
| Image tags (`:latest`, `:1.0.0`) | Bundle versions (`DRAFT`, `1.0.0`) |

Just as Docker manifests organize layers without being layers themselves, SCS bundles organize SCDs without being SCDs.

---

## 3. Bundle Types

SCS 0.5.0 defines **five bundle types**:

### 3.1 Project Bundle

**Type**: `project`
**Purpose**: Top-level orchestrator bundle for a complete project
**Cardinality**: 1 per project
**Imports**: MUST import meta, standards, and domain bundles
**SCDs**: Typically empty (all context in imported bundles)

The project bundle is the single entry point for all project context.

**Example**:
```yaml
id: bundle:medication-adherence
type: project
version: "1.0.0"
title: "Medication Adherence System"

imports:
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  # ... all domain bundles

scds: []
```

---

### 3.2 Meta Bundle

**Type**: `meta`
**Purpose**: Standard vocabulary and semantic foundations
**Cardinality**: 1 per project (imported from SCS specification)
**Imports**: None (meta is the foundation)
**SCDs**: Meta-tier SCDs (roles, capabilities, domains, concepts)

The meta bundle provides standardized terminology that all projects reference.

**Example**:
```yaml
id: bundle:meta
type: meta
version: "1.0.0"
title: "SCS Meta-Tier Standard Bundle"

imports: []

scds:
  - scd:meta:roles
  - scd:meta:capabilities
  - scd:meta:domains
  - scd:meta:concepts
```

---

### 3.3 Standards Bundle

**Type**: `standards`
**Purpose**: Compliance and regulatory requirements
**Cardinality**: 1 per project
**Imports**: MAY import other standards bundles (e.g., SOC2, ISO27001)
**SCDs**: Standards-tier SCDs (project-specific interpretations)

Standards bundles combine external compliance frameworks with project-specific mappings.
Like other bundle types, a standards bundle follows the XOR rule (§9.3): it either imports
other standards bundles, or contains standards-tier SCDs directly — not both in the same
bundle.

**Example (containing SCDs directly)**:
```yaml
id: bundle:standards
type: standards
version: "1.0.0"
title: "Compliance Standards Bundle"

imports: []

scds:
  - scd:standards:hipaa-privacy-rule
  - scd:standards:hipaa-security-rule
```

---

### 3.4 Concept Bundle

**Type**: `concept`
**Purpose**: Context for a Domain Ontology concept — a functional area or cross-cutting aspect
**Cardinality**: Variable (depends on domain)
**Imports**: MUST NOT import other bundles
**SCDs**: MUST contain at least 1 project-tier SCD

Concept bundles organize project-specific context by functional area (architecture, security,
performance, etc.). The concept itself — its id, taxonomy position, and relationships to
other concepts — is defined once, in the domain manifest's `ontology` block
(`domain-ontology.md`); the concept bundle here is where that concept's SCDs live. Unlike
"concepts" in 0.3, concept bundles are **domain-scoped, not reusable across domains**
(RFC-0001, parked indefinitely) — see `terminology.md` §2.12.

**Example (Software Development domain, DRAFT — no approval needed yet):**
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

**Example (Medical-Device CDMO domain, versioned — approval required):**
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
**Purpose**: Entry point for an industry vertical or professional domain
**Cardinality**: 1+ per project (Software Development + optional vertical domains)
**Imports**: MUST import concept bundles
**SCDs**: Typically empty (all context in imported concepts)

Domain bundles represent industry verticals (Software Development, Legal, Clinical, etc.) and import the concept bundles appropriate for that domain.

**Example (Software Development domain):**
```yaml
id: bundle:software-development
type: domain
version: "1.0.0"
title: "Software Development Domain"

imports:
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  - bundle:performance-reliability:1.0.0
  - bundle:testing-validation:1.0.0
  - bundle:deployment-operations:1.0.0
  - bundle:data-provenance:1.0.0
  - bundle:compliance-governance:1.0.0
  - bundle:usability-accessibility:1.0.0
  - bundle:safety-risk:1.0.0
  - bundle:ethics-ai-accountability:1.0.0
  - bundle:business-context:1.0.0

scds: []
```

**Example (Legal domain):**
```yaml
id: bundle:legal
type: domain
version: "1.0.0"
title: "Legal Practice Domain"

imports:
  - bundle:case-management:1.0.0
  - bundle:legal-research:1.0.0
  - bundle:client-communication:1.0.0
  - bundle:document-drafting:1.0.0

scds: []
```

---

## 3.6 Alternative Domain Bundle Uses

### Implementation Flexibility

The SCS specification defines Domain bundles structurally: they aggregate Concept bundles and contain no direct SCDs. While the **reference implementation** uses Domain bundles to represent **industry verticals** (Software Development, Legal, Clinical), the bundle type is intentionally flexible.

The validator enforces only **structural rules**:
- `type: domain`
- Imports ≥1 concept bundle
- SCDs array must be empty

The validator does **not** enforce:
- What the domain represents semantically
- How domains are scoped organizationally
- The naming convention for domain bundles

### Alternative Organizational Scopes

Implementations may use Domain bundles to represent different organizational units:

#### **Companies/Enterprises**
```yaml
id: bundle:acme-health-corp
type: domain
title: "Acme Health Corporation - Company Domain"

imports:
  - bundle:acme-architecture:1.0.0
  - bundle:acme-security:1.0.0
  - bundle:acme-clinical-workflow:1.0.0
  # Company-specific concept bundles

scds: []
```

**Use case**: Centralized governance where a company maintains concept bundles representing functional areas within the organization. The domain bundle serves as the corporate context aggregator.

#### **Business Units/Divisions**
```yaml
id: bundle:acme-radiology-division
type: domain
title: "Acme Health - Radiology Division"

imports:
  - bundle:radiology-operations:1.0.0
  - bundle:imaging-protocols:1.0.0
  - bundle:patient-safety:1.0.0

scds: []
```

**Use case**: Large organizations with distinct business units, each with their own concept bundles and governance requirements.

#### **Product Lines**
```yaml
id: bundle:acme-patient-portal
type: domain
title: "Acme Health - Patient Portal Product Line"

imports:
  - bundle:portal-architecture:1.0.0
  - bundle:portal-security:1.0.0
  - bundle:patient-engagement:1.0.0

scds: []
```

**Use case**: Product-specific context where each product maintains its own set of concepts.

### Guidance for Implementers

When deciding how to scope your Domain bundles:

1. **Consider governance boundaries**: Domain bundles should align with organizational ownership and decision-making authority
2. **Don't try to share concept bundles across domains**: concepts are domain-scoped
   (RFC-0001, parked indefinitely) — a `concept:risk-management` in one domain and one in
   another are separately defined, even if named the same. If two domains genuinely need
   the same shape, start both from the same **Ontology Model** (`terminology.md` §2.14)
   instead of trying to import one domain's concept bundle into another.
3. **Document your choice**: Clearly explain in your implementation documentation how you're using Domain bundles
4. **Stay consistent**: Use the same scoping approach across your implementation

### Validator Neutrality

The SCS validator is **semantically neutral** and supports all these organizational patterns. As long as the structural rules are satisfied, any organizational scope is valid.

The reference implementation (Software Development domain) serves as a canonical example, not a prescriptive constraint.

---

## 4. Bundle Hierarchy

Bundles form a four-level hierarchy:

```
Project Bundle (top-level)
├── Meta Bundle (foundation)
├── Standards Bundle (compliance)
└── Domain Bundles (industry verticals)
    ├── Software Development Domain
    │   └── Concept Bundles
    │       ├── Architecture → SCDs
    │       ├── Security → SCDs
    │       ├── Performance & Reliability → SCDs
    │       ├── Testing & Validation → SCDs
    │       ├── Deployment & Operations → SCDs
    │       ├── Data & Provenance → SCDs
    │       ├── Compliance & Governance → SCDs
    │       ├── Usability & Accessibility → SCDs
    │       ├── Safety & Risk → SCDs
    │       ├── Ethics & AI Accountability → SCDs
    │       └── Business Context → SCDs
    │
    └── Legal Domain (optional)
        └── Concept Bundles
            ├── Case Management → SCDs
            ├── Legal Research → SCDs
            ├── Client Communication → SCDs
            └── Document Drafting → SCDs
```

**Key Rules**:
- Project bundle imports meta, standards, and domain bundles
- Meta bundle imports nothing (it's the foundation)
- Standards bundle may import other standards bundles
- Domain bundles import concept bundles (no direct SCDs)
- Concept bundles contain SCDs (no imports)

**Hierarchy Summary**: Project → Domain → Concept → SCD

---

## 5. Bundle Manifest Format

### 5.1 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique bundle identifier (`bundle:name`) |
| `type` | enum | Bundle type: `project`, `meta`, `standards`, `concept`, `domain` |
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
- `bundle:meta:1.0.0` - Versioned meta bundle
- `bundle:architecture:1.0.0` - Versioned domain bundle
- `bundle:standards:soc2-type2:2023.1` - External standards bundle

### 5.4 SCD References

SCD references use this format:
```
scd:<tier>:<name>
```

Examples:
- `scd:meta:roles` - Meta-tier SCD
- `scd:standards:hipaa-privacy-rule` - Standards-tier SCD
- `scd:project:system-context` - Project-tier SCD

---

## 6. Complete Example

**Project Bundle** (`bundles/project-bundle.yaml`):
```yaml
id: bundle:medication-adherence
type: project
version: "1.0.0"
title: "Medication Adherence System - Complete Context Bundle"
description: >
  Complete structured context bundle for the Medication Adherence system.

imports:
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0
  - bundle:software-development:1.0.0
  - bundle:clinical:1.0.0

scds: []

provenance:
  created_by: "sarah.chen@medtech.com"
  created_at: "2025-11-01T09:00:00Z"
  updated_by: "sarah.chen@medtech.com"
  updated_at: "2025-11-20T14:00:00Z"
  version_approved_by: "sarah.chen@medtech.com"
  version_approved_at: "2025-11-20T14:00:00Z"
  rationale: "Version 1.0.0 release - complete context contract for healthcare software"
```

**Domain Bundle** (`bundles/domains/software-development.yaml`):
```yaml
id: bundle:software-development
type: domain
version: "1.0.0"
title: "Software Development Domain"
description: >
  Software Development domain bundle importing all concept bundles
  relevant to software engineering.

imports:
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  - bundle:performance-reliability:1.0.0
  - bundle:usability-accessibility:1.0.0
  - bundle:compliance-governance:1.0.0
  - bundle:data-provenance:1.0.0
  - bundle:testing-validation:1.0.0
  - bundle:deployment-operations:1.0.0
  - bundle:safety-risk:1.0.0
  - bundle:ethics-ai-accountability:1.0.0
  - bundle:business-context:1.0.0

scds: []

provenance:
  created_by: "info@ohana-tech.com"
  created_at: "2025-11-01T10:00:00Z"
  version_approved_by: "info@ohana-tech.com"
  version_approved_at: "2025-11-01T10:00:00Z"
  rationale: "Software Development domain v1.0.0 - reference implementation"
```

**Concept Bundle** (`bundles/concepts/architecture.yaml`):
```yaml
id: bundle:architecture
type: concept
version: "1.0.0"
title: "Architecture Concept Bundle"
description: >
  Architecture concept bundle defining system boundaries, components,
  technology stack, and integration points.

imports: []

scds:
  - scd:project:system-context
  - scd:project:tech-stack
  - scd:project:integration-map
  - scd:project:component-model

provenance:
  created_by: "architecture-team@medtech.com"
  created_at: "2025-11-01T10:00:00Z"
  updated_by: "mike.johnson@medtech.com"
  updated_at: "2025-11-18T11:30:00Z"
  version_approved_by: "mike.johnson@medtech.com"
  version_approved_at: "2025-11-18T11:30:00Z"
  rationale: "Architecture concept v1.0.0 - locked for development"
```

---

## 7. Bundle Semantics

### 7.1 Completeness

The project bundle (with all imported bundles) MUST contain every SCD required to define the system.

### 7.2 Source of Truth

The project bundle is the root context used by:
- Code editors and IDEs
- Validators and linters
- Governance engines
- AI code assistants
- Deployment tools

### 7.3 Immutability

Once versioned (e.g., `1.0.0`), a bundle MUST remain immutable. Changes require a new version.

**Lifecycle**:
1. Create bundle in `DRAFT` state
2. Iterate and refine in `DRAFT` mode
3. Lock and version (e.g., `1.0.0`)
4. Bundle becomes immutable contract
5. Future changes create new versions (e.g., `1.1.0`)

### 7.4 Independence

Domain bundles MAY version independently:
- Architecture team locks `bundle:architecture:1.0.0` in Week 3
- Security team locks `bundle:security:1.0.0` in Week 5
- Project bundle references specific versions of each

### 7.5 Cross-Tier Binding

SCDs from different tiers (Meta → Standards → Project) are bound together through the bundle hierarchy.

---

## 8. Directory Structure

Recommended project structure:

```
project-name/
├── bundles/
│   ├── project-bundle.yaml          # Top-level bundle
│   ├── meta-bundle.yaml             # Meta vocabulary (imported)
│   ├── standards-bundle.yaml        # Compliance standards
│   ├── domains/
│   │   ├── software-development.yaml  # Software Development domain
│   │   └── clinical.yaml              # Clinical domain (example)
│   └── concepts/
│       ├── architecture.yaml
│       ├── security.yaml
│       ├── performance-reliability.yaml
│       └── ... (11 total concept bundles for Software Development)
│
├── context/
│   ├── meta/                        # Meta-tier SCDs
│   │   ├── roles.yaml
│   │   ├── capabilities.yaml
│   │   └── ...
│   ├── standards/                   # Standards-tier SCDs
│   │   ├── hipaa-privacy-rule.yaml
│   │   └── ...
│   └── project/                     # Project-tier SCDs
│       ├── system-context.yaml
│       ├── tech-stack.yaml
│       └── ... (38+ SCDs)
│
└── .scs/
    └── config.yaml                  # SCS tooling config
```

---

## 9. Validation Requirements

Tools MUST validate that:

### 9.1 Schema Validation
- Bundle conforms to JSON schema (`schema/bundles/scd-bundle-schema.json`)
- All required fields present
- Field types and patterns correct
- Conditional rules satisfied (e.g., domain bundles have no imports)

### 9.2 Reference Resolution
- All SCD references resolve to actual SCD files
- All bundle imports resolve to actual bundle files
- No circular imports (domain and concept bundles have specific import rules)
- SCD identifiers are unique within bundle

### 9.3 Type Consistency
- Bundle `type` matches usage pattern
- Concept bundles MUST NOT import other bundles (imports array MUST be empty)
- Concept bundles MUST contain at least one SCD
- Domain bundles MUST import at least one concept bundle
- Domain bundles MUST NOT directly contain SCDs (scds array MUST be empty)
- Meta bundles contain only meta-tier SCDs
- Standards bundles contain only standards-tier SCDs

### 9.4 Version Consistency
- Version follows semantic versioning or `DRAFT`
- Imported bundle versions exist
- No conflicting version requirements

### 9.5 Approval (non-`DRAFT` versions only)
- `provenance.version_approved_by` and `version_approved_at` are present once `version` is
  a real semantic version — not required while `version: "DRAFT"` (RFC-0001, Provenance and
  approval)

Tools MAY also perform:
- Cross-tier semantic checks
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

1. Teams create concept bundles in `DRAFT` state
2. Teams iterate, add SCDs, refine content
3. Teams validate bundle completeness
4. Teams lock concept bundles with versions (e.g., `bundle:security:1.0.0`)
5. Domain bundle imports all versioned concept bundles
6. Domain bundle locks (e.g., `bundle:software-development:1.0.0`)
7. Project bundle imports versioned domain bundles
8. Project bundle locks (e.g., `bundle:project:1.0.0`)
9. Development proceeds against locked contract

---

## 11. Bundle Structure for Projects

Production projects typically include:

**Required:**
- **1 Project Bundle** (top-level orchestrator)
- **1 Meta Bundle** (imported from SCS - universal vocabulary)
- **1+ Domain Bundles** (at least one domain for the project's context)

**Optional:**
- **Standards Bundles** (as needed for compliance requirements)
- **Additional Domain Bundles** (for multi-domain projects)

### Software Development Projects

Software development projects typically import the **Software Development domain**, which includes 11 concept bundles:

1. Architecture
2. Security
3. Performance & Reliability
4. Usability & Accessibility
5. Compliance & Governance
6. Data & Provenance
7. Testing & Validation
8. Deployment & Operations
9. Safety & Risk
10. Ethics & AI Accountability
11. Business Context

### Multi-Domain Projects

Projects may import multiple domains. For example, a healthcare software project might import:
- **Software Development domain** (for software engineering concepts)
- **Clinical domain** (for healthcare-specific concepts)

**There are no universally prescribed bundles** - the appropriate bundles depend on the domain(s) your project operates within.

---

## 12. Examples

Complete working examples are available in:
- `examples/bundles/` - Medication Adherence System bundle examples
- `examples/bundles/README.md` - Detailed explanation of example structure

These examples demonstrate:
- All 5 bundle types (project, meta, standards, concept, domain)
- Hierarchical imports (project → domain → concept → SCD)
- Multi-domain composition
- Domain Ontology depth (Medical-Device CDMO reference domain)
- Healthcare compliance (HIPAA, SOC2)
- Realistic project structure

---

## 13. Schema Reference

**Bundle Schema**: `schema/bundles/scd-bundle-schema.json`
**Domain Manifest Schema**: `schema/domain/domain-manifest-schema.json` (the `ontology`
block — see `domain-ontology.md`)
**SCD Schemas**:
- Meta-tier: `schema/scd/meta-scd-template.json`
- Standards-tier: `schema/scd/standards-scd-template.json`
- Project-tier: `schema/scd/project-scd-template.json`

---

## 14. Future Extensions

Future versions may introduce:
- Bundle inheritance/extension
- Bundle signatures for attestation
- Multi-bundle workspaces
- Dynamic or environment-specific bundles
- Registry-based bundle resolution
- Bundle dependency graph visualization

SCS 0.5.0 defines the minimal, stable bundle representation with multi-domain support.

---

## 15. Related Documentation

- [Bundle Lifecycle](../../docs/bundle-lifecycle.md) - How bundles evolve through development
- [Project Structure](../../docs/project-structure.md) - Recommended directory layout
- [Minimum Project SCDs](../../docs/minimum-project-scds.md) - Required SCD set
- [Validation Workflow](../../docs/validation-workflow.md) - How to validate bundles

---

## 16. Key Takeaways

1. **Bundles are manifests, not content** - They organize and reference SCDs
2. **Five bundle types** - Project, Meta, Standards, Concept, Domain
3. **Container model** - Think Docker manifests, not Docker layers
4. **Approved contracts** - A real (non-`DRAFT`) version requires
   `version_approved_by`/`version_approved_at`, then it's locked
5. **Hierarchical imports** - Project → Domain → Concept → SCD
6. **Bundle independence** - Concepts and domains can version separately
7. **Type enforcement** - Schema validates bundle type rules (concepts can't import, domains can't contain SCDs)
8. **Multi-domain support** - Projects can combine multiple industry domains
9. **Concepts are domain-scoped** - Not shared across domains; an **Ontology Model** is the
   reusable unit instead (`domain-ontology.md`)

---

## 17. Feedback

Comments and refinements for the Bundle Format should be submitted through:
- [GitHub Issues](https://github.com/tim-mccrimmon/scs-spec/issues)
- [GitHub Discussions](https://github.com/tim-mccrimmon/scs-spec/discussions)
