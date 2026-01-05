---
title: "Security Context Brief (Template)"
domain: "security"
version: "1.0"
status: "Template"
scs_version: "0.2.0"
structure_hash: "sha256:f7039194c1ae3e44"
---

## 1. Purpose and Scope
**Team Member Instructions:**  
Summarize the security scope for this system: what we must protect, from whom,
and at what assurance level. Focus on PHI/PII, privileged access, and critical
flows.

**AI Mapping →** authn-authz.scope, data-protection.scope, data-handling.scope
---

## 2. Security Objectives
**Team Member Instructions:**  
List the primary security objectives, in business terms, not just controls.
Examples: protect PHI, ensure only authorized clinicians see adherence data,
prevent privilege escalation, ensure integrity of adherence events.

**AI Mapping →** authn-authz.objectives, data-protection.objectives

---

## 3. Trust Boundaries & Security Zones
**Team Member Instructions:**  
Describe trust boundaries and security zones (e.g., public internet, app tier,
data tier, admin interfaces, customer network). Note which actors/systems reside
in each zone.

**AI Mapping →** threat-model.trust_boundaries

---

## 4. Authentication (AuthN) Model
**Team Member Instructions:**  
Describe how users and services authenticate:

- Patients  
- Clinicians / Coordinators  
- Admins  
- Internal services  

Address:

- Identity providers (IdPs)  
- Protocols (OIDC/OAuth2, SAML, etc.)  
- MFA requirements  
- Session and token lifetimes  

**AI Mapping →** authn-authz.authentication

---

## 5. Authorization (AuthZ) & Role Model
**Team Member Instructions:**  
Define:

- Roles (e.g., Patient, Clinician, Coordinator, Admin, Support)  
- Permissions for each role (read/write PHI, program config, user management)  
- Scope concepts (per-tenant, per-patient, per-program)  
- How least privilege is enforced  

**AI Mapping →** authn-authz.authorization

---

## 6. Service-to-Service Security
**Team Member Instructions:**  
Describe how internal services authenticate and authorize with each other:

- mTLS?  
- JWTs or service tokens?  
- API gateways and policy enforcement points?  

**AI Mapping →** authn-authz.service_to_service

---

## 7. Data Protection in Transit
**Team Member Instructions:**  
Define expectations for:

- Protocols (TLS versions, cipher requirements)  
- HSTS / secure cookies  
- Restrictions on PHI in URLs/query strings  
- Handling of webhooks or callbacks, if any  

**AI Mapping →** data-protection.in_transit

---

## 8. Data Protection at Rest
**Team Member Instructions:**  
Describe:

- Encryption at rest requirements (e.g., FIPS 140-2)  
- Key management (KMS, rotation)  
- Separation of duties for key access  
- Special protection for audit logs and backups  

**AI Mapping →** data-protection.at_rest

---

## 9. Secrets Management
**Team Member Instructions:**  
Document:

- Where secrets live (vault, parameter store, etc.)  
- Who can access them  
- Rotation policies  
- How secrets are injected into services (env vars, sidecars, etc.)  

**AI Mapping →** data-protection.secrets_management

---

## 10. Data Handling & Minimization
**Team Member Instructions:**  
Describe rules for:

- What PHI is allowed in which channels (e.g., logs, notifications, URLs)  
- Masking/redaction requirements  
- Anonymization/pseudonymization practices  
- Handling of test data (no production PHI in lower envs, etc.)  

**AI Mapping →** data-handling.policies

---

## 11. Secure Coding & SDLC Practices
**Team Member Instructions:**  
Summarize baseline secure engineering practices:

- Static/dynamic code analysis  
- Dependency scanning  
- Secure coding guidelines  
- Code review requirements  
- Security training expectations  

**AI Mapping →** data-handling.secure_sdlc

---

## 12. Threat Model Overview
**Team Member Instructions:**  
Provide a high-level threat model:

- Primary threat actors (e.g., external attackers, malicious insiders, misconfig)  
- Key assets (PHI, credentials, tokens, configuration, audit logs)  
- Likely threat scenarios (STRIDE-style or equivalent)  

Focus on the most important threats, not every edge case.

**AI Mapping →** threat-model.threats, threat-model.assets

---

## 13. Mitigations & Security Controls
**Team Member Instructions:**  
For each major threat scenario, list the primary mitigating controls. Reference
categories like:

- Authentication & Authorization  
- Network segmentation  
- Input validation  
- Rate limiting & abuse detection  
- Logging & anomaly detection  

**AI Mapping →** threat-model.mitigations, authn-authz.controls, data-protection.controls

---

## 14. Security Monitoring & Alerting
**Team Member Instructions:**  
Describe:

- What security signals must be monitored (login failures, unusual access, etc.)  
- Alert thresholds  
- Who responds to alerts  
- Integrations with SIEM/SOC, if any  

**AI Mapping →** threat-model.monitoring, audit-requirements.security_signals (if cross-referenced)

---

## 15. Security Risks & Open Questions
**Team Member Instructions:**  
List known security risks (e.g., SMS channel exposure, EHR connectivity risk) and
open design questions.

**AI Mapping →** threat-model.risks, authn-authz.risks, data-protection.risks

---

## 16. Provenance
created_by: "{{ NAME }}"
created_at: "{{ ISO8601 }}"
source: "Intent Phase – Security Domain"
notes: "Initial security context; to be refined during design and implementation."