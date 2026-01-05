# SCD Validator

**Version**: 0.1.0
**Status**: Alpha

---

## Overview

The SCD Validator is a command-line tool for validating Structured Context Specification (SCS) documents and bundles. It ensures that SCDs are syntactically correct, schema-compliant, and semantically consistent.

## Features

- **Syntax Validation**: Validates YAML/JSON syntax
- **Schema Validation**: Validates against tier-specific JSON schemas
- **Semantic Validation**: Ensures logical consistency (type/tier matching, valid semver, provenance completeness)
- **Bundle Validation**: Validates bundle structure and completeness
- **Multiple Output Formats**: Text (colored) and JSON output
- **Strict Mode**: Fail on warnings
- **CI/CD Integration**: Exit codes for automated pipelines

## Installation

### From Source

```bash
cd tools/scd-validator

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Requirements

- Python 3.11 or higher
- Dependencies listed in `requirements.txt`

## Usage

### Basic Usage

```bash
# Validate a single SCD file
scs-validate context/meta/roles.yaml

# Validate multiple SCD files
scs-validate context/meta/*.yaml

# Validate a bundle
scs-validate --bundle context/bundle.yaml
```

### Advanced Options

```bash
# Strict mode (fail on warnings)
scs-validate --bundle context/bundle.yaml --strict

# JSON output
scs-validate --bundle context/bundle.yaml --output json

# Specify schema directory
scs-validate --bundle context/bundle.yaml --schema-dir ./schema

# Disable colored output
scs-validate --bundle context/bundle.yaml --no-color

# Verbose mode
scs-validate --bundle context/bundle.yaml --verbose
```

### Running as a Module

```bash
# Run directly as Python module
python -m scs_validator --bundle context/bundle.yaml
```

## Output Examples

### Text Output (Default)

```
SCS Validator v0.1.0

✓ Syntax validation passed (3 files)
✓ Schema validation passed (3 files)
✓ Semantic validation passed (3 files)

Warnings:
  ⚠ context/project/api.yaml (scd:project:api) - Provenance 'rationale' is recommended but missing

Summary:
  0 errors
  1 warnings

Status: ✓ VALID
```

### Error Output

```
SCS Validator v0.1.0

✓ Syntax validation passed (2 files)
✗ Schema validation failed

Errors:
  ✗ context/meta/roles.yaml (scd:meta:roles) - Missing required field: 'version'
  ✗ context/project/auth.yaml (scd:project:auth) - Type 'meta' does not match tier 'project' in ID

Summary:
  2 errors
  0 warnings

Status: ✗ FAILED
```

### JSON Output

```json
{
  "validator_version": "0.1.0",
  "strict_mode": false,
  "validation_levels": {
    "syntax": {
      "status": "passed",
      "error_count": 0,
      "warning_count": 0,
      "files_checked": 3
    },
    "schema": {
      "status": "passed",
      "error_count": 0,
      "warning_count": 0,
      "files_checked": 3
    }
  },
  "errors": [],
  "warnings": [],
  "summary": {
    "total_errors": 0,
    "total_warnings": 0,
    "status": "valid"
  }
}
```

## Exit Codes

- `0` - Validation passed (no errors)
- `1` - Validation failed (errors found)
- `2` - Validation passed with warnings (when `--strict` mode is enabled)
- `3` - Invalid command-line arguments
- `4` - File not found or permission error
- `5` - Internal validator error

## Validation Levels

The validator performs multiple levels of validation:

### Level 1: Syntax Validation
- Validates YAML/JSON syntax
- Ensures files are well-formed

### Level 2: Schema Validation
- Validates against tier-specific JSON schemas
- Ensures all required fields are present
- Validates field types and patterns

### Level 3: Semantic Validation
- Ensures `type` field matches tier in `id`
- Validates version follows semantic versioning
- Validates provenance completeness
- Checks timestamp formats (ISO8601)

### Future Levels (Coming Soon)
- **Level 4**: Relationship validation
- **Level 5**: Bundle completeness
- **Level 6**: Compliance validation

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest

# Run specific test
pytest tests/test_schema_validator.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Validate SCS Bundle
  run: |
    pip install -e tools/scd-validator
    scs-validate --bundle context/bundle.yaml --strict --output json > validation-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
scs-validate --bundle context/bundle.yaml --strict
if [ $? -ne 0 ]; then
  echo "❌ SCS validation failed"
  exit 1
fi
```

## Troubleshooting

### Schema Not Found

If you see "Schema directory not found", specify the schema directory:

```bash
scs-validate --bundle context/bundle.yaml --schema-dir /path/to/scs-spec/schema
```

### Invalid YAML Syntax

Ensure your YAML files have:
- Proper indentation (spaces, not tabs)
- Balanced quotes
- Valid field names

Use a YAML linter for debugging:

```bash
pip install yamllint
yamllint context/meta/roles.yaml
```

## Contributing

See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## Documentation

- [Validator Overview](VALIDATOR_OVERVIEW.md) - Technical design document
- [Validation Workflow](../../docs/validation-workflow.md) - Complete validation guide
- [SCS Specification](../../spec/0.1/) - Core specification

## License

Apache License 2.0 - See [LICENSE.md](../../LICENSE.md)

## Questions?

- Open an [issue](https://github.com/tim-mccrimmon/scs-spec/issues)
- See the [FAQ](../../docs/faq.md)
