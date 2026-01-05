# Structured Context Specification (SCS)

**If you are using AI and not using Structured Context - you are doing it wrong.**

**A universal, domain-agnostic platform for reliable AI-assisted professional work across all industries.**

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-Apache_2.0-green)
![Status](https://img.shields.io/badge/status-active_development-orange)

---

## The Problem

AI is transforming professional work across all domains — legal, clinical, financial, software development, and more. But without structured context, AI assistance creates critical challenges:

- **No provenance**: Can't prove what context AI used when generating deliverables (code, contracts, treatment plans, financial models)
- **No compliance proof**: Can't demonstrate adherence to regulations (HIPAA, Bar standards, clinical guidelines, SOC2)
- **Conflicting outputs**: Multiple AI tools lack coordination and shared context
- **No audit trail**: Can't trace professional decisions back to human approval
- **Legal liability**: AI-generated work product is indefensible in regulated professional environments

**Across regulated professions (healthcare, legal, finance, software), these limitations make AI assistance unreliable for production work.**

---

## The Solution

**SCS provides a machine-readable framework for structured context** that is:

- **Human-readable** and reviewable
- **Machine-readable** for AI and automation
- **Version-controlled** in git
- **Enforceable** through validation
- **Governable** through autonomic agents
- **Legally defensible** with complete provenance

SCS makes **context a first-class, version-controlled artifact** — not ephemeral input that disappears after use.

---

## Why This Matters

### Legal Protection & Indemnification
**Without SCS**: "The AI generated it. We don't know what context it used."
**With SCS**: "The AI operated within documented constraints, satisfied compliance requirements, and was validated by [human]. Here's the provenance."

### Compliance on Launch Day
**Traditional**: Ship → Retrofit compliance (6-12 months) → Maybe certify
**With SCS**: Continuous validation → **Certified on launch day**
**Impact**: Saves millions in post-facto compliance work and delayed market entry

### Multi-AI Coordination
As teams add AI assistants (dev, security, architecture, compliance), coordination becomes chaos without shared context.

**SCS provides**: A single source of truth that all AI tools consume, preventing conflicts and ensuring alignment.

### Autonomic Governance
Governance agents operating over SCD bundles can:
- Continuously validate compliance with standards
- Detect architectural drift and missing mappings
- Answer "Are we HIPAA compliant?" in real-time
- Perform impact analysis ("What breaks if we change this?")
- Generate audit reports automatically

### Transparency by Design
Every SCD includes provenance:
```yaml
provenance:
  created_by: tim@company.com
  created_at: 2025-12-09T10:00:00Z
  rationale: "Changed encryption to AES-256 per CSO requirement for HIPAA"
```

---

## Core Concepts

SCS 0.3 introduces a **multi-domain platform** supporting professional work across all industries.

### Three-Tier SCD Model

**Structured Context Documents (SCDs)** are organized into three tiers:

#### Meta-Tier: Universal Semantic Foundation
Defines universal concepts across all domains:
- Roles and capabilities
- Domain concepts
- Cross-cutting concerns
- Architectural patterns

#### Standards-Tier: External Obligations
Represents compliance frameworks as importable contracts:
- HIPAA, SOC2, GDPR, ISO standards (software)
- Bar association rules (legal)
- Clinical practice guidelines (healthcare)
- Financial regulations (finance)

#### Project-Tier: Your Actual Work
Describes the specific work being done:
- System architecture (software)
- Case strategy (legal)
- Treatment protocols (clinical)
- Risk models (financial)

### Five Bundle Types

**Bundles** are manifest documents that organize SCDs and other bundles:

1. **Project Bundle** - Top-level orchestrator for complete project context
2. **Meta Bundle** - Universal vocabulary
3. **Standards Bundle** - Compliance requirements
4. **Concern Bundle** - Functional area (Architecture, Security, Case Management, Treatment Planning)
5. **Domain Bundle** - Industry vertical (Software Development, Legal, Clinical, Financial)

**Hierarchy**: Project → Domains → Concerns → SCDs

### Multi-Domain Platform

SCS 0.3 supports multiple professional domains:
- **Software Development** (reference implementation) - 11 software engineering concerns
- **Legal** (future) - Case management, legal research, document drafting
- **Clinical** (future) - Patient care, treatment protocols, clinical decision support
- **Financial** (future) - Portfolio management, risk assessment
- **And more...** - Domain experts create domains for their professions

**Platform Model**: SCS provides the architecture; domain experts create domain-specific concerns and content schemas.

---

## What's in This Repository

This repository contains the **complete SCS 0.3 specification**:

✅ **Normative specification** ([spec/0.3/](spec/0.3/)) - Core specification documents
✅ **Domain manifests** ([schema/domain/](schema/domain/)) - Domain definition schemas
✅ **JSON Schemas** ([schema/](schema/)) - Bundle and SCD validation schemas
✅ **YAML Templates** ([templates/](templates/)) - Quick-start files
✅ **Educational guides** ([docs/](docs/)) - Documentation and guides
✅ **Validation tools** ([tools/](tools/)) - Domain-aware SCD validator
✅ **Example implementations** ([examples/](examples/)) - Software Development domain reference

---

## Repository Structure

```
scs-commercial/
├── spec/0.3/                  # Normative specification (0.3 multi-domain release)
│   ├── overview.md            # Multi-domain vision and platform model
│   ├── terminology.md         # Domains, concerns, and bundle types
│   ├── bundle-format.md       # 5 bundle types and validation rules
│   └── ...
├── schema/                    # JSON Schemas for validation
│   ├── domain/                # Domain manifest schema
│   ├── bundles/               # Bundle schema (5 types)
│   └── scd/                   # Meta, project, standards SCD schemas
├── templates/                 # YAML starter files
│   ├── scd/                   # SCD templates by tier
│   └── bundles/               # Bundle templates by type
├── docs/                      # Documentation and guides
│   ├── concern-docs/          # Concern-specific templates and examples
│   └── ...
├── tools/                     # Validation and tooling
│   └── scd-validator/         # Domain-aware SCD and bundle validator
├── examples/                  # Complete example bundles
│   └── bundles/
│       ├── concerns/          # Software Development concern bundles (11)
│       ├── domains/           # Domain bundles (software-development)
│       └── ...                # Meta, standards, project bundles
├── context/                   # Working context files
├── rfcs/                      # RFC process for major changes
├── CONTRIBUTING.md            # How to contribute
└── LICENSE                    # Apache 2.0 license
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/tim-mccrimmon/scs-spec.git
cd scs-spec
```

### 2. Explore the Documentation

**New to SCS? Start with:**
1. [spec/0.3/overview.md](spec/0.3/overview.md) - Why SCS matters and the complete vision
2. [docs/quick-start-guide.md](docs/quick-start-guide.md) - Build your first bundle in 30 minutes
3. [docs/FAQ.md](docs/FAQ.md) - Common questions answered
4. [docs/scd-guide.md](docs/scd-guide.md) - Complete SCD reference

**Understanding the system?**
1. [spec/0.3/overview.md](spec/0.3/overview.md) - Multi-domain vision and platform model
2. [spec/0.3/terminology.md](spec/0.3/terminology.md) - Domains, concerns, and bundle types
3. [spec/0.3/bundle-format.md](spec/0.3/bundle-format.md) - 5 bundle types and validation

**Building tools or creating domains?**
1. [schema/domain/](schema/domain/) - Domain manifest schema
2. [schema/bundles/](schema/bundles/) - Bundle schemas
3. [examples/bundles/domains/](examples/bundles/domains/) - Software Development domain reference
4. [tools/scd-validator/](tools/scd-validator/) - Domain-aware validation

### 3. Create Your First SCD

```bash
# Copy a template
cp templates/scd/project_scd_template.yaml my-first-scd.yaml

# Edit it following the specification
# See docs/ for guidance

# Validate it
cd tools/scd-validator
python validate.py ../../my-first-scd.yaml
```

### 4. Build a Bundle

```bash
# Copy a bundle template
cp templates/bundles/minimal-project-bundle.yaml my-bundle.yaml

# Reference your SCDs in the bundle
# Validate the bundle
cd tools/scd-validator
python validate.py --bundle ../../my-bundle.yaml
```

---

## Who Should Use SCS?

### Professional Domains

**Software Development:**
- Development teams using AI code assistants
- CTOs integrating AI safely without regulatory risk
- Chief Architects maintaining architectural integrity
- DevOps teams managing complex systems

**Legal:**
- Law firms using AI for case research and document drafting
- Compliance officers tracking regulatory adherence
- Legal operations managers coordinating casework

**Clinical/Healthcare:**
- Clinicians using AI for diagnosis and treatment planning
- Healthcare administrators ensuring HIPAA compliance
- Clinical decision support system developers

**Financial:**
- Financial analysts using AI for portfolio management
- Risk officers assessing and modeling risk
- Compliance teams tracking financial regulations

**Cross-Domain:**
- **Domain experts** creating new domains for their professions
- **Governance officers** enforcing standards and compliance
- **Auditors** validating and tracing professional decisions
- **Tool builders** creating domain-aware AI assistants

### Use Cases
- **AI-assisted professional work** - Using AI assistants across any domain
- **Regulated professions** - Where compliance and accountability are mandatory
- **Complex decision-making** - Need clear context and governance
- **Multi-team coordination** - Alignment across teams and AI tools
- **Domain creation** - Building structured context frameworks for new industries

---

## Key Features

### Three-Tier Architecture
Separates universal semantics (meta), external obligations (standards), and project specifics (project)

### Knowledge Graph
SCDs form relationships enabling impact analysis, compliance checking, and dependency tracking

### Git-Native
YAML/JSON formats integrate seamlessly with version control, enabling full change history and provenance

### Autonomic Governance
AI agents operate over bundles to continuously validate compliance and detect issues

### Shared Standards Registry
Import standards-tier SCDs from scs-registry instead of reinventing compliance

### Schema-Driven Validation
JSON Schemas enable validation, IDE integration, and automated governance tooling

### Provenance by Default
Every SCD tracks who, when, and why for complete accountability and legal defensibility

---

## Part of the SCS Ecosystem

SCS is the specification layer within a larger ecosystem:

- **scs-spec** (this repo) - The specification itself
- **scs-registry** - Shared standards-tier SCDs (HIPAA, SOC2, ISO, etc.)
- **scs-tools** - Validators, editors, governance agents
- **scs-reference-implementation** - Healthcare example demonstrating SCS

---

## Current Status

**Version**: 0.3.0 (Multi-Domain Release)
**Status**: Active development
**Stability**: Suitable for experimentation, early adoption, and feedback

### Completed in 0.3 ✅
- **Multi-domain architecture** - Platform supporting all professional domains
- **Five bundle types** - Project, Meta, Standards, Concern, Domain
- **Domain manifest specification** - How domains are defined and structured
- **Software Development domain** - Reference implementation with 11 concerns
- **Updated JSON Schemas** - Bundle and domain validation
- **Domain-aware validator** - Validates new bundle type rules
- **Updated documentation** - Spec, examples, and guides for 0.3

### Completed Previously ✅
- Core specification documents
- JSON Schemas for three SCD tiers
- YAML templates for SCDs and bundles
- Educational guides and documentation
- Governance model with RFC process

### Roadmap
- **Domain creation** - Legal, Clinical, Financial domains by domain experts
- **Domain registry** - Marketplace for domains and compliance standards
- **Enhanced tooling** - IDE integrations, domain-aware AI assistants
- **Real-world validation** - Production use cases across multiple domains
- **Public working group** - Community governance for v1.0

---

## Getting Involved

### Report Issues or Request Features
[Open an issue](https://github.com/tim-mccrimmon/scs-spec/issues/new/choose) for bugs, suggestions, or questions

### Propose Changes
- **Minor changes** (typos, examples, clarifications): Submit a PR directly
- **Major changes** (new concepts, breaking changes): [Open a discussion](https://github.com/tim-mccrimmon/scs-spec/discussions) first, then submit an RFC

See [rfcs/README.md](rfcs/README.md) for the RFC process.

### Contribute
Read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Contribution guidelines
- Development standards
- PR process and review criteria
- Branch naming conventions

### Join the Community
- **GitHub Discussions**: Ask questions, share ideas, propose features
- **Issues**: Report bugs, request enhancements
- **RFCs**: Propose major specification changes ([rfcs/](rfcs/))

---

## Governance

SCS follows a **Benevolent Maintainer** model during v0.x:
- **Tim McCrimmon** serves as primary maintainer
- Community input welcomed via issues, discussions, and RFCs
- Major changes require formal RFC (Request for Comments) process (see [rfcs/README.md](rfcs/README.md))
- Transition to community governance planned for v1.0

---

## License

**Apache License 2.0**

Copyright © 2026 Tim McCrimmon / Ohana Consulting LLC

See [LICENSE](LICENSE) for complete terms.

---

## Learn More

- **Specification Documents**: [spec/0.3/](spec/0.3/) - Multi-domain architecture and vision
- **Domain Manifest Schema**: [schema/domain/](schema/domain/) - How to create domains
- **Example Domain**: [examples/bundles/](examples/bundles/) - Software Development reference
- **RFC Process**: [rfcs/README.md](rfcs/README.md) - How to propose major changes
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

## Why Now?

AI is transforming professional work across all domains — but without structured context, professionals and organizations face increased risks in governance, liability, and compliance management.

As AI adoption spreads across legal, clinical, financial, and software domains, the need for **structured, auditable, version-controlled context** becomes critical — especially in regulated professions where accountability and traceability are mandatory.

**SCS provides the universal infrastructure for trustworthy, governable, AI-assisted professional work across all industries.**

We welcome contributions from domain experts to create new domains and expand the SCS platform.

---

**Questions?** [Open an issue](https://github.com/tim-mccrimmon/scs-spec/issues/new/choose) or [start a discussion](https://github.com/tim-mccrimmon/scs-spec/discussions).
