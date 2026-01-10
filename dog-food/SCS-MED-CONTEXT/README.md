# SCS Structured Context - Dogfooding

**Purpose:** Using SCS to manage SCS - structured context for AI systems working with SCS

**Created:** 2026-01-10

**Coverage:** Medium detail level - comprehensive but concise

---

## What This Is

This directory contains structured context bundles for SCS (Structured Context Specification) itself. It's **dogfooding** - using SCS's own structured context approach to document SCS.

When you load this bundle into an AI system (Claude, ChatGPT, etc.), it provides comprehensive understanding of:
- What SCS is and the problem it solves (CLAUDE.md isn't enough)
- The core insight (AI needs to be bounded, not smarter)
- SCS specification format (SCDs, bundles, tiers, validation)
- CLI tools and workflows
- Launch strategy and positioning

---

## How to Use

### Option 1: Load the Complete Bundle (Recommended)

**For Claude Code or similar:**
```bash
# From the OICP root directory
cat dog-food/SCS-MED-CONTEXT/bundles/scs-project.yaml
cat dog-food/SCS-MED-CONTEXT/scds/project/*.yaml
```

Copy the output and provide it to your AI at the start of a session.

### Option 2: Load Specific SCDs

If you only need specific context, load individual SCDs:

**For overview:**
```bash
cat dog-food/SCS-MED-CONTEXT/scds/project/scs-overview.yaml
```

**For specification:**
```bash
cat dog-food/SCS-MED-CONTEXT/scds/project/scs-specification.yaml
```

**For CLI tools:**
```bash
cat dog-food/SCS-MED-CONTEXT/scds/project/scs-cli-tools.yaml
```

**For launch strategy:**
```bash
cat dog-food/SCS-MED-CONTEXT/scds/project/scs-launch-strategy.yaml
```

---

## Structure

```
SCS-MED-CONTEXT/
├── README.md                          # This file
├── bundles/
│   └── scs-project.yaml              # Bundle manifest
└── scds/
    └── project/
        ├── scs-overview.yaml          # What SCS is, problem/solution, Martians analogy
        ├── scs-specification.yaml     # Spec format, SCDs, bundles, validation
        ├── scs-cli-tools.yaml         # CLI commands, workflows, best practices
        └── scs-launch-strategy.yaml   # Target audience, positioning, launch plan
```

---

## What's Covered

### Product Context
- What SCS is (open spec for structured context)
- The problem (CLAUDE.md isn't enough)
- The insight (AI needs to be bounded, not smarter)
- The Martians analogy (why context matters)
- Target audience (developers using AI coding assistants)
- Use cases (solo dev, team, open source project)

### Specification
- SCD structure (id, tier, version, content)
- Bundle structure (id, type, scds, imports)
- The 3 tiers (meta, standards, project)
- Validation philosophy (loose vs. strict)
- Composability and precedence rules
- Versioning (semantic versioning, DRAFT, immutability)
- Git integration

### CLI Tools
- Installation (pip install scs-tools)
- Commands (init, new, bundle create, validate)
- Typical workflows
- CI/CD integration (GitHub Actions)
- Tips and best practices

### Launch Strategy
- Target audience (individual devs, teams, OSS maintainers)
- Positioning (stop re-teaching AI, bounded not smarter)
- Differentiation (vs. CLAUDE.md, RAG, prompt engineering, fine-tuning)
- Distribution channels (GitHub, HN, Dev.to, Reddit, Twitter)
- Launch week schedule (Jan 13-17)
- Success metrics
- Relationship to OICP (open source funnel)

---

## Why Dogfooding Matters

**The Test:** "If SCS can't manage SCS, why would anyone use it?"

**The Proof:** By creating structured context for SCS using SCS's own approach, we validate that:
1. The specification format works in practice
2. Structured context is clearer than prose documentation
3. Context can be versioned, composed, and validated
4. AI systems get better, more consistent answers

**Before structured context:**
- AI had to parse marketing docs and README files
- Inconsistent understanding of SCS across sessions
- Had to re-explain the problem, solution, and spec format repeatedly

**With structured context:**
- Load bundle once, AI has complete understanding
- Consistent answers about SCS specification and positioning
- Can ask "What's the difference between loose and strict validation?" and get accurate answers
- Updates to launch strategy reflected by updating scs-launch-strategy.yaml

---

## Example Questions AI Can Answer

With this bundle loaded, AI can accurately answer:

**Product Questions:**
- "What is SCS?"
- "What problem does SCS solve?"
- "Why isn't CLAUDE.md enough?"
- "What's the Martians analogy?"
- "Who should use SCS?"

**Specification Questions:**
- "What's the structure of an SCD?"
- "What are the 3 tiers?"
- "How does bundle composability work?"
- "What's the difference between loose and strict validation?"
- "How do I version a bundle?"

**CLI Questions:**
- "How do I install SCS CLI?"
- "What command creates a bundle?"
- "How do I validate my bundle?"
- "How do I integrate SCS with GitHub Actions?"

**Positioning Questions:**
- "How is SCS different from RAG?"
- "How is SCS different from prompt engineering?"
- "What's SCS's relationship to OICP?"
- "Who is the target audience?"
- "When is SCS launching?"

---

## Maintenance

**Update Frequency:** As needed when SCS spec or strategy changes

**Files to Update:**
- `scs-launch-strategy.yaml` - Update as launch progresses, metrics come in
- `scs-overview.yaml` - Update if problem statement or positioning changes
- `scs-specification.yaml` - Update if spec format changes (rare)
- `scs-cli-tools.yaml` - Update when new commands added

**Version History:** Track in `bundles/scs-project.yaml` metadata

---

## Next Steps

1. **Use it:** Load this bundle when working on SCS with AI
2. **Validate it:** Test if AI gives better answers with this context
3. **Iterate it:** Update as SCS evolves (especially after launch)
4. **Expand it:** Add more SCDs as needed (e.g., contribution guidelines, examples)

---

## Meta Note

This is exactly what SCS users will do:
- Define structured context for their domain (we defined it for SCS)
- Version it (currently DRAFT, will move to 1.0.0 post-launch)
- Use it to train AI systems (we use it to train AI about SCS)
- Update it as the project evolves (we'll update post-launch)

**The dogfooding validates the approach.**

This bundle also serves as a **reference implementation** - developers can look at these SCDs to see what good structured context looks like.

---

## Using This for Launch Week

During launch week (Jan 13-17), load this bundle when:
- Writing social media posts (consistent messaging)
- Responding to questions on HN/Reddit (accurate answers)
- Creating follow-up content (blog posts, videos)
- Explaining SCS to potential users

The AI will have complete context about:
- The problem statement (CLAUDE.md isn't enough)
- The core messaging (bounded not smarter)
- The positioning (dev-time AI, not enterprise agents)
- The differentiation (vs. RAG, prompt engineering, etc.)

---

**Last Updated:** 2026-01-10
**Status:** DRAFT (ready to use, will version post-launch)
