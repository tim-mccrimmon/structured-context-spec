# CHAI Prior Authorization Standards Bundle

## What This Is

A transposition of the [CHAI (Coalition for Health AI) Prior Authorization Best Practice Guide and Testing & Evaluation Framework](https://www.chai.org/workgroup/use-case/ai-supported-prior-authorization-criteria-matching) into SCS standards bundle format.

CHAI defines **what** responsible AI looks like for prior authorization. This bundle encodes those requirements as structured, versioned, machine-readable governance context that can be delivered to AI agents via SCS/SCP.

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

## How This Gets Used

A payer building an AI prior auth agent would compose their project bundle like:

```yaml
# The payer's project bundle
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

## Why This Matters

CHAI's T&E Framework says:
- Track policy coverage completeness → **SCS bundles version the policies**
- Monitor performance after policy updates → **SCP tags push updates with zero downtime**
- Ensure context version auditability → **SCP's audit trail knows which context every agent had at every timestamp**

CHAI defines the rules. SCS delivers them.

## Status

**DRAFT** — This is an initial transposition for validation purposes. The content faithfully represents CHAI's published T&E Framework v1.0 requirements. It has not been reviewed or endorsed by CHAI.

## Next Steps

1. Review against full CHAI BPG (Best Practice Guide) for completeness
2. Submit to CHAI PA work group as example of structured implementation
3. Validate bundle with `scs validate`
4. Build companion example showing agent behavior with/without this bundle
