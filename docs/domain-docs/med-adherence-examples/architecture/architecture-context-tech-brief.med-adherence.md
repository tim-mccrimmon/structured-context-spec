# Architecture Context & Technical Brief (Enhanced)
Medication Adherence Platform  
Version: 1.0  
Status: Draft  
Phase: Intent  
Domain: Architecture

This document provides a structured, human-friendly, and AI-friendly architectural
overview for the Medication Adherence Platform. It is designed as both:
1. A **team template** used during the Intent Phase.
2. A **machine-readable feeder** for generating Architecture SCDs:
   - system-context
   - tech-stack
   - integration-map
   - component-model

---

## 1. Purpose and Instructions
**Team Member Explanation:**  
This brief describes the architectural landscape of the Medication Adherence
Platform: its system boundaries, actors, constraints, components, integrations,
technology choices, deployment context, and quality attributes.

**AI Mapping:**  
Feeds top-level fields in `system-context.scd.yaml`.

---

## 2. Business and Technical Drivers
The platform exists to solve the widespread issue of post-operative and chronic-care
medication non-adherence. Missed doses and timing deviations lead to preventable
complications, readmissions, and degraded quality metrics for health systems.

Primary architectural drivers:
- Enable reliable, timely medication reminders for patients.
- Capture adherence events with complete auditability.
- Provide clinicians and care coordinators with real-time adherence visibility.
- Support event-driven escalation workflows for missed doses.
- Operate as a **multi-tenant HIPAA-compliant cloud platform**.
- Integrate seamlessly with EHR systems using open standards (SMART on FHIR).
- Deliver predictable performance during high-demand windows (morning/evening doses).

**AI Mapping →** system-context.business_drivers

---

## 3. Guiding Architectural Principles
- **Simplicity & Maintainability:** Favor minimal service boundaries early in the product lifecycle.
- **Interoperability:** Rely on FHIR R4, OAuth2/OIDC, and standards-based identity flows.
- **Security by Design:** End-to-end encryption, least privilege, centralized auditing.
- **Event-Driven Insight:** Asynchronous workflows for missed-dose detection and escalation.
- **Observability Everywhere:** Traces, structured logs, health checks, metrics.
- **Incremental Evolution:** Architecture must support chronic-care use cases with minimal redesign.

**AI Mapping →** system-context.quality_attributes.principles

---

## 4. High-Level Architecture Overview
The Medication Adherence Platform is organized into **three major architectural domains**:

### 1. Patient Engagement Layer
- Mobile-responsive web app and optional native wrappers.
- Receives scheduled notifications (push or SMS).
- Displays medication schedules and collects check-ins.

### 2. Clinical Insight Layer
- Web-based clinician dashboard.
- Provides adherence summaries, trends, and patient-level detail.
- Supports care coordinator workflows for escalations.

### 3. Core Platform Services
- Medication Schedule Service (EHR ingestion + schedule generation)
- Adherence Tracking Service (event ingestion + metrics)
- Notification Service (push/SMS orchestration)
- Escalation Engine (rules evaluation + coordinator routing)
- Integration Layer (FHIR, IdP, messaging gateways)
- Data storage, audit logs, and background workers

**AI Mapping →** system-context.context, component-model.high_level_components

---

## 5. External Actors
- **Patient** — receives reminders, submits check-ins.
- **Clinician** — reviews adherence summaries and patient-level adherence data.
- **Care Coordinator** — monitors escalations, performs follow-up outreach.
- **Program Administrator** — configures programs, monitors metrics.
- **IT/Integration Administrator** — manages identity integration and EHR connectivity.

**AI Mapping →** system-context.external_actors

---

## 6. External Systems
- **EHR (FHIR R4)**  
  MedicationRequest + MedicationStatement ingestion; SMART on FHIR for auth.
- **Identity Provider (IdP)**  
  OAuth2/OIDC (Okta, Azure AD, or health system IdP).
- **Push Notification Gateway**  
  APNs/FCM for mobile push messages.
- **SMS Vendor**  
  Twilio for fallback SMS notifications.
- **Analytics Consumers**  
  Health system quality programs ingest summary metrics (batch API or CSV export).

**AI Mapping →** system-context.external_systems  
**AI Mapping →** integration-map.targets

---

## 7. System Boundaries

### In Scope (v1)
- Medication plan ingestion via FHIR.
- Schedule normalization and display to patients.
- Time-based reminders via push/SMS.
- Patient check-ins and adherence event recording.
- Escalation logic and alerts to care coordinators.
- Clinician dashboards with real-time adherence metrics.

### Out of Scope (v1)
- Full pharmacy dispensing integration.
- Automated clinical decision support.
- Real-time chat.
- Writing adherence data back into the EHR.

**AI Mapping →** system-context.system_boundaries

---

## 8. Deployment & Hosting Context
- **Hosting:** Azure cloud (App Service or AKS).
- **Residency:** US-only regions for HIPAA-compliant workloads.
- **Tenancy:** Logical multi-tenancy with enforced patient and tenant isolation.
- **Connectivity:**  
  - Outbound API access to EHR endpoints.  
  - Public HTTPS endpoints for patient app and clinician dashboard.  
