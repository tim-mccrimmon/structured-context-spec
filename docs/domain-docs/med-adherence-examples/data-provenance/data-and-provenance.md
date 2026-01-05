# Data & Provenance Context Brief (Template)
Project: {{ PROJECT NAME }}
Domain: Data & Provenance
Version: 1.0
Status: Draft
Phase: Intent

This document provides a structured, human-friendly, and AI-friendly overview
of the project’s data model, provenance strategy, and retention policies.
It serves as the primary input for generating the following SCDs:

- scd:project:data-model
- scd:project:provenance-tracking
- scd:project:retention-policy

---

## 1. Purpose and Instructions
**Team Member Instructions:**  
Describe, at a conceptual and logical level, what data the system manages,
where it comes from, how its lineage is tracked, and how long it must be
retained. Avoid low-level implementation details (e.g., table schemas); focus
on concepts, responsibilities, and policies.

**AI Mapping:**  
Feeds the `data-model`, `provenance-tracking`, and `retention-policy` SCDs.

---

## 2. Data Domain Overview
**Team Member Instructions:**  
Provide a short overview of the data domain for this system. Summarize the main
data categories and why they matter to the business and clinical outcomes.

**AI Mapping →** data-model.overview

---

## 3. Core Data Entities & Concepts
**Team Member Instructions:**  
List the main conceptual entities the system manages (e.g., PatientProfile,
MedicationPlan, AdherenceEvent). For each entity, describe:

- What it represents
- Why it exists
- How it is used

You do **not** need to describe every field here; focus on concepts.

### Example Structure

- **Entity Name:**  
  - Description:  
  - Category: (e.g., master, reference, event, configuration)  
  - Primary consumers: (which roles/services use it)  

**AI Mapping →** data-model.entities[*]

---

## 4. Fields & Attributes (Logical Model)
**Team Member Instructions:**  
For the most critical entities, outline their key attributes at a logical level.
You do not need full schema, but include fields that matter for safety,
reporting, or provenance.

For each entity, list:

- Field name
- Description
- Type (string, date, enum, etc.)
- Sensitivity (PII, PHI, internal, public)
- Required? (yes/no)
- Notes (any constraints or semantics)

You can keep this focused to the entities that matter most.

**AI Mapping →** data-model.entities[*].fields[*]

---

## 5. Relationships Between Entities
**Team Member Instructions:**  
Describe how entities relate to each other (e.g., “A MedicationPlan has many
AdherenceEvents”). Capture cardinality and direction where possible.

Example:

- PatientProfile 1 — N MedicationPlan  
- MedicationPlan 1 — N AdherenceEvent  
- AdherenceEvent 0 — 1 EscalationEvent  

**AI Mapping →** data-model.relationships[*]

---

## 6. Data Ownership & System of Record
**Team Member Instructions:**  
Identify, for each entity, which system or component is the **system of record**,
and which components maintain derived copies.

For each entity:

- System of record: (EHR, platform service, external partner, etc.)
- Derived copies: (analytics, caches, logs, etc.)

**AI Mapping →** data-model.entities[*].ownership, provenance-tracking.systems_of_record

---

## 7. Data Sensitivity & Classification
**Team Member Instructions:**  
Classify entities by sensitivity. Use labels like:

- PHI (Protected Health Information)
- PII
- Confidential internal
- Operational metadata
- Aggregate/non-identifiable

If needed, call out any entities that contain especially sensitive attributes
(e.g., mental health notes, genomic data).

**AI Mapping →** data-model.entities[*].sensitivity

---

## 8. Data Provenance: Sources and Ingestion Paths
**Team Member Instructions:**  
Describe **where each major entity comes from** and **how it enters the system**:

- Source systems (EHR, patient input, devices, admin config)
- Ingestion mechanisms (API pull, push, batch file, manual entry)
- Frequency (real-time, scheduled, ad-hoc)

Example:

- MedicationPlan: pulled from EHR via FHIR
- AdherenceEvent: created by patient app check-ins
- ProgramConfig: created/edited by admins in portal

**AI Mapping →** provenance-tracking.sources, provenance-tracking.ingestion_paths

---

## 9. Transformations, Derivations & Lineage
**Team Member Instructions:**  
Describe key transformations:

- Which entities are derived from others?
- What calculations or aggregations are applied?
- Are any risk scores or composite metrics computed?

Call out where lineage must be explicitly tracked (e.g., “metric X is derived
from Y and Z with formula …”).

**AI Mapping →** provenance-tracking.transformations, provenance-tracking.lineage_model

---

## 10. Auditability & Traceability
**Team Member Instructions:**  
Describe how you will prove:

- who created or modified data
- when it changed
- what changed
- which system or actor performed the change

Call out:

- audit log strategy
- identifiers used to trace events (request IDs, correlation IDs)
- any regulatory expectations (e.g., CHAI, HIPAA audit trails)

**AI Mapping →** provenance-tracking.audit_model

---

## 11. Data Retention & Deletion Policies
**Team Member Instructions:**  
For each major entity (or category of data), define:

- Minimum retention period
- Maximum retention (if applicable)
- Legal/regulatory basis (HIPAA, contract, policy)
- Archival strategy (hot vs. cold vs. offline)
- Deletion or anonymization behavior

Example:

- AdherenceEvent: retain 7 years (HIPAA), then archive or anonymize.
- NotificationEvent: retain 2 years for troubleshooting, then delete.

**AI Mapping →** retention-policy.entries[*]

---

## 12. Data Residency & Cross-Border Rules
**Team Member Instructions:**  
Describe where data may reside geographically and any cross-border restrictions.

Example:

- US-only residency for PHI.
- No cross-region replication of raw PHI outside customer jurisdiction.

**AI Mapping →** retention-policy.residency

---

## 13. Backup, Restore & Disaster Recovery
**Team Member Instructions:**  
Summarize expectations at a data level:

- Backup frequency
- Restore time objectives (RTO)
- Data loss tolerance (RPO)
- Any exceptions for specific data types

**AI Mapping →** retention-policy.backup_and_dr

---

## 14. Risks & Open Questions (Data & Provenance)
**Team Member Instructions:**  
List known risks and unresolved questions specific to data, provenance, and retention.

Examples:

- Risk: incomplete medication data from EHR.
- Risk: over-retention of PHI without clear basis.
- Question: Should adherence summaries be written back to EHR?

**AI Mapping →** data-model.risks, provenance-tracking.risks, retention-policy.risks

---

## 15. Provenance
created_by: "{{ YOUR NAME OR ROLE }}"
created_at: "{{ ISO8601 TIMESTAMP }}"
source: "Intent Phase – Data & Provenance Domain"
notes: "Initial draft; subject to revision as architecture and business context evolve."