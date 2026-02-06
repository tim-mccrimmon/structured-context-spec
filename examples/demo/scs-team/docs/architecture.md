# Patient Portal - Architecture Document

**Author:** Lisa Torres, CTO
**Last Updated:** 2026-01-20
**Status:** Draft

## System Overview

The Patient Portal is a web application providing patients secure access to their health records, appointment scheduling, provider messaging, and medication management. It integrates with Acme Health's existing Epic EHR system via FHIR R4 APIs.

## Architecture Style

API-first monolith with planned decomposition. We start as a single deployable service with clear module boundaries, then extract services as scaling demands arise (messaging and notifications are the first candidates).

## Technology Stack

- **Backend**: Python 3.12, FastAPI
- **Database**: PostgreSQL 16 (portal-specific data: messages, preferences, audit logs)
- **Cache**: Redis 7 (session management, rate limiting, appointment slot caching)
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **API Protocol**: REST (JSON) for portal, FHIR R4 for EHR integration
- **Auth**: OAuth 2.0 + PKCE (patients), SAML 2.0 (staff via Okta)
- **Infrastructure**: AWS (ECS Fargate, RDS, ElastiCache, ALB, CloudFront)
- **CI/CD**: GitHub Actions → ECR → ECS (blue-green deployment)

## Component Architecture

```
┌─────────────────────────────────────────────────┐
│                   CloudFront CDN                 │
├─────────────────────────────────────────────────┤
│              Application Load Balancer           │
├──────────────┬──────────────┬───────────────────┤
│  React SPA   │  FastAPI     │   FHIR Client     │
│  (Static)    │  (API)       │   (Integration)   │
├──────────────┴──────────────┴───────────────────┤
│                 Service Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │ Patient  │ │Scheduling│ │    Messaging      ││
│  │ Service  │ │ Service  │ │    Service        ││
│  └──────────┘ └──────────┘ └──────────────────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │ Lab      │ │Medication│ │  Notification     ││
│  │ Service  │ │ Service  │ │  Service          ││
│  └──────────┘ └──────────┘ └──────────────────┘│
├─────────────────────────────────────────────────┤
│                 Data Layer                       │
│  ┌──────────────┐  ┌──────────┐  ┌───────────┐ │
│  │ PostgreSQL   │  │  Redis   │  │  S3       │ │
│  │ (portal data)│  │  (cache) │  │ (files)   │ │
│  └──────────────┘  └──────────┘  └───────────┘ │
├─────────────────────────────────────────────────┤
│              External Integrations               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │ Epic EHR │ │  Okta    │ │ SendGrid/Twilio  ││
│  │ (FHIR)   │ │  (SSO)   │ │ (Notifications)  ││
│  └──────────┘ └──────────┘ └──────────────────┘│
└─────────────────────────────────────────────────┘
```

## Module Boundaries

| Module | Responsibility | Data Owned |
|--------|---------------|------------|
| Patient Service | Demographics, health summary, preferences | User profiles, preferences |
| Scheduling Service | Appointment CRUD, availability, calendar sync | Appointment records |
| Messaging Service | Secure messaging, thread management | Messages, threads |
| Lab Service | Lab result retrieval, trend calculation | Cached lab results |
| Medication Service | Medication list, refill requests | Refill request records |
| Notification Service | Email/SMS delivery, preference management | Notification log |
| FHIR Client | EHR integration, data sync | Sync state, cache |

## API Design

### Patient-Facing API (REST)

```
/api/v1/patients/me                    GET     Patient profile
/api/v1/patients/me/health-summary     GET     Dashboard data
/api/v1/appointments                   GET     List appointments
/api/v1/appointments                   POST    Book appointment
/api/v1/appointments/{id}              PUT     Reschedule
/api/v1/appointments/{id}              DELETE  Cancel
/api/v1/appointments/availability      GET     Provider availability
/api/v1/labs                           GET     Lab results
/api/v1/labs/{id}                      GET     Lab detail with trends
/api/v1/medications                    GET     Medication list
/api/v1/medications/{id}/refill        POST    Request refill
/api/v1/messages                       GET     Message threads
/api/v1/messages                       POST    Send message
/api/v1/messages/{thread_id}           GET     Thread detail
/api/v1/notifications/preferences      GET/PUT Notification prefs
```

### Internal/Admin API

```
/api/v1/admin/providers/{id}/schedule  GET/PUT Provider availability
/api/v1/admin/analytics/usage          GET     Portal usage stats
/api/v1/admin/patients/{id}/account    PUT     Account management
```

## Data Architecture

### Portal Database (PostgreSQL)

The portal maintains its own database for portal-specific data. Clinical data lives in Epic and is accessed via FHIR APIs (not copied to portal DB except for caching with TTL).

**Tables:**
- `users` - Portal accounts (patient_id, email, password_hash, mfa_enabled, last_login)
- `messages` - Secure messages (sender_id, recipient_id, thread_id, body, created_at, read_at)
- `message_threads` - Thread metadata (subject, patient_id, provider_id, status)
- `appointments` - Portal appointment records (patient_id, provider_id, datetime, type, status)
- `refill_requests` - Medication refill tracking (patient_id, medication_id, status, requested_at)
- `notification_preferences` - Per-patient notification settings
- `audit_log` - PHI access audit trail (user_id, action, resource, timestamp, ip_address)

### Caching Strategy

- **Session data**: Redis, 30-minute TTL
- **Appointment availability**: Redis, 5-minute TTL
- **Lab results**: Redis, 1-hour TTL (invalidated on FHIR webhook)
- **Patient demographics**: Not cached (always fetched from EHR)

## Authentication & Authorization

### Patient Authentication
1. OAuth 2.0 + PKCE flow
2. Email/password with MFA required
3. MFA options: TOTP (authenticator app), SMS
4. Session timeout: 15 minutes of inactivity
5. Password requirements: 12+ chars, complexity enforced

### Staff Authentication
1. SAML 2.0 via Okta
2. Role-based access: Provider, Admin, Support
3. Inherits Okta MFA policy

### Authorization Model
- RBAC with resource-level scoping
- Patients can only access their own data
- Providers can access data for their assigned patients
- Admins have full portal access (no clinical data)
- All access decisions logged to audit trail

## Deployment

- **Compute**: ECS Fargate (2 vCPU, 4GB per task, auto-scaling 2-10 tasks)
- **Database**: RDS PostgreSQL (db.r6g.large, Multi-AZ)
- **Cache**: ElastiCache Redis (cache.r6g.large, 2 replicas)
- **CDN**: CloudFront for React SPA and static assets
- **Regions**: Primary us-east-1, DR us-west-2 (RDS read replica)
- **Deployment**: Blue-green via ECS, automated rollback on health check failure

## Observability

- **Logging**: Structured JSON logs → CloudWatch Logs
- **Metrics**: CloudWatch custom metrics + Prometheus (via ECS sidecar)
- **Tracing**: AWS X-Ray for request tracing
- **Alerting**: PagerDuty integration for P1/P2 incidents
- **Dashboard**: Grafana for operational metrics
