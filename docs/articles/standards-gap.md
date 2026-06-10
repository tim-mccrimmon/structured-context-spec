# The Standards Gap: When AI Governance Gets Lost in Translation

Standards bodies in healthcare AI are doing important, careful work. Organizations like the Coalition for Health AI (CHAI) bring together hundreds of experts — clinicians, payers, technologists, ethicists — to define how AI systems should behave in high-stakes settings. The output of that work is substantial: best practice guides, testing frameworks, consensus metrics developed over months of deliberation.

But there's a structural disconnect between how these standards are published and how the AI systems they govern actually operate. Standards arrive as prose documents — PDFs, web pages, best practice guides written for human readers. AI agents operate on structured data, configuration, and explicit constraints. Nothing connects the two.

The question isn't whether good standards exist. They do. The question is whether they reach the systems they're meant to govern.

## The telephone game

Consider how a standard like CHAI's Testing & Evaluation Framework for prior authorization actually reaches the AI agent doing criteria matching at a health plan.

CHAI publishes the framework. A compliance team at the health plan reads it, interprets it, and writes internal policy documents. Those policies get summarized into implementation requirements for the engineering team. A developer gets a checklist — maybe. The AI agent performing prior authorization criteria matching gets... nothing. It operates on whatever its developers built into it, informed by however many layers of interpretation stood between the original standard and the code.

This isn't a criticism of anyone in that chain. It's how organizations work. Compliance is someone else's job. Developers don't typically read regulatory frameworks — they read tickets and technical specifications. The compliance team doesn't typically write YAML — they write policy documents. Everyone does their part well. But by the time CHAI's carefully constructed requirement that "PPV difference greater than 0.05 across any demographic subgroup triggers mandatory review" reaches the system actually making criteria matching assessments, it's been paraphrased, summarized, and reinterpreted through three or four layers of human translation.

The standard and the system it governs never actually meet.

## The experiment

We wanted to see what it would look like if they did.

CHAI published their T&E Framework v1.0 for AI-supported prior authorization criteria matching in December 2025. It was developed by over 100 experts from UnitedHealth Group, CVS Health, Blue Cross Blue Shield of Minnesota, MCG Health, Mayo Clinic, Duke, Stanford, and others. It defines 13 consensus metrics across four principles: usefulness, fairness, safety, and transparency.

We transposed that framework into structured, machine-readable format using the Structured Context Specification (SCS), an open specification for encoding governance context. The result: 24KB, 494 lines, 15 requirements across 4 documents — one per CHAI principle.

Every requirement has an identifier, a measurable benchmark, a measurement phase, a responsible role, and implementation guidance. Here's what the difference looks like.

