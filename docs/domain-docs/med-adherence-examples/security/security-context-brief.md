# Security Context Brief
Project: Medication Adherence Platform
Domain: Security
Version: 1.0
Status: Draft
Phase: Intent

This document describes the security posture for the Medication Adherence
Platform and supports generation of:

- scd:project:authn-authz
- scd:project:data-protection
- scd:project:data-handling
- scd:project:threat-model

---

## 1. Purpose and Scope
The Medication Adherence Platform processes PHI for patients enrolled in
adherence programs and exposes clinician and admin interfaces. Security must:

- Protect PHI and PII from unauthorized access or disclosure.
- Ensure only authorized clinicians and care teams can see patient adherence.
- Preserve integrity of adherence events and medication plans.
- Prevent abuse of notification channels.

Scope includes:

- Patient web/mobile interface
- Clinician and coordinator dashboards
- Backend services (schedules, adherence, notifications, escalation)
- Integration layer (EHR, IdP, messaging providers)
- Data storage and audit logs

Out of scope:

- Governance of the health system’s own EHR infrastructure
- Research environments using de-identified data with separate controls

---

## 2. Security Objectives
- Ensure adherence data is only visible to authorized clinicians and care teams.
- Prevent unauthorized access to patient accounts.
- Prevent tampering with adherence records and escalation workflows.
- Minimize PHI exposure in logs, notifications, and integrations.
- Provide enough security telemetry to detect and investigate incidents.

---

## 3. Trust Boundaries & Security Zones

- **Public Internet Zone**  
  - Patient browser/mobile clients  
  - Clinician web clients  

- **Application Zone (Cloud)**  
  - API gateway  
  - Backend services (schedule, adherence, notification, escalation)  

- **Data Zone (Cloud)**  
  - Primary database for PHI  
  - Audit log store  
  - Analytics store (aggregated data)  

- **External Partner Zone**  
  - EHR APIs  
  - IdP (SSO)  
  - SMS and push providers  

Key trust boundaries:

- Between public clients and API gateway (authn/authz, rate limiting).  
- Between app zone and data zone (DB access controlled by service identities).  
- Between platform and external systems (EHR, IdP, messaging vendors).

---

## 4. Authentication (AuthN) Model

**Patients**
- Authenticate with platform-managed credentials (email/phone + password or magic link).
- Optional MFA via SMS or authenticator app for high-risk cohorts.
- Short-lived session tokens; device binding where possible.

**Clinicians / Coordinators**
- Authenticate via health system IdP using OIDC (SSO).
- MFA enforced by customer IdP policy.
- No local password storage for clinicians in the platform.

**Admins**
- Authenticate via corporate IdP with enforced MFA.
- Access restricted to limited set of internal users.

**Internal Services**
- Use short-lived service tokens or mTLS for service-to-service communication.

---

## 5. Authorization (AuthZ) & Role Model

Roles:

- **Patient**  
  - Can only access own data (MedicationPlan, AdherenceEvents, notifications).  

- **Clinician**  
  - Can access adherence data for patients assigned to their care team.  
  - Cannot modify system-level program configuration.  

- **Care Coordinator**  
  - Can access adherence and EscalationEvents for assigned programs/panels.  
  - Can document outreach and resolution.  

- **Admin**  
  - Can manage ProgramConfig and tenant-level settings.  
  - No direct access to PHI by default (unless also granted a clinical role).  

Authorization model:

- Enforced via RBAC with resource-level checks (tenant, patient, program).
- Claims-based authorization in tokens (role, tenant, permitted scopes).
- All sensitive API endpoints enforce both role and scope checks.

---

## 6. Service-to-Service Security

- Backend services authenticate to each other using:
  - mTLS between services inside the cluster.
  - Service identity tokens issued by the platform (short-lived JWTs).
- API gateway acts as a central policy enforcement point:
  - Validates tokens  
  - Injects identity/tenant context into downstream requests  

---

## 7. Data Protection in Transit

- All external communications use TLS 1.2+ (prefer 1.3).
- HSTS enabled for web endpoints.
- PHI never placed in URLs or query strings; use request bodies or opaque IDs.
- WebSockets (if used) must also run over TLS with authenticated sessions.

---

