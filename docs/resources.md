# SCS Resources

## How It Works

![Create, Validate, Version Structured Context](../images/scs-create-validate-version.png)

SCS follows a three-stage workflow: **Create, Validate, Version.**

1. **Gather your governance docs.** Start with what you already have — regulatory compliance policies, corporate standards, security requirements, architecture decisions, business guidance, performance targets, reliability expectations, topology definitions. These are the source materials.

2. **Transcode with AI assistance.** Feed your documents to any LLM (Claude, ChatGPT, Gemini) along with SCS transcoding and validation rules. The AI transforms unstructured prose into structured context documents (SCDs) — concise, precise YAML artifacts that capture the same knowledge in a machine-readable format.

3. **Review, refine, and bundle.** Executives and team leads review the generated SCDs for accuracy and completeness. Iterate as needed — this is a collaborative process between humans and AI. Once approved, SCDs are composed into a structured context bundle.

4. **Version and lock.** When the bundle is ready, it gets a semantic version (e.g., v1.2.3) and becomes immutable. This is your approved, locked context — versioned alongside code, auditable, and ready for consumption by AI agents across your organization.

The feedback loop between steps 2 and 3 is where the real value emerges: domain experts validate that AI correctly captured their knowledge, and the structured output makes gaps and conflicts visible in a way that scattered documents never could.

---

## Specification and Source Code

**GitHub Repository**
https://github.com/tim-mccrimmon/structured-context-spec

The complete SCS specification (v0.3), JSON schemas, validation tooling, examples, and templates. Open source under the Apache 2.0 license.

**Website**
https://structuredcontext.dev

The website includes links to YouTube demos of both the SCS Vibe and SCS Team plugins in action.

---

## Claude Code Plugins

SCS ships two Claude Code plugins for different team profiles:

### SCS Vibe

> Stop Claude from coding you into corners. In 15 minutes.

For solo developers and vibe coders. A quick, conversational setup that generates structured context for your project through a few targeted questions. No PRDs or architecture docs required.

**Commands:**
- `/scs-vibe:init` — Interactive setup that generates structured context
- `/scs-vibe:validate` — Validate your context files
- `/scs-vibe:explain` — Explain what SCS is doing in your project

### SCS Team

> Transform your documentation into context Claude actually uses.

For teams with existing documentation — PRDs, architecture docs, security requirements, compliance checklists. SCS Team processes your docs into structured context and maintains a dual-layer output: structured source (`.scs/`) and compiled Claude Code rules (`.claude/rules/`).

**Commands:**
- `/scs-team:init` — Scaffold `.scs/` with 11 concern bundles
- `/scs-team:add` — Process existing docs into structured context
- `/scs-team:use` — Add compliance standards (e.g., HIPAA, SOC2)
- `/scs-team:draft` — Draft context for areas not yet documented
- `/scs-team:status` — See coverage and gaps across concerns
- `/scs-team:validate` — Validate context structure and completeness
- `/scs-team:version` — Version and lock your context bundle

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/tim-mccrimmon/structured-context-spec.git
cd structured-context-spec

# Explore the spec
ls spec/0.3/

# Try a plugin (local development)
claude --plugin-dir plugins/scs-vibe
# or
claude --plugin-dir plugins/scs-team
```

For detailed guides, see the [Quick Start Guide](quick-start-guide.md) and [SCD Authoring Guide](scd-guide.md).
