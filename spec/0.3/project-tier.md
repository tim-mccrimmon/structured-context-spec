# SCS 0.1 — Project-Tier SCDs  
**Version:** 0.1 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2025-11-17  

---

## 1. Purpose

The **Project-Tier** of the Structured Context Specification (SCS) defines the **specific system or product being built**.

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
- relationships to Meta- and Standards-Tier SCDs  

These SCDs form the **authoritative, machine-readable definition of the system**.

---

## 2. Role of the Project-Tier

Project-Tier SCDs are where the **abstract concepts** defined in the Meta-Tier and the **external obligations** defined in the Standards-Tier are applied to a real system.

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
- reference Meta- and Standards-Tier SCDs instead of restating content  

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
| `relationships`| References to Meta/Standards/Project SCDs                   |
| `provenance`   | Authorship and change metadata                              |

---

## 5. Common Project-Tier SCD Types

SCS 0.1 does not prescribe specific SCDs but recommends common patterns.

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
content:
  security_controls:
    - id: sec:authn
      name: "Authentication"
      description: "Only authenticated users may access protected endpoints."
      method: "OAuth2"
      requirement_level: "Required"
      maps_to:
        - scd:standards:hipaa-164.312(d)
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

### 6.2 With Standards-Tier

Project-Tier SCDs frequently map system elements to standards obligations:

```yaml
relationships:
  - type: satisfies
    target: scd:standards:soc2:cc2.1
```

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

AI agents SHOULD load Project-Tier SCDs only after interpreting Meta- and Standards-Tier SCDs.

---

## 9. Validation Requirements

In SCS 0.1:

- Project-Tier SCDs MUST conform to scd.project.schema.json.
- The type MUST be project.
- Field structures must match the schema.
- Relationships MUST reference valid SCD identifiers.

Semantic validation (e.g., architectural coherence) is tool-dependent and out of scope for 0.1.

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