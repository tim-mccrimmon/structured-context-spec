# SCS Team - Structured Context for Teams

> Transform your documentation into context Claude actually uses.

## The Problem

Your team has PRDs, architecture docs, security requirements, compliance checklists. Claude doesn't know any of it. So it makes decisions that conflict with what's already been decided.

Re-explaining your architecture every session isn't sustainable.

## The Solution

SCS Team takes your existing documentation and transforms it into structured context. Claude gets the full picture - business objectives, architecture decisions, security constraints, compliance requirements - before it writes a single line of code.

**Dual-layer output**: SCS Team maintains structured source (`.scs/`) AND compiled Claude Code rules (`.claude/rules/`). Edit the source, compilation keeps Claude in sync.

## Installation

```bash
/install scs-team
```

## Quick Start

```bash
/scs-team:init                    # Scaffold .scs/ with 11 concern bundles
/scs-team:add ./docs/PRD.md       # Process existing docs
/scs-team:use hipaa               # Add compliance standards
/scs-team:draft architecture      # Draft what's not documented
/scs-team:status                  # See coverage and gaps
```

## Workflow

### Phase 0: Initialize

Scaffold your project's structured context:

```bash
/scs-team:init
```

Scans your project, creates `.scs/` with all 11 concern bundle placeholders, and recommends where to start based on what it finds (existing docs, compliance signals, etc.).

### Phase 1: Build Context

Get your documentation into structured form:

```bash
# Add existing documents
/scs-team:add ./docs/PRD.md
/scs-team:add ./docs/architecture.md
/scs-team:add ./docs/security-requirements.md

# Reference known standards (from bundled library)
/scs-team:use hipaa
/scs-team:use soc2

# Draft areas without docs (conversational)
/scs-team:draft deployment
/scs-team:draft performance
```

Each modifying command automatically compiles to `.claude/rules/` so Claude picks up the context immediately.

### Phase 2: Validate

Check what you have and review for accuracy:

```bash
/scs-team:status    # What exists, what's missing, compilation sync
/scs-team:validate  # Structure check + issues to review
```

**Critical**: Read the generated context. Claude drafts it, you verify it's correct. Missing something important? Add it or flag it.

### Phase 3: Version

Lock it down when you're satisfied:

```bash
/scs-team:version   # Semantic versioning, git integration
```

## Commands

### `/scs-team:init`

Initialize structured context for your project.

```bash
/scs-team:init
/scs-team:init my-project-name
```

Creates `.scs/` scaffold with all 11 concern bundles, scans the project for language/framework and existing docs, and recommends next steps.

### `/scs-team:add <file>`

Process a document into structured context.

```bash
/scs-team:add ./docs/PRD.md
```

Analyzes the document, extracts relevant information, generates SCDs, updates concern bundles, and compiles to `.claude/rules/`.

### `/scs-team:use <standard>`

Add known compliance/regulatory standards from the bundled library.

```bash
/scs-team:use hipaa      # Healthcare - PHI, audit, BAA requirements
/scs-team:use soc2       # Security - Trust service criteria
/scs-team:use pci        # Payments - Card data handling
/scs-team:use chai       # AI - Coalition for Health AI guidelines
/scs-team:use gdpr       # Privacy - EU data protection
```

Copies pre-built standards SCDs from the plugin's standards library rather than generating from scratch.

### `/scs-team:draft <concern>`

Conversational drafting when you don't have documentation.

```bash
/scs-team:draft architecture    # System structure, components
/scs-team:draft security        # Auth, data protection, threats
/scs-team:draft performance     # Response times, availability, scaling
/scs-team:draft usability       # UX principles, accessibility
/scs-team:draft compliance      # Regulatory requirements
/scs-team:draft data            # Data models, flow, retention
/scs-team:draft testing         # Test strategy, coverage
/scs-team:draft deployment      # Infrastructure, CI/CD, monitoring
/scs-team:draft safety          # Risk assessment, safety checklists
/scs-team:draft ethics          # AI usage, bias detection, audit trails
/scs-team:draft business        # Problem, stakeholders, objectives
```

Claude asks targeted questions and generates draft SCDs.

### `/scs-team:status`

See what context exists and what's missing.

```bash
/scs-team:status
```

Shows:
- Bundles and SCDs created
- Coverage across all 11 concerns
- Compilation sync status (`.scs/` vs `.claude/rules/`)
- Draft vs. versioned status

