# Concept Guides (Software Development ontology)

One page per concept of the Software Development (`sdlc`) Ontology Model, the default for
`scs new domain`. Each page says what the concept covers, which template SCDs the engine
scaffolds for it in a Domain and in a Project, its default owner role, and what to gather.

| Concept | Domain | Project |
|---|---|---|
| [Architecture](architecture/README.md) | yes | yes |
| [Business Context](business-context/README.md) | | yes |
| [Compliance & Governance](compliance-governance/README.md) | yes | yes |
| [Data & Provenance](data-provenance/README.md) | yes | yes |
| [Deployment & Operations](deployment-operations/README.md) | yes | yes |
| [Ethics & AI Accountability](ethics-ai-accountability/README.md) | yes | yes |
| [Performance & Reliability](performance-reliability/README.md) | | yes |
| [Safety & Risk](safety-risk/README.md) | | yes |
| [Security](security/README.md) | yes | yes |
| [Testing & Validation](testing-validation/README.md) | yes | yes |
| [Usability & Accessibility](usability-accessibility/README.md) | yes | yes |

A Domain also gets `company` (facts about the organization) and `prohibited` (binary
prohibitions). The concepts are a starting point, not a requirement: keep what applies,
retire the rest, and add your own with `scs add bundle <name> --new`. Other Ontology Models
(`cdmo`, `mca`, `personal`) have their own concepts; see
[`spec/0.7/domain-ontology.md`](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/domain-ontology.md).
