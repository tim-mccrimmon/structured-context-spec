# SCS 0.7.0 — Core Model  
**Version:** 0.7.0 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2026-10-28  

---

## 1. Purpose

The Core Model defines the foundational structures and semantics of the Structured Context Specification (SCS).  
It establishes the conceptual architecture upon which SCDs, tiers, bundles, schemas, and tools are built.

This model is **normative** for SCS 0.7.0 and is intended to remain stable across future versions.

This document describes the model as it applies to any single AI actor reasoning over a
bundle. For how context is *selected* for a given actor, how tool permissions become
governed context, and how a workflow records which context version applied at a given
step, see `any-ai-actor-model.md` (RFC tracked as ISS-006).

---

## 2. Model Overview

The SCS Core Model is built around three fundamental concepts:

1. **Structured Context Documents (SCDs)**  
2. **SCD Tiers**  
3. **SCD Bundles**

These concepts form a layered representation of system context that is:

- modular  
- hierarchical  
- versionable  
- analyzable  
- AI-consumable  
- tool-friendly  

The model ensures that context is explicit, structured, and governed.

---

## 3. Structured Context Documents (SCDs)

An **SCD** is the atomic unit of structured context.  
All SCDs share a common structural template, but each SCD type (tier) applies specific semantics and constraints.

### 3.1 Required Properties

Every SCD must include:

| Property | Description |
|---------|-------------|
| `id` | Unique, stable identifier for the SCD |
| `type` | One of: `meta`, `project` (`standards` is deprecated in 0.6.0; see `standards-tier.md`) |
| `title` | Human-readable title |
| `version` | SCD version (independent of the SCS version) |
| `description` | Summary of purpose and scope |
| `content` | Structured fields defined by the SCD schema |
| `cites` | Optional list of standard citation references (`citations.md`) |
| `relationships` | Optional set of typed references to other SCDs |
| `provenance` | Metadata on authorship, dates, and decisions |

These properties provide minimal requirements for:

- traceability  
- interoperability  
- tool compatibility  
- human readability  

---

## 4. SCD Structure

While SCD structures may evolve, the 0.7.0 version establishes the following top-level pattern:

```yaml
id: scd:<unique-id>
type: meta | project
title: <string>
version: <string>
description: <string>

content:
  <structured fields as defined by schema>

cites:                     # optional; citation references, no standard text
  - std:<standard>[:<edition>][#<clause>]

relationships:
  - type: <relationship-type>
    target: scd:<id>       # or a std: citation, for satisfies
    description: <optional>

provenance:
  created_by: <human-or-agent>
  created_at: <timestamp>
  updated_by: <human-or-agent>
  updated_at: <timestamp>
  rationale: <optional description>
```

This structure ensures:

- consistency
- clarity
- machine-readability
- schema validation

### 4.1 Item Provenance

Items in `content.prohibitions`, `content.directives`, and `content.facts` MAY carry a
`derived_from` list recording where the item came from. Each entry has exactly one of `intake`
(the id of an answer in the workspace's intake record, `bundle-format.md` §8.4) or `source` (the
id of a source document in it), plus an optional `locator` string:

```yaml
content:
  directives:
    - id: DC-007
      directive: "Draft DHF changes as redlines for human review."
      derived_from:
        - source: doc-qm
          locator: "section 4.2.5"
```

`derived_from` records where an individual item came from; the SCD-level `provenance` object
records who created the SCD. `derived_from` is never compiled (`runtime-artifact.md` §2.1). An
id that does not resolve in the workspace's intake record is a warning
(`DERIVED_FROM_UNRESOLVED`). Agents that draft items record it (`agent-interface.md` §6).

---

## 5. SCD Tiers (Type Model)

Each SCD must belong to exactly one tier. SCS 0.7.0 has two active tiers, Meta and
Project. The Standards tier is deprecated (§5.2).

### 5.1 Meta-Tier

Defines the conceptual foundation of a system.

Includes:
	•	roles
	•	domain concepts
	•	capabilities
	•	cross-cutting concerns
	•	lifecycle semantics
	•	naming conventions
	•	abstract structures

### 5.2 Standards-Tier (Deprecated)

Deprecated in 0.6.0 and scheduled for removal. External standards are no longer represented
as SCDs. An SCD that implements a standard cites it with a **citation reference**
(`std:iso-13485:2016#7.3.9`), which carries edition and clause but no standard text.
Organizational policy is authored as project-tier SCDs in the organization's Domain bundle.
See `standards-tier.md` and `citations.md`.

### 5.3 Project-Tier

