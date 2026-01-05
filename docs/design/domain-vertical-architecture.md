# Domain Vertical Architecture - Design Discussion

**Status:** Design Exploration
**Date:** 2025-12-15
**Context:** Rethinking domain architecture to support industry verticals

---

## Vision

**Tagline:** "If you are using AI and not using Structured Context - you are doing it wrong"

**Core Idea:**
SCS is the foundational framework for safe, effective AI assistance across ALL professional domains, not just software development.

---

## The Core Problem

**Companies and professionals are using AI agents to help with their work, but AI suffers from:**
- **Drift** - AI strays from requirements and constraints over time
- **Hallucinations** - AI makes up facts, processes, or context
- **Inconsistency** - AI provides different answers to the same questions
- **Lack of auditability** - No way to trace AI decisions back to authoritative sources
- **Compliance risk** - AI doesn't understand regulatory requirements

**Without structured context, AI is unreliable for professional work.**

---

## The Solution

**Structured Context = The authoritative foundation for AI assistance**

By providing AI agents with structured, versioned, validated context:
- AI stays within defined boundaries (no drift)
- AI references authoritative sources (no hallucinations)
- AI maintains consistency (same context = same behavior)
- AI decisions are traceable (provenance and relationships)
- AI respects compliance requirements (standards built-in)

**The complexity of SCS (domains, concerns, bundles, SCDs) exists to solve these AI reliability problems.**

---

## The Target Market

**Not just developers - ANY professional using AI agents:**
- Legal aids using AI for case management and research
- Clinicians using AI for diagnosis support and treatment planning
- Traders using AI for market analysis and portfolio management
- Sales professionals using AI for lead qualification and opportunity management
- Accountants, engineers, educators, researchers, etc.

**These professionals have money to spend because AI reliability is critical to their work.**

Software Development domain is the proof-of-concept. The broader professional market is the business opportunity.

---

## The Problem with Current "Domain" Terminology

### Current State (Confusing):

1. **"Domain" as bundle type** (schema/bundles/scd-bundle-schema.json)
   - Bundle `type: "domain"` is one of four bundle types
   - Used for bundles like "Architecture Domain Bundle", "Security Domain Bundle"
   - Makes "domain" feel like a concern area

2. **"Domain" as industry vertical** (schema/domain/domain-manifest-schema.json)
   - Domain manifest schema exists with `id: "domain:healthcare"`
   - Implies domains are industry verticals (Healthcare, Finance, Legal)
   - Has schemas, templates, validation rules, industry metadata

3. **Result:** The word "domain" is overloaded and confusing
   - Is Architecture a domain? Or is Healthcare a domain?
   - Are they the same concept or different?

---

## Proposed Mental Model

### Domain = Industry Vertical (A manifest that lists bundles)

A **Domain** is a manifest that defines structured context for a specific professional area.

**Examples:**

#### Domain: Software Development
```yaml
domain:
  id: domain:software-development
  version: 1.0.0
  name: "Software Development"
  description: "Context for developers building software systems"
  bundles:
    - bundle:architecture:1.0.0
    - bundle:security:1.0.0
    - bundle:performance-reliability:1.0.0
    - bundle:testing-validation:1.0.0
    - bundle:deployment-operations:1.0.0
    - bundle:data-provenance:1.0.0
    - bundle:compliance-governance:1.0.0
    - bundle:usability-accessibility:1.0.0
    - bundle:safety-risk:1.0.0
    - bundle:ethics-ai-accountability:1.0.0
    - bundle:business-context:1.0.0
```

