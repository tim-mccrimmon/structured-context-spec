# Structured Context Specification (SCS) — Overview
**Version:** 0.5.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-09-22

---

## 1. Introduction

**If you are using AI and not using Structured Context - you are doing it wrong.**

AI is transforming professional work across all domains:
- **Legal aids** draft contracts and analyze case law
- **Clinicians** diagnose conditions and recommend treatments
- **Financial analysts** evaluate portfolios and assess risk
- **Sales professionals** qualify leads and generate proposals
- **Software developers** write code and design systems

But AI remains unreliable without **clear, structured, machine-readable context**.

Professionals across all domains face the same challenges:

- critical knowledge is scattered across documents
- requirements and constraints are buried in emails and meetings
- compliance information is lost in PDFs
- expert judgment and decision rationale are rarely preserved
- governance depends on meetings instead of data
- context crucial for AI assistance is unavailable

The **Structured Context Specification (SCS)** provides a unified, domain-agnostic model for capturing, organizing, and evolving professional context in a way that is:

- human-readable
- machine-readable
- versionable
- enforceable
- governable
- and directly consumable by AI agents

SCS is not a programming framework or industry-specific tool.
It is a **universal context framework** — a platform for representing the truth of professional work across all domains.

---

## 2. What SCS Provides

SCS defines:

- a standardized structure for **SCDs** (Structured Context Documents)
- a consistent way to bundle SCDs into **domain-specific contexts**
- **domain manifests** with a **Domain Ontology** — each domain's own concepts, taxonomy,
  and relationships (RFC-0001)
- **concept bundles** that organize functional areas within domains
- schemas that ensure machine interpretability
- semantics that enable tools and AI agents to reason over professional work
- a governance-friendly, standards-friendly model
- a way to align universal vocabulary, domain standards, and project specifics

In short:
**SCS makes professional context a first-class, version-controlled, domain-aware artifact.**

### Multi-Domain Platform

SCS 0.5.0 introduces a **platform model** supporting multiple professional domains:

- **Software Development** (reference implementation) - architecture, testing, deployment
- **Legal** - case management, legal research, document drafting
- **Clinical** - patient care, treatment protocols, clinical decision support
- **Financial** - portfolio management, risk assessment, compliance
- **And more...** - any professional domain can define its own concepts and context structure

Each domain is created by **domain experts** in their field, not by SCS maintainers. SCS provides the platform; domain experts provide the expertise.

---

## 3. Motivation

Without structured context, AI-assisted professional work is unpredictable across all domains.

AI cannot reliably:

- generate correct deliverables (code, contracts, treatment plans, financial models)
- maintain domain coherence (architecture, case strategy, clinical protocols, risk models)
- enforce professional constraints and standards
- reason about impact of changes
- evaluate compliance with regulations
- support governance and decision-making
- help teams stay aligned with domain expertise

Professionals also cannot reliably:

- preserve expert judgment and decision rationale
- maintain consistency across work products
- ensure compliance with domain-specific regulations
- trace decisions back to requirements
- understand dependencies and impacts
- scale expertise across contributors
- onboard new team members effectively

**The Reliability Problem is Universal**

Whether you're:
- Building software that must meet HIPAA requirements
- Managing legal cases with strict confidentiality rules
- Providing clinical care with evidence-based protocols
- Advising clients on financial compliance

You face the same fundamental challenge: **AI cannot help reliably without structured context.**

SCS solves this by redefining **context** as the shared substrate across:

- humans
- teams
- domain experts
- tools
- and AI agents  

---

## 4. Core Concepts

### 4.1 Structured Context Document (SCD)

An **SCD** is the atomic unit of SCS.

Each SCD describes a coherent slice of system context, such as:

- architecture component  
- domain model  
- compliance requirement  
- quality attribute  
- data flow  
- governance rule  
- operational constraint  
- performance expectations  
- security posture  

Every SCD is:

- structured  
- typed  
- versioned  
- machine-readable  
- linkable to other SCDs  
- independently reviewable  

---

### 4.2 SCD Tiers

