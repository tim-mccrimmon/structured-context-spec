# SCS Resources

## How It Works


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

The website's demo videos show the earlier SCS Vibe and SCS Team plugins, which SCS 0.7
replaces with Agent Skills.

---

## Agent Skills

SCS 0.7 ships seven Agent Skills in [`skills/`](../skills/README.md): `scs-intake`, `scs-draft`,
`scs-review`, `scs-validate`, `scs-version`, `scs-compile`, and `scs-explain`. They let an AI
assistant set up, maintain, version, and compile your context through the SCS engine,
confirming each change with you first. They replace the earlier SCS Vibe and SCS Team plugins,
which were removed in 0.7.

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/tim-mccrimmon/structured-context-spec.git
cd structured-context-spec

# Explore the spec
ls spec/0.3/

# Try the Agent Skills in Claude Code (see skills/README.md)
cp -R skills/scs-* ~/.claude/skills/
```

For detailed guides, see the [Quick Start Guide](quick-start-guide.md) and [SCD Authoring Guide](scd-guide.md).
