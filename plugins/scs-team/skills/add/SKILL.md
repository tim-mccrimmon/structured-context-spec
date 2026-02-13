---
name: add
description: Process a document (PRD, architecture doc, security requirements, etc.) into structured context. Extracts relevant information and generates appropriate SCDs.
argument-hint: "<file-path>"
allowed-tools: Read, Glob, Grep, Write, Bash(mkdir -p *)
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-team:add`. Never auto-invoke based on project state or conversation context.
- **Confirm before writing**: After analyzing the document, present a summary of the SCDs you plan to generate and the files you'll create/modify. Get explicit user confirmation before writing any files.

---

# SCS Team Add - Process Document into Structured Context

You are helping the user transform an existing document into structured context that Claude can use.

## Your Process

### Step 1: Read and Analyze the Document

First, read the document the user provided:
- Identify the document type (PRD, MRD, architecture, security, compliance, etc.)
- Understand its structure and content
- Note which of the 11 concerns it addresses

### Step 2: Identify Extractable Information

Based on the document type, look for:

**PRD / MRD (Product/Market Requirements)**:
- Problem definition
- Target users/stakeholders
- Success criteria / KPIs
- Business objectives
- Constraints and assumptions

**Architecture Documents**:
- System context and boundaries
- Component model
- Technology stack
- Integration points
- Data flow

**Security Requirements**:
- Authentication/authorization approach
- Data protection requirements
- Threat considerations
- Access control model

**Compliance Documents**:
- Regulatory requirements
- Audit requirements
- Policy constraints

**Performance / SLA Documents**:
- Response time targets
- Availability requirements
- Scalability approach
- Fault tolerance strategy

**UX / Design Documents**:
- Design principles
- Accessibility requirements
- Error handling patterns

**Operational / Runbooks**:
- Infrastructure definition
- Monitoring approach
- Incident response procedures

**Risk / Safety Documents**:
- Risk assessments
- Safety checklists
- Mitigation strategies

**AI / Ethics Documents**:
- AI usage policies
- Bias detection approach
- Audit trail requirements

### Step 3: Map to Concerns

Map extracted information to the 11 concern areas:

| # | Concern | SCDs |
|---|---------|------|
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

### Step 4: Generate SCDs

Create Structured Context Documents (SCDs) in YAML format.

**SCD Structure**:
```yaml
id: scd:project:<name>
version: "DRAFT"
title: "<Title>"
description: "<Brief description>"
tier: project

content:
  # Structured content extracted from document

provenance:
  created_by: "<User or document source>"
  created_at: "<ISO timestamp>"
  source_document: "<Original document path>"
  rationale: "Extracted from <document type>"
```

### Step 5: Place Files and Update Bundles

1. Create `.scs/scds/` directory if it doesn't exist
2. Name files descriptively: `problem-definition.yaml`, `system-context.yaml`, etc.
3. **Update the relevant concern bundle** in `.scs/concerns/` to include the new SCD in its `scds:` array
   - If the concern bundle doesn't exist, create it following the standard format

### Step 6: Compile to Claude Code Format

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

### Step 7: Report What Was Created

Tell the user:
1. What document type was detected
2. What SCDs were generated
3. What concern bundles were updated
4. What `.claude/rules/` files were compiled
5. What might be missing or need human review

## Guidelines

**Be specific, not generic**:
- Extract actual details from the document
- Don't generate placeholder content
- If something isn't in the document, note it as missing

**Preserve intent**:
- Keep the meaning from the source document
- Don't invent requirements that aren't there
- Flag ambiguities for human review

**Structure for Claude**:
- Organize information so Claude can quickly understand constraints
- Highlight boundaries and limits
- Make patterns and anti-patterns explicit

## Example Interaction

User: `/scs-team:add ./docs/PRD.md`

You: "Let me analyze this document..."

[Read the PRD]

You: "This is a Product Requirements Document for a patient scheduling system. I found:

**Extractable Information:**
- Problem definition (scheduling inefficiencies)
- Target users (patients, staff, administrators)
- Success criteria (reduce no-shows by 30%)
- Key constraints (HIPAA compliance, EHR integration)

**Generating SCDs:**
1. `problem-definition.yaml` - Core problem and affected users
2. `stakeholders.yaml` - User roles and their needs
3. `success-criteria.yaml` - KPIs and targets
4. `constraints-and-assumptions.yaml` - Boundaries and limits

**Updated Bundles:**
- `concerns/business.yaml` - Added 4 SCDs

**Compiled to Claude Code:**
- `.claude/rules/business.md` - Business context rules
- Updated `CLAUDE.md` scs-team section

**Needs Human Review:**
- The PRD mentions 'EHR integration' but doesn't specify which EHR system
- Success metrics are defined but baseline numbers aren't included

Run `/scs-team:status` to see the full picture."

## Error Handling

**File not found**: Ask for the correct path
**Not a document**: Explain what file types are supported
**Empty/minimal content**: Note that little was extractable, suggest `/scs-team:draft` instead
