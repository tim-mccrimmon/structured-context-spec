---
name: draft
description: Conversational drafting for a specific concern area when documentation doesn't exist. Ask targeted questions and generate draft SCDs.
argument-hint: "<concern: architecture|security|performance|usability|compliance|data|testing|deployment|safety|ethics|business>"
allowed-tools: Read, Glob, Grep, Write, Bash(mkdir -p *)
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-team:draft`. Never auto-invoke based on project state or conversation context.
- **Confirm before writing**: After the conversation, present a summary of the SCDs you plan to generate and the files you'll create/modify. Get explicit user confirmation before writing any files.

---

# SCS Team Draft - Conversational Context Creation

You are helping the user create structured context for a specific concern area through conversation. Use this when they don't have existing documentation.

## The 11 Concerns

| # | Concern | Slug | What It Covers |
|---|---------|------|----------------|
| 1 | Architecture | `architecture` | System structure, components, boundaries, tech stack |
| 2 | Security | `security` | Auth, data protection, threats, access control |
| 3 | Performance & Reliability | `performance` | Response times, availability, fault tolerance, scaling |
| 4 | Usability & Accessibility | `usability` | UX principles, accessibility, error handling patterns |
| 5 | Compliance & Governance | `compliance` | Regulatory requirements, audit, governance |
| 6 | Data & Provenance | `data` | Data models, data flow, retention, provenance |
| 7 | Testing & Validation | `testing` | Test strategy, coverage requirements, validation approach |
| 8 | Deployment & Operations | `deployment` | Infrastructure, CI/CD, environments, monitoring |
| 9 | Safety & Risk | `safety` | Risk assessments, safety checklists, mitigation strategies |
| 10 | Ethics & AI Accountability | `ethics` | AI usage policies, bias detection, audit trails |
| 11 | Business Context | `business` | Problem definition, stakeholders, objectives, success criteria |

## Your Process

### Step 1: Understand Current State

Before asking questions:
- Check what context already exists (`.scs/` directory)
- Scan the codebase to understand what's already built
- Note any existing patterns or choices

### Step 2: Ask Targeted Questions

Ask questions specific to the concern area. Be conversational, not interrogative.

**Architecture Questions**:
- "What's the high-level structure? Monolith, microservices, serverless?"
- "What are the 3-5 main components and what does each do?"
- "What external systems does this integrate with?"
- "What's your primary data store? Any caching, queues, etc.?"
- "Are there any architectural patterns you're following? (Event sourcing, CQRS, etc.)"

**Security Questions**:
- "How do users authenticate? (OAuth, JWT, sessions, etc.)"
- "What's the authorization model? (RBAC, ABAC, simple roles?)"
- "What sensitive data does this system handle?"
- "Are there any known threat vectors you're concerned about?"
- "What security controls are already in place?"

**Performance & Reliability Questions**:
- "What response time targets do you have? (p50, p95, p99?)"
- "What's your availability target? (99.9%, 99.99%?)"
- "How do you handle failures? Circuit breakers, retries, fallbacks?"
- "What's your scaling strategy? Horizontal, vertical, auto-scaling?"
- "Are there traffic patterns you need to plan for? (Spikes, seasonal?)"

**Usability & Accessibility Questions**:
- "Who are the primary users and what are their technical skill levels?"
- "Are there accessibility requirements? (WCAG level, Section 508?)"
- "What are the key UX principles for this project?"
- "How should errors be presented to users?"
- "Are there any specific device or browser requirements?"

**Compliance Questions**:
- "What regulations apply? (HIPAA, SOC2, GDPR, PCI, etc.)"
- "Are there audit requirements? What needs to be logged?"
- "Who is responsible for compliance decisions?"
- "Are there data residency requirements?"

**Data Questions**:
- "What are the core data entities?"
- "Where does data come from? Where does it go?"
- "What are the retention requirements?"
- "Is there sensitive/PII data? Where does it live?"

**Testing Questions**:
- "What's your testing strategy? (Unit, integration, E2E?)"
- "What coverage targets do you have?"
- "Are there critical paths that must always be tested?"
- "How do you validate before releasing?"

**Deployment Questions**:
- "Where does this run? (AWS, GCP, Azure, on-prem, hybrid?)"
- "How does code get from commit to production?"
- "What environments exist? (dev, staging, prod?)"
- "How do you monitor the system? What alerts exist?"
- "What's the incident response process?"

**Safety & Risk Questions**:
- "What are the highest-impact things that could go wrong?"
- "Are there safety-critical operations? (Healthcare decisions, financial transactions?)"
- "What risk mitigations are in place?"
- "Are there regulatory safety requirements?"

**Ethics & AI Accountability Questions**:
- "Does this project use AI/ML? In what capacity?"
- "How do you detect and handle bias in AI outputs?"
- "Is there a human-in-the-loop for AI decisions?"
- "What audit trail exists for AI-generated recommendations?"
- "Are there AI usage policies or guidelines to follow?"

**Business Questions**:
- "In one sentence, what problem does this solve?"
- "Who are the primary users? What do they need?"
- "What does success look like? How will you measure it?"
- "What are the key constraints or assumptions?"

### Step 3: Push Back on Vague Answers

If answers are too vague, ask for specifics:

- "You said 'a database' - which one? Postgres, MySQL, MongoDB?"
- "What do you mean by 'standard auth'? OAuth? JWT? Session cookies?"
- "When you say 'microservices', how many? What are they?"

### Step 4: Generate Draft SCDs

Based on the conversation, generate SCDs with version: "DRAFT".

**Be honest about gaps**:
- If something wasn't discussed, mark it as "TBD" or "Needs input"
- Don't invent details that weren't provided
- Flag areas that need follow-up

**Update concern bundle**: After creating SCDs, update the relevant `.scs/concerns/<concern>.yaml` to include the new SCDs in its `scds:` array.

### Step 5: Compile to Claude Code Format

After creating/modifying SCDs, compile the `.scs/` source to `.claude/rules/` output:

1. Read all SCDs in `.scs/scds/` and all concern bundles in `.scs/concerns/`
2. For each concern that has SCDs:
   a. Compress the SCD content to actionable rules (constraints, boundaries, patterns - NOT documentation)
   b. Target 300-500 tokens per concern file
   c. Write to `.claude/rules/<concern-name>.md`
   d. Add header: `<!-- scs-team:managed -->` and footer with source SCD attribution
3. Generate/update the scs-team section in CLAUDE.md:
   a. If CLAUDE.md exists, find `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers
   b. If markers exist, replace content between them
   c. If no markers, append the section at the end
   d. If no CLAUDE.md, create one with the markers
   e. Content: project overview, architecture summary, quick reference table, links to rules files
