# SCD Validator - Technical Overview

**Version**: 0.1
**Status**: Design Document
**Last Updated**: 2025-11-20

---

## Purpose

The SCD Validator is a command-line tool that validates Structured Context Documents (SCDs) and SCD bundles against the SCS specification. It ensures that SCDs are syntactically correct, schema-compliant, semantically consistent, and ready for use in AI-native development and autonomic governance.

---

## Validation Levels

The validator implements six levels of validation, from basic syntax to advanced compliance checking:

### Level 1: Syntactic Validation
**Purpose**: Ensure files are valid YAML/JSON

**Checks**:
- Valid YAML/JSON syntax
- Proper indentation
- Balanced quotes and brackets
- Correct data types

**Dependencies**: YAML/JSON parser

---

### Level 2: Schema Validation
**Purpose**: Ensure SCDs conform to their tier-specific schemas

**Checks**:
- All required fields present (`id`, `type`, `title`, `version`, `description`, `content`, `provenance`)
- Field types match schema definitions
- ID patterns match tier (`scd:meta:*`, `scd:project:*`, `scd:standards:*`)
- No unexpected fields (in strict mode)

**Dependencies**: JSON Schema validator, tier-specific schemas

**Schemas**:
- `schema/scd/meta-scd-template.json`
- `schema/scd/project-scd-template.json`
- `schema/scd/standards-scd-template.json`
- `schema/bundles/scd-bundle-schema.json`

---

### Level 3: Semantic Validation
**Purpose**: Ensure logical consistency within individual SCDs

**Checks**:
- `type` field matches tier in `id` (e.g., `scd:meta:*` → `type: meta`)
- Version follows semantic versioning (semver)
- ID patterns are consistent
- Content structure is appropriate for tier
- Provenance fields are complete and valid
  - `created_by` is identifiable
  - Timestamps are ISO8601 format
  - `rationale` is present and meaningful

**Dependencies**: Semver parser, pattern matching

---

### Level 4: Relationship Validation
**Purpose**: Ensure relationships between SCDs are valid

**Checks**:
- All relationship targets exist in the bundle
- Relationship types are valid
- No orphaned references
- Dependency graph is acyclic (for `depends-on` relationships)
- Relationship patterns are appropriate for tier combinations

**Dependencies**: Graph analysis, bundle context

---

### Level 5: Bundle Validation
**Purpose**: Ensure bundles are complete and consistent

**Checks**:
- All SCDs referenced in bundle exist at specified paths
- No duplicate SCD IDs within bundle
- At least one meta-tier SCD present
- At least one project-tier SCD present
- All relationship targets exist within bundle
- Import references are valid
- Bundle metadata is complete

**Dependencies**: File system access, bundle schema

---

### Level 6: Compliance Validation (Optional/Advanced)
**Purpose**: Validate compliance with standards-tier requirements

**Checks**:
- All standards-tier requirements have corresponding `satisfies` relationships from project-tier SCDs
- Required controls are implemented
- No unsatisfied obligations
- Coverage gaps identified and reported

**Dependencies**: Relationship graph, standards interpretation

**Note**: This level enables autonomic governance and is optional for basic validation.

---

## Command-Line Interface

### Basic Usage

```bash
# Validate single SCD
scs-validate context/meta/roles.yaml

# Validate multiple SCDs
scs-validate context/meta/*.yaml

# Validate bundle
scs-validate --bundle context/bundle.yaml
```

### Advanced Options

```bash
# Strict mode (fail on warnings)
scs-validate --bundle context/bundle.yaml --strict

# Validate relationships only
scs-validate --bundle context/bundle.yaml --check-relationships

# Validate compliance (requires standards-tier SCDs)
scs-validate --bundle context/bundle.yaml --check-compliance

# Output formats
scs-validate --bundle context/bundle.yaml --output text    # default
scs-validate --bundle context/bundle.yaml --output json    # machine-readable
scs-validate --bundle context/bundle.yaml --output junit   # CI integration

# Specify schema directory (if not default)
scs-validate --bundle context/bundle.yaml --schema-dir ./schema

# Verbose output
scs-validate --bundle context/bundle.yaml --verbose

# Validate specific levels
scs-validate --bundle context/bundle.yaml --level syntax
scs-validate --bundle context/bundle.yaml --level schema
scs-validate --bundle context/bundle.yaml --level all  # default
```

---

## Output Format

### Text Output (Default)

```
SCS Validator v0.1.0

Validating bundle: bundle:healthcare-platform

✓ Syntax validation passed (8 files)
✓ Schema validation passed (8 files)
✓ Semantic validation passed (8 files)
✓ Relationship validation passed
  - 12 relationships validated
  - 0 orphaned references
  - 0 circular dependencies
✓ Bundle completeness passed
  - 3 meta-tier SCDs
  - 2 standards-tier SCDs
  - 3 project-tier SCDs

Warnings:
  ⚠ scd:project:patient-api has no 'satisfies' relationships to standards
  ⚠ scd:meta:capabilities version 0.1.0 is older than scd:meta:roles 1.0.0

Summary:
  8 SCDs validated
  0 errors
  2 warnings

Status: ✓ VALID
```

