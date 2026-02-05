---
paths:
  - careplan/models.py
  - careplan/service.py
  - careplan/storage.py
---

# PHI Handling Rules

> These files handle PHI. HIPAA awareness required.

**This rule only loads when working on the files listed above.**

## Context

This codebase handles Protected Health Information (PHI):
- Patient names
- Medications (name, dosage, frequency)
- Appointments (provider, datetime, location)
- Health tasks and completion logs

HIPAA applies. While this is a local-only tool (contained risk), development practices must still protect PHI.

## Rules

1. **Never log PHI**: No patient names, medications, or appointment details in logs
2. **Generic error messages**: Use `"Patient not found"` NOT `"Patient John Smith not found"`
3. **No PHI in exceptions**: Exception messages may end up in logs or error reports
4. **Validate before storage**: All inputs validated in service layer before persisting
5. **Minimize PHI exposure**: Only load/display what's needed for the operation

## What is PHI in This System?

| Data | PHI? |
|------|------|
| Patient name | Yes |
| Patient ID | Yes |
| Medication names/dosages | Yes |
| Appointment details | Yes |
| Task descriptions | Yes (may contain health info) |
| Log entries | Yes (timestamped health activities) |

## Safe to Log

- Operation type (`add_medication`, `log_task`)
- Timestamps
- Success/failure status
- Generic counts (`"Added 1 medication"`, not `"Added Metformin"`)

## Before Making Changes

- [ ] Does this change touch PHI?
- [ ] Are error messages generic (no PHI)?
- [ ] Is logging PHI-free?
- [ ] Is validation in place?

## Current Limitations (Accepted for v1)

- Data file (`~/.careplan/data.json`) is not encrypted at rest
- No audit logging of who accessed what
- No role-based access control

*Note: Acceptable for v1 internal tool - workstations have full-disk encryption via IT policy.*

---

*Source: `scd:project:phi-handling:1.0.0`*
