# Migration Guide: Upgrading to SCS 0.3

**Last Updated:** 2025-12-15

---

## Overview

SCS 0.3 introduces a **multi-domain architecture** that expands SCS beyond software development to support all professional domains (Legal, Clinical, Financial, etc.). This guide helps you migrate existing bundles and SCDs to the new model.

---

## What's New in 0.3

### Five Bundle Types (Previously Four)

**0.2 and earlier:**
- Project, Meta, Standards, Domain (4 types)
- "Domain" meant functional areas like Architecture, Security

**0.3:**
- Project, Meta, Standards, **Concern**, **Domain** (5 types)
- "Concern" = functional areas (Architecture, Security, etc.)
- "Domain" = industry verticals (Software Development, Legal, Clinical)

### Key Changes

1. **Bundle type rename**: What was `type: domain` is now `type: concern`
2. **New domain bundles**: Industry verticals that import concern bundles
3. **Updated hierarchy**: Project → Domains → Concerns → SCDs (was Project → Domains → SCDs)
4. **Domain manifests**: New specification for defining industry domains

---

## Migration Steps

### Step 1: Understand the New Model

**Old Model (0.2):**
```
Project Bundle
├── Meta Bundle
├── Standards Bundle
└── Domain Bundles (Architecture, Security, etc.)
    └── SCDs
```

**New Model (0.3):**
```
Project Bundle
├── Meta Bundle
├── Standards Bundle
└── Domain Bundles (Software Development, Legal, etc.)
    └── Concern Bundles (Architecture, Security, etc.)
        └── SCDs
```

### Step 2: Update Your Bundles

#### Rename Bundle Type: domain → concern

**Before (0.2):**
```yaml
id: bundle:architecture
type: domain
version: "1.0.0"
title: "Architecture Domain Bundle"
imports: []
scds:
  - scd:project:system-context
  - scd:project:tech-stack
```

**After (0.3):**
```yaml
id: bundle:architecture
type: concern
version: "1.0.0"
title: "Architecture Concern Bundle"
imports: []
scds:
  - scd:project:system-context
  - scd:project:tech-stack
```

**Changes:**
- `type: domain` → `type: concern`
- "Domain Bundle" → "Concern Bundle" in comments/descriptions
- "domain bundle" → "concern bundle" in descriptions

#### Update Project Bundle

**Before (0.2):**
```yaml
id: bundle:my-project
type: project
imports:
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  # ... 11 total bundles
scds: []
```

**After (0.3) - Option A: Import software-development domain**
```yaml
id: bundle:my-project
type: project
imports:
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0
  - bundle:software-development:1.0.0  # Imports all 11 concerns
scds: []
```

**After (0.3) - Option B: Import concerns directly**
```yaml
id: bundle:my-project
type: project
imports:
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0
  - bundle:architecture:1.0.0  # Now type: concern
  - bundle:security:1.0.0      # Now type: concern
  # ... still valid in 0.3
scds: []
```

**Recommendation**: Use Option A (import software-development domain) to align with the new architecture.

### Step 3: Create Software Development Domain Bundle (Optional)

If you want to use the new domain model, create a software-development domain bundle:

```yaml
# bundles/domains/software-development.yaml
id: bundle:software-development
type: domain
version: "1.0.0"
title: "Software Development Domain"
description: >
  Software Development domain bundle importing all concern bundles
  relevant to software engineering.

imports:
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  - bundle:performance-reliability:1.0.0
  - bundle:testing-validation:1.0.0
  - bundle:deployment-operations:1.0.0
  - bundle:data-provenance:1.0.0
  - bundle:compliance-governance:1.0.0
  - bundle:usability-accessibility:1.0.0
  - bundle:safety-risk:1.0.0
  - bundle:ethics-ai-accountability:1.0.0
  - bundle:business-context:1.0.0

scds: []

provenance:
  created_by: "your-team@company.com"
  created_at: "2025-12-15T10:00:00Z"
  rationale: "Software Development domain for SCS 0.3 migration"
```

### Step 4: Update Directory Structure

**Before (0.2):**
```
bundles/
├── project-bundle.yaml
├── meta-bundle.yaml
├── standards-bundle.yaml
└── domains/
    ├── architecture.yaml
    ├── security.yaml
    └── ...
```

