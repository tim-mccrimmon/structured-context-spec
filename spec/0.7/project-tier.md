# SCS 0.7.0 — Project-Tier SCDs  
**Version:** 0.7.0 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2026-10-25  

---

## 1. Purpose

The **Project-Tier** of the Structured Context Specification (SCS) holds the context an
adopter authors. It appears in two places:

- in an organization's **Domain bundle**, through its concept bundles: the organization's
  own rules, applied to every project
- in a **Project bundle**: the **specific system or product being built** and the rules
  that apply only to it

The two bundles are independent. A Project bundle MUST NOT import the Domain bundle and
SHOULD NOT repeat its rules (`bundle-format.md`).

The tier identifies **who authors** an SCD, not **where it applies**. An SCD's scope comes
from the bundle that includes it: through a Domain bundle it applies to all work, through a
Project bundle to one project. Tools MUST NOT infer an SCD's scope from its tier.

> **Naming note.** The name "Project" is historical: it predates the separation of Domain
> and Project bundles in 0.6.0. Read it as "adopter-authored". The name is kept because SCD
> identifiers (`scd:project:<name>`) must stay stable; see ISSUES.md ISS-041.

Project-Tier SCDs describe:

- architecture  
- components  
- capabilities  
- data flows  
- requirements  
- constraints  
- quality attributes  
- security posture  
- compliance mappings  
- operational policies  
- relationships to Meta-Tier SCDs  
- citations of the external standards they implement (`citations.md`)  

These SCDs form the **authoritative, machine-readable definition of the system**.

---

## 2. Role of the Project-Tier

Project-Tier SCDs are where the **abstract concepts** defined in the Meta-Tier and the
**external obligations** of the standards an adopter follows are applied to a real
organization or system. The adopter's rules are its interpretation of those standards; the
standards themselves are cited, not reproduced.

This tier defines:

- what the system is  
- what the system does  
- how the system is organized  
- what decisions have been made  
- how it satisfies external requirements  
- how it evolves over time  

Project-Tier SCDs are expected to change frequently as the system evolves.

---

## 3. Responsibilities of Project-Tier SCDs

Project-Tier SCDs MUST:

- describe the system accurately and unambiguously  
- provide enough structure for AI agents to reason over the system  
- map system components to relevant compliance requirements  
- declare all relevant constraints  
- connect capabilities to implementations  
- document important decisions  
- provide provenance for traceability  

They SHOULD:

- remain focused and modular  
- avoid duplication  
- reference Meta-Tier SCDs instead of restating content  
- cite external standards rather than reproduce their text  

---

## 4. Project-Tier SCD Structure

Project-Tier SCDs follow the general SCD structure described in the Core Model.

### 4.1 Required Properties

| Property       | Description                                                  |
|----------------|--------------------------------------------------------------|
| `id`           | Unique stable identifier (e.g., `scd:project:architecture`) |
| `type`         | MUST be `project`                                           |
| `title`        | Human-readable title                                        |
| `version`      | Version of this SCD                                         |
| `description`  | Summary of the system element described                     |
| `content`      | Structured project-specific context                         |
| `relationships`| References to Meta/Project SCDs, or citations for `satisfies` |
| `provenance`   | Authorship and change metadata                              |

### 4.2 Optional Properties

| Property   | Description                                                                 |
|------------|-------------------------------------------------------------------------------|
| `cites`    | Citation references to the external standards this SCD implements (e.g., `std:iso-13485:2016#7.3.9`) — `citations.md`. Carries no standard text. |
| `concept`  | The Domain Ontology concept this SCD realizes (e.g., `concept:risk-management`) — `domain-ontology.md`, RFC-0001. Optional at the schema level, but expected for an SCD that lives in a concept bundle. |

---

## 5. Common Project-Tier SCD Types

SCS 0.6.0 does not prescribe specific SCDs but recommends common patterns.

### 5.1 Architecture SCD

Describes the architecture of the system.

```yaml
content:
  architecture_style: "modular-service"
  components:
    - id: component:ingestion-service
      name: "Ingestion Service"
      description: "Receives and normalizes incoming data."
      responsibilities:
        - "Validate input"
        - "Perform schema normalization"
      interfaces:
        inputs:
          - "FHIR Resource (HTTP POST)"
        outputs:
          - "Normalized Event (Kafka)"
```

### 5.2 Capability SCD

Links project-specific capabilities to implementation.

```yaml
content:
  capabilities:
    - capability_id: capability:clinical-insight
      implemented_by:
        - component:ai-evaluator
      related_roles:
        - role:clinician
      description: "Generate context-aware clinical suggestions."
```

