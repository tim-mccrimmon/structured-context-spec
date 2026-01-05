# Testing & Validation Domain

## Overview
The Testing & Validation domain defines testing strategy, validation approach, quality assurance processes, and verification methods. It establishes how the system is tested to ensure correctness, reliability, and quality.

## Domain Owner
**Typical Role:** Test Manager / QA Lead
**Responsibilities:**
- Define overall testing strategy and methodology
- Establish test coverage requirements
- Define validation and verification approaches
- Establish QA processes and quality gates
- Define CI/CD testing integration

## Generated SCDs
This domain produces 3-4 SCDs:
1. **scd:project:testing-strategy** - Overall testing approach, methodologies, test types
2. **scd:project:test-coverage-requirements** - Required coverage levels for unit, integration, E2E tests
3. **scd:project:validation-approach** - How correctness is validated, acceptance criteria
4. **scd:project:qa-processes** (optional) - QA workflows, quality gates, CI/CD integration

## Templates to Complete
- **testing-and-validation-brief-template.md** - Complete testing and validation context

## How to Complete
1. **Prerequisite:** Review multiple domains to understand testing needs:
   - business-context (success criteria, critical workflows)
   - architecture (components to test, integration points)
   - security (security testing requirements)
   - performance-reliability (performance testing needs)

2. **Gather information from:**
   - Engineering team (current testing practices)
   - Product team (acceptance criteria)
   - Security team (security testing requirements)
   - Compliance team (validation requirements)

3. **Define testing approach:**
   - Testing strategy (unit, integration, E2E, security, performance)
   - Coverage targets (code coverage, feature coverage)
   - Validation methods (automated, manual, user acceptance)
   - QA processes and quality gates

4. **Move to completed:**
   - Place finished template in `../../intent/completed/testing-validation/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand what to test)
  - architecture (understand test boundaries)
  - security (security testing requirements)
  - performance-reliability (performance testing requirements)
- **Provides context to:**
  - deployment-operations (CI/CD testing integration)
  - compliance-governance (validation for compliance)

## Workflow Position
**SECOND WAVE** - Can begin after business-context, architecture, security, and performance are understood. Testing strategy depends on knowing what needs to be tested.

## What Happens Next
Your completed template generates 3-4 testing and validation SCDs that establish testing approach and quality standards.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/testing-validation/testing-and-validation-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
