# Compliance & Governance Domain

## Overview
The Compliance & Governance domain defines regulatory compliance requirements, audit trails, governance policies, and how standards are satisfied. It ensures the system meets legal, regulatory, and organizational requirements.

## Domain Owner
**Typical Role:** Compliance Officer / Governance Lead
**Responsibilities:**
- Identify applicable regulations (HIPAA, SOC2, GDPR, etc.)
- Map compliance requirements to system controls
- Define audit and evidence collection requirements
- Establish governance policies and decision-making
- Ensure standards satisfaction and documentation

## Generated SCDs
This domain produces 3-4 SCDs:
1. **scd:project:compliance-mapping** - How project satisfies regulatory requirements
2. **scd:project:audit-requirements** - Audit trails, evidence collection, logging
3. **scd:project:governance-policies** - Governance framework, decision-making, change control
4. **scd:project:standards-satisfaction** (optional) - Mapping to specific standards

## Templates to Complete
- **compliance-and-governance-brief-template.md** - Complete compliance and governance context

## How to Complete
1. **Prerequisite:** Review business-context, security, and data-provenance domains to understand:
   - What regulations apply (HIPAA for healthcare, GDPR for EU data, etc.)
   - What data is being processed (PHI, PII)
   - Security controls in place

2. **Gather information from:**
   - Legal team (regulatory requirements)
   - Security team (technical controls)
   - Business team (organizational policies)
   - External auditors (audit requirements)

3. **Define compliance approach:**
   - Applicable regulations and standards
   - Compliance controls and mappings
   - Audit trail requirements
   - Governance and oversight processes

4. **Move to completed:**
   - Place finished template in `../../intent/completed/compliance-governance/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand regulatory landscape)
  - security (understand security controls)
  - data-provenance (understand data handling)
- **Provides context to:**
  - security (compliance-driven security requirements)
  - deployment-operations (audit logging requirements)
  - testing-validation (compliance testing)

## Workflow Position
**SECOND WAVE** - Can begin after business-context, security, and data-provenance are understood. Critical for regulated industries.

## What Happens Next
Your completed template generates 3-4 compliance and governance SCDs that establish regulatory requirements and inform all other domains.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/compliance-governance/compliance-and-governance-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
