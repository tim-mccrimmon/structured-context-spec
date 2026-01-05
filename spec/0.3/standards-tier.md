# SCS 0.1 — Standards-Tier SCDs  
**Version:** 0.1 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2025-11-17  

---

## 1. Purpose

The **Standards-Tier** of the Structured Context Specification (SCS) captures **external standards**, **regulatory frameworks**, and **formal requirements** that a system must comply with.

Standards-Tier SCDs provide a machine-readable representation of:

- regulatory requirements (e.g., HIPAA, CHAI)  
- certification frameworks (e.g., SOC2, ISO 27001)  
- interoperability standards (e.g., FHIR, OAuth2, NIST guidelines)  
- organizational policies  
- domain-specific rules  

These SCDs form the **compliance and standards layer** of SCS.

They allow systems—human and AI—to reason about compliance, map project context to external obligations, and support autonomic governance.

---

## 2. Role of the Standards-Tier

The Standards-Tier exists to:

- **import** external standards into the project context  
- **normalize** standards into a structured format  
- **simplify** compliance interpretation  
- **support** validation, audit, and governance  
- **provide** reference points for mapping project SCDs  
- **enable** multi-standard alignment  

Where traditional compliance is handled in documents, PDFs, and long checklists, SCS turns these into **formal, structured context**.

This enables:

- automated reasoning  
- automated checklist completion  
- AI-assisted governance  
- traceability to external obligations  
- consistent system-wide alignment  

---

## 3. Standards-Tier SCD Characteristics

### Standards-Tier SCDs are:

- **importable** into any project  
- **versioned** independently of the project  
- **extensible** but not overwritten  
- **referenced** by Project-Tier SCDs  
- **semantically stable** over time  

### Standards-Tier SCDs are *not*:

- implementation-specific  
- describing project choices  
- mutable on a per-project basis  
- tied to a particular architecture  

If a project requires specialization, it must be done in Project-Tier SCDs.

---

## 4. Standards-Tier SCD Structure

Standards-Tier SCDs follow the core SCD structure defined in `core-model.md`.

### 4.1 Required Properties

| Property       | Description                                                  |
|----------------|--------------------------------------------------------------|
| `id`           | Unique identifier (e.g., `scd:standards:hipaa-privacy`)     |
| `type`         | MUST be `standards`                                         |
| `title`        | Human-readable title                                        |
| `version`      | Version of this SCD                                         |
| `description`  | Summary of the standard or requirement being represented    |
| `content`      | Structured representation of the standard’s clauses         |
| `relationships`| Optional links to meta or project SCDs                      |
| `provenance`   | Authorship and change details                               |

---

## 5. Standards-Tier Content Structures

Standards are divided into structured elements suited for machine interpretation, such as:

- **controls**  
- **requirements**  
- **clauses**  
- **sections**  
- **mappings**  
- **obligations**  
- **constraints**  

Example structure for a regulatory standard:

```yaml
content:
  standard_name: "HIPAA Security Rule"
  sections:
    - id: hipaa:164.308(a)(1)(i)
      title: "Risk Analysis"
      description: "Conduct an accurate and thorough assessment of risks..."
      category: "Administrative Safeguard"
      requirement_type: "Required"
      obligations:
        - "Perform risk analysis on electronic PHI systems."
      related_controls:
        - soc2:cc1.1
        - nist:800-53:RA-3
```

This format supports mapping between standards and project context.

---

## 6. Standard Categories

### 6.1 Regulatory Standards

Examples:

- HIPAA
- GDPR
- CHAI
- CMS Blue Button

These define legal or compliance obligations.

### 6.2 Certification Standards

Examples:
- SOC2
- ISO 27001
- FedRAMP

These define formal controls for certification and audits.

### 6.3 Interoperability Standards

Examples:
- FHIR (HL7)
- OAuth2
- SMART-on-FHIR
- USCDI

These define how systems communicate and exchange data.

### 6.4 Organizational Policies

Examples:
- Corporate security policy
- Data retention policies
- Access management policies

These represent internal rules unique to an organization but usable across its projects.

---

## 7. Relationships With Other Tiers

Standards-Tier SCDs often serve as targets of relationships from Meta-Tier and Project-Tier SCDs.

### 7.1 Example Relationships

From Project-Tier SCD to Standards-Tier:

```yaml
relationships:
  - type: satisfies
    target: scd:standards:hipaa-164.308(a)(1)(i)
    description: "This module performs automated risk assessment."
```

From Standards-Tier to Meta-Tier:

```yaml
relationships:
  - type: aligns-with
    target: scd:meta:security-concerns
```

Relationships support compliance automation, impact analysis, and governance.

---

## 8. Versioning of Standards

Standards typically evolve.

SCS treats Standards-Tier SCDs as independently versioned artifacts, meaning:

- new versions of standards → new SCD versions
- projects may choose which versions to import
- bundles may include multiple versions for migration
- governance tools must be aware of version mapping

Example:
scd:standards:hipaa-0.1
scd:standards:hipaa-0.2
scd:standards:hipaa-1.0

Each version describes the standard at that point in time.

---

## 9. Mapping Standards to Project Context

A common use of the Standards-Tier is mapping:

- project capabilities
- services
- data flows
- architecture elements

…to external requirements.

Example:

```yaml
relationships:
  - type: satisfies
    target: scd:standards:soc2:cc2.1
  - type: informed-by
    target: scd:standards:iso27001:a.9.2.3
```

Project-Tier SCDs use these relationships to create full compliance coverage.

---

## 10. AI and Autonomic Governance

Standards-Tier SCDs are essential for:

- AI-assisted compliance
- automated control mapping
- AI answering compliance questions
- filling in certification checklists
- autonomic governance
- change-impact analysis
- risk modeling

Because Standards-Tier SCDs are:

- machine-readable
- structured
- linked to project context

…AI can:

- reason over requirements
- detect conflicts
- evaluate system posture
- recommend remediations

---

## 11. Validation Requirements

In SCS 0.1:

- Standards-Tier SCDs MUST conform to scd.standards.schema.json (in /schema/scd/).
- type MUST be standards.
- id MUST be stable and uniquely identifiable.
- content MUST follow the schema-defined structure.

Cross-standard harmonization (e.g., mapping HIPAA → SOC2 → ISO) is encouraged but not required in 0.1.

---

## 12. Future Extensions

Future versions may add:

- standard vocabularies for compliance obligations
- cross-standard control libraries
- reusable SCDs for common regulatory frameworks
- advanced mapping semantics
- richer metadata for audit evidence
- support for temporal standards evolution

---

## 13. Feedback

Feedback regarding the Standards-Tier or example SCD structures should be submitted through GitHub Issues.

