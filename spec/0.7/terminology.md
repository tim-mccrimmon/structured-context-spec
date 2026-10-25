# SCS 0.7.0 — Terminology
**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-25  

---

## 1. Purpose

This document defines the terminology used throughout the Structured Context Specification (SCS).  
Terms defined here are considered **normative** for all SCS documents unless explicitly stated otherwise.

Clear terminology ensures that humans, tools, and AI agents interpret SCS consistently.

---

## 2. Core Concepts

### **2.1 Context**
Information that describes the structure, behavior, intent, constraints, responsibilities, or requirements of a system.

Context includes:
- architecture  
- requirements  
- compliance expectations  
- operational constraints  
- performance goals  
- security posture  
- design intent  
- domain concepts  

SCS treats context as a first-class artifact.

---

### **2.2 Structured Context**
Context represented in a **machine-readable**, **human-readable**, and **version-controlled** form.

Structured context is:
- explicit  
- precise  
- hierarchical  
- linkable  
- analyzable  
- AI-interpretable  

SCDs (Structured Context Documents) are the units of structured context.

---

### **2.3 Structured Context Document (SCD)**  
A **self-contained, typed, versioned document** that represents a coherent slice of system context.

An SCD includes:
- metadata  
- descriptive fields  
- requirements or constraints  
- relationships to other SCDs  
- references to standards or domains  

SCDs are the foundational building blocks of SCS.

---

### **2.4 SCD Type**
Each SCD belongs to exactly one SCS tier:

1. **Meta-Tier** — system-level semantics and conceptual framing  
2. **Project-Tier** — the organization's or project's own context and rules
3. **Standards-Tier** — *deprecated in 0.6.0*; standards are cited instead (§3.2)

The SCD type determines:
- semantic role  
- schema used  
- allowed references  
- placement in bundles  

---

### **2.5 Bundle**
A **manifest document** that organizes and references SCDs and other bundles. Bundles are NOT SCDs themselves - they are container documents similar to Docker manifests or Kubernetes pod specifications.

Bundles:
- organize SCDs into logical groupings
- reference other bundles (imports)
- define boundaries and scope
- are versioned as immutable contracts, except a `DRAFT` working bundle (see §2.16)
- serve as the unit of analysis for tools
- come in four types: domain, project, meta, concept (a fifth, standards, is deprecated in 0.6.0)

See section 2.15 for detailed bundle type definitions.

---

### **2.6 Identifier**
A unique, stable identifier assigned to each SCD, used for:

- cross-SCD linking  
- external references  
- traceability  
- versioning  
- tool interoperability  

Identifiers should follow SCS naming conventions (defined in future versions).

---

### **2.7 Relationship**
A typed connection between SCDs.

Examples include:
- *depends-on*  
- *constrains*  
- *extends*  
- *refines*  
- *satisfies*  
- *conflicts-with*  

Relationships support reasoning, impact analysis, and governance.

---

### **2.8 Constraint**
Any requirement, limit, rule, or boundary imposed on the system.

Examples:
- security constraints  
- architectural constraints  
- performance thresholds  
- compliance rules  
- data retention limits  

Constraints may originate from project needs or external standards.

---

### **2.9 Requirement**
An obligation, behavior, or condition the system must fulfill.

Requirements may be:
- functional  
- non-functional  
- compliance-driven  
- architectural  
- operational  

SCDs may define or reference requirements.

---

### **2.10 Capability**
A unit of system functionality or behavior.

Capabilities describe:
- what the system can do  
- the roles involved  
- affected domains  
- relationships to requirements  

Capabilities are often organized in Meta- or Project-Tier SCDs.

---

### **2.11 Domain**
An **organization** (or an organizational unit with its own governance authority) and the
governance context that applies across it, carried in a **Domain bundle**. Deployments often
call this the **Global** context; "organization", "domain", and "global" name the same thing
for different audiences.

An industry and an organization are the same kind of domain at different levels of detail.
An industry is described by an **Ontology Model** (2.14): concepts, skeleton SCDs, and open
decisions. An organization's Domain bundle is that model filled in with its own decisions and
approved. Only the organization's version is governance.

The SCS reference Ontology Models cover these industries:
- **Software Development** - Software engineering practices, architecture, testing, deployment
- **Medical-Device CDMO** - Regulated QMS work, computer-system validation, AI governance for medical-device contract manufacturers
- **Merchant Cash Advance (MCA)** - Origination, underwriting, contract characterization, servicing and collections, AI governance for business-funding providers
- **Legal** - Case management, legal research, document drafting, client communication
- **Clinical** - Patient care workflows, clinical decision support, treatment protocols
- **Financial** - Portfolio management, risk assessment, compliance

Each reference domain is defined by:
- A domain manifest (separate specification document) — see **2.13 Domain Ontology**
- A set of concept bundles relevant to that domain
- Domain-specific content schemas for SCDs
- Templates and validation rules

