# [Project Name]

> [One-line description of what this healthcare system does]

## System Overview

[2-3 paragraphs describing:
- What the system does and who uses it (clinicians, patients, administrators)
- The clinical workflows it supports
- Key integrations (EHR, claims, etc.)]

## Architecture

### High-Level Design

[Describe the overall architecture]
- **Type**: [Monolith / Microservices / Serverless / Hybrid]
- **Deployment**: [Cloud provider, region requirements, on-prem components]
- **Key external dependencies**: [EHR systems, payers, clearinghouses]

### Core Components

| Component | Purpose | Location | Contains PHI? |
|-----------|---------|----------|---------------|
| [Component 1] | [What it does] | `/src/...` | Yes/No |
| [Component 2] | [What it does] | `/src/...` | Yes/No |
| [Component 3] | [What it does] | `/src/...` | Yes/No |

### Data Flow

[Describe how data moves through the system, noting PHI boundaries]

```
Clinical Input → [PHI Boundary] → [Processing] → [PHI Boundary] → Output
                      ↓                              ↓
                 Audit Log                      Audit Log
```

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | | |
| Framework | | |
| Database | | HIPAA-compliant configuration |
| Cache | | Encryption requirements |
| Queue | | |
| Infrastructure | | BAA in place |

## Compliance Context

### HIPAA Requirements

**This system handles PHI. All development must comply with HIPAA.**

#### PHI Locations
- **Database tables containing PHI**: [List tables]
- **API endpoints handling PHI**: [List endpoints]
- **Log fields that may contain PHI**: [List fields to exclude/redact]

#### Required Controls
- [ ] All PHI encrypted at rest (AES-256)
- [ ] All PHI encrypted in transit (TLS 1.2+)
- [ ] Access logging for all PHI access
- [ ] Minimum necessary principle enforced
- [ ] BAA in place with all vendors handling PHI

### Audit Logging Requirements

**Every PHI access must be logged with:**
- Who (user ID, role)
- What (record accessed, fields viewed)
- When (timestamp)
- Why (clinical purpose / workflow context)
- Where (IP, device)

**Audit log location**: [Path/table]
**Retention requirement**: [X years]

### Access Control

| Role | PHI Access Level | Scope |
|------|------------------|-------|
| [Role 1] | [Full/Limited/None] | [What they can access] |
| [Role 2] | [Full/Limited/None] | [What they can access] |

## Patterns We Use

### [Pattern 1 Name]
- **Where**: [Which parts of codebase]
- **Why**: [Reason, especially if compliance-related]
- **Example**: [File or code reference]

### Audit Trail Pattern
- **Where**: All PHI access points
- **Implementation**: [How audit logging is implemented]
- **Example**: [File or code reference]

## Patterns We MUST Avoid

### Direct PHI in Logs
- **Why**: HIPAA violation, audit failure
- **What to do instead**: Use audit service, redact PHI from application logs

### PHI in URLs/Query Params
- **Why**: Logged by infrastructure, HIPAA violation
- **What to do instead**: Use POST bodies, encrypt identifiers

### Storing PHI in Browser Storage
- **Why**: Not encrypted, persists beyond session
- **What to do instead**: Server-side sessions, encrypted cookies

## Constraints

### Regulatory Constraints
- **HIPAA**: All PHI handling must comply
- **State regulations**: [Any state-specific requirements]
- **[Other]**: [HITRUST, SOC2, etc.]

### Technical Constraints
- [Constraint 1]: [Reason and implications]
- [Constraint 2]: [Reason and implications]

### Clinical Safety Constraints
- [Constraint 1]: [Patient safety implication]
- [Constraint 2]: [Clinical workflow requirement]

## Domain Context

### Clinical Terminology
- **[Term 1]**: [Definition - clinical meaning]
- **[Term 2]**: [Definition - clinical meaning]
- **PHI**: Protected Health Information - any individually identifiable health information
- **BAA**: Business Associate Agreement - required contract with vendors handling PHI

### Key Clinical Workflows
1. **[Workflow 1]**: [Description, user roles involved]
2. **[Workflow 2]**: [Description, user roles involved]

### Integration Points
- **EHR**: [System name, integration type (FHIR, HL7, proprietary)]
- **Payers**: [Integration approach]
- **Clearinghouse**: [If applicable]

## Development Guidelines

### Before Making Changes
- [ ] Identify if change touches PHI
- [ ] Verify audit logging is in place
- [ ] Check access control enforcement
- [ ] Review encryption requirements
- [ ] Consult compliance team if uncertain

### Testing Requirements
- All PHI access must have audit log tests
- Access control must be tested for each role
- Encryption must be verified in tests

### Areas Requiring Extra Care

**ANY change involving PHI requires compliance review.**

- **[PHI Component 1]**: Contains patient records - consult [Person/Team]
- **[PHI Component 2]**: Contains clinical data - requires clinical review
- **Authentication/Authorization**: Changes require security review

## Emergency Contacts

- **Compliance Officer**: [Name, contact]
- **Security Team**: [Contact]
- **Clinical Lead**: [Name, contact for clinical questions]

---

*Last updated: [Date]*
*Generated with [SCS](https://structuredcontext.dev)*

**REMINDER**: This codebase handles PHI. When in doubt, ask before implementing.
