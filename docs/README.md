# SCS Documentation

Guides for using the Structured Context Specification (SCS). The normative text is the
[specification](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/overview.md); these pages explain how to use it.

---

## Getting Started

1. **[Overview](scs-overview.md)**: SCS on one page
2. **[What to Gather](what-to-gather.md)**: the documents and answers to have ready
3. **[Quick Start](quick-start-guide.md)**: a Domain from setup to a compiled version, with
   the Agent Skills or the engine
4. **[FAQ](FAQ.md)**: common questions

---

## Guides

- **[Understanding SCDs](scd-guide.md)**: what an SCD holds and how to write good rules
- **[Bundle Lifecycle](bundle-lifecycle.md)**: from DRAFT to a released, compiled version
- **[Validation](validation-guide.md)**: what is checked, and what the results mean
- **[Concept Guides](concept-docs/README.md)**: the Software Development ontology's concepts
- **[Placement](placement/README.md)**: putting a compiled artifact where an AI service reads it
- **[Install Matrix](install-matrix.md)**: which AI clients the skills have been tried in
- **[Glossary](glossary.yaml)**: short definitions; the full ones are in
  [Terminology](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/terminology.md)

---

## Reference

### Specification (0.7)
- [Overview](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/overview.md)
- [Core Model](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/core-model.md)
- [Bundle Format](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/bundle-format.md): bundles, the Domain repository, versioning
- [Runtime Artifact](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/runtime-artifact.md): what `scs compile` produces
- [Domain Ontology](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/domain-ontology.md)
- [Citations](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/citations.md)
- [Agent Interface](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/agent-interface.md): how agents operate SCS for a user
- [Governance & Compliance](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/governance-and-compliance.md)
- [Terminology](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/terminology.md)

### Tools, skills, and examples
- **[Agent Skills](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/skills/README.md)**: `scs-domain`, `scs-project`, `scs-validate`, `scs-explain`
- **[scs CLI](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/tools/cli/README.md)**: the engine (`scs`)
- **[Validator](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/tools/scd-validator/README.md)**: `scs-validate`
- **[JSON Schemas](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/schema)**
- **[Examples](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/examples/README.md)**: a CDMO and a personal Domain repository

---

## Versions

This documentation corresponds to **SCS 0.7.0**. For changes between versions, see the
migration guides, starting with [MIGRATION-0.7.0.md](MIGRATION-0.7.0.md).

---

## Contributing

- **[RFC process](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/rfcs/README.md)**: how spec changes are proposed and decided
- **[CONTRIBUTING.md](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/CONTRIBUTING.md)**
- **[CODE_OF_CONDUCT.md](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/CODE_OF_CONDUCT.md)**
- Questions: [GitHub Discussions](https://github.com/tim-mccrimmon/structured-context-spec/discussions);
  issues: [GitHub Issues](https://github.com/tim-mccrimmon/structured-context-spec/issues)
- License: [Apache 2.0](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/LICENSE)
