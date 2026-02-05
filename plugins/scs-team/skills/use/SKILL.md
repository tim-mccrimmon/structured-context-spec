---
name: use
description: Add known compliance or regulatory standards (HIPAA, SOC2, PCI, CHAI) to your project context. Generates relevant SCDs with standard requirements.
argument-hint: "<standard: hipaa|soc2|pci|chai|gdpr>"
disable-model-invocation: true
allowed-tools: Read, Glob, Write, Bash(mkdir -p *)
---

# SCS Team Use - Add Known Standards

You are helping the user add well-known compliance or regulatory standards to their project context.

## Supported Standards

### HIPAA (Healthcare)
**Use when**: Project handles Protected Health Information (PHI)

Key areas to generate:
- PHI identification and handling
- Minimum necessary principle
- Access controls and audit logging
- Encryption requirements (at rest and in transit)
- Business Associate Agreement requirements
- Breach notification procedures

### SOC2 (Security)
**Use when**: Project needs to demonstrate security controls

Key areas to generate:
- Trust Service Criteria mapping
- Security controls (access, encryption, monitoring)
- Availability requirements
- Processing integrity
- Confidentiality controls
- Privacy considerations

### PCI-DSS (Payments)
**Use when**: Project handles payment card data

Key areas to generate:
- Cardholder data identification
- Network segmentation requirements
- Encryption requirements
- Access control requirements
- Logging and monitoring
- Vulnerability management

### CHAI (AI in Healthcare)
**Use when**: Project uses AI/ML in healthcare context

Key areas to generate:
- Model transparency requirements
- Bias detection and mitigation
- Human oversight requirements
- Clinical validation
- Explainability requirements

### GDPR (Data Privacy)
**Use when**: Project handles EU personal data

Key areas to generate:
- Lawful basis for processing
- Data subject rights
- Data minimization
- Consent requirements
- Data protection impact assessment triggers

## Your Process

### Step 1: Identify the Standard

Parse the user's request to identify which standard(s) they want:
- `hipaa` - HIPAA compliance
- `soc2` - SOC2 Type II
- `pci` - PCI-DSS
- `chai` - Coalition for Health AI
- `gdpr` - General Data Protection Regulation

### Step 2: Generate Standard-Specific SCDs

Create SCDs that capture the key requirements of the standard.

**SCD Structure for Standards**:
```yaml
id: scd:standards:<standard>-<area>
version: "DRAFT"
title: "<Standard> - <Area>"
description: "<What this covers>"
tier: standards

content:
  standard: "<HIPAA|SOC2|PCI-DSS|CHAI|GDPR>"
  version: "<Standard version if applicable>"

  requirements:
    - id: "<REQ-001>"
      description: "<Requirement description>"
      implementation_guidance: "<How to satisfy this>"

  controls:
    - id: "<CTRL-001>"
      description: "<Control description>"
      evidence_required: "<What demonstrates compliance>"

provenance:
  created_by: "SCS Team Plugin"
  created_at: "<ISO timestamp>"
  source: "<Standard name and version>"
  rationale: "Standard requirements for <standard>"
```

### Step 3: Create Concern Bundle

If a compliance concern bundle doesn't exist, create one:

```yaml
id: bundle:compliance
type: concern
version: "DRAFT"
title: "Compliance & Governance"
description: "Regulatory and compliance requirements"

scds:
  - scd:standards:<generated-scd-1>
  - scd:standards:<generated-scd-2>

imports: []

provenance:
  created_by: "<User>"
  created_at: "<ISO timestamp>"
  rationale: "Compliance requirements for project"
```

### Step 4: Report What Was Added

Tell the user:
1. What standard was added
2. What SCDs were generated
3. Key requirements they need to be aware of
4. What they need to verify or customize

## Example Interaction

User: `/scs-team:use hipaa`

You: "Adding HIPAA compliance context to your project...

**Generated SCDs:**

1. `hipaa-phi-handling.yaml`
   - PHI identification (what counts as PHI)
   - Minimum necessary principle
   - Permitted uses and disclosures

2. `hipaa-security-controls.yaml`
   - Access control requirements
   - Audit logging requirements
   - Encryption requirements (AES-256 at rest, TLS 1.2+ in transit)

3. `hipaa-administrative.yaml`
   - BAA requirements
   - Training requirements
   - Incident response procedures

**You Need To Customize:**
- Identify which data elements in YOUR system are PHI
- Specify your audit log retention period (minimum 6 years)
- List your Business Associates

**Key Constraints Claude Will Now Know:**
- Never log PHI to application logs
- All PHI access must be audit logged
- PHI must be encrypted at rest and in transit
- Minimum necessary: only access PHI needed for the task

Run `/scs-team:status` to see how this fits with your other context."

## Multiple Standards

Users can add multiple standards:

```
/scs-team:use hipaa
/scs-team:use soc2
```

When multiple standards apply, note overlapping requirements and how they reinforce each other.

## Unknown Standards

If the user requests a standard you don't have templates for:
1. Acknowledge you don't have pre-built templates
2. Offer to use `/scs-team:draft compliance` to create custom compliance context
3. Or ask them to provide compliance documentation via `/scs-team:add`
