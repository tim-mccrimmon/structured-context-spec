---
name: init
description: Initialize structured context for this project. Scaffolds .scs/ with all 11 concern bundles, scans the project, and recommends where to start.
argument-hint: "[project-name]"
allowed-tools: Read, Glob, Grep, Write, Bash(ls *), Bash(mkdir -p *), Bash(cat package.json), Bash(cat requirements.txt), Bash(cat go.mod), Bash(cat Cargo.toml), Bash(cat pyproject.toml)
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-team:init`. Never auto-invoke based on project state or conversation context.
- **Confirm before writing**: After scanning the project, present a summary of the `.scs/` scaffold you plan to create and get explicit user confirmation before writing any files.

---

# SCS Team Init - Initialize Structured Context

You are scaffolding a new `.scs/` directory for this project. This is the entry point for teams adopting structured context.

## Your Process

### Step 1: Detect Project Info

Scan the project to understand what exists:

**Language/Framework Detection** (check in order):
- `package.json` → Node.js (check for Next.js, React, Express, etc.)
- `requirements.txt` or `pyproject.toml` or `setup.py` → Python (check for FastAPI, Django, Flask)
- `go.mod` → Go
- `Cargo.toml` → Rust
- `pom.xml` or `build.gradle` → Java/Kotlin
- `Gemfile` → Ruby
- `.csproj` or `.sln` → .NET

**Existing Documentation** (scan for):
- `docs/`, `doc/`, `documentation/` directories
- Root-level: `PRD.md`, `ARCHITECTURE.md`, `SECURITY.md`, `README.md`
- Any `*.md` files that look like project documentation
- `CLAUDE.md`, `.claude/rules/` (existing Claude context)

**Compliance Signals** (look for keywords in docs and code):
- HIPAA: "PHI", "protected health information", "HIPAA", "healthcare"
- SOC2: "SOC2", "SOC 2", "trust service criteria"
- PCI: "PCI", "cardholder", "payment card"
- GDPR: "GDPR", "personal data", "data subject"
- CHAI: "clinical AI", "health AI", "CHAI"

### Step 2: Determine Project Name

Use the argument if provided. Otherwise:
1. Check `package.json` name field
2. Check `pyproject.toml` project name
3. Check `go.mod` module name
4. Fall back to directory name

### Step 3: Create .scs/ Scaffold

Create the following structure:

```
.scs/
├── project.yaml              # Project bundle manifest
├── concerns/
│   ├── architecture.yaml
│   ├── security.yaml
│   ├── performance.yaml
│   ├── usability.yaml
│   ├── compliance.yaml
│   ├── data.yaml
│   ├── testing.yaml
│   ├── deployment.yaml
│   ├── safety.yaml
│   ├── ethics.yaml
│   └── business.yaml
└── scds/                     # Empty - populated by add/draft/use
```

**Project Bundle** (`project.yaml`):
```yaml
id: bundle:<project-name>
type: project
version: "DRAFT"
title: "<Project Name>"
description: "<Brief description from README or detected context>"

imports:
  - bundle:architecture
  - bundle:security
  - bundle:performance
  - bundle:usability
  - bundle:compliance
  - bundle:data
  - bundle:testing
  - bundle:deployment
  - bundle:safety
  - bundle:ethics
  - bundle:business

scds: []

provenance:
  created_by: "scs-team init"
  created_at: "<ISO timestamp>"
  rationale: "Project bundle scaffolded by scs-team init"
```

**Concern Bundles** (each concern follows this pattern):

```yaml
id: bundle:<concern-slug>
type: concern
version: "DRAFT"
title: "<Project Name> - <Concern Title>"
description: "<Brief description of what this concern covers>"
imports: []
scds: []
provenance:
  created_by: "scs-team init"
  created_at: "<ISO timestamp>"
  rationale: "Scaffolded by scs-team init"