The SCS validator enforces only structural rules for Domain bundles, not what organizational
unit one represents. See [Bundle Format §3.6](bundle-format.md) for scoping guidance.

**Note:** SCS provides the **Software Development domain** and the **Medical-Device CDMO domain** as reference implementations — the latter specifically to show what a Domain Ontology looks like with real depth (taxonomy, relationships, regulatory `satisfies` mapping). Other domains are created by domain experts in their respective fields.

---

### **2.12 Concept**
A **named category of domain knowledge** — the structural building block a domain organizes its context around. Replaces "concern" (SCS 0.3 and earlier; retired in 0.5.0, RFC-0001).

Concepts represent:
- Functional responsibilities (Architecture, Security, Performance)
- Cross-cutting aspects (Testing, Deployment, Compliance)
- Areas of expertise within a domain
- Coherent groupings of related SCDs

Unlike concerns in 0.3, **concepts are domain-scoped, not reusable across domains** — this was
explicitly decided and parked indefinitely (RFC-0001): a CDMO's `concept:risk-management` and a
software project's `concept:security` are each defined once, inside their own domain's ontology,
not shared. What *is* reusable across companies in the same market is the **Ontology Model**
(2.14) a domain's ontology is built from — not individual concepts.

A concept MAY have:
- a **parent** (optional shallow taxonomy)
- **relationships** to other concepts (`depends-on`, `relates-to`) or to standard citations (`satisfies`, see `citations.md`)
- a **bundle** — the concept bundle realizing it

Each concept is packaged as a **concept bundle** containing related SCDs.

**Example concepts (Software Development domain):**
- Architecture - System structure, components, integration
- Security - Threat model, access control, data protection
- Performance & Reliability - SLAs, scalability, fault tolerance
- Testing & Validation - Test strategy, coverage, quality assurance

---

### **2.13 Domain Ontology**
A domain's model of the concepts that structure its work: **concepts**, an optional
**taxonomy** (parent/child), and optional **relationships** between them (RFC-0001). Lives
in the **domain manifest**, in an `ontology` block. Full normative treatment:
`domain-ontology.md`.

The smallest valid Domain Ontology is a flat list of concept names — the same shape "concerns"
had, minus the name and the false claim of cross-domain reusability. Depth (taxonomy,
relationships, a `satisfies` mapping to cited regulatory standards) is added incrementally, and is
expected in regulated domains where "does our context cover clause X?" needs to be a
machine-answerable question.

---

### **2.14 Ontology Model**
A Domain Ontology authored once per **type of business** (a market/industry vertical), not
once per company. So far there are three known: **SDLC** (the original "concerns" list,
generalized software product-plan structure), **CDMO** (medical-device contract
manufacturing — risk management, design controls, supplier qualification, and more that the
SDLC shape has no home for), and **MCA** (merchant cash advance / business funding:
origination, underwriting and decisioning, contract characterization, servicing and
collections, and more).

An Ontology Model is the template for an organization's Domain bundle (2.11, 2.15).
Adopting SCS starts with choosing an Ontology Model — using an existing one if it fits, or
adapting the nearest one — not authoring an ontology from a blank page. How a model is
packaged, versioned, and referenced independently of a specific domain manifest is not yet
specified (RFC-0001, Unresolved Questions).

---

### **2.15 Bundle Types**
SCS 0.6.0 defines four bundle types, plus one deprecated type. Domain and Project bundles are
the two **governance bundles**; they are independent, and either may exist without the other.

