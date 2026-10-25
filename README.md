# Structured Context Specification (SCS)

**Approved, versioned context that serves as the source of truth for AI.**

SCS is an open specification for the context an AI works within: the rules it follows, the
things it must never do, and the facts it should treat as given. That context lives in a
small, validated bundle. Once a person approves a version, it doesn't change. Whatever your AI
vendor or runtime needs (a `CLAUDE.md`, an `AGENTS.md`, a system prompt, a gateway policy) is
a rendering of that bundle, and can always be traced back to the version it came from.

![Version](https://img.shields.io/badge/version-0.6.0-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-green)
![Status](https://img.shields.io/badge/status-active_development-orange)

---

## Why

Most teams building with AI already manage context, usually by hand: instruction files,
rules folders, prompts copied between tools, decisions re-explained every session. It works
for a while. Then it drifts, conflicts, and nobody can say with confidence what the AI was
told, which version, or who decided it.

For regulated organizations, that last question matters most. When an auditor asks how an AI
tool was governed, the answer needs to be a record: what was approved, by whom, and when.

SCS gives that context the discipline of code. It is structured, validated, versioned, and
reviewable, and it isn't tied to any one AI vendor.

---

## How It Works

**Domain.** The capacity work is done in. For an organization, that's company-wide rules: its
quality system, prohibited tools, the facts every AI should know. For an individual
developer, it can be as small as their name, the fact that the work is personal, and a few
rules they want everywhere. One person can work under several Domains, such as personal
projects and their employer's.

**Project.** Context for one AI initiative: its scope, risk, data, and project-specific rules.
Every Project runs under a Domain. Domain and Project bundles are independent and compile
separately, so organization-wide context and project context can be placed where each belongs.

**Structured Context Documents (SCDs).** YAML files holding the content, in three forms:

- **prohibitions:** things that are never allowed;
- **directives:** rules the AI follows, each with an id;
- **facts:** information the AI treats as given.

**Ontologies.** Industry starting points that decide which SCDs a new workspace gets:
software development (`sdlc`), medical-device CDMO (`cdmo`), and merchant cash advance (`mca`).

**Citations.** Standards appear as references, such as `std:iso-13485:2016#7.3.9`, never as
standard text.

**Versioned bundles and runtime artifacts.** A validated bundle is versioned with a named
approver. `scs compile` turns it into one compact, deterministic artifact that names its
bundle and version, ready for any runtime to use.

SCS stops at the versioned bundle and its compiled artifact. Where you put the artifact, and
what form you render it into, is up to you.

---

## Quick Start

```bash
pip install 'scs-tools[validator]'

scs new domain my-org --ontology sdlc     # organization-wide (or personal) context
cd my-org
scs bundle validate
scs compile bundles/domain-bundle.yaml --allow-draft -o global.yaml
```

Fill in the scaffolded SCDs, validate until it's clean, then version it with a named approver
(`scs bundle version --version 1.0.0 --approved-by you@example.com`) and compile without
`--allow-draft`. `scs new project my-app` does the same for a Project.

- [Quick start guide](docs/quick-start-guide.md)
- [Bundle lifecycle](docs/bundle-lifecycle.md)
- [CLI documentation](tools/cli/README.md)
- [Migrating to 0.6.0](docs/MIGRATION-0.6.0.md)

Known issues in the 0.6.0 tooling are tracked in [ISSUES.md](ISSUES.md).

---

## Where SCS Is Heading

SCS 0.6.0 still expects you to learn the format. The next releases aim to remove that
requirement: you describe your organization or project to an AI assistant, and it builds,
validates, and versions the bundles with you, asking for your approval at each step.

- **[RFC 0002: Agent-Mediated SCS](rfcs/RFC-0002-agent-mediated-scs.md)** (accepted, planned
  for 0.7.0). An agent interface to the full lifecycle through Agent Skills and an optional
  MCP server; an adaptive intake for individuals and organizations; one repository per Domain;
  content digests that make versioned bundles verifiably immutable; and an advisory review in
  which the agent raises problems and the human decides.
- **[RFC 0003: Review Profiles](rfcs/RFC-0003-review-profiles.md)** (early stub). Declarative,
  citable checks per framework (for example CHAI, HIPAA, or ISO 13485) that make the agent's
  review consistent and auditable.

Feedback is welcome in Discussions and Issues.

---

## Examples

- [`examples/two-tier-governance/`](examples/two-tier-governance/): a Domain and a Project side by side
- [`examples/medical-device-cdmo/`](examples/medical-device-cdmo/): the `cdmo` ontology applied
- [`examples/merchant-cash-advance/`](examples/merchant-cash-advance/): the `mca` ontology applied

---

## What SCS Is Not

- Not a prompt engineering framework
- Not a RAG system or vector database
- Not an agent orchestration runtime
- Not a way to deliver context at runtime; runtimes consume what SCS produces

---

## Repository Structure

```
structured-context-spec/
├── spec/0.6/          # Normative spec (current draft)
├── schema/            # JSON Schemas
├── meta/              # The published meta bundle (bundle:meta:0.6.0)
├── tools/             # scs CLI and scs-validate
├── templates/         # YAML starters
├── examples/          # Example bundles
├── docs/              # Guides
├── rfcs/              # Proposals for spec changes
└── plugins/           # Claude Code plugins (pre-0.6; see below)
```

---

## Claude Code Plugins (pre-0.6)

The `scs-vibe` and `scs-team` plugins in [`plugins/`](plugins/) offered an early
conversational path into SCS for Claude Code. They're built on the model SCS used before
0.6.0 (concern bundles) and haven't been updated. They remain available for reference; RFC
0002 proposes a portable replacement built on Agent Skills.

---

## Contributing

SCS is at 0.6 (draft), actively evolving, and open to contribution.

- **Discussions:** use cases, boundary arguments, counterexamples that break the model
- **Issues:** schema problems, unclear terminology, missing examples
- **RFCs:** significant changes, through the process in [`rfcs/README.md`](rfcs/README.md)

---

## Governance

v0.x: benevolent maintainer model. Maintainer: Tim McCrimmon.
Goal: transition to broader community governance at v1.0.

---

## License

Apache License 2.0. Copyright © 2026 Tim McCrimmon / Ohana Consulting LLC.