**As prose** (from CHAI's T&E Framework):

> Prediction accuracy must be consistent across demographic subgroups. Positive Predictive Value must not vary significantly by race, sex, age, language, or disability status. A PPV difference greater than 0.05 across any demographic subgroup triggers mandatory review of training data or thresholding.

**As structured context:**

```yaml
- id: "CHAI-PA-FAIR-001"
  name: "Predictive Parity (PPV Parity)"
  description: >
    Positive Predictive Value must not vary significantly
    by race, sex, age, language, or disability status.
  benchmark: "PPV difference >0.05 triggers mandatory review"
  measurement_phase: "pre_and_post_implementation"
  responsible_role: "developer_and_implementer"
  protected_characteristics:
    - "Race/ethnicity"
    - "Sex/gender"
    - "Age"
    - "Primary language"
    - "Disability status"
```

The prose version is written for a human to read and interpret. The structured version is something a system can enforce — a threshold that triggers a specific action, with explicit dimensions to evaluate against.

The full bundle covers the entire T&E Framework: turnaround time compliance with CMS-mandated windows, scope boundary enforcement (the agent must reject clinical judgment queries with 95% accuracy), pre-deployment failure analysis using FMEA with risk priority thresholds, toxicity screening for generated language, decision traceability for every assessment, and demographic disparity monitoring across auto-approved vs. manually reviewed pathways.

CHAI's source material — the Best Practice Guide and T&E Framework — runs to dozens of pages of expert prose. The structured transposition is 24KB. Not because it's a summary, but because structured data is more compact than the explanatory context humans need around it.

One of the more interesting requirements to transpose was CHAI-PA-FAIR-003, which addresses the "Symptoms Paradox" — the observation that AI systems may correctly route complex cases to manual review, but those complex cases disproportionately affect certain populations. Patients with comorbidities, rare conditions, or non-standard presentations experience longer processing times even though the routing logic is clinically appropriate. In prose, this takes a paragraph of careful explanation. In structured form, it becomes a monitoring requirement with specific demographic dimensions to track and a clear obligation to report findings regardless of whether disparity is detected. The nuance survives the transposition. The ambiguity doesn't.

## What we noticed

The structured version isn't a simplification of CHAI's work. Every requirement, every benchmark, every measurement phase is preserved. But it's something fundamentally different from the original document. It's not something humans should sit down and read. It's boundaries an AI system can operate within.

An AI agent doesn't need to "understand" CHAI's rationale for predictive parity. It needs to know: when PPV disparity exceeds 0.05 across these specific demographic dimensions, flag it. The reasoning — why 0.05, why these dimensions, why this matters — belongs in CHAI's prose document, which remains essential for the humans designing, deploying, and overseeing these systems.

The two formats serve different audiences. The prose is for people. The structured version is for systems. Right now, only one of those formats gets published.

There's also a composability dimension that prose doesn't naturally support. A payer building a prior authorization agent needs to comply with CHAI's framework, but also with HIPAA, with CMS regulations, and with their own internal policies. In a prose world, someone has to read all of those documents and synthesize them into a coherent set of instructions. In a structured world, separate bundles — CHAI, HIPAA, internal policy — can be composed into a single governance stack that the agent receives as one unified set of constraints. The standards remain independently authored and versioned, but they arrive at the agent together.

One requirement in particular stood out. CHAI-PA-TRANS-003, "Context Version Auditability," states that it must be possible to determine exactly which governance context an AI agent was operating under at the time of any specific decision. This is a requirement about the delivery mechanism for standards, not just the content of standards. CHAI is asking for something that currently doesn't exist in most implementations: a way to reconstruct what rules the system was following at any given moment. Versioned, immutable bundles of structured context — with audit trails tracking which version each agent had at each timestamp — are one way to provide that.

## The open question

What if standards bodies published machine-readable versions of their frameworks alongside the prose?

Not instead of. The prose documents are essential — they carry the rationale, the context, the expert deliberation that makes the requirements meaningful. But a structured companion artifact, published by the standards body itself, would eliminate the telephone game. The standard would reach the AI agent directly, without three layers of human reinterpretation.

CHAI's T&E Framework has 15 requirements with measurable benchmarks. Those requirements can be expressed as structured data. If CHAI published that structured version alongside their PDF, any payer building an AI prior auth agent could import those requirements directly into their governance stack. Same requirements, no translation loss. And when CHAI updates the framework — revises a threshold, adds a new metric, refines a measurement methodology — the structured version updates too. Every system consuming it gets the update without anyone re-reading a PDF and re-interpreting what changed.

This is, in fact, one of the reasons the Structured Context Specification exists. SCS was designed in part around the observation that standards bodies produce some of the most important governance context in any industry — and that context has no structured path to the AI systems it's meant to govern. The specification includes a dedicated "standards" bundle type specifically so that organizations like CHAI, HIPAA, SOC2, and NIST can publish their requirements in a format that travels directly from the standards body to the AI agent, intact.

The CHAI standards bundle described in this article is [open source in the SCS repository](https://github.com/structured-context-spec/structured-context-spec/tree/main/examples/chai-standards-bundle) as a reference implementation. The original CHAI framework is available at [chai.org](https://www.chai.org/workgroup/use-case/ai-supported-prior-authorization-criteria-matching) and the [CHAI RAI Content repository](https://rai-content.chai.org/en/latest/prior-authorization-ai-supported-criteria-matching/t%26e-framework.html).

This is a transposition of CHAI's publicly available work, not an endorsed partnership. The structured version is faithful to the source material, but it hasn't been reviewed by CHAI. It's an experiment in bridging the gap between how standards are written and how systems consume them — and an invitation to explore what happens when you close that gap.
