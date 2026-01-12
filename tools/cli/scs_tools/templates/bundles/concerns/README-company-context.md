# Company-Context Concern Bundle

## Overview

The **company-context** concern is a special concern bundle type that contains company-specific information that doesn't fit in other concerns like Architecture, Security, or Performance.

**Owner**: CEO (Chief Executive Officer)

**Purpose**: Provide business and organizational context to AI services working on company projects

**Contains**: Company overview, mission, vision, values, stakeholders, business model, strategic priorities

---

## What Goes in Company-Context?

Company-context should include information about **WHO the company is** and **HOW the company operates**, not technical details (those go in other concerns).

### Typical Contents

- **Company Overview**: Name, industry, size, founding, headquarters
- **Mission & Vision**: Why the company exists and where it's going
- **Core Values**: Principles that guide company decisions and culture
- **Key Stakeholders**: Leadership team and decision-makers
- **Business Model**: How the company makes money and delivers value
- **Strategic Priorities**: Current focus areas (optional, consider sensitivity)

### What Does NOT Go Here

- **Technical Architecture** → Goes in Architecture concern
- **Security Controls** → Goes in Security concern
- **Data Schemas** → Goes in Data Provenance concern
- **Compliance Rules** → Goes in Standards bundles (HIPAA, SOC2, etc.)

---

## Ownership Model

| Bundle | Owner | Relationship |
|--------|-------|--------------|
| **Company-Context Concern** | CEO | Creates and maintains |
| **Domain Bundle** | CEO | Imports company-context + other concerns |
| **Project Bundles** | Product Managers | Import domain bundle (get company-context transitively) |

The CEO owns both:
1. The **Company-Context Concern Bundle** (this concern)
2. The **Domain Bundle** (which imports this concern plus others)

---

## Validation Philosophy: Loose Validation

Company-context uses **loose validation** to support different levels of disclosure:

