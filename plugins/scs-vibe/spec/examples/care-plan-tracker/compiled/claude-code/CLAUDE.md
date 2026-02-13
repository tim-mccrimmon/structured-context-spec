# Care Plan Tracker

> CLI tool for care coordinators to track patient medications, appointments, and daily health tasks.

## System Overview

Care Plan Tracker is an internal tool used by care coordinators within a healthcare organization to help patients stay on track with their care plans.

It provides a simple command-line interface for tracking:
- Medications (name, dosage, frequency)
- Appointments (provider, datetime, location)
- Daily health tasks (e.g., "check blood pressure", "walk 30 minutes")

**Users**: Care coordinators (clinical staff)
**Data**: Contains PHI - patient names, medications, appointments, health tasks
**Storage**: Local JSON file per user (`~/.careplan/data.json`)

## Quick Reference

| Aspect | Details |
|--------|---------|
| Language | Python 3.10+ |
| CLI | Click |
| Storage | Local JSON |
| Testing | pytest |
| PHI | Yes - HIPAA awareness required |

## Architecture

Simple 3-layer design:

```
CLI (cli.py)           → Argument parsing, output formatting
    ↓
Service (service.py)   → Business logic, validation
    ↓
Storage (storage.py)   → JSON file I/O, serialization
```

## Project Status

| Component | File | Status |
|-----------|------|--------|
| Models | `careplan/models.py` | Complete |
| Service | `careplan/service.py` | TODO (stub) |
| Storage | `careplan/storage.py` | TODO (stub) |
| CLI | `careplan/cli.py` | TODO |
| Tests | `tests/` | Skeleton only |

## Context Files

Additional context is loaded from `.claude/rules/`:

| File | Content |
|------|---------|
| `tech-stack.md` | Technology choices and versions |
| `architecture.md` | System design and data flow |
| `patterns.md` | Patterns we use and avoid |
| `constraints.md` | Technical and clinical constraints |
| `domain-context.md` | Healthcare terminology and workflows |
| `phi-handling.md` | PHI rules (loads for specific files) |

---

*Compiled from SCS bundle `bundle:project:care-plan-tracker:1.0.0`*
*Generated with [SCS](https://structuredcontext.dev)*

**REMINDER**: This codebase handles PHI. Keep patient data out of logs and error messages.