## 8. Data Protection at Rest

- All databases storing PHI are encrypted at rest with cloud-provider KMS.
- Keys managed via KMS; rotation at least every 12 months (prefer 6).
- Separate KMS keys for:
  - Primary PHI store  
  - Audit log store  
  - Backup storage  
- Access to raw KMS keys restricted to security/infra roles.

---

## 9. Secrets Management

- All API keys (EHR, SMS, push) and service credentials stored in a secure vault
  (e.g., Azure Key Vault or AWS Secrets Manager).
- No secrets in source code or config files.
- Rotation policies:
  - Database credentials: at least annually or after incidents.  
  - External API keys: per vendor recommendation or quarterly.  
- Secrets injected at runtime via environment or sidecar, not committed.

---

## 10. Data Handling & Minimization

- **Notifications (Push/SMS)**  
  - No medication names or diagnoses in message body.  
  - Use generic language (e.g., “You have a scheduled dose”), with details in app.  

- **Logs**  
  - Patient identifiers masked where possible.  
  - PHI only logged at minimal granularity required to troubleshoot issues.  
  - Debug logs with PHI prohibited in production.  

- **Test/Dev Environments**  
  - No real PHI allowed.  
  - Use synthetic or properly de-identified datasets.  

- **Exports**  
  - Exports with PHI only allowed for authorized users and logged aggressively.

---

## 11. Secure Coding & SDLC Practices

- All services:
  - Use dependency scanning (SCA) and static code analysis (SAST) in CI.  
  - Require code review by at least one other engineer.  
  - Follow secure coding guidelines (input validation, parameterized queries, etc.).  

- Libraries:
  - No use of unsupported or end-of-life frameworks.  
  - Critical vulnerabilities patched on an expedited timeline.  

- Security Testing:
  - Regular internal penetration testing for APIs and web apps.  
  - Threat modeling revisited for major feature changes.

---

## 12. Threat Model Overview

**Threat Actors**
- External attackers attempting account takeover or data theft.
- Malicious insiders with elevated access misusing PHI.
- Compromised credentials or tokens.
- Misconfigured integrations exposing data.

**Key Assets**
- PHI in MedicationPlan and AdherenceEvent.
- Access tokens and refresh tokens.
- Admin credentials and program configuration.
- Audit logs and escalation history.

**Key Threat Scenarios (examples)**
- Credential stuffing against patient or clinician logins.
- Enumeration of patient records via weak access controls.
- Abuse of notification channels for phishing or data leakage.
- Tampering with adherence data to hide non-compliance.
- Exploiting vulnerable dependencies in public APIs.

---

## 13. Mitigations & Security Controls

- Strong password policies and rate limiting on login endpoints.
- MFA for all admin and clinician accounts (via IdP).
- RBAC with strict tenant/patient scoping.
- Input validation and protection against injection attacks.
- CSP and other browser security headers for web clients.
- Continuous dependency scanning and patching.
- Security logging and anomaly detection on:
  - excessive failed logins  
  - unusual access patterns  
  - mass export attempts  

---

## 14. Security Monitoring & Alerting

- Security events pushed to a centralized logging system (and SIEM if present).
- Alerts configured for:
  - repeated login failures from same IP/user  
  - unusual access to high-risk patient cohorts  
  - spikes in export/download activity  
  - tampering attempts on ProgramConfig  
- On-call rotation with documented runbooks for security alerts.

---

## 15. Security Risks & Open Questions

**Risks**
- SMS-based MFA and notifications have inherent exposure risks (phone number
  compromise, message preview on lock screen).
- Dependence on third-party vendors for critical services (SMS, push) introduces
  shared responsibility risk.
- Internal misconfigurations (e.g., overly broad admin permissions) could lead
  to excessive PHI access.

**Open Questions**
- Will some customers require FIPS-validated modules end-to-end?
- Do we need device attestation or jailbreak/root detection for mobile apps?
- Should we support hardware security keys for high-sensitivity roles?

---

## 16. Provenance
created_by: "Security Lead – Medication Adherence"
created_at: "2025-11-27T19:00:00Z"
source: "Intent Phase – Security Domain"
notes: "Initial security posture for pilot deployments; to be refined post-threat modeling workshop."