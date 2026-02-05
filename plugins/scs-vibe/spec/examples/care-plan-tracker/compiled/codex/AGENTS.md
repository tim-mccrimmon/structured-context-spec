# Care Plan Tracker

CLI tool for care coordinators to track patient medications, appointments, and daily health tasks.

## System Overview

- **Type**: Internal healthcare tool
- **Users**: Care coordinators (clinical staff)
- **Data**: Contains PHI (patient names, medications, appointments)
- **Storage**: Local JSON file (`~/.careplan/data.json`)
- **Network**: None - all operations local

**IMPORTANT**: This codebase handles PHI. HIPAA awareness required.

## Tech Stack

- Python 3.10+ (type hints, dataclasses)
- Click for CLI
- JSON file for storage
- pytest for testing

No ORMs, no async, no external APIs.

## Architecture

```
CLI (cli.py) → Service (service.py) → Storage (storage.py)
```

Three-layer design. Service handles validation, storage handles I/O.

### Key Files

- `careplan/models.py` - Data classes (Complete)
- `careplan/service.py` - Business logic (TODO)
- `careplan/storage.py` - JSON I/O (TODO)
- `careplan/cli.py` - CLI commands (TODO)

## Patterns

**Use:**
- Dataclasses for models
- UUIDs for all IDs
- ISO 8601 for dates
- Explicit instance passing (no globals)

**Avoid:**
- ORMs (overkill for JSON)
- Global state (testing issues)
- PHI in logs/exceptions (HIPAA)
- Magic strings (use Enums)

## Constraints

**Technical:**
- Python 3.10+ required
- Local-only, no network
- Single JSON file (no concurrent access)

**Clinical:**
- Data accuracy critical (no auto-correct)
- No clinical decision support
- Audit trail needed for v2

## Domain Terms

- **Care Plan**: Medications + appointments + tasks for a patient
- **Adherence**: Whether patient followed the plan
- **Log Entry**: Record of completed care plan item
- **PHI**: Protected Health Information

## PHI Rules (for models.py, service.py, storage.py)

1. Never log patient names, medications, or appointment details
2. Generic error messages only ("Patient not found")
3. No PHI in exception messages
4. Validate all inputs before storage

---

*Compiled from SCS bundle `bundle:project:care-plan-tracker:1.0.0`*
