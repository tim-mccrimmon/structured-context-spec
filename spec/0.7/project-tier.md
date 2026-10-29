# SCS 0.7.0 — Project-Tier SCDs  
**Version:** 0.7.0 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2026-10-28  

---

## 1. Purpose

The **Project-Tier** of the Structured Context Specification (SCS) holds the governance
context an adopter authors: the guidance and guardrails its AI agents are expected to
follow. It appears in two places:

- in an organization's **Domain bundle**, through its concept bundles: the organization's
  own rules, applied to all of its work
- in a **Project bundle**: the rules that apply only to one project, in addition to the
  organization's

The two bundles are independent. A Project bundle MUST NOT import the Domain bundle and
SHOULD NOT repeat its rules (`bundle-format.md`).

The tier identifies **who authors** an SCD, not **where it applies**. An SCD's scope comes
from the bundle that includes it: through a Domain bundle it applies to all work, through a
Project bundle to one project. Tools MUST NOT infer an SCD's scope from its tier.

> **Naming note.** The name "Project" is historical: it predates the separation of Domain
> and Project bundles in 0.6.0. Read it as "adopter-authored". The name is kept because SCD
> identifiers (`scd:project:<name>`) must stay stable; see ISSUES.md ISS-041.

A "project" here is any bounded piece of work an organization governs separately: a
software product, a supplier audit, a product launch, a facility move, a grant application.
SCS does not define project types. The same structure serves all of them, because a
Project bundle records governance, not a model of the work itself.

---

## 2. Role of the Project-Tier

Project-Tier SCDs are where the organization's governance is stated concretely. The
adopter's rules are its interpretation of the standards it follows; the standards
themselves are cited, not reproduced (`citations.md`).

In a Domain bundle, Project-Tier SCDs state what holds for all of the organization's work.
In a Project bundle, they state **only what is different for this project**:

- what the project is and what it is for
- its risk or safety classification, where one applies
- the categories of data it handles
- what AI agents must never do in it
- what they are expected to do in it
- the obligations that apply to it and not to the organization's other work

Governance context is stable. It changes when a policy, a standard, or the project's scope
changes, not as work progresses. Information that changes as work progresses, such as
designs, schedules, and records, is not Project-Tier content; an agent looks it up where it
is kept.

---

## 3. Responsibilities of Project-Tier SCDs

Project-Tier SCDs MUST:

- state rules an agent can follow and facts an agent can check, as prohibitions,
  directives, and facts (§5, `runtime-artifact.md` §2)
- carry provenance identifying who authored them

They SHOULD:

- remain focused and modular, one subject per SCD
- in a Project bundle, add to the Domain bundle's rules rather than restate them
- declare the Domain Ontology concept they realize (`concept`, §4.2)
- reference Meta-Tier SCDs instead of restating their definitions
- cite external standards rather than reproduce their text

Whether the content is accurate or sufficient cannot be checked by a validator. It is
attested by approval (`domain-ontology.md` §7).

---

## 4. Project-Tier SCD Structure

Project-Tier SCDs follow the general SCD structure described in the Core Model.

### 4.1 Required Properties

| Property       | Description                                                  |
|----------------|--------------------------------------------------------------|
| `id`           | Unique stable identifier (e.g., `scd:project:release-gates`) |
| `type`         | MUST be `project`                                           |
| `title`        | Human-readable title                                        |
| `version`      | Version of this SCD                                         |
| `description`  | Summary of what the SCD governs                             |
| `content`      | The SCD's prohibitions, directives, facts, and reviewer context |
| `provenance`   | Authorship and change metadata                              |

### 4.2 Optional Properties

| Property   | Description                                                                 |
|------------|-------------------------------------------------------------------------------|
| `relationships` | References to Meta/Project SCDs, or citations for `satisfies` (§6) |
| `cites`    | Citation references to the external standards this SCD implements (e.g., `std:iso-13485:2016#7.3.9`) — `citations.md`. Carries no standard text. |
| `concept`  | The Domain Ontology concept this SCD realizes (e.g., `concept:risk-management`) — `domain-ontology.md`, RFC-0001. Optional at the schema level, but expected for an SCD that lives in a concept bundle. |
| `derived_from` | On items in `content.prohibitions`, `content.directives`, and `content.facts`: the intake answer or source document the item came from — `core-model.md` §4.1. Never compiled. |

