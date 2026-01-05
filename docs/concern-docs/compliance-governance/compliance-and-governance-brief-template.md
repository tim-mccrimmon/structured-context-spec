---
title: "Compliance & Governance Brief (Template)"
domain: "compliance-governance"
version: "1.0"
status: "Template"
scs_version: "0.2.0"
structure_hash: "sha256:b6027382d50f9733"
---

## 1. Purpose and Instructions
**Team Member Instructions:**  
Describe how the system satisfies regulatory expectations (HIPAA, SOC2), what
controls must exist, how auditability is achieved, and how internal governance
policies are enforced. Focus on *controls*, *evidence*, and *governance
processes* rather than technical implementation.

**AI Mapping:**  
Feeds all four SCDs.
---

## 2. Compliance Scope & Boundaries
**Team Member Instructions:**  
Define the regulatory scope for this system:

- In-scope data types (PHI, PII, operational metadata)
- In-scope services, components, regions, environments
- Out-of-scope elements (e.g., internal analytics not using PHI)

Identify which regulations, standards, and internal policies apply.

**AI Mapping →** hipaa-compliance.scope, soc2-controls.scope, policy-enforcement.scope

---

## 3. Applicable Regulations & Frameworks
**Team Member Instructions:**  
List applicable frameworks, and briefly describe their relevance:

- HIPAA Privacy Rule (if PHI)
- HIPAA Security Rule (Technical Safeguards)
- SOC 2 Trust Services Criteria (Security, Availability, Confidentiality)
- NIST 800-53 / CSF (if used for mapping)
- Vendor/customer contractual requirements
- Internal InfoSec policies

**AI Mapping →** hipaa-compliance.regulations, soc2-controls.frameworks

---

## 4. HIPAA Safeguards: Intent-Level Control Summary
**Team Member Instructions:**  
Describe the high-level approach to HIPAA’s **Technical Safeguards**, including:

- Access control  
- Audit controls  
- Integrity  
- Authentication  
- Transmission security  

Do NOT describe implementation — describe *required outcomes* and “how we achieve compliance.”

**AI Mapping →** hipaa-compliance.safeguards[*]

---

## 5. SOC 2 Trust Services Criteria Mapping
**Team Member Instructions:**  
Summarize how the system intends to meet key SOC 2 Security, Availability, and
Confidentiality principles:

- Logical access  
- Change management  
- Risk assessment  
- Incident response  
- Logging and monitoring  
- Vendor management  

Note: Detailed control tables belong in later phases; this is the Intent-level narrative.

**AI Mapping →** soc2-controls.controls[*]

---

## 6. Access Control & Identity Management Expectations
**Team Member Instructions:**  
Describe access control principles:

- Role-based access  
- Least privilege  
- Separation of duties  
- MFA and session requirements  
- Access provisioning and deprovisioning workflows  
- Patient identity verification expectations  

**AI Mapping →** hipaa-compliance.access_controls, soc2-controls.identity

---

## 7. Data Protection Requirements
**Team Member Instructions:**  
Define the compliance expectations around:

- Data encryption at rest (FIPS 140-2 expectations if applicable)
- Data encryption in transit (TLS 1.2+)
- Key management responsibilities
- PHI/PII minimization
- Data masking or redaction requirements
- Handling of sensitive audit logs

**AI Mapping →** hipaa-compliance.data_protection, retention-policy.references

---

## 8. Logging, Monitoring & Audit Requirements
**Team Member Instructions:**  
Describe the required audit posture:

- Which events must be logged  
- Minimum attributes required per log entry  
- Log tamper-resistance expectations  
- Correlation ID expectations  
- Monitoring scope (security events, access events, performance indicators)
- Retention requirements for logs  

**AI Mapping →** audit-requirements.entries[*], provenance-tracking.audit_model

---

## 9. Incident Response & Breach Notification
**Team Member Instructions:**  
Describe:

- Incident definitions
- Escalation paths
- Reporting timelines (e.g., HIPAA's 60-day rule)
- Forensic logging expectations
- Communication channels with customers and authorities

**AI Mapping →** policy-enforcement.incident_response

---

## 10. Vendor & Third-Party Governance
**Team Member Instructions:**  
Identify:

- Any third-party services that handle PHI/PII
- Required agreements (BAA, DPA)
- Security verification requirements (SOC 2, HITRUST)
- Data transfer limitations

**AI Mapping →** soc2-controls.vendor_requirements, policy-enforcement.third_party

---

## 11. Internal Governance Processes
**Team Member Instructions:**  
Describe:

- How policies are created, reviewed, approved
- How exceptions are managed
- How risk assessments occur
- How internal audits are run
- Ownership of compliance artifacts

**AI Mapping →** policy-enforcement.processes

---

## 12. Evidence & Documentation Expectations
**Team Member Instructions:**  
Define what evidence must exist to prove compliance:

- Policies  
- Standards  
- Architectural diagrams  
- Change management records  
- Access reviews  
- Audit logs  
- Training records  

**AI Mapping →** soc2-controls.evidence, audit-requirements.evidence

---

## 13. Compliance Risks & Open Questions
**Team Member Instructions:**  
List known compliance risks and unresolved questions.

Examples:
- PHI flows may not be traceable across all services.
- Customer-specific retention rules may conflict with defaults.
- External dependencies may lack required documentation.

**AI Mapping →** hipaa-compliance.risks, soc2-controls.risks, audit-requirements.risks, policy-enforcement.risks

---

## 14. Provenance
created_by: "{{ NAME }}"
created_at: "{{ ISO8601 }}"
source: "Intent Phase – Compliance & Governance Domain"
notes: "Initial draft for compliance evaluation."