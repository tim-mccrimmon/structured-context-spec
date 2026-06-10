# Structured Context Specification (SCS)

**Your AI doesn't remember the world you're building.**

Every session starts over. Decisions contradict earlier ones. The architectural intent you had at the start slowly erodes. The vision lives in your head — not in the AI.

SCS is the fix: a structured, versioned format for giving your AI a world to operate in, not just prompts to respond to.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-green)
![Status](https://img.shields.io/badge/status-active_development-orange)

⭐ If this is solving a real problem, a star helps other developers find it.

---

## Start Here: The Plugins

The fastest path into SCS is through the Claude Code plugins. No new format to learn — they output native Claude Code files.

### SCS Vibe — For solo developers and Vibe Coders

Captures your architectural intent, surfaces compliance and security considerations, and writes everything to `CLAUDE.md + .claude/rules/` — exactly where Claude Code expects it.

```
/scs-vibe:init
```

[Plugin overview →](plugins/scs-vibe/scs-vibe-plugin-overview.md)

### SCS Team — For development teams

Structures team-wide context: architecture decisions, coding conventions, domain knowledge, standards compliance. Consistent behavior across the team without constant re-explanation.

[Team plugin →](plugins/scs-team/README.md)

---

## The Problem

If you're building with AI, you're probably already managing context by hand — writing `CLAUDE.md` files, keeping rules somewhere, re-explaining decisions every session. It works until it doesn't.

The real problem: that context ends up scattered across prompts, docs, code comments, wikis, and memory. It drifts. It conflicts. There's no way to validate it, version it, or audit what the AI actually knows about your system.

SCS makes what you're already doing principled: validated, versioned, composable.

---

## What SCS Provides

A specification and tooling for representing AI context as structured, versioned artifacts:

- **Concise** — focused, atomic definitions, not walls of text
- **Precise** — structured YAML, not ambiguous prose
- **Non-conflicting** — explicitly composed and validated
- **Versionable** — git-native, reviewable, auditable
- **Reusable** — composable bundles across standards, domains, and projects

---

## SCS and Claude Code

SCS maps directly onto Claude Code's native context hierarchy:

| Claude Code | SCS |
|-------------|-----|
| `CLAUDE.md` (project / global / enterprise) | Domain / Project bundles |
| `.claude/rules/` | Individual SCDs |
| `.claude/agents/` | Per-agent context composition |

The scs-vibe plugin outputs to this structure by design. If you're writing `CLAUDE.md` files by hand, you're already doing structured context. SCS is how you do it with validation and versioning.

---

## Core Concepts

**Structured Context Documents (SCDs)** — individual YAML files, each containing one specific piece of context: a rule, a constraint, a compliance requirement, a design decision.

**Bundles** — composed collections of SCDs:
- **Standards Bundle** — regulatory requirements (HIPAA, SOC2, CHAI)
- **Domain Bundle** — company-wide or concern-specific context
- **Project Bundle** — your initiative, importing what it needs

---

## Quick Start

### Option 1: Claude Code Plugin (recommended)

```
/scs-vibe:init
```

Walks you through capturing your project's intent and outputs native Claude Code context files. No YAML knowledge required.

### Option 2: CLI

```bash
pip install scs-tools
scs new project my-app
cd my-app
scs validate
```

[CLI documentation →](tools/cli/README.md)

### Option 3: Manual

```bash
git clone https://github.com/tim-mccrimmon/structured-context-spec.git
```

Start with `spec/0.3/overview.md` and `examples/bundles/project-bundle.yaml`.

---

## What SCS Is Not

- Not a prompt engineering framework
- Not a RAG system or vector database
- Not an agent orchestration runtime

---

## Repository Structure

```
structured-context-spec/
├── spec/0.3/          # Normative spec
├── schema/            # JSON Schemas
├── plugins/           # Claude Code plugins
├── templates/         # YAML starters
├── tools/             # Validation & CLI
├── examples/          # Example bundles
├── docs/              # Guides
└── rfcs/              # RFC process
```

---

## Contributing

SCS is v0.3, actively evolving, and open to contribution.

- **Discussions** — use cases, boundary arguments, counterexamples that break the model
- **Issues** — schema problems, unclear terminology, missing examples
- **RFCs** — major changes via `rfcs/README.md`

---

## Governance

v0.x: benevolent maintainer model. Maintainer: Tim McCrimmon.
Goal: transition to broader community governance at v1.0.

---

## License

Apache License 2.0 — Copyright © 2026 Tim McCrimmon / Ohana Consulting LLC

---

⭐ If SCS is solving a real problem for you, a star helps other developers find it.