---

## 5. Common Project-Tier Content Patterns

Only three kinds of content are compiled into the runtime artifact an agent receives:
`content.prohibitions`, `content.directives`, and `content.facts` (`runtime-artifact.md`
§2). An SCD with none of them contributes nothing to the artifact. SCS 0.7.0 does not
prescribe specific SCDs; the patterns below follow the questions an intake asks about a
project, and apply to any kind of project.

### 5.1 Project Identity

What the project is and what it is for, stated as facts.

```yaml
id: scd:project:project-profile
type: project
title: Project Profile
version: "1.0.0"
description: What the supplier requalification project is and what it covers.
concept: concept:business-context
content:
  summary: Requalification of tier-1 component suppliers for the catheter product line.
  facts:
    - id: PP-001
      fact: The project requalifies the six tier-1 suppliers of catheter components.
    - id: PP-002
      fact: The project ends when each supplier has an approved requalification report.
provenance:
  created_by: "quality-lead@medtech-cdmo.example"
  created_at: "2026-10-01T09:00:00Z"
  rationale: Initial approved version
```

### 5.2 Risk Classification

A risk or safety classification, where one applies, and what follows from it.

```yaml
id: scd:project:software-safety-class
type: project
title: Software Safety Class
version: "1.0.0"
description: Safety classification of the pump firmware and what follows from it.
concept: concept:risk-management
content:
  summary: The firmware is IEC 62304 class C.
  directives:
    - id: SSC-001
      directive: >-
        The pump firmware is IEC 62304 software safety class C. Treat every firmware change
        as safety-relevant.
      cites:
        - std:iec-62304:2006-a1#4.3
    - id: SSC-002
      directive: >-
        Do not propose removing or weakening an alarm, interlock, or dose limit check. Refer
        such requests to the risk management lead.
      cites:
        - std:iso-14971:2019
provenance:
  created_by: "fw-lead@medtech-cdmo.example"
  created_at: "2026-10-01T09:00:00Z"
  rationale: Initial approved version
```

### 5.3 Data Handling

The categories of data the project handles, and how they must be treated.

```yaml
id: scd:project:cardholder-data
type: project
title: Cardholder Data
version: "1.0.0"
description: Handling of cardholder data in the payments reconciliation project.
concept: concept:data-security
content:
  summary: The project processes cardholder data in scope for PCI DSS.
  facts:
    - id: CHD-001
      fact: Reconciliation files contain primary account numbers.
  directives:
    - id: CHD-002
      directive: >-
        Never include a full primary account number in output; show the last four digits
        only.
      cites:
        - std:pci-dss:4.0#3.4.1
provenance:
  created_by: "payments-lead@example-fintech.com"
  created_at: "2026-10-01T09:00:00Z"
  rationale: Initial approved version
```

### 5.4 Boundaries

What AI agents must never do in this project, as binary prohibitions
(`runtime-artifact.md` §2.3). A Project bundle MAY add prohibitions; it cannot lift one in
the Domain bundle.

```yaml
id: scd:project:prohibited
type: project
title: Prohibited Tools and Practices
version: "1.0.0"
description: Tools and practices forbidden, without exception, in the requalification project.
content:
  summary: Binary prohibitions for the requalification project.
  prohibitions:
    - id: NO-001
      kind: practice
      subject: sending supplier audit findings to the supplier
      reason: Findings go to the supplier only through the quality lead.
    - id: NO-002
      kind: practice
      subject: changing a supplier's approval status in the ERP system
provenance:
  created_by: "quality-lead@medtech-cdmo.example"
  created_at: "2026-10-01T09:00:00Z"
  rationale: Initial approved version
```

### 5.5 Expected Practice

What agents are expected to do in this project, as directives.

```yaml
id: scd:project:release-gates
type: project
title: Release Gates
version: "1.0.0"
description: Conditions for releasing a firmware build.
concept: concept:verification-validation
content:
  summary: Firmware builds are released only through the release procedure.
  directives:
    - id: RG-001
      directive: >-
        A firmware build is releasable only after unit, integration, and system verification
        have passed and the results are recorded.
      cites:
        - std:iec-62304:2006-a1#5.8
    - id: RG-002
      directive: Generated code must not be merged without review by a firmware engineer.
provenance:
  created_by: "fw-lead@medtech-cdmo.example"
  created_at: "2026-10-01T09:00:00Z"
  rationale: Initial approved version
```

