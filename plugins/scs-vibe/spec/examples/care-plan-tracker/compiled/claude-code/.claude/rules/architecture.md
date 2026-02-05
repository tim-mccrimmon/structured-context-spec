# Architecture

> Simple 3-layer Python CLI application (CLI → Service → Storage).

## Design

- **Type**: Monolith (single CLI application)
- **Style**: Layered architecture
- **Deployment**: Installed on clinic workstations

## Layers

```
┌─────────────────────────────────────────────────────────┐
│  CLI Layer (careplan/cli.py)                            │
│  - Argument parsing (Click commands)                    │
│  - Output formatting (tables, messages)                 │
│  - User interaction                                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Service Layer (careplan/service.py)                    │
│  - Business logic                                       │
│  - Input validation                                     │
│  - Coordinating storage operations                      │
│  NOTE: All PHI operations go through here               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Storage Layer (careplan/storage.py)                    │
│  - JSON file I/O                                        │
│  - Serialization/deserialization                        │
│  - Data persistence                                     │
│  NOTE: Reads/writes PHI - audit considerations          │
└─────────────────────────────────────────────────────────┘
```

## Key Files

| Path | Purpose | Contains PHI? | Status |
|------|---------|---------------|--------|
| `careplan/models.py` | Data classes | Defines PHI structure | Complete |
| `careplan/service.py` | Business logic | Handles PHI | TODO |
| `careplan/storage.py` | File I/O | Reads/writes PHI | TODO |
| `careplan/cli.py` | CLI commands | Displays PHI | TODO |
| `~/.careplan/data.json` | Persisted data | **YES** | Runtime |

## Data Flow

```
User Input → CLI (parse) → Service (validate) → Storage (persist)
                 │              │                    │
           Format output   Apply rules          Load/save JSON
```

## External Dependencies

None. This is a local-only tool with no network communication.

---

*Source: `scd:project:architecture:1.0.0`*