### JSON Output

```json
{
  "validator_version": "0.1.0",
  "bundle_id": "bundle:healthcare-platform",
  "timestamp": "2025-11-20T10:30:00Z",
  "validation_levels": {
    "syntax": {
      "status": "passed",
      "files_checked": 8,
      "errors": []
    },
    "schema": {
      "status": "passed",
      "files_checked": 8,
      "errors": []
    },
    "semantic": {
      "status": "passed",
      "files_checked": 8,
      "errors": []
    },
    "relationships": {
      "status": "passed",
      "relationships_validated": 12,
      "orphaned_references": 0,
      "circular_dependencies": 0,
      "errors": []
    },
    "bundle": {
      "status": "passed",
      "meta_tier_count": 3,
      "standards_tier_count": 2,
      "project_tier_count": 3,
      "errors": []
    }
  },
  "warnings": [
    {
      "scd_id": "scd:project:patient-api",
      "level": "relationship",
      "message": "No 'satisfies' relationships to standards-tier SCDs"
    },
    {
      "scd_id": "scd:meta:capabilities",
      "level": "semantic",
      "message": "Version 0.1.0 is older than related SCD scd:meta:roles (1.0.0)"
    }
  ],
  "summary": {
    "total_scds": 8,
    "errors": 0,
    "warnings": 2,
    "status": "valid"
  }
}
```

### Error Output Example

```
SCS Validator v0.1.0

Validating bundle: bundle:healthcare-platform

✓ Syntax validation passed (8 files)
✗ Schema validation failed

Errors:
  ✗ context/meta/roles.yaml (scd:meta:roles)
    - Missing required field: 'version'
    - Line 1, Column 1

  ✗ context/project/auth-service.yaml (scd:project:auth-service)
    - Type mismatch: expected 'project', got 'meta'
    - Line 3, Column 7

Summary:
  8 SCDs checked
  2 errors
  0 warnings

Status: ✗ FAILED
Exit code: 1
```

---

## Exit Codes

The validator uses standard exit codes for CI/CD integration:

- `0` - Validation passed (no errors)
- `1` - Validation failed (errors found)
- `2` - Validation passed with warnings (when `--strict` mode is enabled)
- `3` - Invalid command-line arguments
- `4` - File not found or permission error
- `5` - Internal validator error

---

## Implementation Architecture

### Core Components

#### 1. Parser Module
**Responsibility**: Load and parse YAML/JSON files

**Functions**:
- `load_scd(path)` - Load single SCD file
- `load_bundle(path)` - Load bundle file
- `parse_yaml(content)` - Parse YAML content
- `parse_json(content)` - Parse JSON content

#### 2. Schema Validator Module
**Responsibility**: Validate against JSON schemas

**Functions**:
- `validate_schema(scd, schema)` - Validate SCD against schema
- `load_schema(tier)` - Load appropriate schema for tier
- `get_tier_from_id(id)` - Extract tier from SCD ID

**Dependencies**: `jsonschema` library

#### 3. Semantic Validator Module
**Responsibility**: Semantic consistency checks

**Functions**:
- `validate_id_type_match(scd)` - Ensure type matches ID tier
- `validate_version(version)` - Validate semver format
- `validate_provenance(provenance)` - Check provenance completeness
- `validate_timestamps(provenance)` - Verify ISO8601 format

#### 4. Relationship Validator Module
**Responsibility**: Validate relationships between SCDs

**Functions**:
- `validate_relationships(bundle)` - Check all relationships in bundle
- `check_orphaned_references(bundle)` - Find broken references
- `detect_circular_dependencies(bundle)` - Find cycles in dependency graph
- `build_relationship_graph(bundle)` - Create graph representation

**Dependencies**: Graph analysis library (e.g., NetworkX)

#### 5. Bundle Validator Module
**Responsibility**: Bundle-level validation

**Functions**:
- `validate_bundle_completeness(bundle)` - Check bundle requirements
- `check_duplicate_ids(bundle)` - Find duplicate SCD IDs
- `verify_file_existence(bundle)` - Ensure all referenced files exist
- `count_by_tier(bundle)` - Count SCDs in each tier

#### 6. Compliance Validator Module (Optional)
**Responsibility**: Standards compliance checking

**Functions**:
- `check_compliance(bundle)` - Validate compliance coverage
- `find_unsatisfied_requirements(bundle)` - Identify gaps
- `generate_compliance_report(bundle)` - Create detailed report

#### 7. Reporter Module
**Responsibility**: Format and output validation results

**Functions**:
- `format_text_output(results)` - Human-readable output
- `format_json_output(results)` - Machine-readable JSON
- `format_junit_output(results)` - JUnit XML for CI
- `print_summary(results)` - Print summary

#### 8. CLI Module
**Responsibility**: Command-line interface

**Functions**:
- `parse_arguments()` - Parse CLI arguments
- `main()` - Entry point
- `handle_errors()` - Error handling and exit codes

---

## Technology Stack

### Language
**Python 3.11+**

