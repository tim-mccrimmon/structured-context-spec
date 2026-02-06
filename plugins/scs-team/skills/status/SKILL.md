---
name: status
description: Show what structured context exists and what's missing. Overview of bundles, SCDs, coverage across all 11 concerns, and compilation sync status.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# SCS Team Status - Context Overview

You are showing the user what structured context exists for their project and highlighting gaps.

## Your Process

### Step 1: Scan for Existing Context

Look for SCS artifacts:
- `.scs/` directory (bundles, concerns, SCDs)
- `.claude/rules/` directory (compiled output)
- `CLAUDE.md` (might have scs-team managed section)

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

### Step 3: Assess Coverage Against All 11 Concerns

Map what exists to the full concern model:

| # | Concern | Expected SCDs | Status |
|---|---------|---------------|--------|
| 1 | Architecture | system-context, tech-stack, integration-map, component-model | Covered / Partial / Missing |
| 2 | Security | authn-authz, data-protection, data-handling, threat-model | Covered / Partial / Missing |
| 3 | Performance & Reliability | response-time, availability, fault-tolerance, scalability | Covered / Partial / Missing |
| 4 | Usability & Accessibility | ux-principles, accessibility-compliance, error-handling-ux | Covered / Partial / Missing |
| 5 | Compliance & Governance | hipaa-compliance, soc2-controls, audit-requirements, policy-enforcement | Covered / Partial / Missing |
| 6 | Data & Provenance | data-model, provenance-tracking, retention-policy | Covered / Partial / Missing |
| 7 | Testing & Validation | test-coverage, validation-plan, qa-procedures | Covered / Partial / Missing |
| 8 | Deployment & Operations | infrastructure-definition, observability, incident-response | Covered / Partial / Missing |
| 9 | Safety & Risk | risk-assessment, safety-checklist | Covered / Partial / Missing |
| 10 | Ethics & AI Accountability | ai-usage-policy, audit-trail, model-bias | Covered / Partial / Missing |
| 11 | Business Context | problem-definition, stakeholders, business-objectives, opportunity-analysis, constraints-and-assumptions, success-criteria | Covered / Partial / Missing |

### Step 4: Check Compilation Sync

Compare `.scs/` source with `.claude/rules/` output:

- For each concern with SCDs, does a corresponding `.claude/rules/<concern>.md` exist?
- Do `.claude/rules/` files have `<!-- scs-team:managed -->` headers?
- Does `CLAUDE.md` have `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers?
- Are there any `.claude/rules/` files that are NOT scs-team managed (project context vs developer context)?

Report sync status:
- **In sync**: Compiled output exists and matches source concerns
- **Out of sync**: Source SCDs exist but compiled output is missing or stale
- **Not compiled**: No `.claude/rules/` output exists yet

### Step 5: Highlight Issues

Flag potential problems:
- SCDs referenced in bundles but not found in `.scs/scds/`
- Stale content (if detectable)
- DRAFT items that might be ready to version
- Missing critical context for the project type
- Compilation out of sync

### Step 6: Suggest Next Steps

Based on gaps, suggest:
- Documents to add (`/scs-team:add`)
- Standards to use (`/scs-team:use`)
- Concerns to draft (`/scs-team:draft`)
- Recompilation if out of sync

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
| scd:standards:hipaa-phi-handling | Compliance | 1.0.0 | /scs-team:use |

### Coverage (11 Concerns)
| # | Concern | Status | SCDs | Notes |
|---|---------|--------|------|-------|
| 1 | Architecture | Partial | 2/4 | Has system-context, tech-stack. Missing integration-map, component-model |
| 2 | Security | Missing | 0/4 | No security context found |
| 3 | Performance & Reliability | Missing | 0/4 | No performance context found |
| 4 | Usability & Accessibility | Missing | 0/3 | No UX context found |
| 5 | Compliance & Governance | Partial | 1/4 | HIPAA added, needs customization |
| 6 | Data & Provenance | Missing | 0/3 | No data model context |
| 7 | Testing & Validation | Missing | 0/3 | No testing context |
| 8 | Deployment & Operations | Missing | 0/3 | No deployment context |
| 9 | Safety & Risk | Missing | 0/2 | No safety context |
| 10 | Ethics & AI Accountability | Missing | 0/3 | No ethics context |
| 11 | Business Context | Partial | 2/6 | Has problem definition, stakeholders. Missing objectives |

### Compilation Status
| Output | Status | Notes |
|--------|--------|-------|
| .claude/rules/architecture.md | In sync | scs-team:managed |
| .claude/rules/compliance.md | Out of sync | Source updated since last compile |
| .claude/rules/business.md | Missing | Not yet compiled |
| CLAUDE.md (scs-team section) | Present | Last updated 2026-01-15 |
| .claude/rules/my-custom-rules.md | Not managed | Developer-owned file (won't touch) |

### Issues
- Security context missing - critical for most projects
- HIPAA SCDs need customization (PHI locations not specified)
- 2 concerns have SCDs but compiled output is stale

### Suggested Next Steps
1. `/scs-team:draft security` - Add security context
2. `/scs-team:add ./docs/data-model.md` - If you have data documentation
3. Review and customize HIPAA SCDs in `.scs/scds/`

### Ready to Version?
Not yet. Recommend addressing security gap first.
Run `/scs-team:validate` for detailed checks.
```

## No Context Found

If no SCS artifacts exist:

```
## SCS Context Status

### Project: <directory-name>

No structured context found.

### Getting Started

Start by initializing:
/scs-team:init

Or if you want to jump right in:

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
