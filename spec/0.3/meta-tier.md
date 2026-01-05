# SCS 0.1 — Meta-Tier SCDs  
**Version:** 0.1 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2025-11-17  

---

## 1. Purpose

This document defines the **Meta-Tier** of the Structured Context Specification (SCS).

Meta-Tier SCDs establish the **conceptual foundation** of a system:

- the vocabulary used to describe it  
- the roles and capabilities involved  
- the core domains and concerns  
- the cross-cutting structures that shape all other context  

Meta-Tier SCDs are intended to be:

- stable over time  
- reusable across projects  
- referenceable by Standards- and Project-Tier SCDs  
- interpretable by AI agents and tools  

---

## 2. Role of the Meta-Tier

The Meta-Tier defines the “language” of a system.

It addresses questions such as:

- What are the key **domains** of this system?  
- What **roles** participate (e.g., Patient, Clinician, Operator, Service)?  
- What **capabilities** does the system provide at a high level?  
- What **cross-cutting concerns** (e.g., security, observability, compliance) must all components respect?  
- How do we **name and classify** components and behaviors?  

Meta-Tier SCDs provide **shared semantics** that:

- guide architecture and design  
- anchor standards and project specifics  
- support consistent reasoning by AI agents  

---

## 3. Meta-Tier SCD Scope

A Meta-Tier SCD should describe **system-wide conceptual structures**, not implementation details.

Typical examples include:

- role models  
- capability maps  
- domain glossaries  
- cross-cutting concern catalogs  
- classification schemes  
- context taxonomies  

Meta-Tier SCDs should **not** describe:

- specific microservices or classes  
- low-level API shapes  
- environment-specific configurations  
- project-specific deadlines or tasks  

Those belong in Project-Tier SCDs.

---

## 4. Meta-Tier SCD Structure

Meta-Tier SCDs follow the general SCD structure defined in the Core Model, with additional semantics appropriate to this tier.

### 4.1 Required Properties

Every Meta-Tier SCD MUST include:

| Property       | Description                                           |
|----------------|-------------------------------------------------------|
| `id`           | Unique identifier (e.g., `scd:meta:roles`)           |
| `type`         | MUST be `meta`                                       |
| `title`        | Human-readable title                                 |
| `version`      | Version of this SCD                                  |
| `description`  | Summary of what this meta SCD defines                |
| `content`      | Structured fields (see below)                        |
| `relationships`| Optional references to other SCDs                    |
| `provenance`   | Metadata about authorship, creation, and updates     |

### 4.2 Example Skeleton

```yaml
id: scd:meta:roles
type: meta
title: "System Roles"
version: "0.1.0"
description: >
  Defines the primary human and system roles that participate
  in this class of systems.

content:
  roles:
    - id: role:patient
      name: "Patient"
      description: "Individual whose data and care are managed by the system."
    - id: role:clinician
      name: "Clinician"
      description: "Licensed provider responsible for clinical decisions."
    - id: role:governance-officer
      name: "Governance Officer"
      description: "Role responsible for compliance and oversight."

relationships: []
provenance:
  created_by: "timmccrimmon"
  created_at: "2025-11-17T10:00:00Z"
  updated_by: "timmccrimmon"
  updated_at: "2025-11-17T10:00:00Z"
  rationale: "Foundation for role-based context across all tiers."
```

---

## 5. Common Meta-Tier SCD Patterns

SCS 0.1 does not mandate specific meta SCDs, but the following patterns are recommended.

### 5.1 Role Model SCD

Describes:
- human and system roles
- responsibilities
- typical interactions
- trust boundaries

Typical content fields:

```yaml
content:
  roles:
    - id: role:<id>
      name: <string>
      description: <string>
      responsibilities:
        - <string>
      trust_level: <string>   # optional
```

### 5.2 Capability Map SCD

Describes high-level capabilities of the system, independent of implementation.

```yaml
content:
  capabilities:
    - id: capability:<id>
      name: <string>
      description: <string>
      related_domains:
        - domain:<id>
      primary_roles:
        - role:<id>
```

### 5.3 Domain Glossary SCD

Defines domain concepts, terms, and their relationships.

```yaml
content:
  terms:
    - id: term:<id>
      name: <string>
      definition: <string>
      aliases:
        - <string>
      category: <string>   # e.g., "clinical", "billing", "security"
```

### 5.4 Cross-Cutting Concerns SCD

Identifies concerns that must be considered across many parts of the system.

```yaml
content:
  concerns:
    - id: concern:security
      name: "Security"
      description: "Protection of confidentiality, integrity, and availability."
      applies_to:
        - capability:<id>
        - domain:<id>
    - id: concern:observability
      name: "Observability"
      description: "Ability to understand system behavior from external outputs."
```

---

## 6. Relationships From Meta-Tier SCDs

Meta-Tier SCDs may relate to:
- other Meta-Tier SCDs
- Standards-Tier SCDs (e.g., “this domain concept maps to CHAI concept X”)
- Project-Tier SCDs (e.g., “this capability is implemented by module Y”)

### 6.1 Example Relationships

```yaml
relationships:
  - type: extends
    target: scd:meta:core-capabilities
    description: "Extends the base capability map for healthcare."
  - type: informs
    target: scd:standards:chai
    description: "Provides domain definitions used in CHAI mapping."
```

Tools MUST NOT assume that every Meta-Tier SCD has relationships, but SHOULD be prepared to resolve them when present.

---

## 7. Meta-Tier and Reuse

One of the primary goals of the Meta-Tier is reuse.

Meta-Tier SCDs may be:

- shared across multiple projects
- versioned independently
- imported into different bundles
- extended or specialized in other SCDs

For example:

- An organization may define a canonical role model for all clinical systems.
- A platform may define a common capability map reused by multiple products.

Reuse is encouraged but not required in 0.1.

---

## 8. Meta-Tier and AI Agents

Meta-Tier SCDs are particularly important for AI agents because they:

- define the vocabulary agents should use
- describe roles, responsibilities, and capabilities
- provide guardrails for interpretation
- align multiple agents on shared semantics

AI agents SHOULD:

- load Meta-Tier SCDs before operating on Standards- or Project-Tier SCDs
- treat Meta-Tier as the semantic foundation for reasoning

---

## 9. Validation Requirements

In SCS 0.1:

- Meta-Tier SCDs MUST conform to the meta SCD schema (defined in /schema/scd.meta.schema.json).
- type MUST be meta.
- id MUST be unique within the bundle.
- content MUST follow the structure defined in the corresponding schema.

Additional semantic validation (e.g., cross-SCD consistency) is out of scope for 0.1 but may be performed by tools.

⸻

## 10. Future Extensions

Future versions of SCS may add:

- standard Meta-Tier SCDs (e.g., canonical role libraries)
- richer relationship types
- inheritance/extension patterns for meta models
- cross-bundle meta libraries
- domain-specific meta taxonomies

The Meta-Tier defined in 0.1 is intentionally minimal but designed for evolution.

---

## 11. Feedback

Feedback on Meta-Tier definitions and patterns should be submitted via GitHub Issues.