#### **Domain Bundle**
- **Purpose**: An organization's governance context (often called Global)
- **Imports**: One pinned meta bundle (SHOULD) and at least one concept bundle (MUST); MUST NOT import project or domain bundles
- **SCDs**: MUST NOT contain SCDs directly (the organization's rules live in its concept bundles)
- **Cardinality**: 1 per organization or deployment
- **Authored by**: The organization's governance or quality team, starting from an Ontology Model

#### **Project Bundle**
- **Purpose**: One project's governance context, and only that
- **Imports**: MAY import concept bundles; MUST NOT import meta, domain, project, or standards bundles
- **SCDs**: Project-tier SCDs directly, or through imported concept bundles (not both)
- **Cardinality**: 1 per project
- **Authored by**: The project team

#### **Meta Bundle**
- **Purpose**: Universal vocabulary and semantic foundations
- **Imports**: None (meta is the foundation)
- **SCDs**: Meta-tier SCDs defining roles, capabilities, concepts
- **Cardinality**: Published once per SCS release; pinned by Domain bundles
- **Authored by**: SCS specification maintainers; read-only to adopters

#### **Concept Bundle**
- **Purpose**: A Domain Ontology concept, realized as SCDs
- **Imports**: MUST NOT import other bundles (imports array MUST be empty)
- **SCDs**: MUST contain at least one project-tier SCD
- **Cardinality**: Variable (11 in Software Development domain, 12 in Medical-Device CDMO, 16 in MCA)
- **Reusability**: Domain-scoped, not reusable across domains (2.12) — the reusable unit is
  the Ontology Model (2.14), not the concept bundle itself

#### **Standards Bundle (deprecated)**
- Deprecated in 0.6.0. Standards are referenced by citation (`citations.md`), not bundled.

**Structure**: Domain → Meta + Concepts → SCDs; Project → SCDs (or Concepts → SCDs)

---

### **2.16 DRAFT and Approved Versions**
A bundle's `version` field is either `DRAFT` (mutable, working state — not yet reviewed) or
a semantic version like `1.0.0` (immutable once set). Only a real, non-`DRAFT` version
requires **approval** — `provenance.version_approved_by` and `version_approved_at`,
naming who signed off on this specific version (RFC-0001, single-source; not per-concept).
A `DRAFT` bundle has no approval fields because there is nothing yet to approve.

This is deliberately a bundle-level event, not a per-SCD one: an SCD's own `provenance`
records authorship only (`created_by`/`created_at`), regardless of whether the bundle
containing it is `DRAFT` or versioned.

---

### **2.17 Standard Citation**
A reference to an external standard, edition, and optionally a clause, in the form
`std:<standard>[:<edition>][#<clause>]` (e.g. `std:iso-13485:2016#7.3.9`). Citations appear
in an SCD's `cites` list and as `satisfies` targets. They carry no text from the standard and
are not resolved against any document. Full definition: `citations.md`.

---

## 3. Tiers

### **3.1 Meta-Tier**
Defines system-wide semantics, roles, cross-cutting structures, and conceptual framing.

Guides:
- how teams speak about the system  
- what concepts mean  
- how context is expressed  

The meta-tier is foundational.

---

### **3.2 Standards-Tier (deprecated)**
Deprecated in 0.6.0. External standards (HIPAA, SOC 2, ISO 13485, NIST 800-53, and so on)
are referenced by **citation** — `std:<standard>[:<edition>][#<clause>]` — from the SCDs and
concepts that address them. A citation carries no standard text. The organization's own
rules, which interpret a standard, are project-tier SCDs in its Domain bundle. See
`citations.md` and `standards-tier.md`.

---

### **3.3 Project-Tier**
Defines the rules and context an organization or project authors for itself: in a Domain
bundle, the organization's rules; in a Project bundle, the actual system being built.
The tier identifies the author, not the scope: scope comes from the bundle that includes the
SCD (`project-tier.md` §1). The name is historical; read it as "adopter-authored".

Project-tier SCDs include:
- architecture  
- modules  
- data flows  
- performance expectations  
- security posture  
- requirements  
- constraints  
- compliance mappings (as citations)  

---

### **3.4 "Corporate / Project / Personal" is Shorthand, Not a Fourth Tier**

Some material (`ROADMAP.md`, engagement-facing docs) describes coverage as Corporate and
Project context, with Personal deferred. "Corporate" means the Domain bundle (the pinned
meta bundle plus the organization's rules); "Project" means a Project bundle; "Personal"
(individual-level context, such as a user's own documents) is not governance and is out of
scope for SCS. See `core-model.md` §5.4 for the full mapping,
including why a "departmental" layer some engagements describe is a scope/audience
distinction, not a tier.

---

## 4. Governance and Traceability

### **4.1 Traceability**
The ability to follow a concept or requirement:

- from definition  
- to implementation  
- to verification  
- to governance evidence  

Traceability is achieved through SCD identifiers, relationships, and bundles.

---

### **4.2 Provenance**
Metadata describing the origin, authorship, changes, and decisions behind an SCD or bundle.

Provenance supports:
- auditing  
- compliance review  
- reproducibility  
- accountability  

---

### **4.3 Context Contract**
A versioned SCD bundle that defines the authoritative context of a system.

It is used by:
- human contributors  
- AI agents  
- governance systems  
- auditors  

The contract evolves through version-controlled change.

---

## 5. AI-Native Concepts

### **5.1 AI Agent**
Any AI system participating in the project lifecycle, including:

- code assistants  
- evaluators  
- governance agents  
- analysis tools  
- documentation assistants  

AI agents consume and produce structured context.

---

### **5.2 Human Contributor**
Any human involved in the definition, development, or governance of a system.

Humans and AI collaborate through shared structured context.

---

### **5.3 Autonomic Governance**
Continuous, AI-driven evaluation of a system’s:

- compliance  
- architecture  
- constraints  
- quality attributes  
- changes over time  

Autonomic governance relies on SCDs and bundles.

---

## 6. Documents in This Specification

### **6.1 Specification**
Authoritative normative documents that define SCS.

Found in the `/spec/` directory.

---

### **6.2 Schema**
Machine-readable definitions for SCD structure.

Found in the `/schema/` directory.

---

### **6.3 Template**
Starter SCD documents for human authors.

Found in the `/templates/` directory.

---

### **6.4 Example**
Concrete, realistic SCD bundles demonstrating SCS use.

Found in the `/examples/` directory.

---

## 7. Feedback

All terminology feedback should be submitted via GitHub Issues for review and incorporation.