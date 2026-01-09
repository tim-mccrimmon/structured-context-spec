# Structured Context Specification (SCS)

A community-driven specification for creating, validating, and versioning structured context for AI systems.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-green)
![Status](https://img.shields.io/badge/status-active_development-orange)

---

## The Problem

If you're building with AI, you know this struggle:

Your agents need clear guidance on how to behave, what rules to follow, and what boundaries to respect. But that "context" ends up scattered across prompts, docs, code comments, wikis, and tribal knowledge. It drifts. It conflicts. It's impossible to validate or version properly.

**You need a better way to manage context.**

---

## What SCS Provides

SCS is a specification (and tooling) for representing agent context as **structured, versioned artifacts** that are:

- **Concise** — focused, atomic definitions (not walls of text)
- **Precise** — structured YAML/JSON (not ambiguous prose)
- **Non-conflicting** — explicitly composed and validated (not scattered)
- **Versionable** — git-native, reviewable, auditable (not lost in chat history)
- **Reusable** — composable bundles (standards, domains, projects)

**Use SCS to:**
- Define agent behavior boundaries and rules
- Package compliance requirements (HIPAA, SOC2, industry standards)
- Structure domain knowledge and constraints
- Version context alongside code
- Validate context before deployment

### Who Uses SCS?

**Development teams** — structure architecture rules, coding conventions, domain concepts
**Standards organizations** — package compliance requirements (HIPAA, SOC2, PCI-DSS) for agent consumption
**Enterprises** — version agent governance policies alongside code
**Anyone building with AI** — create concise, precise, non-conflicting context

**Any industry:** Healthcare, finance, legal, education, government, software development

---

## What This Project Is (and Is Not)

### SCS **is**
- A spec for **Structured Context Documents (SCDs)** and **Bundles**
- Schemas, validation tools, and examples you can use today
- A community space to refine context engineering practices
- Designed for broad adoption (any industry, any use case)

### SCS **is not**
- A prompt engineering framework
- A RAG system or vector database
- An agent orchestration runtime
- A finished standard (it's v0.3, actively evolving)

**This is spec work.** If you disagree with our framing or have better ideas, that's exactly what we need. Open an issue or discussion.

---

## Core Concepts

### Structured Context Documents (SCDs)

SCDs are the atomic building blocks — single, focused definitions of:
- Rules and boundaries
- Constraints and requirements
- Domain concepts and terminology
- Compliance obligations

Each SCD is versioned, validated, and composable.

### Bundles

Bundles are manifests that assemble SCDs into coherent context sets:

- **Meta Bundle** — SCS vocabulary and foundations (provided by spec)
- **Standards Bundle** — regulatory/compliance requirements (HIPAA, SOC2, etc.)
- **Domain Bundle** — concern-specific context (architecture, security, etc.)
- **Project Bundle** — top-level orchestrator (imports all relevant bundles)

### The Three-Tier Model

- **Meta tier** — universal SCS concepts (what is an SCD, a bundle, validation)
- **Standards tier** — external requirements and obligations (optional)
- **Project tier** — your specific context (rules, boundaries, domain knowledge)

This structure is evolving. See `/spec/0.3/` for current details.

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

## How to Engage

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

### 3) Explore examples

```bash
# See real working examples
ls examples/bundles/

# View a complete project bundle
cat examples/bundles/project-bundle.yaml

# View concern-specific bundles
ls examples/bundles/concerns/
```

### 4) Create and validate your own SCD

```bash
# Copy a template
cp templates/scd/project_scd_template.yaml my-first-scd.yaml

# Edit it (add your rules, boundaries, domain concepts)
# Then validate
cd tools/scd-validator
python validate.py ../../my-first-scd.yaml
```

### 5) Join the discussion

- **GitHub Discussions** — share your use case, ask questions
- **Issues** — report problems or suggest improvements
- **RFCs** — propose significant changes to the spec

See `docs/quick-start-guide.md` for a detailed walkthrough.

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
