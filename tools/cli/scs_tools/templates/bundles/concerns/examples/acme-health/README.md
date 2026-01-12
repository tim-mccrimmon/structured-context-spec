# Acme Health Corp - Company-Context Example

This directory contains a **complete working example** of a company-context concern bundle for Acme Health Corp (a fictional healthcare technology company).

## Purpose

This example demonstrates:
1. How to structure a company-overview SCD
2. How to create a company-context concern bundle
3. The "Open CEO" approach (full disclosure)

## Files

```
acme-health/
├── scds/
│   └── company-overview.yaml       # Company context SCD
├── bundles/
│   └── company-context.yaml        # Concern bundle (DRAFT)
└── README.md                        # This file
```

## About Acme Health Corp

**Fictional Company Profile**:
- **Name**: Acme Health Corp
- **Founded**: 2018
- **Industry**: Healthcare Technology
- **Size**: 250 employees
- **Focus**: AI-powered patient engagement and adherence solutions
- **Business Model**: B2B SaaS for health systems and payers

## Using This Example

### To Copy as a Starting Point

```bash
# Copy the entire example
cp -r cli/scs_tools/templates/bundles/concerns/examples/acme-health \
      my-company

# Rename and customize
cd my-company
# Edit scds/company-overview.yaml with your company info
# Edit bundles/company-context.yaml with your company name
```

### To Validate

```bash
# Validate the SCD
python -m scs_validator \
  cli/scs_tools/templates/bundles/concerns/examples/acme-health/scds/company-overview.yaml

# Validate the bundle
scs validate \
  cli/scs_tools/templates/bundles/concerns/examples/acme-health/bundles/company-context.yaml
```

## Customization Guide

### 1. Update Company Information

In `scds/company-overview.yaml`, replace:
- Company name ("Acme Health Corp" → your company)
- Founded year, headquarters, size
- Industry and focus area
- All content fields with your company's information

### 2. Update Bundle ID

In `bundles/company-context.yaml`, replace:
- `bundle:acme-company-context` → `bundle:your-company-context`
- Title and description
- Provenance information

### 3. Adjust Disclosure Level

You can remove or add fields based on your disclosure preferences:

**Minimal Disclosure** (Paranoid CEO):
- Keep only `company_info.name` and `company_info.industry`
- Remove mission, vision, values, stakeholders, business_model, strategic_priorities

**Moderate Disclosure**:
- Keep company_info, mission, vision, values
- Remove stakeholders and strategic_priorities

**Full Disclosure** (Open CEO):
- Keep all fields (as shown in this example)

## Design Choices in This Example

1. **Single SCD**: All company context in one `company-overview.yaml`
   - Simpler to manage
   - Atomic versioning
   - Can split later if needed

2. **Full Disclosure**: Includes all recommended fields
   - Demonstrates what's possible
   - Shows the "Open CEO" approach
   - Provides maximum context to AI

3. **Project-Tier SCDs**: Uses `scd:project:*` tier
   - Company-specific, not universal (not meta)
   - Not regulatory (not standards)
   - Applies to all company projects

## Next Steps

1. **Test with your data**: Replace Acme Health info with your company
2. **Validate**: Run validation to ensure structure is correct
3. **Version**: When ready, version at 1.0.0
4. **Create Domain Bundle**: Import this concern in your domain bundle

## Related Test Case

See the full test case walkthrough:
`/test-plan/concerns/company-concern/TC-001-company-context-acme.md`

## Questions?

- Review the README: `../README-company-context.md`
- Check the test plan: `/test-plan/test-plan.md` (Phase 0)
- See bundle format spec: `/base/spec/0.3/bundle-format.md`