- **Resilience:**  
  - Zones redundancy for backend services.  
  - Event-based retry for EHR sync failures.

**AI Mapping →** system-context.deployment_context

---

## 9. Data Overview
### Data Subjects
- Patients
- Clinicians
- Care teams

### Data Types
- Medication schedules
- Check-ins and adherence events
- Notifications (sent/delivered/failed)
- Escalation events
- Audit logs
- Aggregate adherence metrics

### Sensitivity & Residency
- All PHI stored in encrypted cloud databases.
- All data stays within US-region boundaries.

**AI Mapping →** system-context.data_overview

---

## 10. Quality Attributes
- **Availability:** 99.9% uptime target for core APIs.
- **Performance:**  
  - Notifications delivered within ±5 minutes of scheduled dose.  
  - Adherence dashboard loads in <2 seconds.  
- **Reliability:**  
  - Retry policies for notifications and EHR sync.  
  - Background workers handle recovery.  
- **Scalability:**  
  - Demand spikes around morning/evening dosing windows.  
  - Autoscaling event-driven services.

**AI Mapping →** system-context.quality_attributes

---

## 11. Constraints & Assumptions

### Constraints
- Must integrate with at least one major EHR vendor via SMART on FHIR.
- Must run within a HIPAA-aligned cloud region.
- Must support low-bandwidth or intermittent patient connectivity.

### Assumptions
- Each tenant provides a functioning IdP for clinical login.
- Patients have at least SMS-capable devices.
- Care teams have capacity to manage escalation volumes.

**AI Mapping →** system-context.constraints, system-context.assumptions

---

## 12. Risks & Open Questions

### Risks
- **EHR variability:** Medication data formats differ significantly.
- **Low patient engagement:** Certain cohorts may ignore reminders.
- **Escalation fatigue:** Too many alerts may overwhelm care teams.

### Open Questions
- When (if ever) should adherence summaries be written back to the EHR?
- Should offline-first be mandatory for tablets or frontier clinics?
- Should phase 2 include pharmacy refill signals?

**AI Mapping →** system-context.risks, system-context.open_questions

---

## 13. Technology Stack (Explicit for SCD Extraction)

### Core Technologies
- **Runtime:**  
  - Python 3.12 (backend services)  
  - Node 20.x / TypeScript 5.x (dashboard + patient web app)
- **API Style:** REST (GraphQL optional for analytics v2)
- **Datastore:** MongoDB Atlas 7.x (OLTP)  
- **Audit Store:** Immutable append-only log DB  
- **Analytics:** Cloud-native analytical store (Cosmos DB analytical or BigQuery-like)

### Infrastructure
- **Eventing:** Azure Event Grid (AWS SNS/SQS optional)  
- **Hosting:** Azure App Service, optional AKS for scaling  
- **IaC:** Terraform 1.9  
- **CI/CD:** GitHub Actions  
- **Secrets:** Azure Key Vault / AWS Secrets Manager  

**AI Mapping →** tech-stack.*

---

## 14. Integration Endpoints (Explicit for SCD Extraction)

- **EHR FHIR R4:**  
  - Resources: MedicationRequest, MedicationStatement  
  - Auth: SMART on FHIR  
  - Flow: periodic pull, normalized into medication_plan  
- **IdP:** OAuth2/OIDC  
- **Push:** APNs (iOS), FCM (Android)  
- **SMS:** Twilio REST API  
- **Analytics Export:** Batch CSV/Parquet, optional API endpoint for bulk pulls  

**AI Mapping →** integration-map.endpoints

---

## 15. Component Responsibilities & Data Ownership

### Patient App
- UI for schedules, reminders, check-ins
- Interacts with API Gateway only

### Clinician Dashboard
- Displays patient-level and aggregated adherence metrics
- Interacts with API Gateway

### API Gateway
- Routing, request validation, rate limiting
- Auth enforcement for clinical users and patients

### Medication Schedule Service
- **Owns:** `medication_plan`  
- **Inputs:** EHR FHIR pull, admin config  
- **Outputs:** patient-facing schedules  

### Adherence Tracking Service
- **Owns:** `adherence_event`  
- **Inputs:** patient check-ins  
- **Outputs:** adherence metrics, risk signals  

### Notification Service
- **Owns:** `notification_event`  
- **Inputs:** schedules, escalations  
- **Outputs:** push/SMS notifications  

### Escalation Engine
- **Owns:** `escalation_event`  
- **Inputs:** missed-dose triggers  
- **Outputs:** coordinator alerts  

### Integration Layer
- **Owns:** `ehr_connection_log`  
- **Inputs:** EHR polling  
- **Outputs:** normalized medication schedules  

### Background Workers
- Sync jobs, cleanup, nightly batch analytics, notification retries

**AI Mapping →** component-model.*

---

## 16. Provenance
created_by: "Architecture Lead"
created_at: "2025-11-27"
source: "Intent Phase – Medication Adherence Project"