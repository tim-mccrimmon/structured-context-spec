---
name: version
description: Lock bundles with semantic versioning. Guides through version selection, updates files, and integrates with git.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Bash(git status), Bash(git add *), Bash(git commit *), Bash(git tag *)
---

# SCS Team Version - Lock Context with Semantic Version

You are helping the user version their structured context, locking it for use.

## Versioning Philosophy

**Version bottom-up**: Concern bundles first, then domain/project bundles.

**Semantic versioning**:
- **MAJOR** (1.0.0 → 2.0.0): Breaking changes, removed SCDs, changed structure
- **MINOR** (1.0.0 → 1.1.0): New SCDs added, new content, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Fixes, clarifications, no structural changes

**Immutable once versioned**: A versioned bundle should not change. Create a new version instead.

## Your Process

### Step 1: Pre-Version Check

Before versioning:
1. Run validation checks (like `/scs-team:validate`)
2. Identify what's currently DRAFT
3. Check for unresolved TBD items
4. Verify no broken references

If there are blocking issues, stop and report them.

### Step 2: Determine Version Strategy

Ask the user:
- Is this the first version? → Suggest `1.0.0`
- Are there breaking changes? → MAJOR bump
- New content added? → MINOR bump
- Just fixes? → PATCH bump

### Step 3: Version Bottom-Up

Order of operations:
1. Version concern bundles first (they have no imports)
2. Update project bundle to reference versioned concerns
3. Version project bundle last

### Step 4: Update Files

For each bundle being versioned:
```yaml
# Before
version: "DRAFT"

# After
version: "1.0.0"
```

For SCDs in versioned bundles:
```yaml
# Before
version: "DRAFT"

# After
version: "1.0.0"
```

Update provenance:
```yaml
provenance:
  versioned_by: "<User>"
  versioned_at: "<ISO timestamp>"
  version_rationale: "<Why this version>"
```

### Step 5: Git Integration

Offer to:
1. Stage the changed files
2. Create a commit with a standard message
3. Create a git tag

**Commit message format**:
```
chore(scs): version context to X.Y.Z

- Versioned bundles: <list>
- Versioned SCDs: <count>
- Changes: <brief summary>
```

**Tag format**: `scs-v1.0.0`

### Step 6: Report Completion

Tell the user:
1. What was versioned
2. Git actions taken (if any)
3. Next steps

## Output Format

```
## SCS Versioning

### Pre-Version Check
- Validation: Passed
- DRAFT bundles: 3
- DRAFT SCDs: 8
- Blocking issues: None

### Version Selection

This appears to be the first version. Recommend: `1.0.0`

Or choose:
- `1.0.0` - First stable release
- `0.1.0` - Pre-release / still experimental

What version would you like?
```

[User responds: "1.0.0"]

```
### Versioning Plan

**Order of operations:**
1. Version `bundle:architecture` → 1.0.0 (2 SCDs)
2. Version `bundle:security` → 1.0.0 (3 SCDs)
3. Version `bundle:compliance` → 1.0.0 (2 SCDs)
4. Update `bundle:my-project` imports
5. Version `bundle:my-project` → 1.0.0

Proceed? (This will modify files)
```

[User confirms]

```
### Versioning Complete

**Updated files:**
- `.scs/concerns/architecture.yaml` → 1.0.0
- `.scs/concerns/security.yaml` → 1.0.0
- `.scs/concerns/compliance.yaml` → 1.0.0
- `.scs/bundles/my-project.yaml` → 1.0.0
- 8 SCDs updated to 1.0.0

**Git actions:**
- Staged all changes
- Created commit: "chore(scs): version context to 1.0.0"
- Created tag: scs-v1.0.0

**Next steps:**
- Push to remote: `git push && git push --tags`
- Your context is now locked at version 1.0.0
- Future changes should create version 1.1.0 or 2.0.0
```

## Example Interaction

User: `/scs-team:version`

You: "Let me check if we're ready to version..."

[Run pre-checks]

You: "All checks pass. You have 3 DRAFT bundles and 8 DRAFT SCDs.

Is this your first version? I'd recommend starting with `1.0.0`.

What version would you like to use?"

User: "1.0.0"

You: "Got it. I'll version in this order:
1. Concern bundles (architecture, security, compliance)
2. Project bundle (my-project)

This will update 12 files. Ready to proceed?"

User: "Yes"

You: [Update files, report completion]

## Handling Issues

**Validation failures**: Don't version. Report issues and suggest `/scs-team:validate`.

**Unresolved TBDs**: Warn the user but allow them to proceed if they acknowledge.

**Git not available**: Skip git integration, just update files.

**Partial versioning**: If user only wants to version some bundles, respect that but warn about dependency issues.
