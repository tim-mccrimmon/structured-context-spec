# Safety & Risk Domain

## Overview
The Safety & Risk domain defines safety requirements, risk assessment, hazard analysis, and risk mitigation strategies. It ensures the system operates safely and that risks are identified and managed appropriately.

## Domain Owner
**Typical Role:** Safety Engineer / Risk Manager
**Responsibilities:**
- Conduct risk assessment and hazard analysis
- Define safety requirements for critical functions
- Establish risk mitigation strategies
- Define safety validation and testing approach
- Ensure safety-critical concerns are addressed

## Generated SCDs
This domain produces 3-4 SCDs:
1. **scd:project:risk-assessment** - Identified risks, likelihood, impact analysis
2. **scd:project:safety-requirements** - Safety-critical functions and requirements
3. **scd:project:hazard-analysis** - Hazard identification and analysis
4. **scd:project:risk-mitigation** - Risk mitigation strategies and controls

## Templates to Complete
- **safety-and-risk-brief-template.md** - Complete safety and risk context

## How to Complete
1. **Prerequisite:** Review multiple domains to understand safety risks:
   - business-context (understand impact of failures)
   - architecture (understand system failure modes)
   - security (understand security risks)

2. **Gather information from:**
   - Engineering team (technical risks)
   - Business team (business impact of failures)
   - Compliance team (safety regulations)
   - Industry standards (safety best practices)

3. **Define safety approach:**
   - Risk identification and assessment
   - Safety-critical functions
   - Hazard analysis
   - Mitigation strategies

4. **Move to completed:**
   - Place finished template in `../../intent/completed/safety-risk/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand business impact)
  - architecture (understand failure modes)
  - security (security risks)
- **Provides context to:**
  - testing-validation (safety testing requirements)
  - deployment-operations (safety monitoring)
  - compliance-governance (safety compliance)

## Workflow Position
**SECOND WAVE** - Can begin after business-context, architecture, and security are understood. Particularly important for safety-critical systems (healthcare, transportation, etc.).

## What Happens Next
Your completed template generates 3-4 safety and risk SCDs that establish risk management approach and safety requirements.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/safety-risk/safety-and-risk-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
