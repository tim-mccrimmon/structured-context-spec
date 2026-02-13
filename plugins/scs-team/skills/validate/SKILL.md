---
name: validate
description: Check structure and surface issues for human review. Validates YAML, references, concern coverage, and compilation status.
allowed-tools: Read, Glob, Grep
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-team:validate`. Never auto-invoke based on project state or conversation context.

---

# SCS Team Validate - Structure Check and Review Surface

You are validating the user's structured context and surfacing issues that need human review before versioning.

## Validation Levels

### Level 1: Syntax
- Valid YAML
- Required fields present (id, version, title, description)
- Correct structure

### Level 2: References
- All SCDs referenced in bundles exist
- All bundle imports can be resolved
- No circular dependencies

### Level 3: Consistency
- Version consistency (all DRAFT or all versioned)
- Tier consistency (SCDs in correct tier)
- ID format correctness

### Level 4: Content Quality (Human Review Items)
- Placeholder content detection
- Incomplete sections
- Generic/template text not customized
- TBD items that need resolution

### Level 5: Compilation Check
- Compiled output exists in `.claude/rules/` for each concern with SCDs
- Compiled files have `<!-- scs-team:managed -->` ownership header
- CLAUDE.md has `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers
- Compiled output is not stale (all concerns with SCDs have corresponding rules files)

## Concern Coverage Assessment

Assess coverage across all 11 concerns:

| # | Concern | Expected SCDs |
|---|---------|---------------|
| 1 | Architecture | system-context, tech-stack, integration-map, component-model |
| 2 | Security | authn-authz, data-protection, data-handling, threat-model |
| 3 | Performance & Reliability | response-time, availability, fault-tolerance, scalability |
| 4 | Usability & Accessibility | ux-principles, accessibility-compliance, error-handling-ux |
| 5 | Compliance & Governance | hipaa-compliance, soc2-controls, audit-requirements, policy-enforcement |
| 6 | Data & Provenance | data-model, provenance-tracking, retention-policy |
| 7 | Testing & Validation | test-coverage, validation-plan, qa-procedures |
| 8 | Deployment & Operations | infrastructure-definition, observability, incident-response |
| 9 | Safety & Risk | risk-assessment, safety-checklist |
| 10 | Ethics & AI Accountability | ai-usage-policy, audit-trail, model-bias |
| 11 | Business Context | problem-definition, stakeholders, business-objectives, opportunity-analysis, constraints-and-assumptions, success-criteria |

## Your Process

### Step 1: Find All Artifacts

Scan for:
- `.scs/project.yaml`
- `.scs/concerns/*.yaml`
- `.scs/scds/*.yaml`
- `.claude/rules/*.md`
- `CLAUDE.md`

### Step 2: Run Structural Checks (Levels 1-3)

For each file:
1. Parse YAML (catch syntax errors)
2. Check required fields
3. Validate ID format
4. Check version format

Build a reference map:
1. Map all SCD IDs
2. For each bundle, verify all referenced SCDs exist
3. For each import, verify bundle exists
4. Detect circular dependencies

### Step 3: Check Content Quality (Level 4)

Flag things that need human attention:
- Content marked "TBD" or "TODO"
- Very short descriptions (< 50 chars)
- Generic titles ("Example", "Template", "Placeholder")
- Standards SCDs that need customization
- Areas critical for the project type that are missing

### Step 4: Check Compilation (Level 5)

Verify compiled output:
- For each concern bundle with SCDs, check if `.claude/rules/<concern>.md` exists
- Verify `<!-- scs-team:managed -->` header is present in each managed file
- Check CLAUDE.md for `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers
- Identify any `.claude/rules/` files without the managed header (developer-owned)
- Flag if any concern has SCDs but no compiled output

### Step 5: Provide Clear Report

Separate:
- **Errors** - Must fix before versioning
- **Warnings** - Should review before versioning
- **Human Review** - Needs human judgment
- **Compilation** - Status of compiled output

## Output Format

```
## SCS Validation Report

### Summary
- Files scanned: 12
- Errors: 2
- Warnings: 3
- Human review items: 5
- Compilation: Out of sync

### Errors (Must Fix)

1. **Invalid YAML** - `.scs/scds/tech-stack.yaml:15`
   - Indentation error at line 15
   - Fix: Check YAML indentation

2. **Missing Reference** - `bundle:architecture`
   - References `scd:project:component-model` but file not found
   - Fix: Create the SCD or remove the reference

### Warnings (Should Review)

1. **Inconsistent Versions** - `bundle:my-project`
   - Bundle is DRAFT but imports versioned bundles
   - Consider: Version the bundle or use DRAFT imports

2. **Very Short Description** - `scd:project:stakeholders`
   - Description is only 12 characters
   - Consider: Add more detail

### Human Review Required

These items need your judgment:

1. **TBD Item** - `.scs/scds/system-context.yaml:23`
   - `shipping_api: "TBD - not decided yet"`
   - Question: Has the shipping API been decided?

2. **Needs Customization** - `.scs/scds/hipaa-phi-handling.yaml`
   - PHI locations not specified (currently using standard template)
   - Action: Identify where PHI exists in your system

3. **Missing Critical Context** - Security
   - No security-related SCDs found
   - Question: Is security context needed for this project?

### Concern Coverage
| # | Concern | SCDs | Status |
|---|---------|------|--------|
| 1 | Architecture | 2/4 | Partial |
| 2 | Security | 0/4 | Missing |
| 3 | Performance & Reliability | 0/4 | Missing |
| 4 | Usability & Accessibility | 0/3 | Missing |
| 5 | Compliance & Governance | 3/4 | Partial |
| 6 | Data & Provenance | 0/3 | Missing |
| 7 | Testing & Validation | 0/3 | Missing |
| 8 | Deployment & Operations | 0/3 | Missing |
| 9 | Safety & Risk | 0/2 | Missing |
| 10 | Ethics & AI Accountability | 0/3 | Missing |
| 11 | Business Context | 2/6 | Partial |

### Compilation Status

| Check | Status |
|-------|--------|
| .claude/rules/ exists | Yes |
| Managed files present | 2 of 3 expected |
| Missing compilation | business concern (has SCDs but no rules file) |
| CLAUDE.md markers | Present |
| Unmanaged rules files | 1 (my-custom-rules.md - developer-owned, untouched) |

### Ready to Version?

**Not yet.**

Before running `/scs-team:version`:
1. Fix 2 errors
2. Review 3 warnings
3. Address 5 human review items (or explicitly accept them)
4. Recompile: run any modifying command to trigger compilation

Run `/scs-team:validate` again after fixes.
```

## Clean Validation

If everything passes:

```
## SCS Validation Report

### Summary
- Files scanned: 12
- Errors: 0
- Warnings: 0
- Human review items: 0
- Compilation: In sync

### All Checks Passed

Your structured context is valid and ready for versioning.

### Before You Version

Even though validation passed, consider:
- Have stakeholders reviewed the content?
- Is anything still in flux that shouldn't be locked yet?
- Are you ready to commit to these decisions?

When ready: `/scs-team:version`
```

## Philosophy

**Validation checks STRUCTURE, not COMPLETENESS.**

We don't fail validation because you're missing security context - that's your choice. We DO flag it for human review so you can make an informed decision.

The goal is:
1. Catch real errors (broken YAML, missing references)
2. Surface things that need human judgment
3. Verify compilation is in sync
4. Let you decide what's acceptable for YOUR project
