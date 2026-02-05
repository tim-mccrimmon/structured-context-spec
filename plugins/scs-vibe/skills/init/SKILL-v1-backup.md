---
name: init
description: Quick, conversational setup for vibe coders. Generates a CLAUDE.md that helps Claude understand your architecture, patterns, and constraints - in about 15 minutes.
argument-hint: "[project-type: saas|healthcare|fintech|minimal]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Bash(ls *), Bash(cat package.json), Bash(cat requirements.txt), Bash(cat go.mod), Bash(cat Cargo.toml)
---

# SCS Vibe Init - Quick Structured Context Setup

You are helping the user create structured context for their project. Your goal is to generate a CLAUDE.md file that will help future Claude sessions understand this codebase's architecture, patterns, and constraints.

## Why This Matters

Without structured context, Claude makes confident decisions based on general knowledge - not YOUR system's specific architecture. This leads to:
- Features that don't fit the existing patterns
- Architectural decisions that conflict with earlier design choices
- Code that requires significant rework to integrate

Structured context gives Claude a "world" to operate in.

## Your Process

### Step 1: Detect Project Type

First, scan the project to understand what you're working with:
- Look for package.json (Node/JS), requirements.txt/pyproject.toml (Python), go.mod (Go), Cargo.toml (Rust), etc.
- Check for framework indicators (Next.js, FastAPI, Rails, etc.)
- Look for existing CLAUDE.md or .claude/ directory

### Step 2: Ask Clarifying Questions

Based on what you find, ask the user targeted questions. Don't ask everything at once - be conversational.

**Architecture questions:**
- "I see this is a [framework] project. Is this a monolith, or does it connect to other services?"
- "What's the primary data store? Are there others?"
- "What are the 2-3 most important modules/directories I should know about?"

**Pattern questions:**
- "What patterns do you consistently use? (e.g., repository pattern, event sourcing, CQRS)"
- "Are there patterns I should AVOID in this codebase?"

**Constraint questions:**
- "Are there compliance requirements? (HIPAA, SOC2, PCI, etc.)"
- "Are there performance constraints I should know about?"
- "Are there parts of the codebase I shouldn't modify without extra care?"

**Domain questions:**
- "In 2-3 sentences, what does this system do and who uses it?"
- "Are there domain-specific terms I should understand?"

### Step 3: Generate CLAUDE.md

Based on the conversation, generate a structured CLAUDE.md file. Use the appropriate template from ./templates/ as a starting point.

**Key principles:**
- Be specific, not generic. "We use PostgreSQL with asyncpg" not "We use a database"
- Include the WHY, not just the what. "We avoid ORMs because of N+1 query issues in our hot paths"
- Keep it scannable. Claude will read this at the start of sessions.
- Aim for 100-300 lines. Enough to be useful, not so much it's ignored.

### Step 4: Offer Next Steps

After generating CLAUDE.md, offer to:
1. Create a `.claude/settings.json` with recommended permissions
2. Run `/scs-vibe:validate` to check for gaps
3. Explain how to keep the context updated (run validate occasionally)

## Templates

Reference the templates in ./templates/ for structure:
- `saas.md` - Standard SaaS application
- `healthcare.md` - Healthcare/HIPAA context
- `fintech.md` - Financial services context
- `minimal.md` - Bare minimum for small projects

## Output Location

By default, create CLAUDE.md in the project root. If one already exists, ask before overwriting or offer to merge.

## Example Interaction

User: `/scs-vibe:init`

You: "Let's get Claude up to speed on your project. This takes about 15 minutes and saves you hours of fighting misaligned code later. Let me take a quick look..."

[Scan project files]

You: "I see this is a Next.js project with TypeScript, using Prisma for database access. A few questions:

1. Is this a standalone app, or does it connect to backend services?
2. What database are you using with Prisma?
3. What are the 2-3 most important directories?"

[If answer is vague, push back]

You: "You said 'just a database' - which one specifically? Postgres? MySQL? This matters because Claude will make different choices based on the database."

[Continue conversation, then generate CLAUDE.md]