SCS organizes SCDs into **three tiers**, each serving a different purpose.

#### **1. Meta-Tier SCDs**  
Define universal semantics for a system:

- roles  
- capabilities  
- domain concepts  
- cross-cutting concerns  
- naming conventions  
- system-wide intent  
- meta-structures  

Meta-tier SCDs shape the “language” the rest of the system uses.

#### **2. Standards-Tier SCDs**  
Represent external standards, including:

- CHAI adherence  
- HIPAA  
- SOC2  
- ISO 27001  
- PCI  
- internal policies  

Standards-tier SCDs serve as **importable compliance contracts**.

#### **3. Project-Tier SCDs**  
Describe the actual system being built:

- architecture  
- modules  
- features  
- security policies  
- requirements  
- workflows  
- constraints  
- connections to standards  

This tier is unique to each project.

---

## 5. Bundles and Domains

### 5.1 Bundles

A **bundle** is a manifest document that organizes and references SCDs and other bundles. Bundles are NOT SCDs themselves - they are container documents similar to Docker manifests.

SCS 0.5.0 defines **five bundle types**:

1. **Project Bundle** - Top-level orchestrator for complete project context
2. **Meta Bundle** - Universal vocabulary and semantic foundations
3. **Standards Bundle** - Compliance and regulatory requirements
4. **Concept Bundle** - A Domain Ontology concept, realized as SCDs (Architecture, Security, etc.)
5. **Domain Bundle** - Industry vertical (Software Development, Medical-Device CDMO, Legal, etc.)

Bundles enable:

- domain-specific context organization
- consistent structure across industries
- versioned evolution, with an explicit approval step once a bundle leaves `DRAFT`
  (`terminology.md` §2.16)
- interoperability across tools
- AI-based reasoning within domain context
- governance and compliance checks

**Hierarchy**: Project → Domain → Concept → SCD

### 5.2 Domains

A **domain** represents an industry vertical or professional practice area. Each domain:

- Defines its own **Domain Ontology** — concepts, optional taxonomy, optional relationships
  (`domain-ontology.md`, RFC-0001)
- Provides domain-specific content schemas for SCDs
- Includes templates and validation rules
- Is created by domain experts in that field

**Software Development Domain** (Reference Implementation):
- 11 concept bundles: Architecture, Security, Performance, Testing, Deployment, etc.
- Flat ontology — no taxonomy or relationships modeled yet
- Provides templates for software engineering context

**Medical-Device CDMO Domain** (Reference Implementation for ontology depth):
- 12 concept bundles adapted from the Software Development set, for a regulated
  medical-device contract manufacturer
- Full ontology depth: relationships between concepts, and a `satisfies` mapping from each
  concept to the ISO 13485 / IEC 62304 / 21 CFR 820 / ISO 14971 clauses it exists to address
- Shows what a domain looks like once "does our context cover regulation X?" needs to be a
  machine-answerable question, not just a functional grouping

**Future Domains** (created by domain experts):
- Legal, Clinical, Financial, Trading, Sales, Education, etc.
- Each starts from an existing **Ontology Model** (`terminology.md` §2.14) — SDLC, CDMO, or
  a new one — rather than authoring an ontology from a blank page

Tools built on SCS (e.g., Viewer/Editor, Evaluator, Validator) are domain-aware and operate at the bundle level.

---

## 6. Scope of the 0.5.0 Specification

0.5.0 is a breaking change, anchored on the **Domain Ontology** (RFC-0001): "concern" is
fully retired in favor of "concept," and each domain's set of concepts becomes an explicit,
structured artifact rather than an implicit flat list. Carried over unchanged from 0.3:
SCD structure, the three-tier model, the five-bundle-type model, and multi-domain
architecture.

**Key Additions in 0.5.0:**
- The **Domain Ontology**: concepts, optional taxonomy (`parent`), optional typed
  relationships (`depends-on`, `relates-to`, `satisfies`) — lives in the domain manifest's
  `ontology` block, replacing the flat `concerns` list
- **Ontology Models**: a domain instantiates a reusable model (SDLC, CDMO, and eventually
  others) rather than authoring an ontology from scratch
