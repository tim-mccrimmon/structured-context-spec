---
name: use
description: Add known compliance or regulatory standards (HIPAA, SOC2, PCI, CHAI, GDPR) to your project context. Copies pre-built standards SCDs from the plugin's standards library.
argument-hint: "<standard: hipaa|soc2|pci|chai|gdpr>"
disable-model-invocation: true
allowed-tools: Read, Glob, Write, Bash(mkdir -p *)
---

# SCS Team Use - Add Known Standards

You are helping the user add well-known compliance or regulatory standards to their project context.

## Standards Library

This plugin ships with pre-built standards SCDs. Read them from the plugin's `standards/` directory rather than generating from scratch.

### Available Standards

| Standard | Directory | Files |
|----------|-----------|-------|
| HIPAA | `standards/hipaa/` | hipaa-phi-handling.yaml, hipaa-security-controls.yaml, hipaa-administrative.yaml |
| SOC 2 | `standards/soc2/` | soc2-security.yaml, soc2-availability.yaml, soc2-confidentiality.yaml |
| PCI DSS | `standards/pci/` | pci-data-protection.yaml, pci-access-control.yaml, pci-monitoring.yaml |
| CHAI | `standards/chai/` | chai-transparency.yaml, chai-accountability.yaml |
| GDPR | `standards/gdpr/` | gdpr-data-rights.yaml, gdpr-processing.yaml |

## Your Process

### Step 1: Identify the Standard

Parse the user's request to identify which standard(s) they want:
- `hipaa` - HIPAA compliance (healthcare, PHI)
- `soc2` - SOC2 Type II (security controls)
- `pci` - PCI-DSS (payment card data)
- `chai` - Coalition for Health AI (AI in healthcare)
- `gdpr` - General Data Protection Regulation (EU privacy)

### Step 2: Read Standards from Plugin Library

Read the pre-built standards SCDs from this plugin's `standards/` directory. The path is relative to this plugin's location.

**To find the plugin directory**: Use Glob to find `**/plugins/scs-team/standards/<standard>/` and read the YAML files from there.

### Step 3: Copy Standards to Project

Copy the standard SCD files to `.scs/scds/` in the project:
- Create `.scs/scds/` if it doesn't exist
- Write each standard SCD file to the project's `.scs/scds/` directory
- Preserve the original content but update `provenance.created_at` to current timestamp

### Step 4: Update Concern Bundle

Update the compliance concern bundle (`.scs/concerns/compliance.yaml`) to reference the new SCDs:
- Add each standard SCD to the `scds:` array
- If the compliance concern bundle doesn't exist, create it

### Step 5: Compile to Claude Code Format

After adding standards SCDs, compile the `.scs/` source to `.claude/rules/` output:

1. Read all SCDs in `.scs/scds/` and all concern bundles in `.scs/concerns/`
2. For each concern that has SCDs:
   a. Compress the SCD content to actionable rules (constraints, boundaries, patterns - NOT documentation)
   b. Target 300-500 tokens per concern file
   c. Write to `.claude/rules/<concern-name>.md`
   d. Add header: `<!-- scs-team:managed -->` and footer with source SCD attribution
3. Generate/update the scs-team section in CLAUDE.md:
   a. If CLAUDE.md exists, find `<!-- scs-team:start -->` / `<!-- scs-team:end -->` markers
   b. If markers exist, replace content between them
   c. If no markers, append the section at the end
   d. If no CLAUDE.md, create one with the markers
   e. Content: project overview, architecture summary, quick reference table, links to rules files
4. For SCDs with `applies_to.paths` that reference sensitive data (PHI, PCI):
   a. Add YAML frontmatter with `paths:` to the compiled `.claude/rules/` file
5. **Only overwrite files with `<!-- scs-team:managed -->` header** - leave other `.claude/rules/` files untouched

### Step 6: Report What Was Added

Tell the user:
1. What standard was added
2. What SCDs were copied from the library
3. Key requirements they need to be aware of
4. What they need to verify or customize
5. What `.claude/rules/` files were compiled

## Example Interaction

User: `/scs-team:use hipaa`

You: "Adding HIPAA compliance context from the standards library..."

[Read standards/hipaa/*.yaml, copy to .scs/scds/, update concern bundle]

You: "**Added HIPAA Standards** (3 SCDs from standards library):

1. `hipaa-phi-handling.yaml`
   - PHI identification (18 HIPAA identifiers)
   - Minimum necessary principle
   - Permitted uses and disclosures

2. `hipaa-security-controls.yaml`
   - Access control (unique IDs, session timeout)
   - Audit logging requirements
   - Encryption (AES-256 at rest, TLS 1.2+ in transit)

3. `hipaa-administrative.yaml`
   - BAA requirements
   - Workforce training
   - Incident response and breach notification

**Updated:**
- `concerns/compliance.yaml` - Added 3 HIPAA SCDs
- `.claude/rules/compliance.md` - Compiled compliance rules

**You Need To Customize:**
- Identify which data elements in YOUR system are PHI
- Specify your audit log retention period (minimum 6 years)
- List your Business Associates

**Key Constraints Claude Will Now Follow:**
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
1. Acknowledge you don't have pre-built templates for that standard
2. Offer to use `/scs-team:draft compliance` to create custom compliance context
3. Or ask them to provide compliance documentation via `/scs-team:add`
