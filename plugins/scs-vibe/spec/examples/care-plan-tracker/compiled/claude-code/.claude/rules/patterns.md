# Patterns

> Dataclasses for models, layered architecture, explicit instance passing.

## Patterns We Use

### Dataclasses for Models
- **Where**: `careplan/models.py`
- **Why**: Simple, typed, stdlib - no external dependencies
- **Example**:
  ```python
  @dataclass
  class Medication:
      id: str
      name: str
      dosage: str
      frequency: str
  ```

### Layered Architecture
- **Where**: CLI → Service → Storage separation
- **Why**: Testability, separation of concerns
- **Example**: Service calls `storage.load()`, not JSON directly

### UUIDs for IDs
- **Where**: All entity IDs
- **Why**: No collision risk, works offline, no sequence management
- **Example**: `id: str = field(default_factory=lambda: str(uuid.uuid4()))`

### ISO 8601 for Dates
- **Where**: All datetime serialization
- **Why**: Consistent, sortable, timezone-aware capable
- **Example**: `"2025-02-05T10:30:00Z"`

### Explicit Instance Passing
- **Where**: Throughout codebase
- **Why**: No hidden dependencies, easier testing, clear data flow
- **Example**: `def add_medication(storage: Storage, medication: Medication)`

## Patterns We Avoid

### ORMs
- **Why**: Overkill for JSON file storage
- **Instead**: Direct dataclass serialization to JSON

### Global State
- **Why**: Makes testing hard, hides dependencies, causes bugs
- **Instead**: Pass storage/service instances explicitly

### PHI in Exceptions/Logs
- **Why**: HIPAA violation risk, audit exposure
- **Instead**: Generic error messages
  - Good: `"Patient not found"`
  - Bad: `"Patient John Smith (ID: 12345) not found"`

### Magic Strings for Status/Types
- **Why**: Typos cause bugs, no IDE support
- **Instead**: Use Enums or Literal types

---

*Source: `scd:project:patterns:1.0.0`*