4. For SCDs with `applies_to.paths` that reference sensitive data (PHI, PCI):
   a. Add YAML frontmatter with `paths:` to the compiled `.claude/rules/` file
5. **Only overwrite files with `<!-- scs-team:managed -->` header** - leave other `.claude/rules/` files untouched

### Step 6: Summarize and Suggest Next Steps

After generating:
1. Summarize what was created
2. Note what's still missing
3. Show what was compiled to `.claude/rules/`
4. Suggest other concerns to draft or documents to add

## Example Interaction

User: `/scs-team:draft architecture`

You: "Let's document your architecture. I'll ask a few questions to understand the structure.

First - what's the high-level shape? Is this a monolith, microservices, serverless, or something hybrid?"

User: "It's a monolith right now but we're planning to break out some services"

You: "Got it - monolith with planned decomposition. What's the tech stack? Framework, language, database?"

User: "Python FastAPI, Postgres, Redis for caching"

You: "Nice stack. What are the main modules or domains within the monolith? The 3-5 big pieces?"

User: "Users, Orders, Inventory, and Notifications"

You: "And which of those are candidates for breaking out into services?"

User: "Notifications for sure, maybe Inventory"

You: "Last question - what external systems does this integrate with? Payment processor, shipping, etc.?"

User: "Stripe for payments, SendGrid for email, we're planning to add a shipping API"

You: "Got it. Let me generate the architecture context...

**Generated SCDs:**

1. `system-context.yaml` - Boundaries and external integrations
2. `component-model.yaml` - The 4 domains and their responsibilities
3. `tech-stack.yaml` - FastAPI, Postgres, Redis specifics

**Updated Bundles:**
- `concerns/architecture.yaml` - Added 3 SCDs

**Compiled to Claude Code:**
- `.claude/rules/architecture.md` - Architecture rules and constraints

**Flagged as TBD:**
- Which shipping API (not decided yet)
- Timeline for service decomposition
- Data flow between components

**Suggested Next:**
- `/scs-team:draft deployment` - How this gets deployed
- `/scs-team:draft data` - Data models and flow

Run `/scs-team:status` to see the full picture."

## Tone

- Be conversational, not interrogative
- Acknowledge their answers before asking the next question
- If they don't know something, that's fine - mark it as TBD
- Keep momentum - don't let it feel like a checklist
