# Domain-Agnostic Bundle Format Updates

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Executive Summary

This document defines updates to the SCS bundle format to support pluggable domains. The goal is to make bundles domain-agnostic while maintaining full backwards compatibility with existing bundles.

**Key Changes:**
- Add optional `domain` field to bundles
- SCDs inherit domain from parent bundle
- Update validation to be domain-aware
- Maintain backwards compatibility (default to `domain:software-development`)

**Design Principle:** Minimal changes, maximum backwards compatibility.

---

## 2. Current vs. New Bundle Structure

### 2.1 Current Bundle (Domain-Unaware)

```yaml
id: bundle:medication-adherence
type: project
version: "1.0.0"
title: "Medication Adherence System"
description: "Complete context bundle"

imports:
  - bundle:meta:1.0.0
  - bundle:architecture:1.0.0

scds:
  - scd:project:system-context
  - scd:project:tech-stack

provenance:
  created_by: "tim@example.com"
  created_at: "2025-12-12T10:00:00Z"
```

**Problem:** Implicitly assumes software development domain. Content schemas are hardcoded.

### 2.2 New Bundle (Domain-Aware)

```yaml
id: bundle:patient-care-system
type: project
version: "1.0.0"
domain: "domain:healthcare"  # NEW FIELD
title: "Patient Care System"
description: "Complete context bundle for patient care workflow system"

imports:
  - bundle:meta:1.0.0
  - bundle:architecture:1.0.0

scds:
  - scd:project:care-pathways
  - scd:project:patient-data-flows

provenance:
  created_by: "tim@example.com"
  created_at: "2025-12-12T10:00:00Z"
```

**Solution:** Explicit `domain` field. SCDs validated against healthcare domain schemas.

---

## 3. Bundle Changes Specification

### 3.1 New Field: `domain`

**Field Name:** `domain`
**Type:** `string`
**Pattern:** `^domain:[a-z][a-z0-9-]*$`
**Required:** No (optional for backwards compatibility)
**Default:** `domain:software-development` (if not specified)
**Description:** Specifies which domain's content schemas to use for validation

**Examples:**
- `domain:software-development` - Software development domain (default)
- `domain:healthcare` - Healthcare domain
- `domain:sales` - Sales and marketing domain
- `domain:finance` - Finance and accounting domain

### 3.2 Domain Field Semantics

**At Bundle Level:**
- When specified, applies to ALL SCDs in that bundle
- Affects which content schemas are used for validation
- Determines which templates are available
- Must reference an installed domain

**Inheritance:**
- SCDs within a bundle inherit the bundle's domain
- SCDs CAN override with their own `domain` field (rare)
- Imported bundles maintain their own domain settings

---

## 4. Updated Bundle Schema

### 4.1 Schema Changes

Add the `domain` property to the bundle schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ohana-scs.org/schema/bundle.schema.json",
  "title": "SCS Bundle",
  "description": "Schema for SCS Bundle manifests with multi-domain support.",
  "type": "object",
  "required": ["id", "type", "version", "title", "description", "imports", "scds", "provenance"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^bundle:[a-zA-Z0-9._-]+$"
    },
    "type": {
      "type": "string",
      "enum": ["project", "meta", "standards", "domain"]
    },
    "domain": {
      "type": "string",
      "pattern": "^domain:[a-z][a-z0-9-]*$",
      "description": "Domain this bundle belongs to (e.g., domain:healthcare, domain:sales). Defaults to domain:software-development if not specified."
    },
    "version": {
      "type": "string",
      "pattern": "^(\\d+\\.\\d+\\.\\d+|DRAFT)$"
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string",
      "minLength": 1
    },
    "imports": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^bundle:[a-zA-Z0-9._-]+(:[0-9]+\\.[0-9]+\\.[0-9]+)?$"
      }
    },
    "scds": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^scd:(meta|standards|project):[a-zA-Z0-9._-]+$"
      }
    },
    "provenance": {
      "type": "object",
      "required": ["created_by", "created_at"],
      "properties": {
        "created_by": { "type": "string" },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_by": { "type": "string" },
        "updated_at": { "type": "string", "format": "date-time" },
        "rationale": { "type": "string" }
      }
    }
  },
  "additionalProperties": false
}
```

### 4.2 Validation Rules

**New Validation Rules:**

1. If `domain` is specified, it MUST reference an installed domain
2. All SCDs in the bundle MUST be valid according to the domain's schemas
3. Imported bundles MAY have different domains
4. Domain field is optional (backwards compatibility)

---

## 5. Domain Inheritance and Resolution

### 5.1 Domain Inheritance Flow

```
Bundle
  └─ domain: "domain:healthcare"
       ├─ SCD 1 → inherits domain:healthcare
       ├─ SCD 2 → inherits domain:healthcare
       └─ SCD 3 (domain: "domain:software-development") → overrides
