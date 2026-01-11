# Dogfooding: Using SCS to Build SCS

This directory contains structured context bundles that document SCS itself—built using the SCS specification.

**"If SCS can't manage SCS, why would anyone use it?"**

This is both:
- **Proof** that SCS works in practice
- **Reference implementation** showing what good bundles look like
- **Actual context** we use when developing SCS

---

## Quick Start

Load SCS context into your AI (Claude, ChatGPT, etc.):

```bash
# From the repo root
cat dog-food/SCS-MED-CONTEXT/bundles/scs-project.yaml
cat dog-food/SCS-MED-CONTEXT/scds/project/*.yaml
```

Paste the output into your AI. Now it understands:
- What SCS is and the problem it solves
- The specification format (SCDs, bundles, tiers)
- CLI tools and workflows
- Launch strategy and positioning

---

## What's Inside

### `/SCS-MED-CONTEXT/`

**SCS Medium Detail Context**

A complete SCS project bundle documenting SCS itself:

**SCDs (Structured Context Documents):**
- `scs-overview.yaml` - Problem/solution, the Martians analogy, target audience
- `scs-specification.yaml` - Format, structure, validation, versioning
- `scs-cli-tools.yaml` - Commands, workflows, CI/CD integration
- `scs-launch-strategy.yaml` - Positioning, differentiation, launch plan

**Bundle:**
- `scs-project.yaml` - Manifest that ties all SCDs together

---

## Why This Matters

### For New Contributors
Clone the repo, load this bundle, ask your AI:
- "How do I create a bundle?"
- "What's the difference between loose and strict validation?"
- "What are the 3 tiers?"

Get accurate answers immediately. No reading 20 markdown files.

### For Evaluators
See SCS in action on itself. This is what your bundles would look like.

### For the Meta
We're eating our own dog food. The structured context spec uses structured context to document itself.

**That's the validation.**

---

## Try It

1. **Load the bundle** (copy/paste the YAML files above into Claude)
2. **Ask questions** about SCS
3. **Compare** to reading README/docs
4. **Notice** how the AI gives consistent, structured answers

This is the promise of SCS—proven on itself.

---

## As a Reference

Use these SCDs as examples when creating your own:
- See how we structure the `content` field
- See how we organize related information
- See how we handle provenance
- Copy the patterns for your project

---

**Last Updated:** 2026-01-10
**Status:** DRAFT (will version to 1.0.0 post-launch)
