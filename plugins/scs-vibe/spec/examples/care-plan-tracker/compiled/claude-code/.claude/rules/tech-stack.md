# Technology Stack

> Python 3.10+ CLI with Click, local JSON storage, pytest for testing.

## Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | Python 3.10+ | Type hints, dataclasses (stdlib) |
| CLI Framework | Click | Cleaner than argparse, better UX |
| Data Models | dataclasses | stdlib, no ORM needed |
| Storage | JSON file | Local only (`~/.careplan/data.json`) |
| Testing | pytest | Unit tests for service/storage |

## Dependencies

**Runtime:**
- `click>=8.0`

**Dev:**
- `pytest>=7.0`

## Not Using (and why)

| Technology | Reason |
|------------|--------|
| ORMs (SQLAlchemy) | Overkill for JSON file storage |
| async/await | No I/O concurrency needs, CLI is synchronous |
| External APIs | Local-only tool, no network dependencies |

---

*Source: `scd:project:tech-stack:1.0.0`*
