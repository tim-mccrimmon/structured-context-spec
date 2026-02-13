---
name: validate
description: Check your CLAUDE.md for completeness and issues. Identifies missing sections, stale references, and gaps that might bite you later.
allowed-tools: Read, Glob, Grep
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-vibe:validate`. Never auto-invoke based on project state or conversation context.

---

# SCS Vibe Validate - Check Your Context

You are validating the user's structured context (CLAUDE.md) for completeness, accuracy, and usefulness.

## What You're Checking

### 1. Existence and Location
- Does CLAUDE.md exist in project root?
- Is there a user-level ~/.claude/CLAUDE.md?
- Are there any .claude/ directory configurations?

### 2. Required Sections

**Critical (warn if missing):**
- System Overview / What This Is
- Tech Stack
- Architecture / Key Components
- Constraints

**Recommended (suggest if missing):**
- Patterns We Use
- Patterns We Avoid
- Domain Context
- Development Guidelines

### 3. Content Quality

**Check for generic/placeholder content:**
- "[Project Name]" not replaced
- "[Description]" placeholders
- Sections with only template text

**Check for specificity:**
- Tech stack should name specific versions/tools
- Patterns should reference actual files
- Constraints should have concrete reasons

### 4. Stale References

**Verify referenced files/directories exist:**
- File paths mentioned in CLAUDE.md
- Directory structure descriptions
- Code examples or links

**Check for outdated patterns:**
- Technologies mentioned that aren't in package.json/requirements.txt
- Patterns described that don't match current code

### 5. Completeness for Context Type

**If healthcare template detected:**
- PHI locations documented?
- Audit logging mentioned?
- Compliance contacts listed?

**If fintech template detected:**
- Compliance requirements documented?
- Transaction handling patterns?

## Output Format

Provide a clear report:

```
## SCS Context Validation Report

### Summary
- Overall Status: [Good / Needs Work / Critical Issues]
- CLAUDE.md Location: [path]
- Last Modified: [if detectable]

### Critical Issues
[List any critical problems that should be fixed immediately]

### Warnings
[List issues that should be addressed]

### Suggestions
[List nice-to-have improvements]

### What's Good
[Acknowledge what's working well]

### Recommended Actions
1. [Most important fix]
2. [Second priority]
3. [Third priority]
```

## Example Interaction

User: `/scs-vibe:validate`

You: "Let me check your context..."

[Read CLAUDE.md and scan project]

You:
```
## Context Check

### Status: Needs Work
- Location: ./CLAUDE.md
- Lines: 45

### Issues
1. **No Constraints section** - Claude won't know the boundaries
2. **Vague tech stack** - Says "PostgreSQL" but not how it's accessed

### Suggestions
1. Add "Patterns We Avoid" - stops Claude from repeating mistakes
2. `/src/api` is mentioned but doesn't exist (stale?)

### What's Good
- Clear system overview
- Specific file paths for key components

### Quick Fixes
1. Add 2-3 constraints Claude should respect
2. Be specific: "PostgreSQL 15 via Prisma ORM"
3. Remove or fix the /src/api reference
```

Want me to help fix any of these?