### `/scs-team:validate`

Check structure and surface issues for human review.

```bash
/scs-team:validate
```

Five validation levels:
1. **Syntax** - Valid YAML, required fields
2. **References** - SCDs exist, imports resolve, no circular deps
3. **Consistency** - Version and tier correctness
4. **Content Quality** - Placeholders, TBDs, incomplete sections
5. **Compilation** - Compiled output exists with ownership markers

### `/scs-team:version`

Lock bundles with semantic version.

```bash
/scs-team:version
```

Guides you through version selection, updates all files, recompiles output, and optionally creates a git commit and tag.

## The 11 Concerns

SCS Team organizes structured context into 11 concern areas:

| # | Concern | SCDs |
|---|---------|------|
| 1 | Architecture | system-context, tech-stack, integration-map, component-model |
| 2 | Security | authn-authz, data-protection, data-handling, threat-model |
| 3 | Performance & Reliability | response-time, availability, fault-tolerance, scalability |
| 4 | Usability & Accessibility | ux-principles, accessibility-compliance, error-handling-ux |
| 5 | Compliance & Governance | hipaa-compliance, soc2-controls, audit-requirements, policy-enforcement |
| 6 | Data & Provenance | data-model, provenance-tracking, retention-policy |
| 7 | Testing & Validation | test-coverage, validation-plan, qa-procedures |
| 8 | Deployment & Operations | infrastructure-definition, observability, incident-response |
| 9 | Safety & Risk | risk-assessment, safety-checklist |
| 10 | Ethics & AI Accountability | ai-usage-policy, audit-trail, model-bias |
| 11 | Business Context | problem-definition, stakeholders, business-objectives, opportunity-analysis, constraints-and-assumptions, success-criteria |

Not every project needs all 11. Use what's relevant - the status and validate commands tell you what's covered and what's missing.

## What Gets Generated

SCS Team creates a **dual-layer structure**:

### Source Layer (`.scs/`) - Your structured context

```
.scs/
├── project.yaml              # Project bundle manifest
├── concerns/
│   ├── architecture.yaml     # Architecture concern bundle
│   ├── security.yaml         # Security concern bundle
│   ├── performance.yaml      # Performance concern bundle
│   ├── usability.yaml        # Usability concern bundle
│   ├── compliance.yaml       # Compliance concern bundle
│   ├── data.yaml             # Data concern bundle
│   ├── testing.yaml          # Testing concern bundle
│   ├── deployment.yaml       # Deployment concern bundle
│   ├── safety.yaml           # Safety concern bundle
│   ├── ethics.yaml           # Ethics concern bundle
│   └── business.yaml         # Business concern bundle
└── scds/
    ├── system-context.yaml   # From architecture doc
    ├── tech-stack.yaml       # From architecture doc
    ├── threat-model.yaml     # From security requirements
    └── hipaa-phi-handling.yaml  # From /scs-team:use hipaa
```

### Compiled Layer (`.claude/rules/`) - What Claude reads

```
.claude/
└── rules/
    ├── architecture.md       # <!-- scs-team:managed -->
    ├── security.md           # <!-- scs-team:managed -->
    ├── compliance.md         # <!-- scs-team:managed -->
    └── my-custom-rules.md    # (untouched - developer-owned)
```

Files with `<!-- scs-team:managed -->` are owned by scs-team and recompiled automatically. Files without that marker are left untouched.

The scs-team section in `CLAUDE.md` is bounded by `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers. Existing CLAUDE.md content outside those markers is never modified.

## Bundled Standards Library

SCS Team ships with pre-built standards SCDs:

- **HIPAA** - PHI handling, security controls, administrative safeguards
- **SOC 2** - Security, availability, confidentiality
- **PCI DSS** - Data protection, access control, monitoring
- **CHAI** - Transparency, accountability for health AI
- **GDPR** - Data subject rights, processing & transfers

These are concrete requirements (not templates) that get copied into your project and can be customized.

## For Solo Devs

If you don't have documentation yet, check out [SCS Vibe](https://github.com/structuredcontext/scs-vibe) - a quick 15-minute conversational setup.

## Links

- Documentation: https://structuredcontext.io
- GitHub: https://github.com/structuredcontext/scs-team
- For Solo Devs: https://github.com/structuredcontext/scs-vibe

## License

MIT

---

*Built by [Tim McCrimmon](https://github.com/tim-mccrimmon)*
