# SCS 0.7.0 — Governance & Compliance  
**Version:** 0.7.0 (Draft)  
**Status:** Work in Progress  
**Last Updated:** 2026-10-28  

---

## 1. Purpose

The **Governance & Compliance** layer of the Structured Context Specification (SCS) defines how Structured Context Documents (SCDs) support:

- compliance with external standards  
- alignment with internal policies  
- traceable decision-making  
- automated governance  
- continuous verification  

This document formalizes how SCDs serve as the **source of truth** for governance engines, auditors, maintainers, and AI agents.

---

## 2. Goals of Governance in SCS

The governance model of SCS seeks to:

1. **Make compliance explicit**  
   All obligations (regulatory, security, operational, architectural) are represented structurally as rules in Project-Tier SCDs, which cite the external standards they implement.

2. **Make governance continuous**  
   Compliance is checked on each change, using SCDs as the inputs.

3. **Make decisions audit-ready**  
   Rationale, provenance, and relationships create natural audit trails.

4. **Make systems explainable**  
   AI agents can traverse SCD relationships to provide explanations of *why* something is required or impacted.

5. **Make governance distributed**  
   Governance is not centralized or bureaucratic; it is embedded into the development workflow.

---

## 3. What Governance Covers in SCS

The Governance & Compliance layer addresses:

### 3.1 Regulatory Compliance
- HIPAA  
- CHAI  
- SOC2  
- GDPR  
- ISO 27001  
- NIST 800-series controls  

### 3.2 Architectural Governance
- ensuring architectural decisions are validated  
- preventing violations of constraints  
- detecting dependency issues  

### 3.3 Security Governance
- enforcement of cross-cutting concerns  
- validation of data flows  
- adherence to least-privilege principles  

### 3.4 Operational Governance
- monitoring quality attributes  
- verifying operational constraints  
- ensuring SLAs/SLOs are met  

Governance in SCS is **context-driven**—SCDs define the “rules of the system,” and governance agents enforce and interpret those rules.

---

## 4. Governance Inputs

Governance agents rely on:

### 4.1 Governance Bundles  
Two governance bundles, either of which may be absent. Where both exist, both apply: a
project is governed by the Domain bundle and its own Project bundle together.
- **Domain bundle** → the organization's governance: the pinned Meta bundle (semantic
  foundation) plus the organization's own rules, applied to every project  
- **Project bundle** → one project's governance: system design, constraints, flows,
  decisions; it does not repeat the Domain bundle  

External obligations appear as citation references on the rules that implement them
(`citations.md`), not as separate SCDs.

### 4.2 Versioned History  
Every change is traceable via:
- Git history  
- PR metadata  
- SCD provenance fields  

### 4.3 Structured Relationships  
“Satisfies,” “depends-on,” “constrains,” “implements,” and other relationships define the governance graph.

### 4.4 status-context.yaml  
A machine-readable summary of active work, governance findings, and next steps for alignment across human and AI agents.

---

## 5. Compliance Representation in SCS

External standards are represented as **citation references** (`citations.md`): strings
of the form `std:<standard>[:<edition>][#<clause>]`, such as `std:iso-13485:2016#7.3.9`. A
citation names a standard, its edition and a clause. It carries no standard text: most
standards are licensed, and only the adopter holds the text. Where an adopter wants AI
access to that text, it belongs in retrieval as reference material, not in governance
bundles.

The adopter's own rules are its interpretation of a standard. They live in Domain or
Project SCDs, which cite the clauses they implement, either in a `cites` list or as the
target of a `satisfies` relationship.

Standards-Tier SCDs, which represented standards as SCDs, are deprecated in 0.6.0
(`standards-tier.md`).

### 5.1 Example Mapping (Project → Standard)

```yaml
relationships:
  - type: satisfies
    target: std:hipaa#164.312(e)(1)
    description: "Encryption module satisfies HIPAA transmission security."
```

### 5.2 Multi-Standard Mapping

```yaml
cites:
  - std:nist-800-53:r5#SI-4
relationships:
  - type: satisfies
    target: std:soc2:2017#CC6.6
```

SCD relationships and citations form a traceable compliance graph.

---

## 6. Autonomic Governance

Autonomic Governance means governance that:

- runs continuously
- is context-aware
- evaluates each change
- detects issues pre-merge
- provides explanations and remediations
- reduces burden on humans

## 6.1 How It Works

1.	A developer edits an SCD or code.
2.	A GitHub Action or local AI agent loads the relevant governance bundles (Domain and/or Project).
3.	The agent checks for:

