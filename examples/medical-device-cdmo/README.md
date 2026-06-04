# Medical-Device CDMO Domain (reference)

A reference SCS domain for **contract development & manufacturing organizations (CDMOs)** in the
medical-device industry: regulated QMS work, computer-system validation, multi-client program
segregation, and — the reason this domain exists — the **governance of AI assistants** operating
inside that environment.

It adapts the software-development reference domain to a regulated medical-device CDMO:

- **Kept** where they fit: `compliance-governance`, `data-provenance`, `security`, `business-context`.
- **Renamed** where the meaning shifts (the rename is deliberate, so the divergence is visible):
  - `architecture` → `system-architecture` (solution/integration/config, not source code)
  - `testing-validation` → `verification-validation` (CSV lifecycle: IQ/OQ/PQ, requirements traceability)
  - `safety-risk` → `risk-management` (ISO 14971 + project + data-integrity risk)
  - `deployment-operations` → `implementation-cutover` (migration, multi-site rollout, rollback)
  - `ethics-ai-accountability` → `ai-accountability`
- **Added** where the software set has no home:
  - `training-competency` (role-based qualification; ISO 13485 §6.2)
  - `qms-records` (document control, CAPA, retention, systems of record)
  - `supplier-qualification` (GAMP supplier assessment; AI-vendor qualification)
- **Dropped**: `performance-reliability`, `usability-accessibility` (device human factors has no AI agent in it).

**Inclusion rule:** a concern belongs in this domain only where an AI agent actually operates.

## Generic, not customer-specific

This directory contains the **generic** domain structure only — concern definitions and the SCD
*slots* a CDMO program would fill. It contains **no** organization-specific rules, values, or data.
A specific CDMO's actual context (its tier definitions, its retention periods, its program data) is
authored as project-tier SCDs in that organization's **own private workspace**, which imports this
domain by version. The structure is generic; the values are the organization's.

## Layout

```
medical-device-cdmo/
├── domains/medical-device-cdmo.yaml   ← domain bundle (imports the 12 concerns)
└── concerns/                          ← the 12 concern bundles (generic SCD slots)
```

Domain manifest: `schema/domain/examples/medical-device-cdmo-domain.yaml`.

## Provenance

Generalized from a real engagement (a CDMO AI-governance proof of concept). Contributed back as a
reusable domain because the gap it fills — the software-dev ontology not fitting regulated
medical-device work — is one every CDMO shares.
