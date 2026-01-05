# SCS 0.3 — Terminology
**Version:** 0.3 (Draft)
**Status:** Work in Progress
**Last Updated:** 2025-12-15  

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
Each SCD belongs to exactly one of the three SCS tiers:

1. **Meta-Tier** — system-level semantics and conceptual framing  
2. **Standards-Tier** — imported or codified compliance/spec standards  
3. **Project-Tier** — system-specific context for the project

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
- are versioned as immutable contracts
- serve as the unit of analysis for tools
- come in five types: project, meta, standards, concern, domain

See section 2.13 for detailed bundle type definitions.

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
An **organizational unit** for which SCS provides structured context aggregation through Domain bundles.

The SCS reference implementation uses domains to represent **industry verticals** or **professional practice areas**:
- **Software Development** - Software engineering practices, architecture, testing, deployment
- **Legal** - Case management, legal research, document drafting, client communication
- **Clinical** - Patient care workflows, clinical decision support, treatment protocols
- **Financial** - Portfolio management, risk assessment, compliance

Each reference domain is defined by:
- A domain manifest (separate specification document)
- A set of concern bundles relevant to that domain
- Domain-specific content schemas for SCDs
- Templates and validation rules

**Alternative Organizational Scopes:**

Implementations may use Domain bundles to represent other organizational units beyond industry verticals:
- **Companies/Enterprises** (e.g., `bundle:acme-health-corp`) - Corporate knowledge aggregators
- **Business Units/Divisions** (e.g., `bundle:acme-radiology-division`) - Divisional context
- **Product Lines** (e.g., `bundle:acme-patient-portal`) - Product-specific context

The SCS validator enforces only structural rules (Domain bundles must import concerns and contain no direct SCDs), not semantic meaning. See [Bundle Format - Alternative Domain Bundle Uses](bundle-format.md#alternative-domain-bundle-uses) for detailed guidance.

**Note:** SCS 0.3 provides the **Software Development domain** as a reference implementation. Other domains are created by domain experts in their respective fields.

---

### **2.12 Concern**
A **functional area** or **cross-cutting aspect** of work within a domain.

Concerns represent:
- Functional responsibilities (Architecture, Security, Performance)
- Cross-cutting aspects (Testing, Deployment, Compliance)
- Areas of expertise within a domain
- Coherent groupings of related SCDs

Concerns are **reusable across domains**. For example:
- The **Security concern** is relevant to Software Development, Legal, and Clinical domains
- The **Compliance & Governance concern** applies across many professional domains
- The **Communication concern** is shared across Legal, Clinical, and Sales domains

Each concern is packaged as a **concern bundle** containing related SCDs.

**Example concerns (Software Development domain):**
- Architecture - System structure, components, integration
- Security - Threat model, access control, data protection
- Performance & Reliability - SLAs, scalability, fault tolerance
- Testing & Validation - Test strategy, coverage, quality assurance

---

### **2.13 Bundle Types**
SCS 0.3 defines five bundle types, each with distinct purpose and rules:

#### **Project Bundle**
- **Purpose**: Top-level orchestrator for a complete project
- **Imports**: Meta, standards, and domain bundles
- **SCDs**: Typically empty (all context comes from imports)
- **Cardinality**: 1 per project

#### **Meta Bundle**
- **Purpose**: Universal vocabulary and semantic foundations
- **Imports**: None (meta is the foundation)
- **SCDs**: Meta-tier SCDs defining roles, capabilities, concepts
- **Cardinality**: 1 per project (imported from SCS specification)

#### **Standards Bundle**
- **Purpose**: Compliance and regulatory requirements
- **Imports**: May import other standards bundles
- **SCDs**: Standards-tier SCDs (regulatory mappings, compliance rules)
- **Cardinality**: 1+ per project (as needed for compliance)

#### **Concern Bundle**
- **Purpose**: Functional area or cross-cutting concern
- **Imports**: MUST NOT import other bundles (imports array MUST be empty)
- **SCDs**: MUST contain at least one project-tier SCD
- **Cardinality**: Variable (11 in Software Development domain)
- **Reusability**: Concerns are reusable across multiple domains

#### **Domain Bundle**
- **Purpose**: Industry vertical or professional practice area
- **Imports**: MUST import at least one concern bundle
- **SCDs**: MUST NOT contain SCDs directly (scds array MUST be empty)
- **Cardinality**: 1+ per project (Software Development + optional vertical domains)
- **Examples**: bundle:software-development, bundle:legal, bundle:clinical

**Hierarchy**: Project → Domains → Concerns → SCDs

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

### **3.2 Standards-Tier**
Represents external standards, including:

- regulatory requirements  
- certification frameworks  
- interoperability standards  
- organizational policies  

Examples:
- HIPAA  
- CHAI  
- SOC2  
- ISO 27001  
- NIST 800-53  

Standards-tier SCDs serve as contracts imported into a project.

---

### **3.3 Project-Tier**
Defines the actual system being built.

Project-tier SCDs include:
- architecture  
- modules  
- data flows  
- performance expectations  
- security posture  
- requirements  
- constraints  
- compliance mappings  

This tier is unique per project.

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