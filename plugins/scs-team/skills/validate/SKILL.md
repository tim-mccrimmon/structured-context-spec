---
name: validate
description: Check structure and surface issues for human review. Validates YAML, references, and flags areas needing attention before versioning.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
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

## Your Process

### Step 1: Find All Artifacts

Scan for:
- `.scs/bundles/*.yaml`
- `.scs/scds/*.yaml`
- `.scs/concerns/*.yaml`
- Any YAML files with SCS structure

### Step 2: Run Structural Checks

For each file:
1. Parse YAML (catch syntax errors)
2. Check required fields
3. Validate ID format
4. Check version format

### Step 3: Check References

1. Build a map of all IDs
2. For each bundle, verify all referenced SCDs exist
3. For each import, verify bundle exists
4. Detect circular dependencies

### Step 4: Surface Human Review Items

Flag things that need human attention:
- Content marked "TBD" or "TODO"
- Very short descriptions (< 50 chars)
- Generic titles ("Example", "Template", "Placeholder")
- Standards SCDs that need customization
- Areas critical for the project type that are missing

### Step 5: Provide Clear Report

Separate:
- **Errors** - Must fix before versioning
- **Warnings** - Should review before versioning
- **Human Review** - Needs human judgment

## Output Format

```
## SCS Validation Report

### Summary
- Files scanned: 12
- Errors: 2
- Warnings: 3
- Human review items: 5

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

2. **Needs Customization** - `.scs/scds/hipaa-controls.yaml`
   - PHI locations not specified (currently placeholder)
   - Action: Identify where PHI exists in your system

3. **Missing Critical Context** - Security
   - No security-related SCDs found
   - Question: Is security context needed for this project?

4. **Incomplete Section** - `.scs/scds/tech-stack.yaml`
   - `infrastructure:` section is empty
   - Action: Add infrastructure details or remove section

5. **Generic Content** - `.scs/scds/constraints.yaml`
   - Contains "Example constraint" text
   - Action: Replace with actual constraints

### Ready to Version?

**Not yet.**

Before running `/scs-team:version`:
1. Fix 2 errors
2. Review 3 warnings
3. Address 5 human review items (or explicitly accept them)

Run `/scs-team:validate` again after fixes.
```

## Example Interaction

User: `/scs-team:validate`

You: [Run validation and present report]

## Clean Validation

If everything passes:

```
## SCS Validation Report

### Summary
- Files scanned: 12
- Errors: 0
- Warnings: 0
- Human review items: 0

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
3. Let you decide what's acceptable for YOUR project
