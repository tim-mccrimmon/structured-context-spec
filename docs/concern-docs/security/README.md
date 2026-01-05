# Security Domain

## Overview
The Security domain captures authentication, authorization, data protection, threat modeling, and security controls. It defines how the system protects sensitive data, authenticates users, prevents unauthorized access, and mitigates security threats.

## Domain Owner
**Typical Role:** Security Engineer / Chief Information Security Officer (CISO)
**Responsibilities:**
- Define authentication and authorization model
- Establish data protection strategy (encryption, secrets management)
- Create threat model and risk assessment
- Define security controls and monitoring
- Ensure compliance with security standards

## Generated SCDs
This domain produces 4 SCDs:
1. **scd:project:authn-authz** - Authentication and authorization model, roles, permissions
2. **scd:project:data-protection** - Data encryption (transit/rest), secrets management
3. **scd:project:data-handling** - Secure development practices, data handling policies
4. **scd:project:threat-model** - Threats, assets, mitigations, risks, monitoring

## Templates to Complete
- **security-context-brief-template.md** - Complete security context with 15 sections covering authentication, authorization, data protection, threat analysis

## How to Complete
1. **Prerequisite:** Review business-context and architecture domains to understand:
   - What data the system handles (PHI, PII, sensitive data)
   - Who the users are (patients, clinicians, admins)
   - System boundaries and trust zones
   - Integration points and external systems

2. **Gather information from:**
   - Compliance team (regulatory requirements: HIPAA, SOC2)
   - Architecture team (trust boundaries, integration points)
   - Organizational security policies
   - Industry threat intelligence

3. **Define security posture:**
   - Authentication mechanisms (how users prove identity)
   - Authorization model (roles, permissions, scope)
   - Data protection (encryption, key management)
   - Threat landscape and mitigations

4. **Review with:**
   - Compliance team (regulatory alignment)
   - Architecture team (implementation feasibility)
   - Operations team (monitoring and incident response)

5. **Move to completed:**
   - Place finished template in `../../intent/completed/security/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand what we're protecting)
  - architecture (understand trust boundaries)
- **Provides context to:**
  - compliance-governance (security controls map to compliance requirements)
  - deployment-operations (security monitoring and incident response)
  - data-provenance (data encryption and protection mechanisms)
  - testing-validation (security testing requirements)

## Workflow Position
**SECOND WAVE** - Can begin after business-context and architecture are complete. Critical for understanding how to protect the system.

## What Happens Next
Your completed template will be processed by an AI transposer agent that:
1. Reads the structured security context (15 sections with AI Mapping annotations)
2. Maps sections to 4 SCD fields
3. Generates 4 security SCDs with proper controls and threat model
4. Creates `bundles/domains/security.yaml` bundle

These SCDs establish the security foundation and inform compliance, operations, and testing.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26
- ⚠️ **Do not modify template structure** - 15 AI Mapping annotations depend on exact section structure

## Need Help?
- **Review example:** `../med-adherence-examples/security/security-context-brief.md`
- **SCS Documentation:** [Security Guide](../../README.md)
- **Questions:** Open an issue in the SCS repository

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
