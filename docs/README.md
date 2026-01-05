# SCS Documentation

Welcome to the Structured Context Specification (SCS) documentation. This directory contains practical guides and reference materials for understanding and using SCS.

---

## Getting Started

**New to SCS? Start here:**

1. **[Quick Start Guide](quick-start-guide.md)** - Build your first SCD bundle in 30 minutes
2. **[FAQ](FAQ.md)** - Common questions about SCS answered
3. **[Glossary](glossary.yaml)** - Key terminology and definitions

---

## Core Concepts

**Understanding how SCS works:**

- **[Understanding SCDs](scd-guide.md)** - What SCDs are, how to create them, and best practices
- **[Bundle Lifecycle](bundle-lifecycle.md)** - How bundles evolve from concept to versioned contract
- **[Validation Guide](validation-guide.md)** - Ensuring quality, compliance, and integrity

---

## Reference Materials

### Specification
- **[Normative Specification](../spec/0.1/)** - The complete SCS specification
  - [Overview](../spec/0.1/overview.md) - High-level introduction
  - [Core Model](../spec/0.1/core-model.md) - Data structures and relationships
  - [Meta Tier](../spec/0.1/meta-tier.md) - Semantic foundation
  - [Project Tier](../spec/0.1/project-tier.md) - Project-specific context
  - [Standards Tier](../spec/0.1/standards-tier.md) - External obligations
  - [Bundle Format](../spec/0.1/bundle-format.md) - Bundle structure
  - [Governance & Compliance](../spec/0.1/governance-and-compliance.md)
  - [Terminology](../spec/0.1/terminology.md)

### Schemas & Templates
- **[JSON Schemas](../schema/)** - Validation schemas for SCDs and bundles
- **[YAML Templates](../templates/)** - Ready-to-use SCD and bundle templates

### Examples
- **[Domain Documentation Examples](domain-docs/)** - Real-world implementations
  - [Med Adherence Project](domain-docs/med-adherence-examples/)

---

## Tools & Validation

- **[SCD Validator](../tools/scd-validator/)** - Command-line validation tool
  - [Validator README](../tools/scd-validator/README.md) - Usage instructions
  - [Validator Overview](../tools/scd-validator/VALIDATOR_OVERVIEW.md) - Technical details

---

## Project Resources

### Governance & Contributing
- **[GOVERNANCE.md](../GOVERNANCE.md)** - Governance model and RFC process
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute
- **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** - Community standards

### License
- **[LICENSE.md](../LICENSE.md)** - Apache 2.0 license terms
- **[NOTICE.md](../NOTICE.md)** - Attribution and notices

---

## Documentation Map

### By Use Case

**"I want to understand SCS"**
→ Start with [FAQ](FAQ.md), then read [SCD Guide](scd-guide.md)

**"I want to build my first bundle"**
→ Follow the [Quick Start Guide](quick-start-guide.md)

**"I need to understand bundles in depth"**
→ Read [Bundle Lifecycle](bundle-lifecycle.md)

**"I need to validate my SCDs"**
→ Read [Validation Guide](validation-guide.md), then use the [SCD Validator](../tools/scd-validator/)

**"I want to see examples"**
→ Browse [domain-docs/](domain-docs/)

**"I'm building tools that use SCS"**
→ Study the [JSON Schemas](../schema/) and [Core Model](../spec/0.1/core-model.md)

**"I want to understand the specification formally"**
→ Read the [Normative Specification](../spec/0.1/)

---

## Version

This documentation corresponds to **SCS v0.2.0**.

For information about changes between versions, see the project [CHANGELOG](../CHANGELOG.md) (when available).

---

## Questions or Feedback?

- **Ask questions**: [GitHub Discussions](https://github.com/tim-mccrimmon/scs-spec/discussions)
- **Report issues**: [GitHub Issues](https://github.com/tim-mccrimmon/scs-spec/issues)
- **Propose improvements**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