```

Use these exact concern definitions:

| # | Slug | Title | Description | Expected SCDs |
|---|------|-------|-------------|---------------|
| 1 | `architecture` | Architecture | System structure, components, technology stack, and integration points | system-context, tech-stack, integration-map, component-model |
| 2 | `security` | Security | Authentication, authorization, data protection, and threat modeling | authn-authz, data-protection, data-handling, threat-model |
| 3 | `performance` | Performance & Reliability | Response times, availability targets, fault tolerance, and scaling strategy | response-time, availability, fault-tolerance, scalability |
| 4 | `usability` | Usability & Accessibility | UX principles, accessibility compliance, and error handling | ux-principles, accessibility-compliance, error-handling-ux |
| 5 | `compliance` | Compliance & Governance | Regulatory requirements, audit controls, and policy enforcement | hipaa-compliance, soc2-controls, audit-requirements, policy-enforcement |
| 6 | `data` | Data & Provenance | Data models, lineage tracking, and retention policies | data-model, provenance-tracking, retention-policy |
| 7 | `testing` | Testing & Validation | Test coverage, validation plans, and QA procedures | test-coverage, validation-plan, qa-procedures |
| 8 | `deployment` | Deployment & Operations | Infrastructure, observability, and incident response | infrastructure-definition, observability, incident-response |
| 9 | `safety` | Safety & Risk | Risk assessments and safety checklists | risk-assessment, safety-checklist |
| 10 | `ethics` | Ethics & AI Accountability | AI usage policies, audit trails, and bias detection | ai-usage-policy, audit-trail, model-bias |
| 11 | `business` | Business Context | Problem definition, stakeholders, objectives, opportunity analysis, constraints, and success criteria | problem-definition, stakeholders, business-objectives, opportunity-analysis, constraints-and-assumptions, success-criteria |

### Step 4: Report Findings and Recommend Next Steps

Present a summary:

```
## SCS Initialized

**Project**: <name>
**Language**: <detected language/framework>
**Location**: .scs/ (11 concern bundles scaffolded)

### What I Found

<table of detected docs, compliance signals, existing context>

### Recommended Next Steps

<prioritized list based on what was found>
```

**Recommendation Logic**:

1. **Found existing documentation** → Start with `/scs-team:add`:
   ```
   /scs-team:add ./docs/PRD.md
   /scs-team:add ./docs/architecture.md
   ```

2. **No documentation found** → Start with drafting:
   ```
   /scs-team:draft business      # Start with the "why"
   /scs-team:draft architecture  # Then the "how"
   ```

3. **Compliance keywords detected** → Add standards:
   ```
   /scs-team:use hipaa    # Healthcare detected
   /scs-team:use soc2     # Security controls detected
   ```

4. **Existing CLAUDE.md found** → Note it will be enhanced (not replaced):
   ```
   Existing CLAUDE.md found - scs-team will add a managed section
   (your existing content will not be modified)
   ```

## Important Rules

- **Do NOT generate any SCDs** - init only creates the scaffold
- **Do NOT modify existing files** - only create new ones in `.scs/`
- **Do NOT overwrite** if `.scs/` already exists - warn the user and show what's there
- **Keep it fast** - scan, scaffold, report. Don't ask questions during init.
- The `scds: []` arrays in concern bundles are intentionally empty - they get populated by `add`, `draft`, and `use`

## If .scs/ Already Exists

```
## SCS Already Initialized

Found existing .scs/ directory with:
- <N> concern bundles
- <N> SCDs
- Project bundle: <version status>

Run `/scs-team:status` to see the full picture.
To start fresh, delete .scs/ and run `/scs-team:init` again.
```

## Example Interaction

User: `/scs-team:init`

You: "Let me scan your project..."

[Scan project files, docs, dependencies]

You: "## SCS Initialized

**Project**: patient-portal
**Language**: Python (FastAPI)
**Location**: .scs/ (11 concern bundles scaffolded)

### What I Found

| Item | Details |
|------|---------|
| Language | Python 3.11 (FastAPI, SQLAlchemy) |
| Docs | `docs/PRD.md`, `docs/api-spec.md` |
| Compliance | HIPAA keywords found in README |
| Existing Context | CLAUDE.md exists (will be enhanced, not replaced) |

### Recommended Next Steps

1. **Process your docs** (you have existing documentation):
   ```
   /scs-team:add docs/PRD.md
   /scs-team:add docs/api-spec.md
   ```

2. **Add HIPAA compliance** (healthcare keywords detected):
   ```
   /scs-team:use hipaa
   ```

3. **Draft what's missing** (no architecture doc found):
   ```
   /scs-team:draft architecture
   /scs-team:draft security
   ```

4. **Check progress**:
   ```
   /scs-team:status
   ```"
