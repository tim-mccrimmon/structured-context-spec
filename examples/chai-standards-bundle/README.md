# CHAI Prior Authorization Standards Bundle

## What This Is

A transposition of the [CHAI (Coalition for Health AI) Prior Authorization Best Practice Guide and Testing & Evaluation Framework](https://www.chai.org/workgroup/use-case/ai-supported-prior-authorization-criteria-matching) into SCS standards bundle format.

CHAI defines **what** responsible AI looks like for prior authorization. This bundle encodes those requirements as structured, versioned, machine-readable governance context that can be delivered to AI agents via SCS.

## Source Documents

- **Best Practice Guide (BPG)**: [CHAI PA BPG v1.0](https://www.chai.org/workgroup/use-case/ai-supported-prior-authorization-criteria-matching) (December 2025)
- **Testing & Evaluation Framework**: [CHAI PA T&E Framework](https://rai-content.chai.org/en/latest/prior-authorization-ai-supported-criteria-matching/t%26e-framework.html)
- **GitHub**: [coalition-for-health-ai/responsible-ai-content](https://github.com/coalition-for-health-ai/responsible-ai-content)

## Bundle Structure

```
chai-standards-bundle/
├── bundle.yaml                          # Standards bundle manifest
├── README.md                            # This file
└── scds/
    ├── chai-pa-usefulness.yaml          # Usefulness, Usability, Efficacy
    ├── chai-pa-fairness.yaml            # Fairness and Bias Management
    ├── chai-pa-safety.yaml              # Safety and Reliability
    └── chai-pa-transparency.yaml        # Transparency
```

## The Four CHAI Principles → Four SCDs

| SCD | CHAI Principle | Key Requirements |
|-----|---------------|-----------------|
| `chai-pa-usefulness` | Usefulness, Usability, Efficacy | TAT compliance (72hr/7day), >=90% policy coverage, >=95% scope rejection, appeal overturn monitoring |
| `chai-pa-fairness` | Fairness and Bias Management | PPV parity across demographics (>0.05 triggers review), toxicity scoring (<10%), auto-approve vs. manual review disparity |
| `chai-pa-safety` | Safety and Reliability | FMEA with RPN <100, >=99.9% uptime, fail-safe to human review, AI-specific risk categories |
| `chai-pa-transparency` | Transparency | CHAI Model Card, decision traceability, context version auditability |

## Using This Today

### Option 1: With the SCS Team Plugin (Recommended)

If you have the [SCS Team plugin](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/plugins/scs-team) installed:

1. Clone or download this repository
2. Copy the four SCD files into your project's `.scs/scds/` directory:
   ```bash
   cp scds/*.yaml /your-project/.scs/scds/
   ```
3. Run `/scs-team:status` — the plugin picks up the new SCDs automatically and compiles them to `.claude/rules/`

Claude will now operate within CHAI governance boundaries for prior authorization criteria matching.

### Option 2: Direct Context (No Plugin Required)

If you are not using the SCS Team plugin, load the YAML files directly as context for your Claude session:

1. Clone or download this repository
2. Add the contents of the `scds/` directory to your project
3. Reference them in your `CLAUDE.md` or load them as context at the start of your session

The YAML files are human-readable and can be included in any Claude context — no special tooling required.

### Option 3: Bundle Import (With SCS Control Plane)

For teams running the SCS Control Plane, compose your project bundle to import this standards bundle:

```yaml
# Your project bundle
id: bundle:acme-prior-auth-agent
type: project
imports:
  - bundle:acme-health-domain:1.0.0    # Company domain (all concerns)
  - bundle:chai-prior-auth:1.0.0       # CHAI standards (this bundle)
  - bundle:hipaa:1.0.0                 # HIPAA standards
scds:
  - scd:project:acme-formulary-rules
  - scd:project:acme-pa-scope
```

The agent subscribes to a tag (e.g., `prior-auth-agent:latest`) and receives the full resolved bundle graph — including CHAI governance requirements alongside company-specific policies.

---

**Note:** The SCS Team plugin also includes a general CHAI standards bundle (`/scs-team:use chai`) based on the CHAI Blueprint for Trustworthy AI (2023). This prior authorization bundle is different — it is based on the CHAI T&E Framework v1.0 (December 2025) and is specific to prior authorization criteria matching. Use this bundle if your use case involves AI-supported prior authorization.

## Why This Matters

CHAI's T&E Framework says:
- Track policy coverage completeness → **SCS bundles version the policies**
- Monitor performance after policy updates → **SCS bundles version policies so updates are structured and traceable**
- Ensure context version auditability → **SCS versioned bundles make it possible to know exactly what context an agent had at any point in time**

CHAI defines the rules. SCS delivers them.

## SCS Alignment: Where CHAI and SCS Meet

CHAI Requirement **TRANS-003 (Context Version Auditability)** states that it must be possible to determine exactly which governance context an AI agent was operating under at the time of any specific decision — enabling retrospective audit and investigation.

This maps directly to what SCS provides:

- **Immutable versioned bundles** — once published, a bundle version never changes
- **Structured provenance** — every bundle records who created it, when, and why
- **Version auditability** — it is always possible to determine exactly which bundle version an agent was using at any point in time

CHAI defines the auditability requirement. SCS is the mechanism that satisfies it.

## Status

**DRAFT** — This is an initial transposition for validation purposes. The content faithfully represents CHAI's published T&E Framework v1.0 requirements. It has not been reviewed or endorsed by CHAI.

## Known Scope Boundary

This bundle is based on the CHAI **T&E Framework v1.0**. A full review against the CHAI **Best Practice Guide (BPG)** for additional requirements not captured in the T&E Framework has not yet been completed. The BPG may contain requirements beyond what is represented here.

## Next Steps

1. Review against full CHAI BPG (Best Practice Guide) for completeness — known open item
2. Submit to CHAI PA work group as example of structured implementation
3. Validate bundle with `scs validate`
4. Build companion example showing agent behavior with/without this bundle
