# Structured Context Specification (SCS) — Overview
**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-25

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
- a governance-friendly model, with **citation references** that trace rules to external
  standards without reproducing their text
- two independent governance bundles: an organization's **Domain** bundle and each
  project's **Project** bundle

In short:
**SCS makes professional context a first-class, version-controlled, domain-aware artifact.**

### Multi-Domain Platform

SCS (since 0.5.0) provides a **platform model** supporting multiple professional domains:

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

SCS organizes SCDs into tiers. Two are active in 0.6.0, Meta and Project; the Standards
tier is deprecated.

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

#### **2. Project-Tier SCDs**  
Describe an organization's rules (in its Domain bundle) or the actual project or system
being built (in a Project bundle):

- architecture  
- modules  
- features  
- security policies  
- requirements  
- workflows  
- constraints  
- citations of the standards they implement  

#### **Standards-Tier SCDs (deprecated)**  
Deprecated in 0.6.0. Standards such as ISO 13485, HIPAA or SOC 2 are no longer
represented as SCDs. A rule that implements a standard cites it with a citation reference
(`std:iso-13485:2016#7.3.9`), which names edition and clause but carries no standard text.
See `standards-tier.md` and `citations.md`.

---

## 5. Bundles and Domains

### 5.1 Bundles

A **bundle** is a manifest document that organizes and references SCDs and other bundles. Bundles are NOT SCDs themselves - they are container documents similar to Docker manifests.

SCS 0.6.0 defines **five bundle types**, one of them deprecated:

1. **Domain Bundle** - An organization's governance, applied to every project (deployments
   often call it "Global"). It pins the Meta bundle and imports concept bundles holding the
   organization's rules. An industry Ontology Model (Software Development, Medical-Device
   CDMO, Merchant Cash Advance) is its template; the organization's Domain bundle is that
   ontology filled in and approved.
2. **Project Bundle** - One project's governance only. Independent of the Domain bundle and
   does not repeat it.
3. **Meta Bundle** - Universal vocabulary, published and versioned with the SCS
   specification; read-only to adopters
4. **Concept Bundle** - A Domain Ontology concept, realized as SCDs (Architecture, Security, etc.)
5. **Standards Bundle** - Deprecated in 0.6.0; replaced by citation references

Bundles enable:

- domain-specific context organization
- consistent structure across industries
- versioned evolution, with an explicit approval step once a bundle leaves `DRAFT`
  (`terminology.md` §2.16)
- interoperability across tools
- AI-based reasoning within domain context
- governance and compliance checks

**Structure**: two independent trees — Domain → Meta + Concept → SCD, and
Project → SCD (or Project → Concept → SCD). Neither requires the other.

### 5.2 Domains

A **domain** represents an industry vertical or professional practice area, and an
organization's Domain bundle is that domain specialized with the organization's own rules.
Each domain:

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
  concept to citation references for the ISO 13485 / IEC 62304 / 21 CFR 820 / ISO 14971
  clauses it exists to address
- Shows what a domain looks like once "does our context cover regulation X?" needs to be a
  machine-answerable question, not just a functional grouping

**Merchant Cash Advance (MCA) Domain** (Reference Ontology for business funding):
- 16 concepts in three clusters: nine industry-native (origination, underwriting and
  decisioning, contract characterization, servicing and collections, ...), three
  infrastructure, and four universal AI-governance concepts
- A small set of `depends-on` / `relates-to` relationships; best-practice AI governance, so it
  deliberately carries no regulatory `satisfies` mapping
- A customer-neutral skeleton SCD and concept bundle for each concept, under
  `examples/merchant-cash-advance/`: every field a `TODO`, ready to be filled with real decisions
- Shows that the ontology follows the industry: the concepts an MCA funder needs have no home
  in the software or medical-device shapes

**Future Domains** (created by domain experts):
- Legal, Clinical, Financial, Trading, Sales, Education, etc.
- Each starts from an existing **Ontology Model** (`terminology.md` §2.14) — SDLC, CDMO, MCA, or
  a new one — rather than authoring an ontology from a blank page

Tools built on SCS (e.g., Viewer/Editor, Evaluator, Validator) are domain-aware and operate at the bundle level.

---

## 6. Scope of the 0.6.0 Specification

0.6.0 separates governance into two independent bundles and retires standards-as-SCDs:

- **Domain and Project bundles are independent.** A Domain bundle is the organization's
  governance and imports the pinned Meta bundle plus concept bundles. A Project bundle holds
  only project governance and MUST NOT import Meta or Domain bundles. Either may exist
  without the other.
- **Meta** is published with the specification, not authored by adopters.
- **Standards bundles and the Standards tier are deprecated**, replaced by citation
  references (`citations.md`).

0.5.0 was a breaking change, anchored on the **Domain Ontology** (RFC-0001): "concern" is
fully retired in favor of "concept," and each domain's set of concepts becomes an explicit,
structured artifact rather than an implicit flat list. Carried over unchanged from 0.3:
SCD structure, the three-tier model, the five-bundle-type model, and multi-domain
architecture.

**Key Additions in 0.5.0:**
- The **Domain Ontology**: concepts, optional taxonomy (`parent`), optional typed
  relationships (`depends-on`, `relates-to`, `satisfies`) — lives in the domain manifest's
  `ontology` block, replacing the flat `concerns` list
- **Ontology Models**: a domain instantiates a reusable model (SDLC, CDMO, MCA, and eventually
  others) rather than authoring an ontology from scratch
- **Bundle approval provenance**: `version_approved_by` / `version_approved_at`, required
  once a bundle leaves `DRAFT` — a bundle is not just authored, it's approved
- The **Medical-Device CDMO domain**, as the reference example for ontology depth
- The **MCA (merchant cash advance) ontology**, as the reference for a third industry
- Cross-domain concept sharing, which 0.3 assumed ("concerns are reusable across domains"),
  is explicitly not pursued — concepts are domain-scoped; Ontology Models are the reuse unit

0.5.0 establishes the foundation for a **multi-domain platform** where domain experts can create their own professional context frameworks.

---

## 7. Out of Scope (For 0.6.0)

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
4. **Standards are cited, not reproduced.**  
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

The SCS 0.6.0 specification includes:

- **terminology.md** - Definitions of core concepts, domains, and bundle types
- **core-model.md** - The foundational SCD/tier/bundle/relationship model
- **bundle-format.md** - Detailed bundle structure, types, and validation rules
- **domain-ontology.md** - The Domain Ontology: concepts, taxonomy, relationships, Ontology
  Models, bundle approval provenance (RFC-0001)
- **meta-tier.md**, **project-tier.md** - SCD structure per tier
- **standards-tier.md** - Deprecation of the Standards tier and migration
- **citations.md** - Standard citation references
- **runtime-artifact.md** - Compiled runtime artifacts for Domain and Project bundles
- **governance-and-compliance.md** - How SCDs support compliance and autonomic governance
- **../../schema/** - JSON schemas for bundles, domain manifests, and SCDs
- **../../examples/** - Complete working examples, including the Software Development and
  Medical-Device CDMO domains

These documents together form the complete SCS 0.6.0 specification.

**For Domain Experts:**
If you want to create a domain for your professional field (Legal, Clinical, Financial, etc.), start with `domain-ontology.md` and an existing Ontology Model (Software Development, Medical-Device CDMO, or Merchant Cash Advance) as a reference.

---

## 12. Feedback

All feedback should be submitted through GitHub Issues.  
Pull Requests are welcome for:

- corrections  
- clarifications  
- examples  
- improvements  

The specification is developed openly and collaboratively.