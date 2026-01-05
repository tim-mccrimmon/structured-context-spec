# Business Context Domain

## Overview
The Business Context domain captures the foundational "what/why/who" of the project: the problem being solved, the stakeholders involved, business objectives, market opportunity, constraints, and success criteria. This domain provides the essential business rationale that all other technical domains depend on.

## Domain Owner
**Typical Role:** Business Manager (bM) / Product Manager
**Responsibilities:**
- Define the business problem and its impact
- Identify and analyze stakeholders
- Establish business objectives and success metrics
- Articulate the market opportunity and timing
- Document constraints and key assumptions

**IMPORTANT:** This domain must be completed FIRST before other domains can begin their work.

## Generated SCDs
This domain produces 6 SCDs:
1. **scd:project:problem-definition** - Core problem, affected populations, pain points, root causes
2. **scd:project:stakeholders** - Stakeholder groups, roles, needs, goals, constraints
3. **scd:project:business-objectives** - Strategic objectives, measurable outcomes, KPIs
4. **scd:project:opportunity-analysis** - Market context, competitive landscape, timing factors
5. **scd:project:constraints-and-assumptions** - Non-technical constraints, organizational boundaries, key assumptions
6. **scd:project:success-criteria** - Measurable success indicators and performance metrics

## Templates to Complete
- **business-context-opportunity-brief-template.md** - Comprehensive business context covering problem, opportunity, stakeholders, objectives, and success criteria (maps to all 6 SCDs)

## How to Complete
1. **Gather information from:**
   - Executive leadership (strategic objectives)
   - Product team (user needs and market analysis)
   - Sales/Customer success (customer pain points)
   - Finance (budget and ROI expectations)
   - Operations (organizational constraints)

2. **Fill out all sections:**
   - Problem Overview → problem-definition SCD
   - Target Users & Stakeholders → stakeholders SCD
   - Why Now → opportunity-analysis SCD
   - Opportunity Summary → opportunity-analysis SCD
   - Desired Business Outcomes → business-objectives SCD
   - Guiding Principles & Vision → business-objectives SCD
   - Key Assumptions → constraints-and-assumptions SCD
   - Constraints → constraints-and-assumptions SCD
   - Success Metrics → success-criteria SCD

3. **Review and validate:**
   - Ensure all sections are complete
   - Validate with Product Manager
   - Confirm stakeholder alignment

4. **Move to completed:**
   - Place finished template in `../../intent/completed/business-context/`

## Dependencies
- **Prerequisite domains:** None (this is the first domain)
- **Provides context to:** ALL other domains (architecture, security, performance, usability, compliance, data, testing, deployment, safety, ethics)

## Workflow Position
**FIRST DOMAIN** - Must be completed before any other domain work begins. The business context establishes:
- What we're building and why
- Who will use it and benefit from it
- How we'll measure success
- What constraints shape the solution

Without this foundation, technical domains cannot make informed decisions about architecture, security, data models, or other implementation details.

## What Happens Next
Your completed template will be processed by an AI transposer agent that:
1. Reads the structured business context you provided
2. Maps sections to 6 SCD fields using semantic understanding
3. Generates 6 machine-readable project-tier SCDs
4. Creates `bundles/domains/business-context.yaml` bundle referencing all 6 SCDs

These SCDs become the foundation for all subsequent domain work.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26
- ⚠️ **Do not modify template structure** - AI mapping depends on section structure remaining consistent

## Need Help?
- **Review example:** `../med-adherence-examples/business-context/business-context-opportunity-brief.md`
- **SCS Documentation:** [Business Context Guide](../../README.md)
- **Questions:** Open an issue in the SCS repository

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
