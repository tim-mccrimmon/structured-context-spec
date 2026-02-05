# SCS Team - Structured Context for Teams

> Transform your documentation into context Claude actually uses.

## The Problem

Your team has PRDs, architecture docs, security requirements, compliance checklists. Claude doesn't know any of it. So it makes decisions that conflict with what's already been decided.

Re-explaining your architecture every session isn't sustainable.

## The Solution

SCS Team takes your existing documentation and transforms it into structured context. Claude gets the full picture - business objectives, architecture decisions, security constraints, compliance requirements - before it writes a single line of code.

## Installation

```bash
/install scs-team
```

## Workflow

### Phase 1: Build Context

Get your documentation into structured form:

```bash
# Add existing documents
/scs-team:add ./docs/PRD.md
/scs-team:add ./docs/architecture.md
/scs-team:add ./docs/security-requirements.md

# Reference known standards
/scs-team:use hipaa
/scs-team:use soc2

# Draft areas without docs (conversational)
/scs-team:draft deployment
```

### Phase 2: Validate

Check what you have and review for accuracy:

```bash
/scs-team:status    # What exists, what's missing
/scs-team:validate  # Structure check + issues to review
```

**Critical**: Read the generated context. Claude drafts it, you verify it's correct. Missing something important? Add it or flag it.

### Phase 3: Version

Lock it down when you're satisfied:

```bash
/scs-team:version   # Semantic versioning, git integration
```

## Commands

### `/scs-team:add <file>`

Process a document into structured context.

```bash
/scs-team:add ./docs/PRD.md
```

Claude will:
1. Analyze the document type (PRD, architecture, security, etc.)
2. Extract relevant information
3. Generate appropriate SCDs (Structured Context Documents)
4. Place them in the right location

### `/scs-team:use <standard>`

Add known compliance/regulatory standards.

```bash
/scs-team:use hipaa      # Healthcare - PHI, audit, BAA requirements
/scs-team:use soc2       # Security - Trust service criteria
/scs-team:use pci        # Payments - Card data handling
/scs-team:use chai       # AI - Coalition for Health AI guidelines
```

### `/scs-team:draft <concern>`

Conversational drafting when you don't have documentation.

```bash
/scs-team:draft architecture    # System structure, components
/scs-team:draft security        # Auth, data protection, threats
/scs-team:draft deployment      # Infrastructure, CI/CD, monitoring
/scs-team:draft compliance      # Regulatory requirements
```

Claude will ask targeted questions and generate draft SCDs.

### `/scs-team:status`

See what context exists and what's missing.

```bash
/scs-team:status
```

Shows:
- Bundles and SCDs created
- Concerns covered vs. gaps
- Draft vs. versioned status

### `/scs-team:validate`

Check structure and surface issues for human review.

```bash
/scs-team:validate
```

Checks:
- YAML structure valid
- References resolve
- No circular dependencies
- Flags areas that need human attention

### `/scs-team:version`

Lock bundle with semantic version.

```bash
/scs-team:version
```

Guides you through:
- Version number selection (major/minor/patch)
- Git commit and tag
- Updating dependent bundles

## What Gets Generated

SCS Team creates **bundles** containing **SCDs** (Structured Context Documents):

```
.scs/
├── bundles/
│   └── my-project.yaml       # Project bundle (imports concerns)
├── concerns/
│   ├── architecture.yaml     # Architecture concern bundle
│   ├── security.yaml         # Security concern bundle
│   └── compliance.yaml       # Compliance concern bundle
└── scds/
    ├── system-context.yaml   # From architecture doc
    ├── tech-stack.yaml       # From architecture doc
    ├── threat-model.yaml     # From security requirements
    └── hipaa-controls.yaml   # From /scs-team:use hipaa
```

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
