# SCS Team Demo - Patient Portal

A demo project for testing the `scs-team` Claude Code plugin.

## Scenario

You're on a team building a patient portal for Acme Health. The project has a PRD (product manager), an architecture doc (CTO), and security requirements (CISO). There's working code for the API layer. No structured context exists yet.

## Prerequisites

- Claude Code installed and working
- This directory open as your project root

## Demo

### 1. Install the plugin

```
/install <path-to>/plugins/scs-team
```

### 2. Initialize

```
/scs-team:init
```

Watch it scan the project - it should find:
- Python FastAPI project (from pyproject.toml and code)
- 3 docs in `docs/` directory
- HIPAA/healthcare signals throughout

### 3. Process existing documentation

```
/scs-team:add docs/PRD.md
/scs-team:add docs/architecture.md
/scs-team:add docs/security-requirements.md
```

Each command extracts structured context, creates SCDs, updates concern bundles, and compiles to `.claude/rules/`.

### 4. Add compliance standards

```
/scs-team:use hipaa
```

Copies pre-built HIPAA standards SCDs from the plugin's library.

### 5. Check coverage

```
/scs-team:status
```

See the 11-concern coverage table. Which concerns are covered? Which have gaps? The PRD covers business context. The architecture doc covers architecture and deployment. The security doc covers security. What's missing? (Data, testing, performance, usability, safety, ethics...)

### 6. Draft what's missing

```
/scs-team:draft performance
/scs-team:draft testing
```

Fill gaps through conversation.

### 7. Validate

```
/scs-team:validate
```

Check for structural issues, missing references, and human review items before versioning.

## What's in this project

### Documentation (the interesting part)

| File | Author | Content |
|------|--------|---------|
| `docs/PRD.md` | Product Manager | Full PRD with stakeholders, user stories, timeline, success criteria |
| `docs/architecture.md` | CTO | System architecture, tech stack, API design, deployment |
| `docs/security-requirements.md` | CISO | Data classification, auth requirements, encryption, audit logging |

### Code (real enough to be credible)

| File | Status |
|------|--------|
| `src/patient_portal/main.py` | FastAPI app with routes |
| `src/patient_portal/models.py` | SQLAlchemy models (users, messages, appointments, audit log) |
| `src/patient_portal/auth.py` | OAuth2 + JWT authentication |
| `src/patient_portal/routes/` | Patient, appointment, and messaging endpoints |
| `tests/` | Stub test files |

### Intentional gaps (for the demo to find)

- No CLAUDE.md or structured context
- No performance/SLA documentation
- No testing strategy
- No data model documentation (beyond what's in code)
- No accessibility requirements doc
- Security doc mentions HIPAA but doesn't have full coverage
- Code has a hardcoded secret key in `auth.py`
- No audit logging implementation despite the model existing