Defines governance and context for an organization (in a Domain bundle's concept bundles)
or for a specific project or system (in a Project bundle). The tier identifies the author
(the adopter), not the scope; scope comes from the bundle that includes the SCD, and tools
MUST NOT infer it from the tier (`project-tier.md` §1).

Includes:
	•	prohibitions
	•	directives
	•	facts
	•	citations of the standards they implement
	•	reviewer context (summaries, rationale, decisions), which is not compiled

### 5.4 Terminology Note: Corporate / Project / Personal

`ROADMAP.md` and engagement-facing material sometimes describe SCS coverage as
**Corporate**, **Project**, and **Personal** context. This is audience-facing shorthand, not
a schema tier. It maps onto bundles as follows:

- **"Corporate"** is an organization's **Domain bundle**: the pinned Meta bundle plus the
  organization's own rules, applied to every project. Deployments often call this tier
  "Global".
- **"Project"** is a **Project bundle**: one project's governance, independent of the
  Domain bundle and not repeating it.
- **"Personal"** is a **personal Domain**: one person's Domain bundle, covering all of that
  person's work, usually built on the `personal` Ontology Model (`terminology.md` §2.11). It
  is a Domain like any other, kept in its own Domain repository, and not a separate tier.
  Context that an application's own repository carries for its users is outside SCS.

A **"departmental"** layer appears in some engagement narratives (policy that applies to
one department rather than the whole org). This is a description of a bundle's audience and
governance scope, not a tier: a department-specific policy is still authored as an ordinary
project-tier SCD, scoped by its content and provenance, not by a schema field that names
"department."

The tier names in §5.1–5.3 (Meta / Standards / Project) remain the normative schema
vocabulary — `tier:` values, file paths, and validator rules all use these names. Corporate,
Project, Personal, and departmental are explanatory framing for non-technical audiences,
not an alternate or competing tier taxonomy.

---

## 6. Relationships

Relationships enable SCDs to form a connected knowledge graph.

### 6.1 Relationship Types

Common relationship types include:

- depends-on
- constrains
- satisfies
- refines
- extends
- conflicts-with
- implements

Tools may introduce additional semantics, but 0.7.0 defines the minimal set.

**Note:** these are SCD-to-SCD relationships. A domain's **Domain Ontology**
(`domain-ontology.md`, RFC-0001) defines a separate, smaller relationship set
(`depends-on`, `relates-to`, `satisfies`) between the domain's `concept:` ids — a
different graph, one level up from the SCDs themselves.

### 6.2 Requirements

A relationship must include:

- type
- target (another SCD id, or for `satisfies`, a citation reference per `citations.md`)
- optional description

### 6.3 Purpose

Relationships support:

- impact analysis
- dependency mapping
- compliance tracing
- multi-tier reasoning
- autonomic governance

---

## 7. SCD Bundles

An SCD Bundle is a versioned set of SCDs. SCS 0.7.0 defines two independent governance
bundles (`bundle-format.md`):

| Bundle | Holds | Includes Meta? |
| ---- | ---- | ---- |
| Domain bundle | The organization's governance | Yes — imports one pinned Meta bundle |
| Project bundle | One project's governance | No — MUST NOT import Meta or Domain bundles |

Neither requires the other. A deployment may have a Domain bundle, Project bundles, or both.

### 7.1 Bundle Form

A bundle may be represented as:

- a folder of SCD files
- a bundle.yaml manifest referencing individual SCDs
- a structured package for tools

### 7.2 Required Properties

Bundles must define:

- bundle id
- bundle version
- list of SCDs
- optional metadata or tags

Example minimal bundle file:

```yaml
id: bundle:example-system
version: "0.1.0"
scds:
  - scd:project:architecture
  - scd:project:access-control
```
---

## 8. Versioning Model

SCDs and bundles are versioned independently of the SCS specification version.

### 8.1 SCD Versioning

Each SCD includes its own version field.

Version changes reflect:

- content changes
- structural updates
- compliance adjustments
- refinement or clarification

### 8.2 Bundle Versioning

Bundle versions represent:

- addition/removal of SCDs
- changes in SCD versions
- relationship updates

### 8.3 SCS Version (Spec Version)

SCS 0.7.0 defines:

- schema templates
- required fields
- allowed SCD structure

Future SCS versions may introduce changes, but SCDs written for 0.6.0 and 0.7.0 must remain readable by compatible tools.

---

## 9. Governance-Ready Architecture

The Core Model supports autonomic governance through:

- explicit semantics
- traceable relationships
- versioned context
- audit-ready provenance
- standard citation references
- machine-validatable structure

AI governance agents operate over bundles to:

- evaluate compliance
- detect inconsistencies
- monitor evolution
- analyze risk
- enforce constraints

These capabilities emerge from the Core Model itself.

---

## 10. Tooling Implications (Non-Normative)

The Core Model enables future tools such as:

- SCD Bundle Viewer/Editor
- SCD Validator
- SCD Evaluator
- Compliance Mappers
- Architecture Graph Viewers
- Change Impact Analyzers

While tooling is out of scope for the Core Model, the Core Model is designed to support it from the beginning.

---

## 11. Extensibility

SCS 0.7.0 defines the minimal Core Model.

Future versions may extend:
	•	relationship types
	•	domain-specific SCD structures
	•	compliance mapping schemas
	•	governance semantics
	•	bundle metadata
	•	visualization formats

The Core Model is intended to remain stable while allowing structured evolution.

---

## 12. Feedback

Suggested improvements to the Core Model may be submitted via GitHub Issues.