- **Bundle approval provenance**: `version_approved_by` / `version_approved_at`, required
  once a bundle leaves `DRAFT` — a bundle is not just authored, it's approved
- The **Medical-Device CDMO domain**, as the reference example for ontology depth
- Cross-domain concept sharing, which 0.3 assumed ("concerns are reusable across domains"),
  is explicitly not pursued — concepts are domain-scoped; Ontology Models are the reuse unit

0.5.0 establishes the foundation for a **multi-domain platform** where domain experts can create their own professional context frameworks.

---

## 7. Out of Scope (For 0.5.0)

The following will be addressed in later versions:

- enforcement of cross-SCD relationships
- full semantic validation across tiers
- automated compliance mapping
- governance decision frameworks
- lifecycle and workflow specifications
- SCS Tooling Suite full implementations
- domain-specific SCD libraries beyond Software Development
- domain registry and marketplace
- domain versioning and compatibility rules
- cross-domain dependency management  

---

## 8. Guiding Principles

SCS is based on a few core principles:

1. **Context is the source of truth.**  
2. **Humans and AI operate from the same structure.**  
3. **Every SCD is independent, testable, and versionable.**  
4. **Standards should be importable, not reinvented.**  
5. **Governance must be context-driven, not meeting-driven.**  
6. **Project context must be transparent and inspectable.**  
7. **SCS is descriptive, not prescriptive.**  
8. **Tools should be optional, but powerful.**

---

## 9. Intended Audience

SCS is intended for **professionals using AI assistance across all domains**:

**Software Development:**
- architects, developers, DevOps engineers
- AI-assisted development teams
- technical governance officers

**Legal:**
- attorneys, paralegals, legal aids
- compliance officers
- contract managers

**Clinical/Healthcare:**
- clinicians, nurses, medical researchers
- clinical decision support specialists
- healthcare compliance teams

**Financial:**
- financial analysts, advisors
- risk management professionals
- regulatory compliance teams

**Cross-Domain:**
- governance officers
- standards bodies
- auditors
- compliance teams
- domain experts creating new domains
- tool builders creating domain-aware AI assistants

Anyone who needs to provide reliable, structured context to AI systems while maintaining professional standards, compliance, and governance.

---

## 10. Relationship to AI-Native Professional Work

SCS provides the **structured context** that AI assistants and governance agents need across all professional domains.

This includes:

- consistent inputs for AI reasoning
- persistent context across sessions
- explainable representations of professional work
- foundations for autonomic governance
- reliable data for AI-assisted deliverable generation
- stable references for expert decisions and domain knowledge
- domain-specific validation and compliance checking

Without SCS, AI-native professional work is brittle and unreliable.
With SCS, it becomes structured, predictable, and governable across all domains.

---

## 11. Specification Documents

The SCS 0.5.0 specification includes:

- **terminology.md** - Definitions of core concepts, domains, and bundle types
- **core-model.md** - The foundational SCD/tier/bundle/relationship model
- **bundle-format.md** - Detailed bundle structure, types, and validation rules
- **domain-ontology.md** - The Domain Ontology: concepts, taxonomy, relationships, Ontology
  Models, bundle approval provenance (RFC-0001)
- **meta-tier.md**, **standards-tier.md**, **project-tier.md** - SCD structure per tier
- **governance-and-compliance.md** - How SCDs support compliance and autonomic governance
- **../../schema/** - JSON schemas for bundles, domain manifests, and SCDs
- **../../examples/** - Complete working examples, including the Software Development and
  Medical-Device CDMO domains

These documents together form the complete SCS 0.5.0 specification.

**For Domain Experts:**
If you want to create a domain for your professional field (Legal, Clinical, Financial, etc.), start with `domain-ontology.md` and an existing Ontology Model (Software Development or Medical-Device CDMO) as a reference.

---

## 12. Feedback

All feedback should be submitted through GitHub Issues.  
Pull Requests are welcome for:

- corrections  
- clarifications  
- examples  
- improvements  

The specification is developed openly and collaboratively.