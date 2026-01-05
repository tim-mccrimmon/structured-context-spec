# Deployment & Operations Domain

## Overview
The Deployment & Operations domain defines deployment strategy, operational procedures, monitoring, incident response, and maintenance. It establishes how the system is deployed, monitored, and maintained in production.

## Domain Owner
**Typical Role:** DevOps Engineer / Site Reliability Engineer (SRE)
**Responsibilities:**
- Define deployment strategy and pipeline
- Establish monitoring and observability approach
- Define incident response and escalation procedures
- Establish operational runbooks and maintenance procedures
- Define infrastructure and environment management

## Generated SCDs
This domain produces 4 SCDs:
1. **scd:project:deployment-strategy** - How software is deployed to environments, CI/CD pipeline
2. **scd:project:monitoring-approach** - System monitoring, observability, alerting
3. **scd:project:incident-response** - How incidents are detected, triaged, and resolved
4. **scd:project:operations-runbook** - Operational procedures, maintenance, troubleshooting

## Templates to Complete
- **deployment-and-operations-brief-template.md** - Complete deployment and operations context

## How to Complete
1. **Prerequisite:** Review multiple domains to understand operational needs:
   - architecture (deployment topology, infrastructure)
   - security (security monitoring, incident response)
   - performance-reliability (performance monitoring, capacity planning)
   - compliance-governance (audit logging, compliance monitoring)

2. **Gather information from:**
   - Engineering team (deployment practices)
   - Infrastructure team (platform capabilities)
   - Security team (security monitoring requirements)
   - Business team (uptime requirements, maintenance windows)

3. **Define operations approach:**
   - Deployment pipeline and strategy
   - Monitoring and alerting
   - Incident response procedures
   - Operational runbooks

4. **Move to completed:**
   - Place finished template in `../../intent/completed/deployment-operations/`

## Dependencies
- **Prerequisite domains:**
  - architecture (understand what to deploy)
  - security (security monitoring)
  - performance-reliability (performance monitoring)
  - compliance-governance (audit logging)
- **Provides context to:**
  - testing-validation (deployment testing)

## Workflow Position
**SECOND WAVE** - Can begin after architecture, security, performance, and compliance are understood. Operations depends on knowing what needs to be deployed and monitored.

## What Happens Next
Your completed template generates 4 deployment and operations SCDs that establish operational approach and procedures.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/deployment-operations/deployment-and-operations-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
