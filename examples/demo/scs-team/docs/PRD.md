# Patient Portal - Product Requirements Document

**Author:** Sarah Chen, Product Manager
**Last Updated:** 2026-01-15
**Status:** Approved
**Stakeholders:** Dr. James Park (CMO), Lisa Torres (CTO), Mark Rivera (CISO), Product Team

## Executive Summary

Build a patient-facing web portal that gives patients secure access to their health records, appointment scheduling, messaging with providers, and medication management. This replaces our current phone-based scheduling and paper-based communication workflow.

## Problem Statement

Patients at Acme Health currently have no self-service access to their health information. All appointment scheduling goes through a call center (avg. wait time: 12 minutes). Lab results are delivered by mail (avg. 5 days). Medication refill requests require a phone call to the provider's office.

This creates:
- Patient dissatisfaction (NPS: 32, industry avg: 45)
- High call center costs ($2.1M/year for scheduling alone)
- Delayed care decisions due to slow information access
- Provider time wasted on administrative tasks

## Goals

1. **Patient self-service**: 60% of appointments booked online within 6 months
2. **Reduce call center volume**: 40% reduction in scheduling calls
3. **Faster information access**: Lab results available within 4 hours of completion
4. **Provider efficiency**: Reduce admin time by 25% through async messaging
5. **Patient satisfaction**: NPS improvement to 50+ within 12 months

## Non-Goals

- Clinical decision support or AI-driven diagnostics
- Insurance/billing portal (separate initiative, Q3 2026)
- Mobile native app (responsive web first, native app in v2)
- Integration with external pharmacies (v2)

## Stakeholders

| Role | Name | Interest |
|------|------|----------|
| Executive Sponsor | Dr. James Park (CMO) | Clinical workflow, patient outcomes |
| Technical Lead | Lisa Torres (CTO) | Architecture, scalability, integration |
| Security Lead | Mark Rivera (CISO) | HIPAA compliance, PHI protection |
| Clinical Lead | Dr. Amy Nguyen | Provider workflow, messaging |
| Operations | Carlos Mendez | Call center impact, training |
| Patient Advisory | Patient Advisory Board | Usability, accessibility |

## User Stories

### Patient

1. As a patient, I can log in securely and view my health summary dashboard
2. As a patient, I can view my lab results with reference ranges and trends
3. As a patient, I can schedule, reschedule, or cancel appointments with available providers
4. As a patient, I can send secure messages to my care team
5. As a patient, I can view my medication list and request refills
6. As a patient, I can update my demographics and insurance information
7. As a patient, I can view and download my visit summaries
8. As a patient, I can set notification preferences (email, SMS)

### Provider

9. As a provider, I can view and respond to patient messages in a queue
10. As a provider, I can see my upcoming appointment schedule
11. As a provider, I can view a patient's portal activity before a visit

### Admin

12. As an admin, I can manage provider schedules and availability
13. As an admin, I can view portal usage analytics
14. As an admin, I can manage patient accounts (unlock, reset)

## Data Requirements

### Patient Record
- Demographics: name, DOB, address, phone, email, emergency contact
- Insurance: carrier, member ID, group number
- Clinical: allergies, conditions, medications, immunizations
- Lab results: test name, value, reference range, date, ordering provider

### Appointment
- Patient, provider, location, datetime, type (in-person, telehealth), status
- Notes (provider-facing), reason for visit (patient-facing)

### Message
- Sender, recipient, subject, body, timestamp, read status
- Thread ID for conversation tracking
- Attachments (images, documents)

## Integration Requirements

- **EHR System (Epic)**: Bidirectional sync via FHIR R4 APIs for patient records, lab results, medications, appointments
- **Identity Provider**: SSO via SAML 2.0 for staff, OAuth 2.0 + PKCE for patients
- **Notification Service**: SendGrid for email, Twilio for SMS
- **Scheduling Engine**: Existing internal scheduling API (REST)

## Compliance Requirements

- HIPAA Privacy and Security Rule compliance required
- All PHI must be encrypted at rest and in transit
- Audit logging for all PHI access
- BAAs required with all third-party vendors handling PHI
- 21 CFR Part 11 compliance for electronic signatures (future)
- WCAG 2.1 AA accessibility compliance

## Technical Constraints

- Must integrate with existing Epic EHR (FHIR R4)
- Must support 50,000 active patients within 12 months
- Page load time < 2 seconds (p95)
- 99.9% uptime SLA
- Must run in Acme Health's AWS environment (us-east-1, us-west-2)

## Timeline

| Milestone | Target Date | Scope |
|-----------|-------------|-------|
| Alpha | 2026-03-15 | Auth, patient dashboard, lab results |
| Beta | 2026-05-01 | Scheduling, messaging, medication management |
| GA | 2026-07-01 | Full feature set, 3 pilot clinics |
| Scale | 2026-10-01 | All 12 clinics, 50K patients |

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Online appointment booking rate | 60% | Portal bookings / total bookings |
| Call center volume reduction | 40% | Monthly call volume comparison |
| Lab result access time | < 4 hours | Time from result to patient view |
| Patient NPS | 50+ | Quarterly survey |
| Portal adoption | 40% of eligible patients | Active accounts / eligible patients |
| System uptime | 99.9% | Monthly availability report |

## Risks

1. **EHR Integration Complexity**: Epic FHIR APIs may not expose all needed data. Mitigation: early API discovery phase.
2. **Patient Adoption**: Patients may not adopt the portal. Mitigation: onboarding campaign, staff training.
3. **HIPAA Breach**: PHI exposure through the portal. Mitigation: security review, penetration testing, audit logging.
4. **Provider Resistance**: Providers may not adopt messaging workflow. Mitigation: clinical champion program.
