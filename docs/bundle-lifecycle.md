# Bundle Lifecycle and Workflow

**Version**: 0.1
**Last Updated**: 2025-11-21

---

## Overview

This document describes the complete lifecycle of SCD Bundles within a project, from initial concept through development and change management. It explains how teams work with bundles, when they are created, how they evolve, and how they function as versioned contracts that govern the entire development process.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Project Initiation](#project-initiation)
3. [Content Creation Phase](#content-creation-phase)
4. [Review and Validation](#review-and-validation)
5. [Versioning and Locking](#versioning-and-locking)
6. [Bundle Hierarchy](#bundle-hierarchy)
7. [Development Phase](#development-phase)
8. [Change Management](#change-management)
9. [Automation Opportunities](#automation-opportunities)
10. [Best Practices](#best-practices)

---

## Core Concepts

### The Bundle as Contract

A **versioned bundle** is not just documentation—it is a **complete contract** that contains everything needed to:

- **Build** the system (architecture, tech stack, component models)
- **Test** the system (test criteria, performance requirements)
- **Manage** the system (operational requirements, monitoring)
- **Govern** the system (decision frameworks, approval processes)
- **Comply** with regulations (standards mappings, evidence)

### Context-First Development

SCS follows a **context-first approach**:

1. Define and lock the complete context (bundles)
2. Build the system to that contract
3. Changes require new versioned contracts

This ensures that all stakeholders—humans, AI assistants, and governance agents—operate from the same authoritative source of truth.

### Bundle States

Bundles exist in two primary states:

- **DRAFT Bundle**: Working state, evolving, not yet committed
- **VERSIONED Bundle**: Locked, immutable contract

---

## Project Initiation

### Starting Point

Every project begins with:
- A **concept** or problem to solve
- Defined **goals** and objectives
- Initial **scope** understanding

### Team Formation

Assemble a **domain team** structure:

- **Architecture Team** (typically 1 person + AI assistant)
- **Security Team** (typically 1 person + AI assistant)
- **Governance Team** (typically 1 person + AI assistant)
- **Performance Team** (typically 1 person + AI assistant)
- Additional domain teams as needed (compliance, operations, testing, etc.)

**Key characteristic**: Each domain team consists of a subject matter expert paired with an AI assistant. The human provides domain expertise; the AI assistant helps structure context and generate SCDs.

### Domain Team Responsibilities

Each domain team is responsible for:
- Gathering relevant information for their domain
- Creating SCDs that capture domain-specific context
- Managing their domain bundle
- Reviewing and validating their contributions
- Committing to versioned bundles

---

## Content Creation Phase

### Gathering Materials

Each domain team gathers or creates materials describing their domain:

**Architecture Team:**
- System context and boundaries
- Technology stack decisions
- Component models and interactions
- Deployment models
- Integration patterns

**Security Team:**
- Threat models
- Security controls
- Authentication and authorization approaches
- Encryption requirements
- Security policies

**Governance Team:**
- Decision frameworks
- Approval processes
- Roles and responsibilities
- Risk management approaches

**Performance Team:**
- Performance requirements
- Load expectations
- Scalability requirements
- Performance testing criteria

**Compliance Team:**
- Applicable standards (HIPAA, SOC2, GDPR, etc.)
- Regulatory requirements
- Audit requirements
- Evidence collection approaches

### Creating DRAFT SCDs

As each domain team develops their understanding, they create **DRAFT SCDs**:

1. **Human + AI Collaboration**:
   - Human provides domain expertise and content
   - AI assistant structures it according to SCS specification
   - AI ensures schema compliance and proper formatting

2. **SCD Creation**:
   - Each SCD captures a specific aspect of the domain
   - Example: Architecture domain might create:
     - `scd:project:system-context`
     - `scd:project:tech-stack`
     - `scd:project:component-model`
     - `scd:project:deployment-model`

3. **DRAFT Domain Bundle**:
   - Each domain team maintains a DRAFT bundle
   - Lists all SCDs for their domain
   - Evolves as understanding develops

**DRAFT Status**: SCDs and bundles marked as DRAFT are works in progress. They can be modified, refined, and iterated upon.

### Validation During DRAFT Phase

Even during the DRAFT phase, validation is valuable:

- **Syntax validation**: Ensure YAML/JSON is well-formed
- **Schema validation**: Verify SCDs conform to tier schemas
- **Semantic validation**: Check ID patterns, versioning, provenance
- **Warnings vs. Errors**: DRAFT validation may be more lenient, producing warnings rather than hard failures for incomplete sections

**Tool Support**: The `scs-validate` CLI tool can validate DRAFT SCDs and bundles to catch issues early.

---

## Review and Validation

### Checkpoint Process

When domain teams believe their bundles are ready, a **checkpoint** is triggered:

#### 1. Completeness Review

Each domain team reviews their bundle for:
- All required aspects covered
- All SCDs present and complete
- Relationships properly defined
- Provenance documented
- Cross-references validated

#### 2. Validation

Run comprehensive validation:

```bash
# Validate domain bundle
scs-validate --bundle bundles/architecture-bundle.yaml --strict

# Check for completeness, orphaned references, circular dependencies
```

#### 3. Cross-Domain Review

Domain teams review each other's bundles:
- Architecture reviews Security's infrastructure assumptions
- Security reviews Architecture's threat surface
- Governance reviews decision points across all domains
- Compliance reviews standards mappings

#### 4. Analysis and Review Tools

**Viewer/Editor/VersionLocker Tool** (separate product):
- Rich UI for bundle visualization
- Relationship graph visualization
- Gap analysis (unsatisfied standards, missing relationships)
- Collaboration features for team review
- Approval workflows
- Version locking mechanism

**CLI Validator** (open source):
- Fast feedback during development
- CI/CD integration
- Automated validation checks

---

## Versioning and Locking

### The Versioning Decision

When the team agrees that the bundle is complete and ready, they commit to **versioning**.

### What Gets Locked

When a bundle is versioned and locked:

1. **The bundle manifest** is locked (immutable)
2. **All SCDs referenced in that bundle** are versioned and locked
3. **All imported bundles** are locked at their specific versions
4. **The entire context set** becomes an immutable contract

### Versioning Structure

#### Domain Bundle Versioning

```yaml
id: bundle:architecture
type: domain
version: "1.0.0"
title: "Architecture Bundle"
description: "Complete architectural context for Project X"
imports: []  # Domain bundles cannot import other bundles
scds:
  - scd:project:system-context
  - scd:project:tech-stack
  - scd:project:integration-map
  - scd:project:component-model
provenance:
  created_by: "alice@company.com"
  created_at: "2025-11-20T10:00:00Z"
  rationale: "Initial architecture definition for Project X launch"
```

#### Project Bundle Versioning

```yaml
id: bundle:project-x
type: project
version: "1.0.0"
title: "Project X Complete Context Bundle"
description: "Complete context contract for Project X development"
imports:
  # Foundation bundles
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0

  # Domain bundles (11 prescribed)
  - bundle:architecture:1.0.0
  - bundle:security:1.0.0
  - bundle:performance-reliability:1.0.0
  - bundle:usability-accessibility:1.0.0
  - bundle:compliance-governance:1.0.0
  - bundle:data-provenance:1.0.0
  - bundle:testing-validation:1.0.0
  - bundle:deployment-operations:1.0.0
  - bundle:safety-risk:1.0.0
  - bundle:ethics-ai-accountability:1.0.0
scds: []  # All SCDs are in imported bundles
provenance:
  created_by: "project-lead@company.com"
  created_at: "2025-11-20T14:00:00Z"
  rationale: "Project X v1.0 development contract - approved by all domain teams"
```

### Immutability

Once versioned:
- **No modifications allowed** to that version
- Bundle serves as the authoritative contract
- All stakeholders operate from this locked context
- Changes require creating a new version (see [Change Management](#change-management))

---

## Bundle Hierarchy

### Compositional Structure

SCS bundles are **hierarchical and compositional** with **4 bundle types**:

```
Project Bundle (type: project, top-level orchestrator)
  │
  ├─ Meta Bundle:1.0.0 (type: meta, foundational vocabulary)
  │   ├─ scd:meta:roles
  │   ├─ scd:meta:capabilities
  │   ├─ scd:meta:domains
  │   └─ scd:meta:concerns
  │
  ├─ Standards Bundle:1.0.0 (type: standards, compliance)
  │   ├─ scd:standards:hipaa-privacy-rule
  │   └─ scd:standards:hipaa-security-rule
  │
  ├─ Architecture Bundle:1.0.0 (type: domain)
  │   ├─ scd:project:system-context
  │   ├─ scd:project:tech-stack
  │   ├─ scd:project:integration-map
  │   └─ scd:project:component-model
  │
  ├─ Security Bundle:1.0.0 (type: domain)
  │   ├─ scd:project:authn-authz
  │   ├─ scd:project:data-protection
  │   ├─ scd:project:data-handling
  │   └─ scd:project:threat-model
  │
  ├─ Governance Bundle:1.0.0
  │   ├─ scd:meta:roles:1.0.0
  │   ├─ scd:project:decision-framework:1.0.0
  │   └─ scd:project:approval-process:1.0.0
  │
  └─ Compliance Bundle:1.0.0
      ├─ scd:standards:hipaa:1.0.0
      ├─ scd:project:hipaa-mappings:1.0.0
      └─ scd:project:audit-evidence:1.0.0
```

### Domain Teams Own Domain Bundles

- **Architecture team** owns and manages `bundle:architecture`
- **Security team** owns and manages `bundle:security`
- **Governance team** owns and manages `bundle:governance`
- Each domain team works independently on their bundle
- Each domain bundle can version independently (during iterations)

### Project Bundle Composition

The **project bundle** is the master contract that:
- Imports specific versions of all domain bundles
- May contain cross-cutting SCDs that span domains
- Represents the complete, versioned context for the project
- Is what the development team builds against

### File Organization (Recommended)

```
project-x/
├── bundles/
│   ├── project-bundle.yaml          # Master contract
│   ├── architecture-bundle.yaml     # Domain bundle
│   ├── security-bundle.yaml         # Domain bundle
│   ├── governance-bundle.yaml       # Domain bundle
│   ├── performance-bundle.yaml      # Domain bundle
│   └── compliance-bundle.yaml       # Domain bundle
│
└── scd/
    ├── meta/
    │   ├── roles.yaml
    │   └── capabilities.yaml
    │
    ├── standards/
    │   ├── hipaa.yaml
    │   └── soc2.yaml
    │
    └── project/
        ├── system-context.yaml
        ├── tech-stack.yaml
        ├── component-model.yaml
        ├── threat-model.yaml
        ├── security-controls.yaml
        └── ... (more SCDs)
```

---

## Development Phase

### Starting Development

Development **begins only after** the project bundle is versioned and locked.

**Why?** Because the bundle is the complete contract. It contains everything needed to build, test, manage, govern, and comply.

### How the Bundle is Used

#### By AI Assistants

AI coding assistants consume the versioned bundle as context:
- Generate code that conforms to the architecture
- Apply security controls as specified
- Follow governance decisions
- Meet performance requirements
- Satisfy compliance obligations

Example:
```
AI Assistant loads: bundle:project-x:1.0.0
  → Understands complete system context
  → Generates code aligned with tech stack
  → Applies security controls from bundle
  → Meets performance criteria from bundle
```

#### By Developers

Human developers reference the bundle:
- Understand system architecture
- Know what standards apply
- Follow governance processes
- Implement required security controls
- Build to the contract

#### By Governance Agents

Autonomic governance agents validate against the bundle:
- Check code compliance with architecture
- Verify security controls are implemented
- Validate standards satisfaction
- Generate compliance reports
- Identify gaps

#### By Compliance Auditors

Auditors review the bundle as evidence:
- See complete context and rationale
- Trace requirements to implementations
- Verify standards mappings
- Review provenance and decisions
- Assess risk management

### Bundle as Source of Truth

During development, the **versioned bundle is the authoritative source of truth**:
- Architectural decisions
- Technology choices
- Security requirements
- Performance criteria
- Compliance obligations
- Testing requirements
- Operational needs

---

## Change Management

### When Changes Are Needed

During development, changes may be needed due to:
- Discovered technical constraints
- New requirements
- Standards updates
- Security vulnerabilities
- Performance issues
- Regulatory changes

### SDLC Rules Apply

Changes to the context require going through the full process:

1. **Change Request**:
   - Document the needed change
   - Identify impacted domains
   - Assess impact on existing contract

2. **Domain Team Review**:
   - Relevant domain teams evaluate the change
   - Update DRAFT SCDs as needed
   - Update DRAFT domain bundles

3. **Validation**:
   - Validate updated domain bundles
   - Check for breaking changes
   - Assess downstream impacts

4. **Cross-Domain Review**:
   - Review impact across all domains
   - Ensure consistency maintained

5. **Version Increment**:
   - Create new version of affected domain bundles
   - Update project bundle with new imports
   - Version and lock the new project bundle

6. **Transition**:
   - Development transitions to new bundle version
   - Old version remains for reference
   - Git tags track bundle versions

### Versioning Strategy

**Semantic Versioning** applies to bundles:

- **Major (2.0.0)**: Breaking changes, significant restructuring
- **Minor (1.1.0)**: Additive changes, new SCDs, expanded context
- **Patch (1.0.1)**: Corrections, clarifications, non-breaking fixes

**Example Change Flow**:

```
Initial: bundle:project-x:1.0.0
  ├─ bundle:architecture:1.0.0
  └─ bundle:security:1.0.0

Change Request: Add new component to architecture

Updated DRAFT: bundle:architecture (DRAFT)
  → Add scd:project:new-component

Validated & Versioned: bundle:architecture:1.1.0

New Project Bundle: bundle:project-x:1.1.0
  ├─ bundle:architecture:1.1.0  ← updated
  └─ bundle:security:1.0.0      ← unchanged
```

---

## Automation Opportunities

While the process may sound time-consuming, **most of it can be automated**:

### Automated SCD Generation

- AI assistants generate DRAFT SCDs from conversations and documents
- Templates and schemas guide structure
- Provenance tracking is automated

### Automated Validation

```bash
# Pre-commit hooks
git commit → automatic validation → pass/fail

# CI/CD pipelines
PR opened → validate all bundles → report results → block merge if failed

# Continuous validation
File changed → re-validate → notify team
```

### Automated Review Workflows

- Viewer/Editor tools automate review workflows
- Assign reviewers by domain
- Track approval status
- Generate review reports
- Identify gaps and inconsistencies

### Automated Version Management

- Semantic version bumping based on change analysis
- Automated git tagging of bundle versions
- Automatic provenance updates
- Bundle diff generation

### Automated Governance

- Autonomic agents continuously validate compliance
- Detect gaps in real-time
- Generate audit reports automatically
- Monitor for standards changes
- Alert on violations

### Integration with Development Tools

- IDE plugins consume bundle context
- AI coding assistants auto-load relevant bundles
- Code review tools validate against bundle contracts
- CI/CD enforces bundle compliance

---

## Best Practices

### 1. Start with Domain Teams

Form domain teams early and let each own their context:
- Clear ownership improves quality
- Parallel work accelerates timeline
- Domain expertise is captured properly

### 2. Iterate in DRAFT Mode

Don't rush to version:
- Spend adequate time in DRAFT mode
- Validate early and often
- Cross-review between domains
- Refine until confident

### 3. Make Versioning Meaningful

Version when you have a true contract:
- Complete enough to build against
- Reviewed and validated
- Team consensus achieved
- Ready to commit

### 4. Automate Validation

Integrate validation into workflows:
- Pre-commit hooks catch issues early
- CI/CD blocks invalid bundles
- Continuous feedback loops
- Fast failure = fast fixes

### 5. Use Tools Effectively

Leverage both CLI and rich tools:
- **CLI validator**: Fast feedback, automation, CI/CD
- **Viewer/Editor**: Rich review, analysis, collaboration
- Different tools for different needs

### 6. Document Rationale

Always complete provenance:
- Why was this SCD created?
- What problem does it solve?
- Who requested it?
- What changed in this version?

Rationale is invaluable for:
- Future team members
- Auditors
- Change impact analysis
- Historical understanding

### 7. Keep Bundles Focused

Domain bundles should be cohesive:
- Architecture focuses on architecture
- Security focuses on security
- Avoid mixing concerns
- Clear boundaries improve clarity

### 8. Version Thoughtfully

Not every change needs a version:
- DRAFT mode allows iteration
- Version when contract-ready
- Semantic versioning communicates impact
- Major versions signal breaking changes

### 9. Maintain History

Keep old bundle versions:
- Git tags for each bundle version
- Archived bundles for reference
- Audit trail of changes
- Learning from evolution

### 10. Train Teams

Ensure everyone understands:
- Bundle lifecycle
- Their role in the process
- How to use tools
- Why context matters
- How AI consumes bundles

---

## Timeline Example

Here's a realistic timeline for a medium-complexity project:

### Week 1: Initiation
- Day 1-2: Form domain teams, define scope
- Day 3-5: Gather initial materials and content

### Week 2-3: Content Creation (DRAFT)
- Domain teams work in parallel
- Create DRAFT SCDs
- Build DRAFT domain bundles
- Iterate and refine
- Continuous validation

### Week 4: Review and Validation
- Day 1-2: Domain team self-review
- Day 3-4: Cross-domain review
- Day 5: Validation and gap analysis

### Week 5: Refinement
- Address gaps identified
- Update DRAFT bundles
- Re-validate

### Week 6: Versioning
- Final reviews
- Version domain bundles
- Compose project bundle
- Lock and commit

### Week 7+: Development Begins
- Build against versioned bundle
- AI assistants use bundle context
- Governance agents validate
- Development proceeds

**With Automation**: Timeline can compress significantly:
- AI-assisted SCD generation
- Automated validation and review routing
- Parallel workflows
- Continuous feedback

---

## Summary

The bundle lifecycle follows a clear progression:

```
Concept → Team Formation → Content Creation (DRAFT) →
Review & Validation → Versioning & Locking → Development →
Change Management (repeat as needed)
```

**Key Principles:**
1. **Context-first**: Define complete context before building
2. **Team-owned**: Domain teams own their context
3. **Contract-based**: Versioned bundles are immutable contracts
4. **Automation-friendly**: Most steps can be automated
5. **SDLC-aligned**: Change management follows standard practices

**The Result:**
- Clear, complete context for all stakeholders
- Humans and AI work from the same source of truth
- Governance and compliance built in from the start
- Traceable decisions and rationale
- Reduced risk and increased confidence

---

## Related Documentation

- [Bundle Format Specification](../spec/0.1/bundle-format.md) - Technical bundle structure
- [Validation Workflow](validation-workflow.md) - How to validate bundles
- [SCS Overview](../spec/0.1/overview.md) - Core SCS concepts
- [Getting Started](getting-started.md) - Creating your first SCD

---

## Questions?

- Open an [issue](https://github.com/tim-mccrimmon/scs-spec/issues)
- Start a [discussion](https://github.com/tim-mccrimmon/scs-spec/discussions)
- See the [FAQ](faq.md)