**After (0.3):**
```
bundles/
├── project-bundle.yaml
├── meta-bundle.yaml
├── standards-bundle.yaml
├── domains/
│   └── software-development.yaml
└── concerns/
    ├── architecture.yaml
    ├── security.yaml
    └── ...
```

**Migration commands:**
```bash
# Create concerns directory
mkdir bundles/concerns

# Move bundle files
mv bundles/domains/*.yaml bundles/concerns/

# Create domains directory (if using domain bundles)
mkdir bundles/domains

# Create software-development domain (if desired)
# (manually create the file as shown in Step 3)
```

### Step 5: Validate Updated Bundles

```bash
cd tools/scd-validator

# Validate concern bundles
python3 -m scs_validator validate --bundle ../../bundles/concerns/architecture.yaml

# Validate domain bundle
python3 -m scs_validator validate --bundle ../../bundles/domains/software-development.yaml

# Validate project bundle
python3 -m scs_validator validate --bundle ../../bundles/project-bundle.yaml
```

---

## Breaking Changes

### 1. Bundle Type Validation

The validator now enforces strict rules for concern and domain bundles:

**Concern bundles (type: concern):**
- MUST NOT import other bundles (`imports` array MUST be empty)
- MUST contain at least one SCD

**Domain bundles (type: domain):**
- MUST import at least one concern bundle
- MUST NOT contain SCDs directly (`scds` array MUST be empty)

### 2. Schema Changes

- `schema/bundles/scd-bundle-schema.json` updated to include `concern` and `domain` types
- New conditional validation rules for concern and domain bundles
- New `schema/domain/domain-manifest-schema.json` for domain definitions

---

## Non-Breaking Changes

### SCDs

**Good news**: SCDs (Structured Context Documents) are unchanged. Your existing SCDs work without modification.

- Meta-tier SCDs: No changes
- Standards-tier SCDs: No changes
- Project-tier SCDs: No changes

### Import Compatibility

Projects can still import concerns directly (not required to use domain bundles):

```yaml
# This still works in 0.3
imports:
  - bundle:architecture:1.0.0  # type: concern
  - bundle:security:1.0.0      # type: concern
```

---

## Frequently Asked Questions

### Do I have to use domain bundles?

No. You can continue importing concern bundles directly in your project bundle. Domain bundles are optional organizational containers.

### Can I keep my old bundle names?

Yes. Bundle IDs like `bundle:architecture` don't need to change—just update the `type` field from `domain` to `concern`.

### Do I need to version my bundles after migration?

If your bundles were already versioned (e.g., `1.0.0`), you should create new versions (e.g., `1.1.0` or `2.0.0`) after updating them to reflect the type change. If they were `DRAFT`, you can update them in place.

### What if I have custom bundles beyond the 11 standard ones?

Follow the same migration:
- If they organize functional areas → `type: concern`
- If they represent industry verticals → `type: domain`

### Can I mix 0.2 and 0.3 bundles?

No. All bundles in a project should use consistent versioning. Complete the migration across all bundles.

---

## Migration Checklist

- [ ] Read and understand the new multi-domain architecture
- [ ] Update bundle files: `type: domain` → `type: concern`
- [ ] Update comments and descriptions
- [ ] Move concern bundles to `bundles/concerns/` directory
- [ ] (Optional) Create software-development domain bundle
- [ ] (Optional) Update project bundle to import domain
- [ ] Validate all bundles with updated validator
- [ ] Update any custom tooling or scripts
- [ ] Update documentation references
- [ ] Test with your workflows

---

## Support

If you encounter issues during migration:

1. Check the [0.3 specification](../spec/0.3/) for detailed documentation
2. Review [example bundles](../examples/bundles/) for reference
3. [Open an issue](https://github.com/tim-mccrimmon/scs-spec/issues) for help
4. [Start a discussion](https://github.com/tim-mccrimmon/scs-spec/discussions) for questions

---

## Next Steps

After completing migration:

1. Explore the [Software Development domain reference](../examples/bundles/domains/software-development.yaml)
2. Consider creating a domain for your industry (if not software)
3. Review the [domain manifest specification](../schema/domain/)
4. Share feedback on the 0.3 release

---

**Happy migrating!** The SCS 0.3 multi-domain architecture opens up structured context to all professional domains.
