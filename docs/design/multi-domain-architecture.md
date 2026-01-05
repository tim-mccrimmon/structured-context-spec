# Multi-Domain Architecture Design

**Version:** 0.1 (Draft)
**Date:** 2025-12-12
**Status:** Design Proposal

---

## 1. Executive Summary

This document proposes architectural changes to evolve SCS from a single-domain (software development) system into a multi-domain platform that supports structured context across any industry or business function.

**Key Goals:**
- Enable domain-specific content schemas (healthcare, sales, legal, etc.)
- Maintain backwards compatibility with existing software-dev bundles
- Support both pre-built domains and user-defined custom domains
- Create foundation for commercial domain offerings

---

## 2. Current Architecture Analysis

### 2.1 What Exists Today

**SCS 0.1 has:**
- **Three-tier model**: meta, standards, project (these are abstraction LAYERS, not domains)
- **SCDs**: Atomic units with standardized structure (id, type, title, version, content, relationships, provenance)
- **Bundles**: Collections of SCDs with bundle types (project, meta, standards, domain)
- **Content schemas**: Hardcoded to software development concepts

### 2.2 What's Domain-Specific Today

The **`content`** field in SCDs is where domain specificity lives:

**Software Development Domain (current):**
```json
"content": {
  "architecture": {...},
  "components": [...],
  "requirements": [...],
  "data_flows": [...],
  "security": {...},
  "decisions": [...]
}
```

**Healthcare Domain (future example):**
```json
"content": {
  "clinical_workflows": [...],
  "patient_populations": [...],
  "care_pathways": [...],
  "compliance_frameworks": [...],
  "data_governance": {...}
}
```

### 2.3 What Stays the Same

**Domain-agnostic SCD structure:**
- `id`, `type`, `title`, `version`, `description`
- `relationships`
- `provenance`
- Three-tier model (meta/standards/project)

**What changes per domain:**
- Content schema definitions
- Templates
- Validation rules
- Domain-specific terminology

---

## 3. Multi-Domain Architecture

### 3.1 Core Concept: Domain as Content Schema Provider

A **domain** is a plugin that provides:

1. **Content schemas** for each tier (meta, standards, project)
2. **Templates** for SCDs and bundles
3. **Validation rules** specific to that domain
4. **Domain metadata** (name, description, version, author)

### 3.2 Domain Definition Structure

Each domain is defined by a domain manifest:

```yaml
# domain.yaml
domain:
  id: "domain:healthcare"
  name: "Healthcare"
  version: "1.0.0"
  description: "Structured context for healthcare systems"
  author: "SCS Commercial"

  schemas:
    meta:
      content_schema: "./schemas/meta-content.json"
      template: "./templates/meta-template.json"

    standards:
      content_schema: "./schemas/standards-content.json"
      template: "./templates/standards-template.json"

    project:
      content_schema: "./schemas/project-content.json"
      template: "./templates/project-template.json"

  validation:
    rules: "./validation/rules.json"

  examples:
    - "./examples/example-bundle.yaml"
```

### 3.3 Domain Registry

Domains are registered and discovered through a domain registry:

**Registry Structure:**
```json
{
  "domains": [
    {
      "id": "domain:software-development",
      "name": "Software Development",
      "version": "1.0.0",
      "location": "builtin",
      "license": "open"
    },
    {
      "id": "domain:healthcare",
      "name": "Healthcare",
      "version": "1.0.0",
      "location": "https://registry.scs.com/domains/healthcare",
      "license": "commercial"
    },
    {
      "id": "domain:sales",
      "name": "Sales & Marketing",
      "version": "1.0.0",
      "location": "https://registry.scs.com/domains/sales",
      "license": "commercial"
    }
  ]
}
```

### 3.4 Bundle Changes

Bundles must specify their domain:

```yaml
id: bundle:patient-care-system
type: project
version: "1.0.0"
domain: "domain:healthcare"  # NEW FIELD
title: "Patient Care System"
description: "Context bundle for patient care workflow system"
imports:
  - bundle:healthcare-meta:1.0.0
  - bundle:hipaa-compliance:1.0.0
scds:
  - scd:project:care-pathways
  - scd:project:patient-data-flows
provenance:
  created_by: "tim@example.com"
  created_at: "2025-12-12T10:00:00Z"
```