**Rationale**:
- Excellent YAML/JSON support
- Rich ecosystem for schema validation
- Easy CLI development
- Wide adoption in developer tooling
- Cross-platform compatibility

### Core Dependencies

```python
# requirements.txt
pyyaml>=6.0              # YAML parsing
jsonschema>=4.20         # JSON Schema validation
click>=8.1               # CLI framework
networkx>=3.0            # Graph analysis for relationships
semver>=3.0              # Semantic versioning validation
colorama>=0.4            # Colored terminal output
tabulate>=0.9            # Formatted tables
```

### Optional Dependencies

```python
# requirements-dev.txt
pytest>=7.4              # Testing
pytest-cov>=4.1          # Coverage
black>=23.0              # Code formatting
mypy>=1.7                # Type checking
ruff>=0.1                # Linting
```

---

## File Structure

```
tools/scd-validator/
├── README.md                    # User documentation
├── VALIDATOR_OVERVIEW.md        # This document
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Dependencies
├── requirements-dev.txt         # Development dependencies
├── src/
│   └── scs_validator/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── cli.py               # CLI interface
│       ├── parser.py            # File parsing
│       ├── schema_validator.py  # Schema validation
│       ├── semantic_validator.py # Semantic validation
│       ├── relationship_validator.py # Relationship validation
│       ├── bundle_validator.py  # Bundle validation
│       ├── compliance_validator.py # Compliance validation
│       ├── reporter.py          # Output formatting
│       └── utils.py             # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_schema_validator.py
│   ├── test_semantic_validator.py
│   ├── test_relationship_validator.py
│   ├── test_bundle_validator.py
│   ├── test_compliance_validator.py
│   └── fixtures/                # Test data
│       ├── valid/
│       ├── invalid/
│       └── bundles/
└── scripts/
    └── install.sh               # Installation script
```

---

## Development Phases

### Phase 1: Core Validation (MVP)
**Goal**: Basic validation functionality

**Features**:
- [ ] CLI framework setup
- [ ] YAML/JSON parsing
- [ ] Schema validation (Levels 1-2)
- [ ] Semantic validation (Level 3)
- [ ] Text output
- [ ] Basic error reporting

**Timeline**: 1-2 weeks

---

### Phase 2: Bundle & Relationships
**Goal**: Bundle-aware validation

**Features**:
- [ ] Bundle loading and parsing
- [ ] Relationship validation (Level 4)
- [ ] Bundle completeness validation (Level 5)
- [ ] Dependency graph analysis
- [ ] Enhanced error messages
- [ ] JSON output format

**Timeline**: 1-2 weeks

---

### Phase 3: Advanced Features
**Goal**: Production-ready validator

**Features**:
- [ ] Compliance validation (Level 6)
- [ ] Strict mode
- [ ] JUnit XML output
- [ ] CI/CD integration examples
- [ ] Performance optimization
- [ ] Comprehensive test suite
- [ ] Documentation

**Timeline**: 2-3 weeks

---

### Phase 4: Polish & Distribution
**Goal**: Easy installation and use

**Features**:
- [ ] PyPI package
- [ ] Installation via `pip install scs-validator`
- [ ] Comprehensive user documentation
- [ ] Tutorial videos
- [ ] Example bundles
- [ ] GitHub Actions integration examples

**Timeline**: 1 week

---

## Testing Strategy

### Unit Tests
- Test each validator module independently
- Mock file I/O for speed
- Test both valid and invalid inputs
- Achieve >90% code coverage

### Integration Tests
- Test full validation workflows
- Use real SCD files from templates
- Test bundle validation end-to-end
- Verify output formats

### Regression Tests
- Maintain test suite of known issues
- Test against specification examples
- Ensure backward compatibility

### Performance Tests
- Validate large bundles (100+ SCDs)
- Benchmark validation speed
- Profile for optimization opportunities

---

## Success Criteria

The SCD Validator will be considered successful when it can:

1. **Validate individual SCDs** against tier-specific schemas
2. **Validate bundles** with complete relationship checking
3. **Detect common errors** with clear, actionable error messages
4. **Integrate with CI/CD** pipelines seamlessly
5. **Support multiple output formats** (text, JSON, JUnit)
6. **Handle large bundles** (100+ SCDs) efficiently (<5 seconds)
7. **Provide actionable feedback** for fixing validation errors
8. **Enable autonomic governance** through compliance validation

---

## Future Enhancements

### v0.2+
- IDE integration (VS Code extension)
- Real-time validation on file save
- Auto-fix capabilities for common errors
- Interactive validation mode
- Web-based validator UI
- Validation caching for performance
- Custom validation rules
- Plugin architecture for extensions

---

## Related Documentation

- [Validation Workflow](../../docs/validation-workflow.md) - Complete validation guide
- [SCS Overview](../../spec/0.1/overview.md) - Specification overview
- [JSON Schemas](../../schema/) - Schema definitions
- [Templates](../../templates/) - SCD templates for testing

---

## Questions & Feedback

For questions or feedback about the validator design:
- Open an issue on GitHub
- Tag with `validator` label
- Reference this document
