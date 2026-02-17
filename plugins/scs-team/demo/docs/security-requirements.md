# Patient Portal - Security Requirements

**Author:** Mark Rivera, CISO
**Last Updated:** 2026-01-18
**Status:** Approved

## Overview

This document defines security requirements for the Patient Portal. The system handles Protected Health Information (PHI) and must comply with HIPAA Security Rule requirements.

## Data Classification

| Classification | Examples | Handling |
|---------------|----------|----------|
| PHI | Patient name + medical data, lab results, medications, appointment details with diagnosis | Encrypt at rest and in transit, audit all access, minimum necessary |
| PII | Email, phone, address (without medical context) | Encrypt at rest, access controls |
| Internal | Provider schedules, system configuration | Standard access controls |
| Public | Portal login page, general health resources | No restrictions |

## Authentication Requirements

- Patient accounts require email verification and MFA enrollment
- MFA must be enforced on every login (not just enrollment)
- Support TOTP and SMS as second factors
- Account lockout after 5 failed attempts (30-minute lockout)
- Password minimum 12 characters with complexity requirements
- Password rotation not required (per NIST 800-63B)
- Session timeout: 15 minutes of inactivity, 8-hour absolute maximum

## Authorization Requirements

- Patients may only access their own records
- Provider access limited to assigned patient panels
- Admin access does not include clinical data viewing
- All authorization decisions must be logged
- API endpoints must validate authorization on every request (no client-side-only checks)

## Encryption

- **At rest**: AES-256 for database (RDS encryption), S3 (SSE-S3), Redis (in-transit encryption)
- **In transit**: TLS 1.2+ required for all connections. TLS 1.0/1.1 disabled.
- **Key management**: AWS KMS with automatic rotation

## Audit Logging

All of the following events must be logged to the audit trail:

- PHI access (view, create, update, delete)
- Authentication events (login, logout, failed login, MFA challenge)
- Authorization failures
- Administrative actions (account management, config changes)
- Data exports or downloads

Audit log fields: user_id, action, resource_type, resource_id, timestamp, source_ip, user_agent, outcome (success/failure)

Audit logs must be:
- Immutable (append-only, no modification or deletion)
- Retained for minimum 6 years
- Shipped to centralized logging (CloudWatch Logs → S3 archive)
- Reviewed weekly by security team

## API Security

- Rate limiting: 100 requests/minute per authenticated user, 10 requests/minute for unauthenticated
- Input validation on all endpoints (reject unexpected fields)
- CORS restricted to portal domain only
- CSRF protection on all state-changing operations
- SQL injection prevention via parameterized queries (SQLAlchemy ORM)
- XSS prevention via React's default escaping + Content-Security-Policy header

## Vulnerability Management

- Dependency scanning in CI pipeline (Dependabot + Safety for Python)
- SAST scanning on every PR
- Quarterly penetration testing by external firm
- Critical/high vulnerabilities patched within 72 hours
- Container image scanning before deployment

## Incident Response

- Security incidents reported to CISO within 1 hour
- PHI breach notification per HIPAA requirements (60 days for 500+, annual for <500)
- Post-incident review within 5 business days
- Incident response runbook maintained in ops wiki

## Third-Party Requirements

All vendors handling PHI must:
- Execute a Business Associate Agreement (BAA)
- Provide SOC 2 Type II report or equivalent
- Support encryption in transit and at rest
- Provide incident notification within 24 hours

Current vendors requiring BAAs:
- AWS (BAA in place)
- SendGrid (BAA needed)
- Twilio (BAA needed)
- Okta (BAA in place)