### 3.5 SCD Changes (Minimal)

SCDs themselves don't change much - the content schema is validated against the domain:

```json
{
  "id": "scd:project:care-pathways",
  "type": "project",
  "domain": "domain:healthcare",  // NEW FIELD (optional, inherited from bundle)
  "title": "Clinical Care Pathways",
  "version": "1.0.0",
  "description": "Care pathways for chronic disease management",
  "content": {
    // Healthcare-specific content validated against domain:healthcare project schema
    "clinical_workflows": [...],
    "patient_populations": [...]
  },
  "relationships": [...],
  "provenance": {...}
}
```

---

## 4. CLI Changes

### 4.1 Domain Management Commands

```bash
# List available domains
scs domain list

# Install a domain
scs domain install healthcare

# Set project domain
scs domain set healthcare

# View current domain
scs domain info
```

### 4.2 Domain-Aware Commands

```bash
# Create new bundle (uses current domain)
scs new bundle my-healthcare-system

# Add SCD (templates come from current domain)
scs add project-scd care-pathways

# Validate bundle against domain
scs validate --domain healthcare
```

### 4.3 Configuration

Project-level domain configuration:

```yaml
# .scs/config.yaml
project:
  domain: "domain:healthcare"
  domain_version: "1.0.0"
```

---

## 5. Implementation Plan

### Phase 1: Core Infrastructure
1. ✅ Analyze current architecture (DONE)
2. Design domain manifest format
3. Implement domain loader/validator
4. Create domain registry client
5. Update bundle schema to include domain field

### Phase 2: Domain Plugin System
6. Implement domain plugin interface
7. Extract software-dev domain as first plugin
8. Create domain template engine
9. Update SCD validator to be domain-aware

### Phase 3: CLI Updates
10. Add domain management commands
11. Update bundle/SCD creation to use domain templates
12. Add domain switching capability
13. Update validation commands

### Phase 4: Testing & Documentation
14. Create healthcare domain as proof-of-concept
15. Test multi-domain scenarios
16. Update documentation
17. Create migration guide for existing bundles

---

## 6. Backwards Compatibility

### 6.1 Default Domain

Bundles without a `domain` field default to `domain:software-development`

### 6.2 Migration Path

Existing bundles continue to work:
- Software-dev becomes a standard domain plugin
- Existing bundles can be migrated by adding `domain: "domain:software-development"`
- Or left as-is and default is applied

---

## 7. Commercial Model Integration

### 7.1 Domain Licensing

Domains can be:
- **Open** (free, bundled with SCS)
- **Commercial** (paid subscription required)

### 7.2 Domain Distribution

- Free domains: Bundled with SCS installation
- Commercial domains: Downloaded from registry after license verification
- Custom domains: User-created, local only or published

### 7.3 License Verification

```bash
# Activate commercial domain
scs domain activate healthcare --license-key XXXXX

# Check license status
scs domain licenses
```

---

## 8. Open Questions

1. **Domain versioning**: How do we handle breaking changes in domain schemas?
2. **Domain dependencies**: Can domains depend on other domains?
3. **Custom domains**: What's the authoring experience for users creating custom domains?
4. **Registry hosting**: Self-hosted vs. cloud registry?
5. **Offline support**: Can users work with domains offline?

---

## 9. Next Steps

1. Review this design with stakeholders
2. Create detailed specification for domain manifest format
3. Prototype domain loader
4. Design registry API
5. Begin Phase 1 implementation

---

## 10. Success Criteria

**Architecture is successful if:**
- ✅ Software-dev domain can be extracted as a plugin
- ✅ Healthcare domain can be implemented without modifying core SCS
- ✅ Users can switch between domains seamlessly
- ✅ Commercial domains can be licensed and activated
- ✅ Custom domains can be created by advanced users
- ✅ Existing bundles continue to work without modification

---

*This is a living document and will be updated as implementation progresses.*
