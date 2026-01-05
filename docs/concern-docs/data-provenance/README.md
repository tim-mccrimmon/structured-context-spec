# Data & Provenance Domain

## Overview
The Data & Provenance domain defines data models, data flow, data governance, provenance tracking, and data lifecycle management. It establishes what data the system manages, how it flows, and how lineage is tracked.

## Domain Owner
**Typical Role:** Data Architect / Data Engineer
**Responsibilities:**
- Define core data models and entities
- Map data flow through the system
- Establish data governance and quality policies
- Define provenance and lineage tracking
- Establish data retention and lifecycle policies

## Generated SCDs
This domain produces 4 SCDs:
1. **scd:project:data-model** - Core data structures, entities, relationships
2. **scd:project:data-flow** - How data moves through system, transformations
3. **scd:project:data-governance** - Data ownership, quality, lifecycle policies
4. **scd:project:provenance-tracking** - Data lineage, audit trails, versioning

## Templates to Complete
- **data-and-provenance-brief-template.md** - Complete data and provenance context

## How to Complete
1. **Prerequisite:** Review business-context and architecture domains to understand:
   - What data the system handles
   - Key workflows and data transformations
   - Integration points and data sources

2. **Gather information from:**
   - Business team (data requirements, entities)
   - Architecture team (data storage approach)
   - Compliance team (data retention, privacy)
   - Existing systems (current data models)

3. **Define data architecture:**
   - Core entities and relationships
   - Data flow and transformations
   - Governance and quality policies
   - Provenance tracking approach

4. **Move to completed:**
   - Place finished template in `../../intent/completed/data-provenance/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand data requirements)
  - architecture (understand data storage)
- **Provides context to:**
  - security (data protection requirements)
  - compliance-governance (data governance policies)
  - testing-validation (data quality testing)

## Workflow Position
**SECOND WAVE** - Can begin after business-context and architecture are complete. Often done in parallel with security.

## What Happens Next
Your completed template generates 4 data and provenance SCDs that establish data architecture and inform security, compliance, and testing.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/data-provenance/data-and-provenance.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
