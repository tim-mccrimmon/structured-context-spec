---
name: status
description: Show what structured context exists and what's missing. Overview of bundles, SCDs, and coverage.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# SCS Team Status - Context Overview

You are showing the user what structured context exists for their project and highlighting gaps.

## Your Process

### Step 1: Scan for Existing Context

Look for SCS artifacts:
- `.scs/` directory
- `*.yaml` files that look like bundles or SCDs
- `CLAUDE.md` (might have informal context)

### Step 2: Inventory What Exists

For each bundle found:
- Bundle ID and type
- Version (DRAFT or semantic version)
- SCDs it contains
- What it imports

For each SCD found:
- SCD ID and tier
- What concern it addresses
- Version status

### Step 3: Assess Coverage

Map what exists to the standard concern areas:

| Concern | Status |
|---------|--------|
| Business Context | Covered / Partial / Missing |
| Architecture | Covered / Partial / Missing |
| Security | Covered / Partial / Missing |
| Compliance | Covered / Partial / Missing |
| Data & Provenance | Covered / Partial / Missing |
| Deployment & Ops | Covered / Partial / Missing |
| Testing | Covered / Partial / Missing |

### Step 4: Highlight Issues

Flag potential problems:
- SCDs referenced but not found
- Stale content (if detectable)
- DRAFT items that might be ready to version
- Missing critical context for the project type

### Step 5: Suggest Next Steps

Based on gaps, suggest:
- Documents to add (`/scs-team:add`)
- Standards to use (`/scs-team:use`)
- Concerns to draft (`/scs-team:draft`)

## Output Format

```
## SCS Context Status

### Project: <project-name or directory>

### Bundles
| Bundle | Type | Version | SCDs |
|--------|------|---------|------|
| bundle:my-project | project | DRAFT | 3 |
| bundle:architecture | concern | DRAFT | 2 |

### SCDs (8 total)
| SCD | Concern | Version | Source |
|-----|---------|---------|--------|
| scd:project:problem-definition | Business | DRAFT | PRD.md |
| scd:project:system-context | Architecture | DRAFT | architecture.md |
| scd:project:tech-stack | Architecture | DRAFT | architecture.md |
| scd:standards:hipaa-controls | Compliance | DRAFT | /scs-team:use |

### Coverage
| Concern | Status | Notes |
|---------|--------|-------|
| Business Context | Partial | Has problem definition, missing stakeholders |
| Architecture | Covered | system-context, tech-stack |
| Security | Missing | No security context found |
| Compliance | Partial | HIPAA added, needs customization |
| Data | Missing | No data model context |
| Deployment | Missing | No deployment context |
| Testing | Missing | No testing context |

### Issues
- Security context missing - critical for most projects
- HIPAA SCDs need customization (PHI locations not specified)

### Suggested Next Steps
1. `/scs-team:draft security` - Add security context
2. `/scs-team:add ./docs/data-model.md` - If you have data documentation
3. Review and customize HIPAA SCDs in `.scs/scds/`

### Ready to Version?
Not yet. Recommend addressing security gap first.
Run `/scs-team:validate` for detailed checks.
```

## Example Interaction

User: `/scs-team:status`

You: [Scan .scs/ directory and present status report]

## No Context Found

If no SCS artifacts exist:

```
## SCS Context Status

### Project: <directory-name>

No structured context found.

### Getting Started

**If you have documentation:**
/scs-team:add ./docs/PRD.md
/scs-team:add ./docs/architecture.md

**If you need compliance:**
/scs-team:use hipaa
/scs-team:use soc2

**If you want to start from scratch:**
/scs-team:draft business
/scs-team:draft architecture

**For quick setup (no docs):**
Consider `/install scs-vibe` for a 15-minute conversational setup.
```