### 5.3 Requirements SCD

Defines functional and non-functional requirements in structured form.

```yaml
content:
  requirements:
    - id: req:latency
      type: "nfr"
      description: "System responses must complete within 200ms"
      metric: "latency"
      constraint: "<= 200ms"
      related_components:
        - component:ui-service
```
### 5.4 Security SCD

Defines security posture and constraints.

```yaml
cites:
  - std:hipaa#164.312(d)
content:
  security_controls:
    - id: sec:authn
      name: "Authentication"
      description: "Only authenticated users may access protected endpoints."
      method: "OAuth2"
      requirement_level: "Required"
```

### 5.5 Data Flow SCD

Describes how information moves through the system.

```yaml
content:
  flows:
    - id: flow:patient-data
      description: "Patient data flows from ingestion to storage."
      path:
        - component:ingestion-service
        - component:data-normalizer
        - component:storage-service
```

### 5.6 Governance SCD

Describes system-level governance concerns.

```yaml
content:
  governance:
    decisions:
      - id: decision:use-multi-tenant
        title: "Adopt Multi-Tenant Architecture"
        rationale: "Cost efficiency and scalability"
        date: "2025-11-10"
```

### 5.7 Policy SCD

Defines which roles may use which tool capabilities, and under what constraints —
**policy-as-context** (`any-ai-actor-model.md` §3, RFC tracked as ISS-006). A tool or
MCP server's permitted operations are a governed decision, the same as any other
guardrail, not a runtime implementation detail.

```yaml
concept: concept:risk-management   # the purpose this policy exists for
content:
  applies_to_roles:
    - role:quality-engineer
  permitted_operations:
    - capability: fetch-data       # capability class, not a specific tool/endpoint
      resource: risk-register
    - capability: write-data
      resource: risk-register
      requires_approval: true
```

`capability` names a functional class (`fetch-data`, `execute-code`, `query-db`,
`write-data`, `send-communication` by default, domain-extensible) rather than a specific
tool or MCP endpoint — the binding to an actual implementation is a runtime concern, not
part of the decision this SCD records. A Policy SCD is declarative; enforcement happens
elsewhere, via a runtime-specific compilation step (`any-ai-actor-model.md` §3.4).

---

## 6. Relationships With Other SCD Tiers

### 6.1 With Meta-Tier

Project-Tier SCDs should reference Meta-Tier SCDs to ensure consistent semantics.

Example:

```yaml
relationships:
  - type: uses-definition
    target: scd:meta:roles
```

### 6.2 With External Standards

The Standards-Tier is deprecated in 0.6.0 (`standards-tier.md`). Project-Tier SCDs map
system elements to standards obligations with citation references (`citations.md`), either
as a `cites` list or as the target of a `satisfies` relationship:

```yaml
cites:
  - std:soc2:2017#CC2.1
relationships:
  - type: satisfies
    target: std:soc2:2017#CC2.1
```

`scd:standards:` targets still validate in 0.6.0 but are deprecated.

### 6.3 With Other Project-Tier SCDs

Project-Tier SCDs may depend on each other:

```yaml
relationships:
  - type: depends-on
    target: scd:project:security
```
--- 

## 7. Versioning and Evolution

Project-Tier SCDs evolve frequently as part of system development.

Version changes should reflect:

- new architecture components
- updated capabilities
- new requirements
- changes in compliance mapping
- retired or obsolete decisions

Tools can track changes for:

- impact analysis
- governance review
- design consistency

---

## 8. AI and Autonomic Governance

Project-Tier SCDs provide the detailed, system-specific context necessary for:

- AI code generation
- AI-driven refactoring
- system analysis
- gap detection
- compliance evaluation
- quality attribute verification
- dependency reasoning

AI agents SHOULD load context in this order: Meta-Tier SCDs, then the Domain bundle's
SCDs, then the Project bundle's SCDs.

---

## 9. Validation Requirements

In SCS 0.6.0:

- Project-Tier SCDs MUST conform to scd.project.schema.json.
- The type MUST be project.
- Field structures must match the schema.
- Relationships MUST reference valid SCD identifiers, or for `satisfies`, well-formed
  citation references.

Semantic validation (e.g., architectural coherence) is tool-dependent and out of scope for 0.6.0.

---

## 10. Future Extensions

Future versions of SCS may add:

- richer architectural structures
- formal modeling constructs
- automated compliance mapping rules
- cross-SCD inheritance or extension
- operational/runtime SCD types
- design decision frameworks (ADR-like SCDs)

---

## 11. Feedback

Feedback regarding Project-Tier definitions and examples should be submitted through GitHub Issues.