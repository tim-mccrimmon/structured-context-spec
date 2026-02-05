---
name: add
description: Process a document (PRD, architecture doc, security requirements, etc.) into structured context. Extracts relevant information and generates appropriate SCDs.
argument-hint: "<file-path>"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Bash(mkdir -p *)
---

# SCS Team Add - Process Document into Structured Context

You are helping the user transform an existing document into structured context that Claude can use.

## Your Process

### Step 1: Read and Analyze the Document

First, read the document the user provided:
- Identify the document type (PRD, MRD, architecture, security, compliance, etc.)
- Understand its structure and content
- Note what concerns it addresses (business context, architecture, security, etc.)

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

### Step 3: Generate SCDs

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

### Step 4: Determine Placement

Place generated SCDs in the appropriate location:
- Create `.scs/scds/` directory if it doesn't exist
- Name files descriptively: `problem-definition.yaml`, `system-context.yaml`, etc.
- Group related SCDs logically

### Step 5: Report What Was Created

Tell the user:
1. What document type was detected
2. What SCDs were generated
3. What information was extracted
4. What might be missing or need human review

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

**Needs Human Review:**
- The PRD mentions 'EHR integration' but doesn't specify which EHR system
- Success metrics are defined but baseline numbers aren't included

Created 4 SCDs in `.scs/scds/`. Run `/scs-team:status` to see the full picture."

## Error Handling

**File not found**: Ask for the correct path
**Not a document**: Explain what file types are supported
**Empty/minimal content**: Note that little was extractable, suggest `/scs-team:draft` instead