```

### 5.2 Resolution Algorithm

```python
def resolve_scd_domain(scd: Dict, bundle: Dict, config: Config) -> str:
    """
    Resolve the domain for an SCD.

    Resolution order:
    1. SCD's own domain field (rare override)
    2. Parent bundle's domain field
    3. Project configuration domain
    4. Global configuration default_domain
    5. Hardcoded default (domain:software-development)
    """
    # 1. SCD explicit domain
    if "domain" in scd:
        return scd["domain"]

    # 2. Bundle domain
    if "domain" in bundle:
        return bundle["domain"]

    # 3. Project config
    if config.project and "domain" in config.project:
        return config.project["domain"]

    # 4. Global config
    if config.global_config and "default_domain" in config.global_config.get("scs", {}):
        return config.global_config["scs"]["default_domain"]

    # 5. Hardcoded default
    return "domain:software-development"
```

---

## 6. Backwards Compatibility Strategy

### 6.1 Compatibility Guarantees

**Existing bundles MUST continue to work unchanged.**

**How this is achieved:**

1. **`domain` field is optional** - Old bundles don't need it
2. **Default domain is software-development** - Matches current behavior
3. **Validation unchanged for default domain** - Uses existing schemas
4. **No breaking changes to structure** - All existing fields remain valid

### 6.2 Migration Paths

**Option 1: No Migration Required (Recommended)**
```yaml
# Existing bundle continues to work
id: bundle:my-app
type: project
version: "1.0.0"
# No domain field - defaults to domain:software-development
```

**Option 2: Explicit Migration (Optional)**
```yaml
# Add domain field for clarity
id: bundle:my-app
type: project
version: "1.0.0"
domain: "domain:software-development"  # Explicit
```

**Option 3: Domain Change (For new domains)**
```yaml
# Change to different domain
id: bundle:my-healthcare-app
type: project
version: "1.0.0"
domain: "domain:healthcare"  # New domain
```

### 6.3 Validation Compatibility

```python
# OLD validator (pre-domain support)
validate_bundle(bundle_path)

# NEW validator (with domain support)
# Still works the same for existing bundles
validate_bundle(bundle_path)  # Uses domain:software-development by default

# Explicit domain
validate_bundle(bundle_path, domain="domain:healthcare")
```

---

## 7. Terminology Clarification

**IMPORTANT:** The term "domain" is overloaded in the current spec. We need to clarify:

### 7.1 Current Terminology Issue

In the existing bundle format spec, "domain bundle" refers to **subject area bundles** like:
- Architecture bundle
- Security bundle
- Performance bundle
- etc.

These are NOT the same as the new multi-domain concept.

### 7.2 New Terminology

**Going Forward:**

| Term | Meaning |
|------|---------|
| **Domain** | Industry/function context provider (healthcare, sales, finance) |
| **Bundle Type: `domain`** | Subject area bundle (architecture, security, etc.) |
| **Domain Field** | Specifies which industry domain to use |

**Bundle Types (unchanged):**
- `project` - Top-level bundle
- `meta` - Foundational vocabulary
- `standards` - Compliance requirements
- `domain` - Subject area (architecture, security, etc.)

**New Domain Field:**
- Specifies industry/function (healthcare, sales, etc.)
- Orthogonal to bundle type

### 7.3 Example Showing Both Concepts

```yaml
# A "domain" bundle (type=domain, subject area=architecture)
# For the healthcare domain (field domain=domain:healthcare)

id: bundle:architecture
type: domain                      # Bundle type (subject area)
domain: "domain:healthcare"       # Industry domain (NEW)
version: "1.0.0"
title: "Healthcare Architecture Bundle"

scds:
  - scd:project:care-pathway-architecture
  - scd:project:clinical-integration-map
