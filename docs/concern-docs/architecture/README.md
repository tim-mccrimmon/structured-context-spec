# Architecture Domain

## Overview
The Architecture domain defines the system's structure, components, boundaries, and technical design. It establishes how the system is organized, what technologies are used, how components interact, and how the system integrates with external systems.

## Domain Owner
**Typical Role:** Solutions Architect / Technical Lead
**Responsibilities:**
- Define system boundaries and context
- Select technology stack and justify choices
- Design component model and relationships
- Map integration points with external systems
- Establish architectural principles and patterns

## Generated SCDs
This domain produces 4 SCDs:
1. **scd:project:system-context** - System boundaries, external actors, key data flows
2. **scd:project:tech-stack** - Languages, frameworks, platforms, and technology rationale
3. **scd:project:component-model** - System components, responsibilities, and relationships
4. **scd:project:integration-map** - External system integrations, APIs, and protocols

## Templates to Complete
- **architecture-context-brief-template.md** - Complete architectural context including system boundaries, tech stack, components, and integrations

## How to Complete
1. **Prerequisite:** Review business-context domain to understand:
   - What problem we're solving
   - Who the users are
   - What the success criteria are
   - What constraints exist

2. **Gather information from:**
   - Engineering team (technical capabilities)
   - Infrastructure team (platform constraints)
   - Security team (security requirements)
   - Existing systems (integration needs)

3. **Define architecture:**
   - System context and boundaries
   - Technology stack choices
   - Component breakdown
   - Integration approach

4. **Review with:**
   - Security team (trust boundaries)
   - Performance team (scalability concerns)
   - Data team (data flow validation)

5. **Move to completed:**
   - Place finished template in `../../intent/completed/architecture/`

## Dependencies
- **Prerequisite domains:** business-context (must understand requirements first)
- **Provides context to:**
  - security (defines trust boundaries and attack surface)
  - performance-reliability (defines scalability approach)
  - data-provenance (defines data storage and flow)
  - deployment-operations (defines deployment topology)
  - testing-validation (defines test architecture)

## Workflow Position
**SECOND WAVE** - Can begin after business-context is complete. Often completed in parallel with other technical domains, but architectural decisions inform many other domain choices.

## What Happens Next
Your completed template will be processed by an AI transposer agent that:
1. Reads the structured architectural context
2. Maps sections to 4 SCD fields
3. Generates 4 architecture SCDs
4. Creates `bundles/domains/architecture.yaml` bundle

These SCDs establish the technical foundation for implementation.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26
- ⚠️ **Do not modify template structure** - AI mapping depends on consistent structure

## Need Help?
- **Review example:** `../med-adherence-examples/architecture/architecture-context-tech-brief.med-adherence.md`
- **SCS Documentation:** [Architecture Guide](../../README.md)
- **Questions:** Open an issue in the SCS repository

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