### What Validation Checks (Structure)
✅ YAML is well-formed
✅ Bundle type is `concern`
✅ Required bundle fields exist (`id`, `type`, `version`, `scds`, `imports`)
✅ `imports` array is empty (concern bundles don't import)
✅ `scds` array has at least one SCD
✅ SCD files exist and are well-formed

### What Validation Does NOT Check (Content)
❌ Does NOT require specific fields in company_info
❌ Does NOT enforce mission/vision statements
❌ Does NOT require stakeholder information
❌ Does NOT validate field completeness

### Why Loose Validation?

Every company is different, and CEOs have different comfort levels with disclosure:

- **Open CEO**: Shares full context (mission, values, stakeholders, strategy, business model)
- **Moderate CEO**: Shares mission and values, basic company info (skips stakeholders, strategy)
- **Paranoid CEO**: Only shares name and industry (minimal disclosure)

**All three approaches are valid** and will pass validation.

---

## File Structure

```
company-context-concern/
├── scds/
│   └── company-overview.yaml       # Main company context SCD
└── bundles/
    └── company-context-bundle.yaml # Concern bundle referencing SCD
```

**Alternative (Multi-SCD Approach)**:
```
company-context-concern/
├── scds/
│   ├── company-overview.yaml       # Basic company info
│   ├── company-values.yaml         # Core values
│   ├── stakeholders.yaml           # Leadership team
│   └── business-model.yaml         # Business operations
└── bundles/
    └── company-context-bundle.yaml # References all SCDs
```

---

## Quick Start Guide

### Step 1: Copy Templates

```bash
# Copy SCD template
cp cli/scs_tools/templates/scds/company-overview.yaml \
   my-company/scds/company-overview.yaml

# Copy bundle template
cp cli/scs_tools/templates/bundles/concerns/company-context.yaml \
   my-company/bundles/company-context-bundle.yaml
```

### Step 2: Fill in Company Information

Edit `my-company/scds/company-overview.yaml`:
- Update `id` with your company name
- Fill in `company_info` (at minimum: name and industry)
- Add mission, vision, values as desired
- Include stakeholders if appropriate
- Describe business model if needed
- **Remember**: All fields are optional - share what makes sense

### Step 3: Update Bundle Reference

Edit `my-company/bundles/company-context-bundle.yaml`:
- Update `id` with your company name
- Update `scds` array to reference your SCD
- Update provenance information

### Step 4: Validate

```bash
# Validate SCD
python -m scs_validator my-company/scds/company-overview.yaml

# Validate bundle
scs validate my-company/bundles/company-context-bundle.yaml
```

### Step 5: Version

```bash
# Version at 1.0.0 when ready
scs bundle version my-company/bundles/company-context-bundle.yaml --version 1.0.0
```

### Step 6: Deploy (Future)

```bash
# Deploy to MCP server
scs deploy my-company/bundles/bundle-company-context-1.0.0.yaml \
  --to mcp-prod-01 --version 1.0.0
```

---

## Design Decisions

### Single vs. Multiple SCDs

**Option A: Single SCD** (Recommended for most)
- One `company-overview.yaml` with all company context
- **Pros**: Simpler, atomic versioning, easier to manage
- **Cons**: Can't selectively share different aspects
- **Good for**: Most companies, initial implementation

**Option B: Multiple SCDs**
- Separate SCDs for overview, values, stakeholders, business-model
- **Pros**: Granular control, independent versioning, selective sharing
- **Cons**: More files to manage, more complex
- **Good for**: Large organizations with sensitive information

**Recommendation**: Start with Option A, split later if needed.

### Required vs. Optional Fields

All fields in the company-overview SCD are **optional** by design.

**Why?**
- Support spectrum from paranoid to open CEOs
- Every company is different
- CEO controls disclosure level
- Flexibility for future evolution

**Minimum recommended fields**:
- `company_info.name`
- `company_info.industry`

Everything else is based on CEO's comfort level and AI's needs.

---

## Examples

### Example 1: Minimal Disclosure (Paranoid CEO)

```yaml
id: scd:project:company-overview
type: project
title: "Acme Corp - Company Overview"
version: "0.1.0"

content:
  company_info:
    name: "Acme Corp"
    industry: "Technology"

provenance:
  created_by: "CEO <ceo@acme.com>"
  created_at: "2025-12-26T10:00:00Z"
  rationale: "Minimal company context"
```

### Example 2: Full Disclosure (Open CEO)

```yaml
id: scd:project:company-overview
type: project
title: "Acme Health - Company Overview"
version: "0.1.0"

content:
  company_info:
    name: "Acme Health Corp"
    founded: "2018"
    headquarters: "San Francisco, CA"
    industry: "Healthcare Technology"
    size: "250 employees"
    focus: "AI-powered patient engagement"

  mission: >
    Improve patient health outcomes through intelligent technology

  vision: >
    A world where every patient has personalized health support

  core_values:
    - value: "Patient-First"
      description: "Every decision starts with patient impact"
    - value: "Evidence-Based"
      description: "Ground solutions in clinical evidence"

  key_stakeholders:
    - role: "CEO"
      name: "Dr. Sarah Chen"
      background: "Physician, healthcare innovation expert"

  business_model:
    model_type: "B2B SaaS"
    target_customers: "Health systems and payers"
    pricing: "Per-patient-per-month"

provenance:
  created_by: "Dr. Sarah Chen <sarah@acmehealth.com>"
  created_at: "2025-12-26T10:00:00Z"
  source_documents:
    - "https://acmehealth.com/about"
  rationale: "Comprehensive company context for AI services"
```

Both examples **pass validation** because all fields are optional!

---

## FAQ

**Q: Is company-context required for every project?**
A: No, but recommended. If you skip it, AI services won't have company-specific context.

**Q: Can I add custom fields not in the template?**
A: Yes! The template is a starting point. Add any fields relevant to your company.

**Q: What if my company structure doesn't fit the template?**
A: Modify the template to fit your needs. Validation checks structure, not content.

**Q: Should I include confidential information?**
A: Only share what you're comfortable with AI services seeing. Consider what helps AI make better decisions vs. what's sensitive.

**Q: How often should I update company-context?**
A: Update when significant changes occur (new mission, leadership changes, strategic shifts). Version incrementally (1.0.0 → 1.1.0 for additions, 2.0.0 for major changes).

**Q: Can different projects use different versions of company-context?**
A: Yes, through versioning. Project A might use company-context:1.0.0 while Project B uses :1.1.0.

---

## Related Documentation

- **Test Plan**: `/test-plan/test-plan.md` - Phase 0: Company-Context Concern
- **Test Case**: `/test-plan/concerns/company-concern/TC-001-company-context-acme.md`
- **Bundle Format Spec**: `/base/spec/0.3/bundle-format.md`
- **Concern Bundles**: `/cli/scs_tools/templates/bundles/concerns/`

---

## Support

For questions or issues with company-context concerns:
1. Review the test case: TC-001-company-context-acme.md
2. Check validation errors: `scs validate --help`
3. Review bundle format spec: `/base/spec/0.3/bundle-format.md`
