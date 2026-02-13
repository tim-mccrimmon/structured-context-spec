---
name: version
description: Lock bundles with semantic versioning. Guides through version selection, updates files, and integrates with git.
allowed-tools: Read, Glob, Grep, Write, Bash(git status), Bash(git add *), Bash(git commit *), Bash(git tag *)
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-team:version`. Never auto-invoke based on project state or conversation context.
- **Confirm before writing**: Present the full versioning plan (which bundles, which version numbers, git actions) and get explicit user confirmation before modifying any files.

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

### Step 5: Recompile to Claude Code Format

After versioning, recompile `.scs/` source to `.claude/rules/` output to reflect the new version:

1. Read all SCDs in `.scs/scds/` and all concern bundles in `.scs/concerns/`
2. For each concern that has SCDs:
   a. Compress the SCD content to actionable rules (constraints, boundaries, patterns - NOT documentation)
   b. Target 300-500 tokens per concern file
   c. Write to `.claude/rules/<concern-name>.md`
   d. Add header: `<!-- scs-team:managed -->` and footer with source SCD attribution including version
3. Generate/update the scs-team section in CLAUDE.md:
   a. If CLAUDE.md exists, find `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers
   b. If markers exist, replace content between them
   c. If no markers, append the section at the end
   d. If no CLAUDE.md, create one with the markers
   e. Content: project overview, architecture summary, quick reference table, links to rules files
   f. Include the version number in the section header
4. **Only overwrite files with `<!-- scs-team:managed -->` header** - leave other `.claude/rules/` files untouched

### Step 6: Git Integration

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

### Step 7: Report Completion

Tell the user:
1. What was versioned
2. What `.claude/rules/` files were recompiled
3. Git actions taken (if any)
4. Next steps

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
- `.scs/project.yaml` → 1.0.0
- 8 SCDs updated to 1.0.0

**Recompiled:**
- `.claude/rules/architecture.md`
- `.claude/rules/security.md`
- `.claude/rules/compliance.md`
- Updated CLAUDE.md scs-team section (v1.0.0)

**Git actions:**
- Staged all changes
- Created commit: "chore(scs): version context to 1.0.0"
- Created tag: scs-v1.0.0

**Next steps:**
- Push to remote: `git push && git push --tags`
- Your context is now locked at version 1.0.0
- Future changes should create version 1.1.0 or 2.0.0
```

## Handling Issues

**Validation failures**: Don't version. Report issues and suggest `/scs-team:validate`.

**Unresolved TBDs**: Warn the user but allow them to proceed if they acknowledge.

**Git not available**: Skip git integration, just update files.

**Partial versioning**: If user only wants to version some bundles, respect that but warn about dependency issues.
