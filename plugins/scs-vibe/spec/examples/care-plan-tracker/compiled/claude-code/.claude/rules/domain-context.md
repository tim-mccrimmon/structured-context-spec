# Domain Context

> Healthcare terminology and care coordination workflows.

## Terminology

| Term | Definition |
|------|------------|
| **Care Plan** | Collection of medications, appointments, and tasks for a patient. The central organizing concept. |
| **Adherence** | Whether the patient followed the care plan. Tracked via log entries. |
| **Log Entry** | Record that a care plan item was completed. Contains: item reference, timestamp, optional notes. |
| **PHI** | Protected Health Information. In this system: patient name, medications, appointments, tasks. |
| **Care Coordinator** | Clinical staff member who manages patient care plans. Primary user of this tool. |
| **Frequency** | How often a medication/task occurs: "daily", "twice daily", "weekly", "as needed". |

## Workflows

### 1. Setup Patient Care Plan
**Actor**: Care Coordinator

1. Add medications with dosage and frequency
2. Add appointments with provider and datetime
3. Add daily tasks with instructions

**Outcome**: Patient has complete care plan in system

### 2. Daily Logging
**Actor**: Care Coordinator (during patient contact)

1. Review today's care plan items with patient
2. Log completed medications
3. Log completed tasks
4. Note any issues or concerns

**Outcome**: Adherence record updated

### 3. Adherence Review
**Actor**: Care Coordinator

1. View patient's care plan summary
2. Review history for date range
3. Identify missed items or patterns
4. Discuss with patient, adjust plan if needed

**Outcome**: Care plan optimized based on actual adherence

## Business Rules

- A patient can have multiple medications, appointments, and tasks
- Each log entry references exactly one care plan item
- Adherence = logged items / expected items
- Appointments are one-time; medications and tasks recur per frequency

---

*Source: `scd:project:domain-context:1.0.0`*
