# SCS 0.7.0 — Meta-Tier SCDs  
**Version:** 0.7.0 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2026-10-25  

---

## 1. Purpose

This document defines the **Meta-Tier** of the Structured Context Specification (SCS).

Meta-Tier SCDs establish the **conceptual foundation** of a system:

- the vocabulary used to describe it  
- the roles and capabilities involved  
- the core domains and concepts  
- the cross-cutting structures that shape all other context  

Meta-Tier SCDs are intended to be:

- stable over time  
- reusable across projects  
- referenceable by Project-Tier SCDs  
- interpretable by AI agents and tools  

**Ownership (since 0.6.0):** the **Meta bundle** and its Meta-Tier SCDs are published and
versioned with the SCS specification (for example, `bundle:meta:0.6.0`). Adopters do not
author or edit them. An organization's Domain bundle imports one pinned Meta bundle version;
Project bundles MUST NOT import it (`bundle-format.md`). Organization-specific vocabulary,
such as an organization's own role model, is authored as project-tier SCDs in the
organization's Domain bundle.

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
- anchor organization and project specifics  
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

The following patterns describe the Meta-Tier SCDs the specification publishes. They are
recorded here so tools and AI agents can interpret them.

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

Identifies cross-cutting concerns — in the classical sense (security, observability, and
similar aspects that touch many parts of a system) — that must be considered across many
parts of the system. This is a different thing from a domain's **Domain Ontology**
(`domain-ontology.md`): the ontology's `concept:` ids are the structural building blocks
a domain organizes its SCDs around, while this SCD is describing implementation-level
cross-cutting aspects. The field is named `concepts` for schema consistency with the rest
of SCS since 0.5.0 (the term "concern" was retired, RFC-0001), but what it holds is unrelated to
the Domain Ontology.

```yaml
content:
  concepts:
    - id: concept:security
      name: "Security"
      description: "Protection of confidentiality, integrity, and availability."
      applies_to:
        - capability:<id>
        - domain:<id>
    - id: concept:observability
      name: "Observability"
      description: "Ability to understand system behavior from external outputs."
```

---

## 6. Relationships From Meta-Tier SCDs

Meta-Tier SCDs may relate to:
- other Meta-Tier SCDs
- external standards, through citation references (`citations.md`), e.g. “this term
  follows the definition in ISO 14971 clause 3.10”

Meta-Tier SCDs do not reference Project-Tier SCDs: Meta is published with the
specification and cannot know any adopter's projects. Project-Tier SCDs reference Meta
instead (`project-tier.md` §6.1).

### 6.1 Example Relationships

```yaml
relationships:
  - type: extends
    target: scd:meta:core-capabilities
    description: "Extends the base capability map for healthcare."
cites:
  - std:iso-14971:2019#3.10
```

Tools MUST NOT assume that every Meta-Tier SCD has relationships, but SHOULD be prepared to resolve them when present.

---

## 7. Meta-Tier and Reuse

One of the primary goals of the Meta-Tier is reuse.

The published Meta bundle is:

- shared by every organization that adopts SCS
- versioned with the specification
- imported, at a pinned version, by an organization's Domain bundle
- extended or specialized by the organization's own project-tier SCDs, not edited

For example, an organization that needs a role model for its clinical systems references
the published Meta roles and adds its own roles as project-tier SCDs in its Domain bundle.

---

## 8. Meta-Tier and AI Agents

Meta-Tier SCDs are particularly important for AI agents because they:

- define the vocabulary agents should use
- describe roles, responsibilities, and capabilities
- provide guardrails for interpretation
- align multiple agents on shared semantics

AI agents SHOULD:

- load Meta-Tier SCDs first, then the Domain bundle's SCDs, then the Project bundle's SCDs
- treat Meta-Tier as the semantic foundation for reasoning

---

## 9. Validation Requirements

In SCS 0.7.0:

- Meta-Tier SCDs MUST conform to the meta SCD schema (defined in /schema/scd.meta.schema.json).
- type MUST be meta.
- id MUST be unique within the bundle.
- content MUST follow the structure defined in the corresponding schema.

Additional semantic validation (e.g., cross-SCD consistency) is out of scope for 0.7.0 but may be performed by tools.

⸻

## 10. Future Extensions

Future versions of SCS may add:

- standard Meta-Tier SCDs (e.g., canonical role libraries)
- richer relationship types
- inheritance/extension patterns for meta models
- cross-bundle meta libraries
- domain-specific meta taxonomies

The Meta-Tier, as defined since 0.6.0, is intentionally minimal but designed for evolution.

---

## 11. Feedback

Feedback on Meta-Tier definitions and patterns should be submitted via GitHub Issues.