# Structured Context Specification (SCS)

A community-driven specification for representing **AI runtime context** as **structured, versioned artifacts**.

SCS exists to explore a practical question:

> If model weights are static and behavior is shaped at runtime — **what should “context” be**, how should it be structured, and how should it be composed?

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-green)
![Status](https://img.shields.io/badge/status-active_development-orange)

---

## What This Project Is (and Is Not)

### SCS **is**
- A draft spec for **structured context documents** and **bundles** (YAML/JSON, git-native)
- A place to **define boundaries** between *prompts*, *RAG*, *memory*, *tools*, and *context*
- A discussion space to refine what “context engineering” means in practice
- A set of schemas + examples you can use to build and validate structured context

### SCS **is not**
- A prompt engineering framework
- A RAG implementation
- An agent framework or orchestration runtime
- A governance / compliance product
- A finished standard

**Disagreement is expected.** If you think the framing below is wrong, that’s exactly the kind of contribution we want.

---

## Why SCS

Teams using LLMs keep rebuilding the same brittle structures:
- long prompts that quietly drift
- scattered “context” across code, docs, wikis, tickets, and embeddings
- unclear provenance (“what did the model actually see?”)
- hard-to-debug behavior (“why did it answer like that?”)

SCS is an attempt to make *context*:
- **explicit** (not implicit glue code)
- **structured** (not just prose)
- **versioned** (reviewable and reproducible)
- **composable** (reusable across projects and tools)
- **validatable** (machine-checkable)

---

## A Useful Working Distinction (Open to Debate)

People use “context” to mean many things. SCS starts with a *proposal*:

- **Prompts**: instructions and coordination (“how to behave / what to do”)
- **RAG**: retrieval of reference material (“what to know”)
- **Memory**: durable personalization and state (“what to remember”)
- **Tools**: executable capabilities and contracts (“what can be done”)
- **Structured Context (SCS)**: the **operating envelope** and **declared assumptions** the system is allowed to use (“what is in-bounds”)

If you disagree with this breakdown, please jump into Discussions and tell us why.

---

## Open Questions

This repo is intentionally a **working space**. Some of the questions we want help answering:

- What information must be **explicit** for reliable AI behavior?
- Where does “context” end and “memory” begin?
- What belongs in a **spec** vs an **implementation detail**?
- Should context be immutable per run? per task? per user session?
- How do we represent **scope**, **constraints**, and **provenance** without over-engineering?
- What is the minimal “Core” that most teams could agree on?

See: **OPEN_QUESTIONS.md** (coming / evolving) — and feel free to propose additions.

---

## Core Concepts (Current Draft)

SCS 0.3 introduces a multi-domain model (still evolving) built around:

### Structured Context Documents (SCDs)
SCDs are the building blocks. They are:
- human-readable
- machine-readable
- versionable in git
- linkable (references, dependencies, provenance)

### A Three-Tier Model (Current)
- **Meta**: universal vocabulary and cross-cutting concerns
- **Standards**: external obligations and imported requirements (optional; evolving)
- **Project**: the work-specific context you want AI systems to operate within

### Bundles
Bundles are manifests that compose SCDs (and other bundles) into usable context sets.

> The structure above is not “final truth” — it’s the current best attempt.  
> The goal is to refine it with real counterexamples.

---

## How to Engage (Best Path)

We’re optimizing for **thoughtful critique** and **practical examples**.

1. **Start with Discussions**
   - “What is context?” debates
   - boundary arguments (prompt vs context vs RAG vs memory)
   - minimal-core proposals
   - counterexamples that break the model

2. **Use Issues for concrete changes**
   - schema problems
   - unclear terminology
   - missing examples
   - validation gaps

3. **Use RFCs for major changes**
   If a change is breaking or introduces a new foundational concept, propose it via an RFC.
   See: `rfcs/README.md`

---

## Quick Start

### 1) Clone

```bash
git clone https://github.com/tim-mccrimmon/structured-context-spec.git
cd structured-context-spec
```

### 2) Read the spec entry points

- `spec/0.3/overview.md`
- `spec/0.3/terminology.md`
- `spec/0.3/bundle-format.md`

### 3) Create and validate an SCD

```bash
cp templates/scd/project_scd_template.yaml my-first-scd.yaml
cd tools/scd-validator
python validate.py ../../my-first-scd.yaml
```

---

## Repository Structure

```
structured-context-spec/
├── spec/0.3/                  # Normative spec (0.3)
├── schema/                    # JSON Schemas (bundles, domains, SCD tiers)
├── templates/                 # YAML starters
├── docs/                      # Guides & explainers
├── tools/                     # Validation & tooling
├── examples/                  # Example bundles & domains
├── rfcs/                      # RFC process for major changes
├── CONTRIBUTING.md
└── LICENSE
```

---

## Roadmap (Community-First)

Near-term goals:
- clarify definitions (prompt vs context vs RAG vs memory)
- stabilize a **Core** subset suitable for broad adoption
- improve examples and counterexamples
- tighten schemas + validation based on real usage

Longer-term:
- domain work streams (by domain experts)
- optional standards imports and registries
- editor/IDE integrations

---

## Governance

During v0.x, SCS uses a **benevolent maintainer** model:
- Maintainer: **Tim McCrimmon**
- Major changes via RFC
- Goal: transition to broader community governance for v1.0

---

## License

Apache License 2.0

Copyright © 2026 Tim McCrimmon / Ohana Consulting LLC
