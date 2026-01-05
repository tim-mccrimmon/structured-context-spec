# Performance & Reliability Domain

## Overview
The Performance & Reliability domain defines performance requirements, reliability targets, scalability approach, availability expectations, and system resilience. It establishes how the system performs under load and recovers from failures.

## Domain Owner
**Typical Role:** Performance Engineer / Site Reliability Engineer (SRE)
**Responsibilities:**
- Define performance requirements and SLAs
- Establish scalability and capacity planning approach
- Set availability and uptime targets
- Define disaster recovery and fault tolerance strategies
- Establish monitoring and alerting for performance/reliability

## Generated SCDs
This domain produces 3-4 SCDs:
1. **scd:project:performance-requirements** - Response time, throughput, resource usage targets
2. **scd:project:scalability-approach** - How system scales to handle load
3. **scd:project:availability-targets** - Uptime requirements, SLA commitments, fault tolerance
4. **scd:project:disaster-recovery** (optional) - Recovery procedures and business continuity

## Templates to Complete
- **performance-and-reliability-brief-template.md** - Complete performance and reliability context

## How to Complete
1. **Prerequisite:** Review business-context and architecture domains to understand:
   - Expected user load and growth projections
   - Critical user workflows and timing requirements
   - System architecture and scalability constraints

2. **Gather information from:**
   - Business team (SLA commitments, user expectations)
   - Architecture team (scalability approach)
   - Operations team (current performance baselines)
   - Product team (acceptable response times)

3. **Define requirements:**
   - Performance targets (response times, throughput)
   - Scalability approach (horizontal/vertical scaling)
   - Availability targets (uptime %, fault tolerance)
   - Recovery time objectives (RTO/RPO)

4. **Move to completed:**
   - Place finished template in `../../intent/completed/performance-reliability/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand user expectations)
  - architecture (understand scalability approach)
- **Provides context to:**
  - deployment-operations (monitoring and capacity planning)
  - testing-validation (performance testing requirements)
  - architecture (validation of scalability design)

## Workflow Position
**SECOND WAVE** - Can begin after business-context and architecture are complete. Often done in parallel with security and other technical domains.

## What Happens Next
Your completed template generates 3-4 performance and reliability SCDs that establish performance targets and inform testing and operations.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/performance-reliability/performance-and-reliability-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
