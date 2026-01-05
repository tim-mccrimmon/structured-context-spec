# Understanding SCDs - A Complete Guide

**Version**: 0.2.0
**Last Updated**: 2025-12-09

---

## Overview

This guide explains **Structured Context Documents (SCDs)** — the fundamental building blocks of the Structured Context Specification (SCS). You'll learn what SCDs are, how they're structured, how to create them effectively, and best practices for using them in AI-native development.

---

## Table of Contents

1. [What is an SCD?](#what-is-an-scd)
2. [Why SCDs Exist](#why-scds-exist)
3. [SCD Anatomy](#scd-anatomy)
4. [The Three Tiers](#the-three-tiers)
5. [Creating SCDs](#creating-scds)
6. [SCD Relationships](#scd-relationships)
7. [Versioning SCDs](#versioning-scds)
8. [Best Practices](#best-practices)
9. [Anti-Patterns](#anti-patterns)
10. [Common Questions](#common-questions)

---

## What is an SCD?

A **Structured Context Document (SCD)** is a machine-readable, atomic unit of context that defines **exactly one thing** about a system.

An SCD can define:
- A rule or constraint
- A boundary or limit
- A domain concept or entity
- An architectural decision
- A compliance requirement
- A quality attribute
- A relationship between concepts

**Key characteristics:**
- **Atomic** - Defines one concept, not multiple
- **Machine-readable** - YAML/JSON format optimized for LLMs
- **Versioned** - Immutable once versioned
- **Provenance-tracked** - Records who, when, and why
- **Relational** - Can reference other SCDs

---

## Why SCDs Exist

### The White Room Problem

AI assistants begin every task in a cognitive void — they have no memory of:
- What system you're building
- What architectural patterns to follow
- What constraints to respect
- What compliance requirements to satisfy

Traditional documentation is scattered, verbose, and optimized for human reading. SCDs solve this by providing:

**For AI Systems:**
- Compact, salient context that fits in context windows
- Structured data that's easy to parse and understand
- Explicit constraints and rules to follow
- Versioned contracts that ensure consistency

**For Humans:**
- Single source of truth for system intent
- Audit trail of all decisions
- Impact analysis through relationships
- Compliance verification

---

## SCD Anatomy

Every SCD has the same core structure:

```yaml
# Required Fields
id: "scd:tier:domain:name"          # Unique identifier
version: "1.0.0"                     # Semantic version
type: "tier-name"                    # meta, project, or standards
domain: "domain-name"                # Which domain (architecture, security, etc.)

provenance:
  author: "email@example.com"
  date: "2025-12-09"
  rationale: "Why this SCD was created"

title: "Human-readable title"

# Content (structure varies by tier and domain)
definition:
  # ... tier-specific content

# Optional Fields
relationships:                       # Links to other SCDs
  - type: "satisfies"
    target: "scd:standards:hipaa-164.312"
    description: "How this satisfies that requirement"

metadata:                            # Additional contextual info
  tags: ["encryption", "security"]
  status: "active"
```

### Field Descriptions

**`id`** - Globally unique identifier following the pattern `scd:tier:domain:name`
- Must match the tier type
- Should be descriptive and specific
- Example: `scd:project:security:encryption-at-rest`

**`version`** - Semantic version (major.minor.patch)
- Follows semver conventions
- Locked when bundle is versioned
- Breaking changes require new major version

**`type`** - The tier this SCD belongs to
- `meta` - Semantic foundation
- `project` - Project-specific context
- `standards` - External obligations

**`domain`** - The domain category (from 11 prescribed domains)
- `architecture`, `security`, `data-provenance`, etc.
- Helps organize and bundle SCDs

**`provenance`** - Accountability and traceability
- `author` - Who created/modified this
- `date` - When it was created/modified
- `rationale` - **Why** this exists (critical for governance)

**`title`** - Human-readable summary

**`definition`** - Tier and domain-specific content (see [The Three Tiers](#the-three-tiers))

**`relationships`** (optional) - Links to other SCDs
- Creates a knowledge graph
- Enables impact analysis and compliance checking

**`metadata`** (optional) - Additional context
- Tags, status, ownership, etc.

---

## The Three Tiers

SCDs are organized into three tiers, each serving a distinct purpose:

### Meta Tier: Semantic Foundation

**Purpose**: Defines the vocabulary and concepts that all other tiers build upon

**Examples:**
- Domain definitions (what "security" means in your context)
- Role definitions (what a "developer" or "architect" does)
- Cross-cutting concerns (logging, monitoring, error handling)
- Naming conventions and standards

**ID Pattern**: `scd:meta:domain:name`

**When to use:**
- Defining foundational concepts
- Establishing shared vocabulary
- Setting universal rules that apply everywhere

**Example:**
```yaml
id: scd:meta:architecture:domain-definition
version: "1.0.0"
type: meta
domain: architecture
provenance:
  author: "architect@example.com"
  date: "2025-12-09"
  rationale: "Define what the architecture domain encompasses"
title: "Architecture Domain Definition"
definition:
  name: "Architecture"
  description: "System structure, components, and their relationships"
  scope:
    - Component design
    - Integration patterns
    - Technology stack decisions
    - Deployment architecture
```

---

### Standards Tier: External Obligations

**Purpose**: Represents compliance frameworks, regulations, and external standards as importable contracts

**Examples:**
- HIPAA requirements (164.312 encryption, etc.)
- SOC2 controls
- ISO standards
- Internal corporate policies
- Industry best practices (WCAG, NIST)

**ID Pattern**: `scd:standards:framework:requirement`

**When to use:**
- Encoding regulatory requirements
- Representing compliance obligations
- Defining quality standards
- Creating reusable compliance contracts

**Example:**
```yaml
id: scd:standards:hipaa:164.312-encryption
version: "1.0.0"
type: standards
domain: security
provenance:
  author: "compliance@example.com"
  date: "2025-12-09"
  rationale: "HIPAA requirement for encryption of ePHI in transit"
title: "HIPAA 164.312(e)(1) - Transmission Security"
definition:
  standard: "HIPAA"
  section: "164.312(e)(1)"
  requirement: "Implement technical security measures to guard against unauthorized access to ePHI transmitted over an electronic communications network"
  controls:
    - "Encryption of ePHI in transit"
    - "Use of TLS 1.2 or higher"
    - "Certificate validation"
```

**Key benefit**: Standards-tier SCDs can be shared via the scs-registry, so you don't have to reinvent HIPAA compliance — just import it.

---

### Project Tier: Your Actual System

**Purpose**: Describes what you're actually building — the specific system, its components, features, and implementation

**Examples:**
- Components and services
- API definitions
- Security implementations
- Data models and flows
- Feature specifications
- Performance targets

**ID Pattern**: `scd:project:domain:name`

**When to use:**
- Defining system components
- Specifying features
- Documenting architecture decisions
- Setting project-specific constraints

**Example:**
```yaml
id: scd:project:security:encryption-service
version: "1.0.0"
type: project
domain: security
provenance:
  author: "dev@example.com"
  date: "2025-12-09"
  rationale: "Implement encryption service to satisfy HIPAA requirements"
title: "Encryption Service Component"
definition:
  component: "EncryptionService"
  description: "Handles encryption/decryption of ePHI in transit and at rest"
  technology: "AES-256-GCM"
  implementation:
    - "Uses AWS KMS for key management"
    - "Automatic key rotation every 90 days"
    - "TLS 1.3 for all network communication"
relationships:
  - type: "satisfies"
    target: "scd:standards:hipaa:164.312-encryption"
    description: "Implements HIPAA encryption requirements"
  - type: "depends-on"
    target: "scd:project:architecture:aws-kms"
    description: "Relies on AWS KMS for key management"
```

**Key benefit**: Project-tier SCDs link to standards-tier via `satisfies` relationships, creating a provable compliance trail.

---

## Creating SCDs

### Step-by-Step Process

**1. Identify What Needs Defining**
- Is it a rule, boundary, concept, or requirement?
- Does it belong in meta, standards, or project tier?
- Which domain does it belong to?

**2. Choose the Right Tier**
- **Meta**: Universal concepts, vocabulary, foundational rules
- **Standards**: External obligations, compliance requirements
- **Project**: Your specific system components and features

**3. Start from a Template**
```bash
# Copy the appropriate tier template
cp templates/scd/meta_scd_template.yaml my-scd.yaml
cp templates/scd/project_scd_template.yaml my-scd.yaml
cp templates/scd/standards_scd_template.yaml my-scd.yaml
```

**4. Fill in Required Fields**
- `id` - Follow the naming pattern
- `version` - Start with `0.1.0` for draft
- `type` - Match your tier
- `domain` - Choose from the 11 domains
- `provenance` - Record who, when, why
- `title` - Clear, descriptive summary
- `definition` - The actual content (structure varies by tier/domain)

**5. Add Relationships (if applicable)**
```yaml
relationships:
  - type: "satisfies"       # This implements that requirement
    target: "scd:standards:hipaa:164.312"
  - type: "depends-on"      # This relies on that component
    target: "scd:project:architecture:auth-service"
  - type: "constrains"      # This limits that component
    target: "scd:project:data:user-database"
```

**6. Validate**
```bash
cd tools/scd-validator
python validate.py ../../my-scd.yaml
```

---

## SCD Relationships

Relationships create a **knowledge graph** that enables:
- Impact analysis ("what breaks if I change this?")
- Compliance checking ("do we satisfy all requirements?")
- Dependency tracking ("what does this rely on?")
- Governance automation

### Relationship Types

**`satisfies`** - Implements or fulfills a requirement
- Usually project → standards
- Example: Encryption service satisfies HIPAA 164.312

**`depends-on`** - Relies on another component/SCD
- Usually project → project
- Example: API service depends on authentication service

**`constrains`** - Limits or restricts another SCD
- Usually meta → project or standards → project
- Example: Security policy constrains data storage

**`references`** - General reference to related concept
- Any tier to any tier
- Example: Architecture references deployment patterns

**`derives-from`** - Based on or extends another SCD
- Usually project → standards or meta
- Example: Custom auth derives from OAuth2 standard

### Relationship Structure

```yaml
relationships:
  - type: "satisfies"
    target: "scd:standards:hipaa:164.312"
    description: "Implements encryption in transit and at rest per HIPAA requirements"
    evidence:
      - "Uses AES-256-GCM encryption"
      - "Automatic key rotation every 90 days"
```

---

## Versioning SCDs

### Version States

**Draft** (`0.x.y`)
- Work in progress
- Can change freely
- Not yet locked

**Released** (`1.0.0+`)
- Locked and immutable
- Part of a versioned bundle
- Changes require new version

### Semantic Versioning

Follow semver conventions:

**Major version** (1.0.0 → 2.0.0) - Breaking changes
- Changed the fundamental definition
- Removed required fields
- Changed behavior incompatibly

**Minor version** (1.0.0 → 1.1.0) - Additions
- Added optional fields
- Expanded definition
- Added relationships

**Patch version** (1.0.0 → 1.0.1) - Fixes
- Corrected typos
- Clarified wording
- Fixed errors without changing meaning

### Version Lifecycle

1. **Create draft**: Start with `0.1.0`
2. **Iterate**: Increment patch (`0.1.1`, `0.1.2`)
3. **Review and validate**: Ensure quality
4. **Release**: Lock as `1.0.0` when bundle is versioned
5. **Maintain**: Create new versions for changes

---

## Best Practices

### 1. One SCD, One Concept (Atomicity)
✅ **Good**: `scd:project:security:encryption-at-rest`
❌ **Bad**: `scd:project:security:all-security-requirements`

**Why**: Atomic SCDs are easier to version, relate, and govern.

---

### 2. Write for Machines First, Humans Second
✅ **Good**: Structured, consistent, parseable
❌ **Bad**: Narrative paragraphs, ambiguous language

**Why**: LLMs process structured data more reliably than prose.

---

### 3. Always Include Rationale
✅ **Good**:
```yaml
provenance:
  rationale: "Changed encryption to AES-256-GCM per CSO requirement for HIPAA compliance"
```
❌ **Bad**:
```yaml
provenance:
  rationale: "Updated encryption"
```

**Why**: Future maintainers need to understand **why**, not just **what**.

---

### 4. Use Relationships to Create Context
✅ **Good**: Link project SCDs to standards they satisfy
❌ **Bad**: Isolated SCDs with no relationships

**Why**: Relationships enable governance, impact analysis, and compliance checking.

---

### 5. Keep Definitions Minimal but Complete
✅ **Good**: Essential information only
❌ **Bad**: Verbose explanations, redundant details

**Why**: Compact context fits in LLM windows and improves salience.

---

### 6. Version Meaningfully
✅ **Good**: Clear version progression with meaningful changes
❌ **Bad**: Random version bumps, no changelog

**Why**: Versions enable change tracking and rollback.

---

### 7. Validate Early and Often
✅ **Good**: Validate after every change
❌ **Bad**: Wait until the end to validate

**Why**: Catch errors early before they propagate.

---

## Anti-Patterns

### ❌ The Mega-SCD
**Problem**: One SCD tries to define everything about a domain

**Example**: `scd:project:security:all-security-rules` with 500 lines

**Fix**: Break into atomic SCDs, one per concept

---

### ❌ The Narrative SCD
**Problem**: Writing SCDs as prose documentation

**Example**:
```yaml
definition:
  description: "The system should use encryption. We decided to use AES-256
                because it's secure and meets industry standards. The CSO
                recommended this approach after consulting with the security team..."
```

**Fix**: Use structured fields, bullet points, and clear definitions

---

### ❌ The Orphan SCD
**Problem**: SCDs with no relationships to other SCDs

**Example**: A project SCD that claims to satisfy HIPAA but has no `satisfies` relationship

**Fix**: Add relationships to create the knowledge graph

---

### ❌ The Vague ID
**Problem**: Non-descriptive, generic IDs

**Example**: `scd:project:security:rule-1`, `scd:project:data:thing`

**Fix**: Use descriptive, semantic IDs like `scd:project:security:tls-configuration`

---

### ❌ The Missing Provenance
**Problem**: No rationale for why the SCD exists

**Example**:
```yaml
provenance:
  author: "dev@example.com"
  date: "2025-12-09"
  rationale: ""
```

**Fix**: Always explain **why** this exists

---

### ❌ The Forever Draft
**Problem**: SCDs that stay in `0.x.y` forever

**Example**: `version: "0.1.0"` for 6 months

**Fix**: Version and lock SCDs when bundles are ready for use

---

## Common Questions

### When should I create a new SCD vs. update an existing one?

**Create new** when:
- Defining a new concept, rule, or component
- The new content doesn't fit atomically within an existing SCD

**Update existing** when:
- Clarifying or expanding an existing concept
- Fixing errors or adding missing details
- Version appropriately (major/minor/patch)

---

### How granular should SCDs be?

**Rule of thumb**: If it can change independently, it should be a separate SCD.

**Example**:
- ✅ Separate SCDs for "encryption-at-rest" and "encryption-in-transit"
- ❌ One SCD for "all-encryption-requirements"

---

### Can SCDs reference external documents?

**Yes**, but keep the essential information in the SCD itself.

**Example**:
```yaml
definition:
  summary: "API follows REST principles with JSON payloads"
  external_docs:
    - url: "https://internal.wiki/api-design-guide"
      description: "Complete API design guide"
```

---

### How do I handle sensitive information in SCDs?

**Don't put secrets in SCDs**. SCDs are context, not configuration.

**Example**:
- ✅ SCD defines "encryption uses AWS KMS key with 90-day rotation"
- ❌ SCD contains the actual KMS key ID or credentials

Use environment variables, secret managers, or configuration files for actual secrets.

---

### Should every SCD have relationships?

**Not necessarily**. Some SCDs (especially meta-tier) are foundational and don't need relationships.

**Guidelines**:
- Project-tier SCDs should usually link to standards they satisfy
- Project-tier SCDs often depend on other project SCDs
- Meta-tier SCDs may not need relationships

---

## Next Steps

Now that you understand SCDs:

1. **Practice**: Create a few SCDs for a simple project
2. **Validate**: Use the [validator](../tools/scd-validator/) to check your work
3. **Bundle**: Learn how SCDs come together in [Bundle Lifecycle](bundle-lifecycle.md)
4. **Validate**: Understand [Validation Guide](validation-guide.md)
5. **Quick Start**: Try the [Quick Start Guide](quick-start-guide.md) for hands-on practice

---

## Additional Resources

- [SCS Specification](../spec/0.1/) - Normative specification
- [FAQ](FAQ.md) - Common questions about SCS
- [Glossary](glossary.yaml) - Terminology reference
- [Templates](../templates/scd/) - SCD templates for all tiers
