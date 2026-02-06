# Care Plan Tracker - Product Requirements Document

## Overview

A command-line application that helps patients stay on track with their care plans by tracking medications, appointments, and daily health tasks.

## Problem Statement

Patients with ongoing care plans often struggle to keep track of multiple medications, appointments, and daily health tasks. A simple tracking tool can help them log adherence and review their progress.

## Goals

- Provide a simple CLI for patients to log and view care plan activities
- Track three types of care plan items: medications, appointments, and daily tasks
- Persist data locally using file-based storage
- Keep the interface minimal and easy to use

## Non-Goals

- Push notifications or reminders
- Multi-user support
- Cloud sync or external integrations
- Web or mobile UI

## User Stories

1. As a patient, I can add a medication to my care plan with dosage and schedule info
2. As a patient, I can add an appointment with date, time, and provider details
3. As a patient, I can add a daily task (e.g., "check blood pressure", "walk 30 minutes")
4. As a patient, I can log that I took a medication
5. As a patient, I can log that I completed a daily task
6. As a patient, I can mark an appointment as attended
7. As a patient, I can view my care plan summary
8. As a patient, I can view my adherence history for a given date range

## Data Model

### Patient
- id: string
- name: string
- care_plan: CarePlan

### CarePlan
- medications: list[Medication]
- appointments: list[Appointment]
- tasks: list[Task]

### Medication
- id: string
- name: string
- dosage: string
- frequency: string (e.g., "daily", "twice daily", "weekly")
- instructions: string (optional)

### Appointment
- id: string
- provider: string
- location: string
- datetime: datetime
- notes: string (optional)

### Task
- id: string
- name: string
- frequency: string
- instructions: string (optional)

### LogEntry
- id: string
- item_type: "medication" | "appointment" | "task"
- item_id: string
- timestamp: datetime
- notes: string (optional)

## CLI Commands

```
careplan add medication <name> --dosage <dosage> --frequency <frequency>
careplan add appointment <provider> --datetime <datetime> --location <location>
careplan add task <name> --frequency <frequency>

careplan log medication <medication_id>
careplan log appointment <appointment_id>
careplan log task <task_id>

careplan list medications
careplan list appointments
careplan list tasks

careplan history [--from <date>] [--to <date>]

careplan summary
```

## Technical Approach

- **Language**: Python 3.10+
- **CLI Framework**: argparse (stdlib) or click
- **Storage**: JSON file in user's home directory (~/.careplan/data.json)
- **Architecture**: Simple layered structure
  - CLI layer: argument parsing and output formatting
  - Service layer: business logic
  - Storage layer: file I/O and data serialization

## File Structure

```
careplan/
├── __init__.py
├── __main__.py          # Entry point
├── cli.py               # CLI argument parsing
├── service.py           # Business logic
├── storage.py           # File I/O
├── models.py            # Data classes
tests/
├── __init__.py
├── test_service.py
├── test_storage.py
pyproject.toml
README.md
PRD.md
```

## Success Criteria

- Patient can manage their full care plan from the command line
- Data persists between sessions
- Commands are intuitive and provide helpful feedback
- Code is testable and maintainable

## Future Considerations (Out of Scope)

- SQLite storage for better querying
- Reminder/notification system
- Export to PDF or share with provider
- Multiple patient profiles