```

This bundle is:
- Type: `domain` (subject area bundle - architecture)
- Domain: `domain:healthcare` (industry context)

---

## 8. Bundle Validation Updates

### 8.1 Validation Pipeline

```python
class BundleValidator:
    """
    Validates bundles with domain awareness.
    """

    def __init__(self, domain_loader: DomainLoader):
        self.domain_loader = domain_loader

    def validate_bundle(self, bundle: Dict[str, Any]) -> ValidationResult:
        """
        Validate a bundle.

        Steps:
        1. Structural validation (domain-agnostic)
        2. Domain resolution
        3. Load domain
        4. Validate all SCDs against domain schemas
        5. Validate imports
        6. Check relationships
        """
        result = ValidationResult()

        # 1. Structural validation
        structural = self._validate_structure(bundle)
        result.merge(structural)

        if structural.has_errors():
            return result

        # 2. Resolve domain
        domain_id = bundle.get("domain", "domain:software-development")

        # 3. Load domain
        try:
            domain = self.domain_loader.load_domain(domain_id)
        except DomainNotFoundError:
            result.add_error(f"Domain not found: {domain_id}")
            return result

        # 4. Validate SCDs
        for scd_ref in bundle.get("scds", []):
            # Load SCD
            scd = self._load_scd(scd_ref)

            # Validate against domain
            scd_result = domain.validate_scd_content(scd)
            result.merge(scd_result)

        # 5. Validate imports
        for import_ref in bundle.get("imports", []):
            import_result = self._validate_import(import_ref)
            result.merge(import_result)

        return result
```

### 8.2 Cross-Domain Validation

When a bundle imports bundles from different domains:

```yaml
id: bundle:my-project
type: project
domain: "domain:healthcare"

imports:
  - bundle:architecture:1.0.0  # Inherits healthcare
  - bundle:sales-integration:1.0.0  # Could be sales domain
```

**Validation Strategy:**
1. Each imported bundle validated against its own domain
2. Cross-domain relationships validated separately
3. Warnings for potential incompatibilities

---

## 9. SCD Changes

### 9.1 Optional Domain Field in SCDs

SCDs get the same optional `domain` field:

```yaml
id: scd:project:care-pathways
type: project
domain: "domain:healthcare"  # OPTIONAL - usually inherited from bundle
title: "Clinical Care Pathways"
version: "1.0.0"
description: "Care pathways for chronic disease management"

content:
  # Healthcare-specific content
  clinical_workflows: [...]
  patient_populations: [...]

relationships: [...]
provenance: {...}
```

### 9.2 Domain Override (Rare Case)

An SCD can override its bundle's domain:

```yaml
# In bundle with domain:healthcare
id: scd:project:payment-processing
type: project
domain: "domain:finance"  # Override - use finance domain instead
title: "Payment Processing"
# ...
```

**Use case:** Mixed-domain systems where some components belong to different domains.

---

## 10. Multi-Domain Projects

### 10.1 Single Domain (Most Common)

```yaml
# Patient Care System - Pure healthcare
id: bundle:patient-care
type: project
domain: "domain:healthcare"

imports:
  - bundle:architecture:1.0.0    # Healthcare architecture
  - bundle:security:1.0.0        # Healthcare security
```

All SCDs use healthcare schemas.

### 10.2 Multi-Domain (Advanced)

```yaml
# Healthcare + Sales Integration
id: bundle:patient-engagement-platform
type: project
domain: "domain:healthcare"  # Primary domain

imports:
  # Healthcare bundles
  - bundle:clinical-workflows:1.0.0

  # Sales/Marketing bundle (different domain)
  - bundle:marketing-automation:1.0.0  # Uses domain:sales
```

**Validation:**
- Each bundle validated against its own domain
- Cross-domain SCDs can reference each other
- Potential incompatibilities flagged as warnings

### 10.3 Domain Boundaries

**Best Practice:** Keep domain boundaries clean

```
bundle:patient-care (domain:healthcare)
  ├─ bundle:clinical (domain:healthcare)
  ├─ bundle:pharmacy (domain:healthcare)
  └─ bundle:billing (domain:finance)      ← Clear boundary
```

---

## 11. Implementation Plan

### 11.1 Phase 1: Schema Updates

- [ ] Update `schema/bundles/scd-bundle-schema.json` - Add `domain` field
- [ ] Update `schema/scd/base-scd-schema.json` - Add `domain` field
- [ ] Create migration guide
- [ ] Update existing example bundles (optional domain field)

### 11.2 Phase 2: Validator Updates

- [ ] Implement domain resolution in validator
- [ ] Add domain loader integration
- [ ] Update validation pipeline
- [ ] Add backwards compatibility tests

### 11.3 Phase 3: Documentation

- [ ] Update bundle format specification
- [ ] Update SCD guide
- [ ] Create multi-domain examples
- [ ] Document migration paths

### 11.4 Phase 4: Testing

- [ ] Test backwards compatibility (old bundles still work)
- [ ] Test single domain scenarios
- [ ] Test multi-domain scenarios
- [ ] Test domain inheritance
- [ ] Test validation with different domains

---

## 12. Examples

### 12.1 Healthcare Bundle

```yaml
id: bundle:ehr-system
type: project
version: "1.0.0"
domain: "domain:healthcare"
title: "Electronic Health Record System"
description: "Complete EHR system context"