- unmet compliance obligations
- broken relationships
- missing mappings
- outdated constraints
- decisions lacking rationale

4.	Issues are raised automatically in GitHub Issues or as PR comments.
5.	status-context.yaml is updated by the AI agent.

## 6.2 Explainability

Governance agents MUST be able to answer:

- “Why is this required?”
- “Which standards does this relate to?”
- “What happens if this changes?”
- “Are we still compliant?”

SCD relationships enable this reasoning.

---

## 7. Governance Artifacts

### 7.1 Provenance Records

Found on every SCD:

```yaml
provenance:
  created_by: human-or-agent
  created_at: timestamp
  updated_by: human-or-agent
  updated_at: timestamp
  rationale: explanation
```

### 7.2 Decision Records

Project-Tier SCDs may include formal decisions:

```yaml
decisions:
  - id: decision:<id>
    title: <string>
    rationale: <string>
    status: accepted|deprecated|rejected
```

### 7.3 Compliance Evidence

Optional future extension:

```yaml
evidence:
  - requirement: std:hipaa#164.308(a)(1)
    artifact: link-to-log-or-document
    timestamp: ...
```

---

## 8. Governance Workflow

Context is managed in the owner's Domain repository ([bundle-format.md](bundle-format.md) §8),
like code. A change follows the same path whether a person makes it directly or an agent makes
it on their behalf:

1. **Intake.** The answers and source documents the context is drafted from are recorded in the
   workspace's intake record.
2. **Draft or change.** SCDs are added, edited, or retired. Each rule traces to an intake answer
   or a source document (`derived_from`), and to the person who gave it.
3. **Validate.** The validator checks schemas, rules, and integrity. Every finding has a
   registered code.
4. **Review.** Findings about the content, such as a rule that conflicts with a cited framework,
   are raised with the owner, and the owner's decision is recorded in the intake record. Review
   is advisory: declining a finding leaves the content as it is.
5. **Summarize.** A deterministic diff shows what the new version changes against the last.
6. **Version.** A named person approves the version. It is recorded as a git tag with the
   approver and a content digest, and it cannot be changed without detection
   ([bundle-format.md](bundle-format.md) §7).
7. **Compile and place.** The version is compiled into a runtime artifact. Where the owner
   places it is their decision, outside SCS ([overview.md](overview.md) §1.1).

Teams that want multi-person review can use pull requests on their own infrastructure. SCS
does not define a review or approval workflow beyond recording the approver.

---

## 9. Role of AI Agents

AI agents relate to SCS in two ways.

**Agents that consume context** read the compiled Domain and Project artifacts that apply to
their work. Such agents:

- interpret the Domain and Project rules that apply
- trace rules to their citations and sources
- detect conflicts between layers and raise them
- answer questions about the context in plain language

**Agents that operate SCS** create and maintain context on a user's behalf, through the SCS
tools, in the user's Domain repository. They work within the scope of
[overview.md](overview.md) §1.1, and every change they make goes through the tools, is shown to
the user, and is confirmed by the user before it is written. The rules for such agents are in
[agent-interface.md](agent-interface.md).

In both roles governance stays human-led. An agent does not approve a version: the approver is
always a person the user names. An agent does not place artifacts, and does not present itself
as providing review workflows, registries, or runtime serving.

---

## 10. Validation Requirements

SCS 0.7.0 requires tools to validate:

### 10.1 Syntactic Validity

- YAML is valid
- schema compliance is satisfied

### 10.2 Tier Consistency
- each SCD has the correct type for its tier

### 10.3 Relationship Validity
- referenced SCDs exist
- citation references are well-formed
- relationship types are valid

### 10.4 Bundle Integrity
- all SCDs in the bundle exist and load correctly

### 10.5 Compliance Completeness (Optional in 0.7.0)

Tools MAY check for:

- unfulfilled required controls
- missing mappings

Full rule-based compliance evaluation will be defined in future SCS versions.

---

## 11. Future Extensions

Future versions of SCS may introduce:

- rule-based compliance engines
- machine-generated audit packages
- evidence attachment models
- dynamic governance (environment-based)
- multi-bundle governance
- attestations and signatures
- provenance lineage graphs
- organizational policy libraries

The 0.7.0 model defines the minimum surface required for explainable, automatable governance.

---

## 12. Feedback

Feedback on governance semantics, tooling requirements, or compliance mapping patterns should be submitted via GitHub Issues.