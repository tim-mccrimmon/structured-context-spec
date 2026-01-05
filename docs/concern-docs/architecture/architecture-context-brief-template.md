---
title: "Architecture Context Brief (Template)"
domain: "architecture"
version: "1.0"
status: "Template"
scs_version: "0.2.0"
structure_hash: "sha256:2a8ef54ce38d441d"
---

## 1. Purpose and Instructions
**Team Member Instructions:**  
Describe the architecture at a high level, focusing on system boundaries, actors,
context, constraints, and guiding principles. Write in clear narrative form.
Avoid speculation—capture known information and open questions.

**AI Extraction Mapping:**  
This section feeds the top-level metadata fields in `system-context.scd.yaml`.
---

## 2. Business and Technical Drivers
**Team Member Instructions:**  
Summarize the core business goals and architectural imperatives. Include only
what is necessary for architecture.

- Improve medication adherence and reduce readmissions.
- Provide reliable reminders and check-ins for patients.
- Provide clinicians with timely adherence visibility.
- Support multi-tenant SaaS with secure tenant isolation.
- Maintain HIPAA compliance and strong security posture.

**AI Mapping →** system-context.business_drivers

---

## 3. Guiding Architectural Principles
**Team Member Instructions:**  
List the principles shaping the architecture. Keep it concise and actionable.

- Simplicity and maintainability.
- Interoperability with healthcare systems.
- Security by design.
- Event-driven insight and extensibility.
- Observability built in.
- Incremental evolution.

**AI Mapping →** system-context.quality_attributes.principles

---

## 4. High-Level Architecture Overview
**Team Member Instructions:**  
Provide a narrative description of the overall architecture and the primary domains.

The Medication Adherence Platform has three primary domains:

1. **Patient Engagement Layer** – mobile/web app, reminders, check-ins.
2. **Clinical Insight Layer** – adherence summaries, dashboards, care team tools.
3. **Core Platform Services** – schedules, adherence tracking, notifications, escalation engine, integrations, storage, analytics.

**AI Mapping →** system-context.context, component-model.high_level_components

---

## 5. External Actors
**Team Member Instructions:**  
List all human users and describe their interactions.

- **Patient:** Receives reminders, submits adherence check-ins.
- **Clinician:** Reviews adherence summaries.
- **Care Coordinator:** Monitors escalations, performs outreach.
- **Admin:** Configures programs and views metrics.
- **IT Admin:** Manages identity integrations and connectivity.

**AI Mapping →** system-context.external_actors

---

## 6. External Systems
**Team Member Instructions:**  
List each external system with purpose and protocols.

- **EHR (FHIR R4):** MedicationRequest, MedicationStatement.
- **IdP:** OAuth2/OIDC for clinician login.
- **Push Gateway:** APNs/FCM for patient notifications.
- **SMS Vendor:** Twilio for fallback messaging.
- **Analytics Consumers:** Downstream reporting.

**AI Mapping →** system-context.external_systems, integration-map.targets

---

## 7. System Boundaries
**Team Member Instructions:**  
Declare scope clearly.

**In Scope:**
- Patient apps, reminders, check-ins.
- Schedule ingestion, adherence tracking.
- Notification delivery.
- Clinician/care-team dashboards.

**Out of Scope (v1):**
- Pharmacy dispensing.
- Billing integrations.
- Two-way chat.
- EHR write-back.

**AI Mapping →** system-context.system_boundaries

---

## 8. Deployment & Hosting Context
**Team Member Instructions:**  
Describe cloud model, regions, tenancy, and connectivity.

- Cloud multi-tenant SaaS.
- Logical tenant isolation for each health system.
- US-based HIPAA-aligned regions.
- Secure outbound access to EHRs.
- Public access for patient devices.

**AI Mapping →** system-context.deployment_context

---

## 9. Data Overview
**Team Member Instructions:**  
Describe types of data, sensitivity, and storage expectations.

- PHI: schedules, check-ins, alerts.
- Event logs and audit trails.
- Analytics aggregates.
- US-only residency.

**AI Mapping →** system-context.data_overview

---

## 10. Quality Attributes
**Team Member Instructions:**  
Define availability, timeliness, performance expectations.

- 99.9% API SLA.
- Notification delivery ±5 minutes.
- Clinician dashboard <2 seconds.
- Reliable retries for EHR and notification failures.

**AI Mapping →** system-context.quality_attributes

---

## 11. Constraints & Assumptions
**Team Member Instructions:**  
List all constraints and explicit assumptions.

**Constraints:**
- Must integrate via SMART on FHIR.
- Must support intermittent connectivity.

**Assumptions:**
- Patients have mobile/SMS access.
- Clinicians authenticate via IdP.

**AI Mapping →** system-context.constraints, system-context.assumptions

---

## 12. Risks & Open Questions
**Team Member Instructions:**  
Identify known risks and unresolved issues.

**Risks:**
- EHR variability.
- Low patient engagement.
- Escalation fatigue.

**Open Questions:**
- EHR write-back timing.
- Offline-first requirements.
- Pharmacy refill integration.

**AI Mapping →** system-context.risks, system-context.open_questions

---

## 13. Technology Stack (Explicit for SCD Extraction)
**Team Member Instructions:**  
Specify the actual technology choices and tentative versions.

- **Runtime:** Python 3.12, Node 20.x (TS 5.x)
- **API Style:** REST (GraphQL optional v2)
- **Datastore:** MongoDB Atlas 7.x
- **Analytics:** Cloud-native analytical store
- **Eventing:** Azure Event Grid (or AWS SNS/SQS)
- **Hosting:** Azure App Service or AKS
- **IaC:** Terraform 1.9
- **CI/CD:** GitHub Actions

**AI Mapping →** tech-stack.*

---

## 14. Integration Endpoints (Explicit for SCD Extraction)
**Team Member Instructions:**  
List all integrations clearly with purposes.

- **EHR FHIR R4:** Read MedicationRequest, MedicationStatement
- **IdP:** OAuth2/OIDC login
- **Push:** APNs/FCM notifications
- **SMS:** Twilio fallback
- **Analytics Export:** Batch CSV/Parquet

**AI Mapping →** integration-map.endpoints

---

## 15. Component Responsibilities & Data Ownership
**Team Member Instructions:**  
List each component with its owned data and interactions.

### Patient App
- responsibilities: reminders, check-ins
- interacts: API Gateway

### Clinician Dashboard
- responsibilities: show adherence summaries
- interacts: API Gateway

### API Gateway
- responsibilities: routing, auth, throttling

### Medication Schedule Service
- owns: `medication_plan`
- inputs: EHR FHIR
- outputs: patient schedule

### Adherence Tracking Service
- owns: `adherence_event`
- inputs: patient check-ins
- outputs: adherence metrics

### Notification Service
- owns: `notification_event`
- inputs: schedules, adherence state

### Escalation Engine
- owns: `escalation_event`
- inputs: missed doses
- outputs: alerts to coordinators

### Integration Layer
- owns: `ehr_connection_log`
- inputs: EHR FHIR pull

### Background Workers
- responsibilities: sync, cleanup, analytics

**AI Mapping →** component-model.*

---

## 16. Provenance
created_by: "tim@example.com"
created_at: "2025-11-27"
source: "Intent Phase – Architecture Domain"