imports:
  - bundle:meta:1.0.0
  - bundle:hipaa-compliance:1.0.0
  - bundle:architecture:1.0.0

scds:
  - scd:project:patient-workflows
  - scd:project:clinical-data-model
  - scd:project:hl7-integration

provenance:
  created_by: "clinical-architect@hospital.com"
  created_at: "2025-12-12T10:00:00Z"
```

### 12.2 Sales Bundle

```yaml
id: bundle:crm-system
type: project
version: "1.0.0"
domain: "domain:sales"
title: "Customer Relationship Management System"
description: "Complete CRM system context"

imports:
  - bundle:meta:1.0.0
  - bundle:architecture:1.0.0

scds:
  - scd:project:sales-pipeline
  - scd:project:customer-journey
  - scd:project:lead-scoring

provenance:
  created_by: "sales-ops@company.com"
  created_at: "2025-12-12T10:00:00Z"
```

### 12.3 Software Development Bundle (Backwards Compatible)

```yaml
# Existing bundle - works unchanged
id: bundle:web-application
type: project
version: "1.0.0"
# NO domain field - defaults to domain:software-development
title: "Web Application"
description: "Standard web app"

imports:
  - bundle:meta:1.0.0
  - bundle:architecture:1.0.0

scds:
  - scd:project:system-context
  - scd:project:tech-stack

provenance:
  created_by: "dev@company.com"
  created_at: "2025-12-12T10:00:00Z"
```

---

## 13. Error Handling

### 13.1 Domain Not Found

```
ERROR: Domain 'domain:healthcare' not found.

To install this domain:
  scs domain install healthcare

To use a different domain:
  Edit bundle.yaml and change 'domain' field

To use the default domain:
  Remove 'domain' field from bundle.yaml
```

### 13.2 Domain Validation Failure

```
ERROR: SCD content validation failed for domain:healthcare

File: context/project/care-pathways.yaml
Field: content.clinical_workflows
Error: Required property 'patient_population' missing

Domain Schema: ~/.scs/domains/healthcare/schemas/project-content-schema.json
See: https://docs.scs.com/domains/healthcare
```

### 13.3 License Required

```
ERROR: Domain 'domain:healthcare' requires a valid license.

Status: Not licensed
Required: Commercial license

To activate:
  scs domain activate healthcare --license-key YOUR-KEY

To purchase a license:
  Visit: https://scs-commercial.com/domains/healthcare
```

---

## 14. Migration Guide

### 14.1 For Existing Projects

**Do Nothing (Recommended)**
- Existing bundles continue to work
- Default to `domain:software-development`
- No changes required

**Add Explicit Domain (Optional)**
```bash
# Add to existing bundle
domain: "domain:software-development"
```

**Switch to New Domain**
1. Install new domain: `scs domain install healthcare`
2. Add domain field: `domain: "domain:healthcare"`
3. Update SCD content to match new domain schemas
4. Validate: `scs validate bundle.yaml`

### 14.2 For New Projects

```bash
# Create new project with specific domain
scs init --domain healthcare --template ehr-system

# Or manually
scs domain set healthcare
scs new bundle my-project
```

---

## 15. Open Questions

1. **Domain Version Pinning**: Should bundles specify domain version?
   ```yaml
   domain: "domain:healthcare:1.0.0"  # With version?
   ```

2. **Cross-Domain References**: How strict should validation be?
   - Allow freely? (permissive)
   - Warn? (informative)
   - Error? (strict)

3. **Domain Registry Resolution**: Should bundle validation fetch domains from registry if not installed locally?

4. **Domain Migration**: Should we provide automated migration tools for switching domains?

---

## 16. Next Steps

1. Review and approve this design
2. Update bundle and SCD schemas
3. Implement validation changes
4. Create test cases
5. Update documentation
6. Test backwards compatibility

---

*This design ensures SCS bundles can support multiple domains while maintaining 100% backwards compatibility with existing bundles.*
