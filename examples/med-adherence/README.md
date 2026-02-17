# SCS Bundle Examples - Medication Adherence System

This directory contains example bundle files for a **Medication Adherence System** project, demonstrating the complete SCS bundle hierarchy.

## Bundle Structure

```
examples/bundles/
├── project-bundle.yaml              # Top-level bundle (imports all others)
├── meta-bundle.yaml                 # Standard meta-tier vocabulary
├── standards-bundle.yaml            # Compliance standards (SOC2, HIPAA)
└── domains/                         # Domain-specific bundles
    ├── architecture.yaml
    ├── security.yaml
    ├── performance-reliability.yaml
    ├── usability-accessibility.yaml
    ├── compliance-governance.yaml
    ├── data-provenance.yaml
    ├── testing-validation.yaml
    ├── deployment-operations.yaml
    ├── safety-risk.yaml
    └── ethics-ai-accountability.yaml
```

## Bundle Hierarchy

The bundle structure follows the **container model** (similar to Docker):

1. **Project Bundle** (`project-bundle.yaml`)
   - Top-level bundle for the entire project
   - Imports: Meta Bundle, Standards Bundle, and all Domain Bundles
   - Lists no SCDs directly (all context is in imported bundles)

2. **Meta Bundle** (`meta-bundle.yaml`)
   - Provided by SCS specification
   - Contains: Standard vocabulary (roles, capabilities, domains, concerns)
   - Imported by every project

3. **Standards Bundle** (`standards-bundle.yaml`)
   - Project-specific compliance requirements
   - Imports: SOC2 bundle (external)
   - Contains: HIPAA SCDs (project interpretations)

4. **Domain Bundles** (`domains/*.yaml`)
   - 10 domain-specific bundles (one per major concern area)
   - Each contains 2-4 SCDs for that domain
   - Domain bundles DO NOT import other bundles - they contain only SCDs

## About the Example Project

**Medication Adherence System**
- Healthcare application helping patients track medication schedules
- Sends medication reminders via mobile app and SMS
- Provides adherence insights to healthcare providers
- Subject to HIPAA and SOC2 compliance

## Key Features Demonstrated

1. **Bundle Types**: Four bundle types (Project, Meta, Standards, Domain)
2. **Version Locking**: All bundles versioned at 1.0.0 (immutable contract)
3. **Hierarchical Imports**: Project imports Meta + Standards + Domains
4. **Bundle Independence**: Each domain bundle can version independently
5. **External Standards**: Standards bundle imports external SOC2 bundle
6. **Healthcare Context**: Realistic HIPAA and SOC2 compliance requirements

## Container Analogy

Think of SCS bundles like Docker containers:

| Docker | SCS |
|--------|-----|
| `Dockerfile` | Bundle manifest |
| Container image | Versioned bundle |
| Base image (`FROM`) | Bundle imports |
| Layers | SCDs |
| `docker-compose.yml` | Project bundle |
| Container registry | SCS registry (future) |

## Using These Examples

These bundles are **manifests only** - they reference SCDs but don't contain the actual SCD content files. To see complete SCD examples, check:

- `examples/scds/` - Individual SCD examples
- SCS Reference Implementation repository - Full templates

## Validation

To validate these bundles:

```bash
# Validate individual bundle (Phase 1 - syntax/schema only)
scs-validator bundles/domains/architecture.yaml

# Validate complete bundle hierarchy (Phase 2 - coming soon)
scs-validator bundles/project-bundle.yaml --recursive
```

## Related Documentation

- [Bundle Format Specification](../../spec/0.1/bundle-format.md)
- [Bundle Lifecycle](../../docs/bundle-lifecycle.md)
- [Project Structure](../../docs/project-structure.md)
- [Minimum Project SCDs](../../docs/minimum-project-scds.md)

---

**Questions?** Open an issue or discussion in the scs-spec repository.
