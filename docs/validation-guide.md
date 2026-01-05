# SCD and Bundle Validation Guide

**Version**: 0.2.0
**Last Updated**: 2025-12-09

---

## Overview

Validation ensures that your Structured Context Documents (SCDs) and bundles are correct, consistent, and ready for use in AI-native development and autonomic governance. This guide explains why validation matters, what gets validated, how validation works, and how to integrate it into your workflow.

---

## Table of Contents

1. [Why Validation Matters](#why-validation-matters)
2. [What Gets Validated](#what-gets-validated)
3. [The Six Validation Levels](#the-six-validation-levels)
4. [Validation Workflow](#validation-workflow)
5. [Using the SCD Validator](#using-the-scd-validator)
6. [Common Errors and Fixes](#common-errors-and-fixes)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)

---

## Why Validation Matters

### Context Integrity

SCDs are the **operating environment** for AI-assisted development. If the context is malformed, inconsistent, or incomplete, AI behavior becomes unpredictable.

**Without validation:**
- ❌ AI tools receive invalid or ambiguous context
- ❌ Relationships break silently
- ❌ Compliance claims can't be verified
- ❌ Governance becomes impossible
- ❌ Teams waste time debugging context errors

**With validation:**
- ✅ Guaranteed syntactic correctness
- ✅ Schema compliance ensures consistency
- ✅ Relationships are verified
- ✅ Compliance can be proven
- ✅ Governance becomes automatable

---

### Governance and Compliance

In regulated industries (healthcare, finance, government), you must **prove** that your system:
- Satisfies all required standards
- Has complete provenance for decisions
- Maintains architectural integrity
- Follows security and compliance requirements

Validation provides the foundation for this proof by ensuring:
- All `satisfies` relationships are valid
- All referenced standards exist
- Provenance is complete
- The compliance graph is intact

---

### Autonomic Agents Depend on Valid Context

Future autonomic governance agents will:
- Continuously monitor compliance status
- Detect architectural drift
- Answer governance questions ("Are we HIPAA compliant?")
- Perform impact analysis

**These agents require validated context** to function reliably. Invalid or inconsistent SCDs will cause governance failures.

---

## What Gets Validated

### SCDs (Individual Documents)

Every SCD is validated for:
- **Syntax** - Valid YAML/JSON
- **Schema** - Matches tier-specific structure
- **Semantics** - Logical consistency (type matches tier, valid versions, etc.)
- **Provenance** - Complete authorship and rationale
- **Relationships** - Valid targets and types (when in a bundle)

### Bundles (Collections of SCDs)

Bundles are validated for:
- **Completeness** - All referenced SCDs exist
- **Uniqueness** - No duplicate IDs
- **Structure** - Valid bundle format
- **Relationships** - All targets exist within the bundle
- **Dependency Graph** - No circular dependencies
- **Coverage** - Required tiers present (meta, project)

---

## The Six Validation Levels

The SCD Validator implements a progressive validation model, from basic syntax to advanced compliance checking.

### Level 1: Syntactic Validation

**Purpose**: Ensure files are valid YAML/JSON

**What it checks:**
- ✅ Valid YAML/JSON syntax
- ✅ Proper indentation
- ✅ Balanced quotes and brackets
- ✅ Correct data types (strings, numbers, arrays, objects)

**Example errors:**
```yaml
# ❌ Bad: Unbalanced quotes
title: "Missing closing quote

# ❌ Bad: Invalid indentation
definition:
name: "Test"

# ✅ Good: Valid YAML
title: "Properly Quoted Title"
definition:
  name: "Test"
```

**When it fails**: File cannot be parsed by YAML/JSON parser

**How to fix**: Use a YAML linter or editor with syntax highlighting

---

### Level 2: Schema Validation

**Purpose**: Ensure SCDs conform to their tier-specific schemas

**What it checks:**
- ✅ All required fields present (`id`, `type`, `title`, `version`, `description`, `provenance`)
- ✅ Field types match schema (string, number, array, object)
- ✅ ID patterns match tier (`scd:meta:*`, `scd:project:*`, `scd:standards:*`)
- ✅ No unexpected fields (in strict mode)

**Example errors:**
```yaml
# ❌ Bad: Missing required field
id: scd:project:security:encryption
type: project
# Missing: version, title, provenance, definition

# ❌ Bad: Wrong type
version: 1.0.0          # Should be string "1.0.0"

# ❌ Bad: ID doesn't match tier
id: scd:meta:security:encryption
type: project           # Type says project, ID says meta

# ✅ Good: All required fields, correct types
id: scd:project:security:encryption
version: "1.0.0"
type: project
domain: security
provenance:
  author: "dev@example.com"
  date: "2025-12-09"
  rationale: "Encryption requirement for HIPAA compliance"
title: "Encryption at Rest"
definition:
  algorithm: "AES-256-GCM"
```

**When it fails**: Required fields missing or wrong types

**How to fix**: Compare against tier-specific schema in `schema/scd/`

---

### Level 3: Semantic Validation

**Purpose**: Ensure logical consistency within individual SCDs

**What it checks:**
- ✅ `type` field matches tier in `id` (e.g., `scd:meta:*` → `type: meta`)
- ✅ Version follows semantic versioning (semver) format
- ✅ ID patterns are consistent and descriptive
- ✅ Provenance fields are complete and meaningful
  - `author` is identifiable (email or name)
  - `date` is ISO8601 format (YYYY-MM-DD)
  - `rationale` is present and non-empty
- ✅ Domain matches one of the 11 prescribed domains

**Example errors:**
```yaml
# ❌ Bad: Type/tier mismatch
id: scd:meta:architecture:pattern
type: project              # Should be 'meta'

# ❌ Bad: Invalid semver
version: "1.0"             # Should be "1.0.0"
version: "v1.0.0"          # No 'v' prefix

# ❌ Bad: Invalid date format
provenance:
  date: "12/9/2025"        # Should be "2025-12-09"

# ❌ Bad: Empty rationale
provenance:
  rationale: ""            # Should explain why

# ✅ Good: Semantically valid
id: scd:meta:architecture:rest-pattern
version: "1.0.0"
type: meta
domain: architecture
provenance:
  author: "architect@example.com"
  date: "2025-12-09"
  rationale: "Define REST API pattern for consistent service design"
```

**When it fails**: Logical inconsistencies or incomplete provenance

**How to fix**: Ensure type matches ID tier, use proper semver, complete provenance

---

### Level 4: Relationship Validation

**Purpose**: Ensure relationships between SCDs are valid

**What it checks:**
- ✅ All relationship targets exist (in bundle context)
- ✅ Relationship types are valid (`satisfies`, `depends-on`, `constrains`, etc.)
- ✅ No orphaned references (targets that don't exist)
- ✅ Dependency graph is acyclic (no circular `depends-on` relationships)
- ✅ Relationship patterns are appropriate for tier combinations

**Example errors:**
```yaml
# ❌ Bad: Target doesn't exist
relationships:
  - type: "satisfies"
    target: "scd:standards:hipaa:164.312"  # This SCD not in bundle

# ❌ Bad: Circular dependency
# scd-a depends on scd-b, scd-b depends on scd-a

# ❌ Bad: Invalid relationship type
relationships:
  - type: "does-something"   # Not a valid type

# ✅ Good: Valid relationship
relationships:
  - type: "satisfies"
    target: "scd:standards:hipaa:164.312"
    description: "Implements HIPAA encryption requirements"
```

**When it fails**: Missing targets, invalid types, circular dependencies

**How to fix**: Ensure all targets exist in bundle, use valid relationship types, avoid cycles

---

### Level 5: Bundle Validation

**Purpose**: Ensure bundles are complete and consistent as a whole

**What it checks:**
- ✅ All SCDs referenced in bundle exist at specified paths
- ✅ No duplicate SCD IDs within bundle
- ✅ At least one meta-tier SCD present
- ✅ At least one project-tier SCD present
- ✅ All relationship targets exist within bundle
- ✅ Import references are valid
- ✅ Bundle metadata is complete (id, version, title, etc.)

**Example errors:**
```yaml
# ❌ Bad: Bundle references non-existent file
includes:
  - path: "context/security/encryption.yaml"  # File doesn't exist

# ❌ Bad: Duplicate IDs
# Two SCDs in bundle both have id: scd:project:security:encryption

# ❌ Bad: No meta-tier SCDs
# Bundle contains only project-tier SCDs

# ❌ Bad: Missing bundle metadata
id: ""                     # Empty bundle ID
version: ""                # Empty version

# ✅ Good: Complete bundle
id: "bundle:project:healthcare-app"
version: "1.0.0"
type: "project"
title: "Healthcare Application Context Bundle"
includes:
  - path: "context/meta/domains.yaml"
  - path: "context/project/security/encryption.yaml"
```

**When it fails**: Missing files, duplicates, incomplete metadata

**How to fix**: Ensure all paths exist, remove duplicates, complete bundle metadata

---

### Level 6: Compliance Validation (Optional/Advanced)

**Purpose**: Validate compliance with standards-tier requirements

**What it checks:**
- ✅ All standards-tier SCDs have corresponding project-tier implementations
- ✅ `satisfies` relationships provide sufficient evidence
- ✅ Compliance coverage is complete (all requirements addressed)
- ✅ Standards are properly versioned and referenced

**Example:**
```yaml
# Standard requirement
id: scd:standards:hipaa:164.312-encryption
definition:
  requirement: "Implement encryption for ePHI in transit"

# Project implementation
id: scd:project:security:tls-config
relationships:
  - type: "satisfies"
    target: "scd:standards:hipaa:164.312-encryption"
    description: "Implements TLS 1.3 for all ePHI transmission"
    evidence:
      - "All API endpoints use TLS 1.3"
      - "Certificate validation enforced"
      - "No fallback to older TLS versions"
```

**When it fails**: Missing implementations, incomplete evidence

**How to fix**: Ensure all standards have `satisfies` relationships from project SCDs

---

## Validation Workflow

### During Development

**Recommended workflow:**

1. **Create SCD** - Start from template
2. **Validate immediately** - `scs-validate my-scd.yaml`
3. **Fix errors** - Iterate until valid
4. **Add to bundle** - Include in bundle manifest
5. **Validate bundle** - `scs-validate --bundle my-bundle.yaml`
6. **Commit** - Once valid, commit to version control

### Before Versioning

Before locking a bundle version:

1. **Full validation** - Run all 5 levels (or 6 if compliance checking)
2. **Strict mode** - Use `--strict` to fail on warnings
3. **Review provenance** - Ensure all rationales are meaningful
4. **Check relationships** - Verify compliance graph is complete
5. **Version and lock** - Increment bundle version, mark as immutable

### Continuous Integration

Add validation to CI/CD pipeline:

```bash
# In your CI script
cd tools/scd-validator
python validate.py --bundle ../../context/bundle.yaml --strict --output json
```

Exit code 0 = valid, non-zero = invalid (fails the build)

---

## Using the SCD Validator

### Installation

```bash
cd tools/scd-validator
pip install -r requirements.txt
```

### Basic Usage

**Validate a single SCD:**
```bash
scs-validate context/meta/roles.yaml
```

**Validate multiple SCDs:**
```bash
scs-validate context/meta/*.yaml
```

**Validate a bundle:**
```bash
scs-validate --bundle context/bundle.yaml
```

### Advanced Options

**Strict mode** (fail on warnings):
```bash
scs-validate --bundle context/bundle.yaml --strict
```

**JSON output** (for CI/CD):
```bash
scs-validate --bundle context/bundle.yaml --output json
```

**Specify schema directory:**
```bash
scs-validate --bundle context/bundle.yaml --schema-dir ./schema
```

**Verbose mode:**
```bash
scs-validate --bundle context/bundle.yaml --verbose
```

### Output Examples

**Success:**
```
SCS Validator v0.2.0

✓ Syntax validation passed (5 files)
✓ Schema validation passed (5 files)
✓ Semantic validation passed (5 files)
✓ Relationship validation passed (5 files)
✓ Bundle validation passed

Summary:
  0 errors
  0 warnings

Status: ✓ VALID
```

**With Errors:**
```
SCS Validator v0.2.0

✓ Syntax validation passed (5 files)
✗ Schema validation failed (1 file)

Errors:
  ✗ context/project/api.yaml - Missing required field 'provenance'
  ✗ context/project/api.yaml - Version must be string, got number

Summary:
  2 errors
  0 warnings

Status: ✗ INVALID
```

**With Warnings:**
```
SCS Validator v0.2.0

✓ Syntax validation passed (3 files)
✓ Schema validation passed (3 files)
✓ Semantic validation passed (3 files)

Warnings:
  ⚠ context/project/api.yaml (scd:project:api) - Provenance 'rationale' is recommended but missing
  ⚠ context/project/db.yaml (scd:project:database) - No relationships defined

Summary:
  0 errors
  2 warnings

Status: ✓ VALID (with warnings)
```

---

## Common Errors and Fixes

### Error: "Missing required field"

**Problem:**
```
✗ context/project/api.yaml - Missing required field 'provenance'
```

**Fix:**
Add the missing field:
```yaml
provenance:
  author: "your-email@example.com"
  date: "2025-12-09"
  rationale: "Why this SCD was created"
```

---

### Error: "Type/tier mismatch"

**Problem:**
```
✗ context/meta/pattern.yaml - Type 'project' doesn't match tier 'meta' in ID
```

**Fix:**
Ensure type matches the tier in the ID:
```yaml
id: scd:meta:architecture:rest-pattern
type: meta    # Must match 'meta' from ID
```

---

### Error: "Invalid semver"

**Problem:**
```
✗ context/project/api.yaml - Version '1.0' is not valid semver
```

**Fix:**
Use proper semantic versioning:
```yaml
version: "1.0.0"  # Must be string with major.minor.patch
```

---

### Error: "Relationship target not found"

**Problem:**
```
✗ context/project/api.yaml - Relationship target 'scd:standards:hipaa:164.312' not found in bundle
```

**Fix:**
Either:
1. Add the missing SCD to the bundle, or
2. Remove/correct the relationship

---

### Error: "Circular dependency detected"

**Problem:**
```
✗ Bundle validation failed - Circular dependency: scd:project:a → scd:project:b → scd:project:a
```

**Fix:**
Redesign the dependency structure to eliminate cycles:
```yaml
# Break the cycle by restructuring relationships
# Option 1: Remove one dependency
# Option 2: Introduce an intermediary SCD
# Option 3: Redesign the architecture
```

---

### Error: "Duplicate SCD ID"

**Problem:**
```
✗ Bundle validation failed - Duplicate ID 'scd:project:security:encryption' found in:
  - context/security/encryption.yaml
  - context/data/encryption.yaml
```

**Fix:**
Rename one of the SCDs to be unique:
```yaml
# Rename to be more specific
id: scd:project:security:transmission-encryption
# or
id: scd:project:data:storage-encryption
```

---

### Warning: "Rationale recommended but missing"

**Problem:**
```
⚠ context/project/api.yaml - Provenance 'rationale' is recommended but missing
```

**Fix:**
Add a meaningful rationale:
```yaml
provenance:
  author: "dev@example.com"
  date: "2025-12-09"
  rationale: "Define REST API structure per architecture review decision ARD-2025-12"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate SCS Bundle

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install validator
        run: |
          cd tools/scd-validator
          pip install -r requirements.txt

      - name: Validate bundle
        run: |
          cd tools/scd-validator
          python validate.py --bundle ../../context/bundle.yaml --strict --output json
```

### GitLab CI Example

```yaml
validate-scs:
  image: python:3.11
  script:
    - cd tools/scd-validator
    - pip install -r requirements.txt
    - python validate.py --bundle ../../context/bundle.yaml --strict
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

cd tools/scd-validator
python validate.py --bundle ../../context/bundle.yaml --strict

if [ $? -ne 0 ]; then
  echo "❌ SCS validation failed. Fix errors before committing."
  exit 1
fi

echo "✅ SCS validation passed"
exit 0
```

---

## Best Practices

### 1. Validate Early and Often
✅ Validate after every SCD change
❌ Wait until the end to validate

**Why**: Catch errors early before they compound

---

### 2. Use Strict Mode for Production
✅ Use `--strict` when validating versioned bundles
❌ Ignore warnings in production bundles

**Why**: Warnings indicate incomplete context that can cause issues

---

### 3. Automate Validation in CI/CD
✅ Add validation to your CI pipeline
❌ Rely on manual validation

**Why**: Prevents invalid bundles from being merged

---

### 4. Fix Provenance First
✅ Ensure complete, meaningful provenance on every SCD
❌ Leave rationale empty or generic

**Why**: Provenance is critical for governance and auditability

---

### 5. Validate Relationships Carefully
✅ Ensure all `satisfies` relationships have evidence
❌ Create relationships without verification

**Why**: Compliance depends on verifiable relationships

---

### 6. Keep Validation Logs
✅ Save validation output for audit purposes
❌ Discard validation results

**Why**: Demonstrates due diligence for compliance

---

## Next Steps

Now that you understand validation:

1. **Try the validator**: Validate some example SCDs
2. **Practice**: Create SCDs and iterate based on validation feedback
3. **Integrate**: Add validation to your development workflow
4. **Automate**: Set up CI/CD validation

---

## Additional Resources

- **[SCD Validator README](../tools/scd-validator/README.md)** - Detailed usage instructions
- **[Validator Technical Overview](../tools/scd-validator/VALIDATOR_OVERVIEW.md)** - Implementation details
- **[SCD Guide](scd-guide.md)** - Understanding SCDs
- **[Bundle Lifecycle](bundle-lifecycle.md)** - How bundles work
- **[JSON Schemas](../schema/)** - Schema definitions for validation
