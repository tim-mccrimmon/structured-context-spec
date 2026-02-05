# SCS Vibe Plugin Overview

> Version: 2.0.0
> Last Updated: 2026-02-05

## What It Is

SCS Vibe is a Claude Code plugin that helps solo developers and small teams create structured context for their projects. It acts as a **professional architect in your pocket** - surfacing compliance, security, and legal considerations you might not think about until they become problems.

The plugin "thinks" in [Structured Context Specification (SCS)](https://structuredcontext.io) but outputs native Claude Code format (CLAUDE.md and `.claude/rules/`), so there's no new format to learn.

## The Problem It Solves

Solo developers building with AI are the highest-risk group in software:

- They move fast without process guardrails
- They don't know what they don't know (HIPAA, PCI, GDPR, etc.)
- AI helps them build faster, but doesn't add governance
- They ship things that become liabilities

**Without structured context**, Claude makes confident decisions based on general knowledge - not YOUR system's specific architecture. This leads to:

- Features that don't fit existing patterns
- Architectural decisions that conflict with earlier design choices
- Code that requires significant rework to integrate
- Compliance violations (PHI in logs, missing encryption, etc.)

## How It Works

### The Init Flow

```
/scs-vibe:init
       │
       ▼
┌─────────────────────────────────────┐
│  1. Detect Project Signals          │
│     - Language/framework            │
│     - Domain (healthcare, fintech)  │
│     - Existing context files        │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  2. Ask Targeted Questions          │
│     - What does this do?            │
│     - Who uses it?                  │
│     - Personal or commercial?       │
└─────────────────────────────────────┘
       │
       ▼ (if commercial)
┌─────────────────────────────────────┐
│  3. Walk Through Considerations     │
│     - HIPAA/PHI requirements        │
│     - GDPR/CCPA requirements        │
│     - Security requirements         │
│     - Legal requirements            │
│     - Capture decisions             │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  4. Generate Output Files           │
│     - CLAUDE.md (overview)          │
│     - CONSIDERATIONS.md (audit)     │
│     - .claude/rules/*.md (modular)  │
└─────────────────────────────────────┘
```

### SCS-Informed Questioning

The plugin asks about concerns that map to SCS categories:

| Question | SCS Concern |
|----------|-------------|
| "What does this do, who uses it?" | System Context |
| "What's your tech stack?" | Tech Stack |
| "Monolith or microservices?" | Component Model |
| "What patterns do you use/avoid?" | Patterns |
| "Compliance requirements?" | Compliance, Security |
| "Domain-specific terms?" | Domain Context |

The SCS spec defines **what matters** for AI to understand a project. The plugin uses that as a mental model for what to ask - without requiring the user to learn SCS.

## Output Files

### Always Generated

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project overview, critical warnings, entry point |
| `.claude/rules/tech-stack.md` | Technology choices and versions |
| `.claude/rules/architecture.md` | System design, layers, key files |
| `.claude/rules/patterns.md` | Patterns to use and avoid |

### Generated If Commercial

| File | Purpose |
|------|---------|
| `CONSIDERATIONS.md` | Compliance decisions audit trail |

### Generated If Applicable

| File | Trigger | Notes |
|------|---------|-------|
| `.claude/rules/phi-handling.md` | Healthcare/PHI detected | **PATH-SPECIFIC** |
| `.claude/rules/pci-handling.md` | Payments detected | **PATH-SPECIFIC** |
| `.claude/rules/data-protection.md` | User data detected | GDPR/CCPA rules |
| `.claude/rules/domain-context.md` | Complex domain | Terminology, workflows |

### Example File Tree

```
project/
├── CLAUDE.md                    # Overview (always)
├── CONSIDERATIONS.md            # Compliance decisions (if commercial)
└── .claude/
    ├── settings.json            # Permissions (optional)
    └── rules/
        ├── tech-stack.md        # Always
        ├── architecture.md      # Always
        ├── patterns.md          # Always
        ├── phi-handling.md      # If healthcare (PATH-SPECIFIC)
        └── domain-context.md    # If complex domain
```

## Key Features

### 1. Architect-Style Considerations Flow

For commercial projects, the plugin walks through applicable compliance, security, and legal considerations:

**Categories covered:**
- Universal (Privacy Policy, Terms of Service)
- User Data (GDPR, CCPA, Data Retention)
- Authentication (Password Security, Session Management)
- Healthcare (HIPAA, PHI, BAAs, Breach Procedures)
- Payments (PCI-DSS, Money Transmission)
- User-Generated Content (Moderation, DMCA, COPPA)
- Accessibility (WCAG, ADA)
- Infrastructure (Secrets, Dependencies, Backups)

**Decision options for each:**
- **Will Address** - Commit to implementing before launch
- **Accepted Risk** - Acknowledge the risk, document why
- **N/A** - Doesn't apply (document why)
- **Already Done** - Already implemented

The plugin pushes back on risky "Accepted Risk" decisions for serious items (HIPAA, encryption).

### 2. CONSIDERATIONS.md Audit Trail

```markdown
# Project Considerations

> Generated: 2026-02-05
> Project: Care Plan Tracker
> Type: Healthcare / Clinical Tool / Commercial (Business Associate)

## Summary

| Category | Items | Will Address | Already Done | N/A |
|----------|-------|--------------|--------------|-----|
| Healthcare/HIPAA | 6 | 6 | 0 | 0 |
| Universal | 3 | 3 | 0 | 0 |
| Security | 3 | 3 | 0 | 0 |

## Decisions

### Healthcare/HIPAA

#### Encryption at Rest
**Decision:** Will Address
**Requirement:** PHI must be encrypted when stored.
**Action needed:** Implement encryption for ~/.careplan/data.json
```

This document becomes evidence of due diligence - proof they thought through the implications before shipping.

### 3. Path-Specific Rules

For sensitive code (PHI, PCI, credentials), rules are scoped to specific files using YAML frontmatter:

```markdown
---
paths:
  - careplan/models.py
  - careplan/service.py
  - careplan/storage.py
---

# PHI Handling Rules

These files handle Protected Health Information. Extra care required.

## Rules

1. **Never log PHI** - No patient names, medications, or appointment details
2. **Generic error messages** - Use "Patient not found" NOT "Patient John Smith not found"
3. **No PHI in exceptions** - Exception messages may appear in crash reports
```

**Why this matters:** Claude Code only loads these rules when working on the specified files. When editing the README, PHI rules don't clutter the context.

### 4. Modular Context Loading

Instead of one giant CLAUDE.md, context is split into focused files:

| File | Loads When |
|------|------------|
| `CLAUDE.md` | Always (project overview) |
| `tech-stack.md` | Always |
| `architecture.md` | Always |
| `patterns.md` | Always |
| `phi-handling.md` | Only for `careplan/*.py` files |
| `domain-context.md` | Always |

This keeps context relevant and reduces token usage.

## Installation

```bash
# Install from Claude Code marketplace
/install scs-vibe

# Or use locally during development
claude --plugin-dir /path/to/scs-vibe
```

## Usage

### Initialize a Project

```bash
# Start Claude Code in your project
cd ~/my-project
claude

# Run init
/scs-vibe:init

# Or specify a template
/scs-vibe:init healthcare
/scs-vibe:init fintech
/scs-vibe:init saas
/scs-vibe:init minimal
```

### Validate Existing Context

```bash
/scs-vibe:validate
```

Checks for:
- Missing critical sections
- Generic/placeholder content
- Stale file references
- Gaps that might bite you later

### Learn More

```bash
/scs-vibe:explain
```

Explains why structured context matters and how it helps.

## Relationship to SCS

**SCS (Structured Context Specification)** is a formal specification for AI context documents:
- YAML-based SCDs (Structured Context Documents)
- Bundle hierarchy (Meta → Standards → Domain → Concern → Project)
- Validation, versioning, registry publishing
- Control plane for production AI agents

**SCS Vibe** is the entry point for developers who don't need all that:
- Plugin thinks in SCS (asks about the right concerns)
- Outputs native Claude Code format (no YAML to learn)
- No bundles, no registry, no control plane
- Just CLAUDE.md and `.claude/rules/`

**Upgrade path:** When a project grows and needs formal process, `scs-team` provides the full SCS workflow with YAML SCDs, validation, and versioning.

```
scs-vibe (solo devs, quick start)
    │
    │ project grows
    ▼
scs-team (teams, full SCS workflow)
    │
    │ enterprise scale
    ▼
SCS Control Plane (production AI governance)
```

## Example Session

```
❯ /scs-vibe:init

● Scanning project...
  Detected: Python 3.10+ CLI, healthcare domain (patient, medication keywords)

● Questions:
  · What does this project do? → Clinical tool for care coordinators
  · Personal or commercial? → Commercial

● This is a healthcare tool for commercial deployment.
  Let's walk through HIPAA considerations.

● HIPAA Considerations:
  · Encryption at rest? → Will Address
  · Audit logging? → Will Address
  · PHI in logs/errors? → Will Address
  ...

● Generated:
  ✓ CLAUDE.md
  ✓ CONSIDERATIONS.md (12 items documented)
  ✓ .claude/rules/tech-stack.md
  ✓ .claude/rules/architecture.md
  ✓ .claude/rules/patterns.md
  ✓ .claude/rules/phi-handling.md (path-specific)
  ✓ .claude/rules/domain-context.md

● Next steps:
  1. Review CONSIDERATIONS.md - these are your commitments
  2. Prioritize encryption (highest risk item)
  3. Would you like me to create a TODO list?
```

## Design Principles

1. **Think in SCS, output native format** - The spec guides questioning; output is what Claude Code understands

2. **Be the architect they can't afford** - Surface considerations solo devs would miss

3. **Force explicit decisions** - Don't let compliance slip through; document everything

4. **Scope context appropriately** - Path-specific rules keep PHI guidance where it matters

5. **Create audit trails** - CONSIDERATIONS.md proves due diligence

6. **No new formats to learn** - Just markdown and YAML frontmatter (native Claude Code)

## Files in This Plugin

```
scs-vibe/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── README.md                    # User-facing README
├── scs-vibe-plugin-overview.md  # This document
└── skills/
    ├── init/
    │   ├── SKILL.md             # Init skill prompt
    │   └── templates/           # Reference templates
    │       ├── healthcare.md
    │       ├── fintech.md
    │       ├── saas.md
    │       └── minimal.md
    ├── validate/
    │   └── SKILL.md             # Validate skill prompt
    └── explain/
        └── SKILL.md             # Explain skill prompt
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-02-05 | Added CONSIDERATIONS.md flow, modular `.claude/rules/`, path-specific rules |
| 1.0.0 | 2026-02-04 | Initial release with basic CLAUDE.md generation |

---

*Built by [Tim McCrimmon](https://github.com/tim-mccrimmon) as part of the [Structured Context Specification](https://structuredcontext.io) project.*
