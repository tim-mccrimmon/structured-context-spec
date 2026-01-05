# SCS Validator Rules

This directory contains the configuration-driven validation rules for the SCS validator.

## Philosophy

**"Strict by Default, Flexible by Configuration"**

The validator ships with strict, production-ready default rules while enabling projects to customize validation for their specific needs.

## Rules Files

### v0.1.0/ - Current Rules Version

```
v0.1.0/
├── scd-rules.yaml              # SCD structure validation rules
├── bundle-rules.yaml           # Bundle organization and XOR constraints
├── relationship-rules.yaml     # 7 relationship types and tier constraints
└── completeness-rules.yaml     # Domain and SCD completeness requirements
```

### Rules File Descriptions

**scd-rules.yaml**
- ID pattern validation
- Type-tier matching
- Version format rules
- Required fields
- DRAFT vs VERSIONED mode behavior
- Stub detection

**bundle-rules.yaml**
- XOR constraint (bundles contain imports OR scds, not both)
- Bundle type-specific rules (project, meta, domain, standards)
- Import/SCD resolution
- Cross-bundle relationships
- Meta bundle version pinning

**relationship-rules.yaml**
- 7 relationship types (depends-on, satisfies, constrains, refines, extends, conflicts-with, implements)
- Tier constraints (which tiers can relate to which)
- Directionality rules
- Circular dependency detection
- Target existence validation

**completeness-rules.yaml**
- 11 prescribed domains
- Recommended SCDs per domain
- Stub detection
- Compliance validation
- **This file can be customized by projects**

## Customizing Validation Rules

### Option 1: Project-Specific Rules (Recommended)

Create `.scs/completeness-rules.yaml` in your project root:

```bash
mkdir -p .scs
cp $VALIDATOR_RULES_DIR/v0.1.0/completeness-rules.yaml .scs/

# Edit .scs/completeness-rules.yaml to customize
```

**Example: Minimal rules for POC**
```yaml
# .scs/completeness-rules.yaml
version: "0.1.0"
description: "Minimal rules for proof-of-concept"
profile: "minimal"

severity: "warning"  # Permissive

required_bundles:
  - type: "meta"
    count: 1

required_domains:
  - id: "architecture"
    name: "Architecture"
    minimum_scds: 1

  - id: "security"
    name: "Security"
    minimum_scds: 1

  - id: "testing-validation"
    name: "Testing & Validation"
    minimum_scds: 1

stub_detection:
  enabled: false  # Don't check for stubs in POC
```

### Option 2: Explicit Rules File

Specify a custom rules file:

```bash
scs-validate --bundle bundle.yaml --completeness-rules my-custom-rules.yaml
```

### Option 3: Skip Completeness Validation

Skip Level 6 validation entirely:

```bash
scs-validate --bundle bundle.yaml --skip-completeness
```

## Rule Loading Priority

1. **Explicit flag** (highest priority)
   ```bash
   --completeness-rules path/to/rules.yaml
   ```

2. **Project-specific**
   ```
   .scs/completeness-rules.yaml
   ```

3. **Default** (fallback)
   ```
   validator/rules/v0.1.0/completeness-rules.yaml
   ```

## Common Customization Scenarios

### Early-Stage Project

**Need**: Focus on core domains, skip completeness for now

**Solution**:
```yaml
# .scs/completeness-rules.yaml
severity: "warning"
required_domains:
  - id: "architecture"
    minimum_scds: 1
  - id: "security"
    minimum_scds: 1
  - id: "testing-validation"
    minimum_scds: 1
```

Or use:
```bash
scs-validate --bundle bundle.yaml --skip-completeness
```

### Non-UI System

**Need**: Remove usability-accessibility domain

**Solution**:
```yaml
# .scs/completeness-rules.yaml
required_domains:
  # Include all 10 except usability-accessibility
  - id: "architecture"
  - id: "security"
  - id: "performance-reliability"
  # - id: "usability-accessibility"  # Removed
  - id: "compliance-governance"
  - id: "data-provenance"
  - id: "testing-validation"
  - id: "deployment-operations"
  - id: "safety-risk"
  - id: "ethics-ai-accountability"
```

### Non-AI System

**Need**: Remove AI-specific domain

**Solution**: Similar to above, remove `ethics-ai-accountability`

### Internal Tool (Non-Compliance)

**Need**: Relax compliance validation

**Solution**:
```yaml
# .scs/completeness-rules.yaml
compliance_validation:
  enabled: true
  severity: "warning"  # Changed from "error"
```

### Enterprise with Custom Domains

**Need**: Add organization-specific domains

**Solution**:
```yaml
# .scs/completeness-rules.yaml
required_domains:
  # ... all 10 standard domains ...
  - id: "legal-compliance"
    name: "Legal & Compliance"
    description: "Legal requirements and IP management"
    minimum_scds: 1
  - id: "cost-management"
    name: "Cost Management"
    description: "Cloud costs and resource optimization"
    minimum_scds: 1
```

## Validation Flags

```bash
# Standard validation (uses default or project rules)
scs-validate --bundle bundle.yaml

# Skip completeness validation
scs-validate --bundle bundle.yaml --skip-completeness

# Extra strict (warnings become errors)
scs-validate --bundle bundle.yaml --strict

# Custom completeness rules
scs-validate --bundle bundle.yaml --completeness-rules minimal-rules.yaml

# JSON output for CI/CD
scs-validate --bundle bundle.yaml --output json
```

## Rules File Format

### Structure

All rules files follow this structure:

```yaml
version: "0.1.0"  # Rules version
description: "Description of what this file contains"

# Rule definitions...

# Error messages
error_messages:
  rule_name: "Template message with {placeholders}"
```

### Patterns

**ID Patterns**: Use regex
```yaml
pattern: "^scd:(meta|standards|project):[a-zA-Z0-9._-]+$"
```

**Recommended SCD Patterns**: Use simplified patterns (converted to regex)
```yaml
pattern: "auth|authn|authz"  # Matches SCDs with these keywords
```

### Severity Levels

- `error` - Validation fails, blocks commit/CI
- `warning` - Validation passes with warnings
- `info` - Informational only
- `skip` - Don't run this check

## Versioning

Rules are versioned alongside the validator.

**Current version**: v0.1.0
**Compatible with**: SCS v0.1

When the validator updates rules:
- Patch version (0.1.0 → 0.1.1): Bug fixes, clarifications
- Minor version (0.1.0 → 0.2.0): New rules, backward compatible
- Major version (0.1.0 → 1.0.0): Breaking changes to rules

Projects should test validation after updating the validator.

## Contributing

To propose changes to default rules:

1. Create an issue in the SCS repository
2. Provide rationale and use cases
3. Include example rules YAML
4. Community discussion period
5. RFC and implementation

See: `docs/issue-*.md` for discussion topics

## Related Documentation

- `docs/scs-v0.1-design-decisions.md` - Canonical design decisions
- `docs/issue-*.md` - Discussion topics with decisions
- `context/meta/validator-meta.yaml` - Validation levels specification

## Questions?

See the validator documentation in `tools/scd-validator/README.md`