### 5.6 Reviewer Context

Content other than prohibitions, directives, and facts (summaries, rationale, decisions,
descriptions of systems) is context for the people who author and review governance. It
MAY appear in any SCD and is not compiled. If an agent needs to follow or know something,
state it as a directive or a fact.

```yaml
content:
  summary: Supplier requalification follows the supplier controls procedure.
  directives:
    - id: SRQ-001
      directive: Base each requalification recommendation on the supplier's audit record.
  rationale: >-
    Requalification recommendations were previously drafted from supplier questionnaires
    alone; the 2026 internal audit required audit evidence.
```

### 5.7 Policy SCD

Defines which roles may use which tool capabilities, and under what constraints —
**policy-as-context** (`any-ai-actor-model.md` §3, RFC tracked as ISS-006). A tool or
MCP server's permitted operations are a governed decision, the same as any other
guardrail, not a runtime implementation detail.

```yaml
concept: concept:risk-management   # the purpose this policy exists for
content:
  applies_to_roles:
    - role:quality-engineer
  permitted_operations:
    - capability: fetch-data       # capability class, not a specific tool/endpoint
      resource: risk-register
    - capability: write-data
      resource: risk-register
      requires_approval: true
```

`capability` names a functional class (`fetch-data`, `execute-code`, `query-db`,
`write-data`, `send-communication` by default, domain-extensible) rather than a specific
tool or MCP endpoint — the binding to an actual implementation is a runtime concern, not
part of the decision this SCD records. A Policy SCD is declarative; enforcement happens
elsewhere, via a runtime-specific compilation step (`any-ai-actor-model.md` §3.4). It is
not compiled into the runtime artifact.

---

## 6. Relationships With Other SCD Tiers

### 6.1 With Meta-Tier

Project-Tier SCDs reference Meta-Tier SCDs rather than restating their definitions.

Example:

```yaml
relationships:
  - type: depends-on
    target: scd:meta:governance-context
```

### 6.2 With External Standards

The Standards-Tier is deprecated in 0.6.0 (`standards-tier.md`). Project-Tier SCDs map
their rules to standards obligations with citation references (`citations.md`), either
as a `cites` list or as the target of a `satisfies` relationship:

```yaml
cites:
  - std:soc2:2017#CC2.1
relationships:
  - type: satisfies
    target: std:soc2:2017#CC2.1
```

`scd:standards:` targets still validate but have been deprecated since 0.6.0.

### 6.3 With Other Project-Tier SCDs

Project-Tier SCDs may depend on each other:

```yaml
relationships:
  - type: depends-on
    target: scd:project:software-safety-class
```

---

## 7. Versioning and Evolution

A Project-Tier SCD gets a new version when its rules or facts change: a policy or standard
changes, the project's scope or classification changes, or a review finds a rule wrong or
missing. Work progressing within the project's scope does not change its governance.

When a project ends, its Project bundle is retired; the Domain bundle is unaffected.

---

## 8. How Agents Receive Project-Tier Context

Agents do not read Project-Tier SCDs directly. A compiler turns a Domain or Project bundle
into a runtime artifact holding its prohibitions, directives, and facts
(`runtime-artifact.md`). When both apply to a request, a consuming tool presents the Domain
artifact first, then the Project artifact (`bundle-format.md` §4.2).

---

## 9. Validation Requirements

In SCS 0.7.0:

- Project-Tier SCDs MUST conform to scd.project.schema.json.
- The type MUST be project.
- Field structures must match the schema.
- Relationships MUST reference valid SCD identifiers, or for `satisfies`, well-formed
  citation references.
- Prohibitions MUST be unconditional (`runtime-artifact.md` §2.3).

A bundle that yields no prohibitions, directives, or facts cannot be compiled
(`runtime-artifact.md`). Whether the content is accurate or sufficient is out of scope for
validation (§3).

---

## 10. Future Extensions

Future versions of SCS may add Project-Tier content patterns through the RFC process.

---

## 11. Feedback

Feedback regarding Project-Tier definitions and examples should be submitted through GitHub Issues.