**Target Audience:** Software developers
**Use Case:** AI coding assistants, governance agents, development tools
**Business Model:** Free/open (developers don't pay, like Eclipse)

---

#### Domain: Legal
```yaml
domain:
  id: domain:legal
  version: 1.0.0
  name: "Legal Practice"
  description: "Context for legal professionals and legal aids"
  bundles:
    - bundle:case-management:1.0.0
    - bundle:legal-research:1.0.0
    - bundle:client-communication:1.0.0
    - bundle:compliance-tracking:1.0.0
    - bundle:document-drafting:1.0.0
    - bundle:billing-time-tracking:1.0.0
```

**Target Audience:** Legal aids, paralegals, lawyers
**Use Case:** AI assistance for legal work (research, case management, drafting)
**Business Model:** Legal professionals PAY for domain-specific AI assistance

---

#### Domain: Clinical
```yaml
domain:
  id: domain:clinical
  version: 1.0.0
  name: "Clinical Practice"
  description: "Context for healthcare clinicians"
  bundles:
    - bundle:patient-care-workflows:1.0.0
    - bundle:clinical-decision-support:1.0.0
    - bundle:diagnosis-support:1.0.0
    - bundle:treatment-planning:1.0.0
    - bundle:medication-management:1.0.0
    - bundle:ehr-integration:1.0.0
```

**Target Audience:** Doctors, nurses, clinicians
**Use Case:** AI assistance for clinical work (diagnosis, treatment planning)
**Business Model:** Healthcare professionals PAY for domain-specific AI assistance

---

#### Domain: Finance/Trading
```yaml
domain:
  id: domain:trading
  version: 1.0.0
  name: "Trading & Financial Analysis"
  description: "Context for traders and financial analysts"
  bundles:
    - bundle:market-analysis:1.0.0
    - bundle:risk-assessment:1.0.0
    - bundle:portfolio-management:1.0.0
    - bundle:regulatory-compliance:1.0.0
    - bundle:trading-strategies:1.0.0
```

**Target Audience:** Traders, financial analysts
**Use Case:** AI assistance for trading decisions and analysis
**Business Model:** Traders PAY for domain-specific AI assistance

---

## How Projects Use Domains

### Example: Healthcare Software Project

```yaml
id: bundle:my-healthcare-app
type: project
version: "1.0.0"

imports:
  # Foundation bundles (always present)
  - bundle:meta:1.0.0
  - bundle:standards:1.0.0

  # Domain: Software Development (brings in 11 bundles)
  - domain:software-development:1.0.0

  # Domain: Healthcare (brings in healthcare-specific bundles)
  - domain:clinical:1.0.0

scds: []
```

When this project bundle is loaded, it transitively imports:
- All bundles from Software Development domain (Architecture, Security, etc.)
- All bundles from Clinical domain (Patient care, Diagnosis, etc.)

---

## Why This Model is Better

### 1. Clarity
- "Domain" clearly means industry vertical
- No confusion between concern areas and industries

### 2. Composability
- Projects compose multiple domains
- Software + Healthcare, Software + Finance, etc.

### 3. Extensibility
- New industries don't require spec changes
- Anyone can create new domain manifests

### 4. Less Hierarchical
- Domains aren't "above" bundles, they're collections of bundles
- Reduces feeling of rigid hierarchy

### 5. Commercial Viability
- Professional domains (Legal, Clinical, Trading) are commercial offerings
- Software Development domain can be free/open
- Eclipse model: developers free, end users pay

### 6. Matches Existing Schema
- domain-manifest-schema.json already exists in codebase
- This model aligns with that schema

---

## The Business Model (Platform + Tools)

**The Model:**
SCS is a **platform business**, not a domain content business.

**Open Source (Platform):**
- SCS domain architecture and specifications
- Domain manifest schema
- Bundle/concern/SCD model
- Software Development domain (reference implementation)
- Tooling for creating domains

**Commercial (Tools & Services):**
- **Compliance agents** - Autonomic governance and compliance checking
- **Governance agents** - Decision tracking, approval workflows, audit trails
- **Validation platform** - Domain-aware validation and testing
- **Document extraction** - AI-powered bundle creation from existing docs
- **Professional services** - Help enterprises deploy and customize
- **Enterprise support** - Dedicated support, white-label, on-premise

**Why This Model Works:**

1. **We don't need domain expertise**
   - Domain experts (legal, clinical, finance professionals) create domains
   - We provide the framework and tools
   - Community builds the domain content

2. **Network effects**
   - More domains = more users = more tool sales
   - Domain creators become our ecosystem
   - We focus on what we're good at: architecture + automation

3. **Clear monetization**
   - Tools have recurring revenue (SaaS subscriptions)
   - Professional services scale with enterprise adoption
   - Not dependent on creating domain content ourselves

4. **Faster growth**
   - 10 domain experts can build 10 domains in parallel
   - We're not bottlenecked by our own domain knowledge
   - Quality is higher (built by actual experts)

**Analogies:**
- **Kubernetes:** Platform = open, tools (Datadog, etc.) = commercial
- **WordPress:** CMS = open, hosting/plugins = commercial
- **Red Hat:** Linux = open, enterprise tools/support = commercial

---

## Value Proposition by Domain

### For Software Developers (Free Domain):
- AI coding assistants work within architectural constraints
- Governance agents validate compliance automatically
- Traceability from requirements to code
- Autonomic compliance checking

### For Legal Professionals (Paid Domain):
- AI assistance that understands legal context and rules
- Case management within proper legal frameworks
- Compliance tracking for bar requirements
- Audit trails for professional liability

### For Clinicians (Paid Domain):
- AI clinical decision support within medical guidelines
- Patient safety constraints enforced
- HIPAA compliance built-in
- Evidence-based medicine references

### For Traders (Paid Domain):
- AI market analysis within risk parameters
- Regulatory compliance (SEC, FINRA) enforced
- Portfolio constraints respected
- Audit trails for compliance

---

## Decisions Made

### 1. Bundle Types - DECIDED ✓

**Added 5th bundle type: `"concern"`**

Bundle types are now:
1. `type: "project"` - top-level project bundle
2. `type: "meta"` - foundational vocabulary (universal)
3. `type: "standards"` - compliance/regulatory bundles
4. `type: "concern"` - functional area bundles (Architecture, Security, etc.)
5. `type: "domain"` - industry vertical bundles (entry point for end user types)

**Hierarchy:**
- Domain bundles (type: domain) contain/import Concern bundles (type: concern)
- Concern bundles (type: concern) contain SCDs

### 2. Domain Imports - DECIDED ✓

**Transitive import model**

When a project imports a domain, it automatically gets:
- All concern bundles listed in that domain
- All SCDs within those concerns
- Domain-specific validation rules
- Domain-specific tooling and templates

```yaml
# User selects domain → gets everything
id: bundle:my-project
type: project
imports:
  - domain:software-development:1.0.0  # ← brings in all 11 concerns + validator + tools
```

**Domain = complete distribution package for an end user type**

### 3. The 11 Prescribed Bundles - DECIDED ✓

**NO universal prescribed bundles**

- The 11 bundles (Architecture, Security, Performance, etc.) are **specific to Software Development domain**
- Legal domain has completely different concerns (Case Management, Legal Research, etc.)
- Sales domain has completely different concerns (Lead Qualification, Territory Management, etc.)
- Each domain defines its own concerns based on end user needs
- There is **no such thing as a "prescribed bundle"** across all domains

### 4. Versioning - DECIDED ✓

**All bundles follow same versioning rules**

- Domain bundles (type: domain) → same versioning rules
- Concern bundles (type: concern) → same versioning rules
- Meta, Standards, Project bundles → same versioning rules

**Rules:**
- Start in `DRAFT` state (mutable)
- Lock with semantic version (e.g., `1.0.0`) → immutable
- Changes require new version (e.g., `1.1.0`)
- Bundle references include explicit versions

**No special cases for domains.** Clean and consistent.

### 5. Meta and Standards Bundles - DECIDED ✓

**Meta: Universal**
- All domains use the same meta bundle
- `bundle:meta:1.0.0` is referenced by every domain

**Standards: Domain-agnostic but selectively imported**
- Standards bundles are created by compliance agencies (internal or external)
- Standards are domain-agnostic (HIPAA is the same regardless of domain)
- Domains import the standards relevant to their users
- Example: `bundle:standards:hipaa:1.0.0` can be imported by Software Development, Clinical, and Legal domains

---

## Core Design Principles - ESTABLISHED ✓

### Bottom-Up Reusability

1. **SCDs are general-purpose** (as much as practical)
   - An SCD can be included in multiple bundles
   - Avoid domain-specific SCDs when possible
   - Example: An SCD about "role-based access control" can be used across multiple concerns/domains

2. **Bundles are reusable**
   - A concern bundle can be imported by multiple domains
   - Example: A "Security" concern bundle might be used by Software Development, Legal, and Sales domains

3. **Maximum reusability at all levels**
   - SCDs are atomic, reusable building blocks
   - Concerns can be shared across domains
   - Domains compose the concerns appropriate for their end users

---

## Next Steps

1. Update bundle schema to add `type: "concern"`
2. Update domain manifest schema to align with decisions
3. Update documentation to reflect new mental model
4. Create example domains (Software Development is reference, Legal/Sales/Clinical as examples)
5. Update validator to support new bundle types
6. Plan migration path for existing bundles

---

## Risks / Concerns

### Complexity
- Adding domains as a layer between projects and bundles adds complexity
- Need to ensure this doesn't make the system too hard to understand

### Breaking Changes
- Current spec has projects importing bundles directly
- This model has projects importing domains (which contain bundles)
- Migration path needed

### Scope Creep
- Creating domains for Legal, Clinical, Finance is a HUGE undertaking
- Each requires deep domain expertise
- Need to stay focused on Software Development domain first as proof-of-concept

---

## Success Criteria

We'll know this model works if:

1. **Clear separation** between industry verticals (domains) and concern areas (bundles)
2. **Easy composition** - projects can easily combine multiple domains
3. **Extensible** - new industries can create domain manifests without changing SCS spec
4. **Commercial viability** - clear path to monetize professional domains
5. **Not overly complex** - model is understandable to users in different professions

---

## References

- Current bundle schema: `schema/bundles/scd-bundle-schema.json`
- Current domain manifest schema: `schema/domain/domain-manifest-schema.json`
- Bundle format spec: `spec/0.1/bundle-format.md`
- Terminology: `spec/0.1/terminology.md`
