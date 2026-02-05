# Constraints

> Python 3.10+, local-only storage, clinical data accuracy requirements.

## Technical Constraints

| Constraint | Reason | Implication |
|------------|--------|-------------|
| Python 3.10+ | Using modern type hints, dataclasses, match statements | Cannot use older Python syntax |
| No external services | Local-only tool, simplicity | All operations must work offline |
| Single JSON file storage | Simplicity for v1 | No concurrent access, file corruption = data loss |
| Click for CLI | Cleaner command syntax | Must follow Click patterns |

## Clinical Constraints

### Data Accuracy is Critical
- **Reason**: Medication dosages, appointment times must be exact
- **Implication**:
  - Validate inputs strictly
  - Don't auto-correct or guess values
  - Display exactly what was entered

### No Clinical Decision Support
- **Reason**: Out of scope - this tracks adherence, doesn't recommend
- **Implication**:
  - Don't suggest medication changes
  - Don't flag "dangerous" combinations
  - Don't provide medical advice

### Audit Trail Needed (Future)
- **Reason**: HIPAA requires knowing who accessed what
- **Implication**:
  - Design storage to accommodate audit fields
  - v1 acceptable without, v2 must have

## Operational Constraints

| Constraint | Implication |
|------------|-------------|
| Care coordinators are users | Can assume training, technical error messages OK |
| Clinic workstations | Windows/Linux, full-disk encryption, no admin rights |

---

*Source: `scd:project:constraints:1.0.0`*
