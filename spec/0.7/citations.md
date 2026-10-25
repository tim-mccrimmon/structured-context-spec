# SCS 0.7.0 — Standard Citations

**Version:** 0.7.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-10-25

---

## 1. Purpose

This document defines how SCS refers to external standards (ISO 13485, IEC 62304, HIPAA,
SOC 2, and so on). In 0.6.0 a standard appears in SCS only as a **citation reference**: an
identifier for a standard, an edition, and optionally a clause. A citation carries no text
from the standard.

Citations replace Standards bundles and the Standards tier, which are deprecated in 0.6.0
(see `standards-tier.md`).

---

## 2. Why Citations, Not Standards Content

Three observations drove the change:

1. **The text of most standards is licensed.** The adopter holds the licence; a spec, a
   template library, or a vendor generally does not. SCS artifacts that reproduced or
   paraphrased clauses at length would be hard to distribute and hard to keep accurate.
2. **Standards bodies do not author SCS content.** Any "Standards bundle" was therefore an
   interpretation by someone else, with unclear ownership. In practice the adopter's own
   quality system (for example, its SOPs) is the authoritative interpretation.
3. **Governance context is rules an agent is expected to follow.** "Design changes require
   documented review before implementation" is a rule an agent can act on. ISO 13485
   §7.3.9 is the reason that rule exists. SCS keeps the rule as context and the standard as
   a reference.

Where an adopter wants AI systems to consult the full text of a standard it has licensed,
that text belongs in retrieval (reference material), not in a governance bundle. Whether a
given licence permits that use is a question for the adopter.

---

## 3. Citation Reference Format

```
std:<standard>[:<edition>][#<clause>]
```

| Part | Required | Pattern | Notes |
|---|---|---|---|
| `std:` | yes | literal | Prefix, alongside `scd:`, `bundle:`, `concept:` |
| `<standard>` | yes | `[a-z0-9][a-z0-9.-]*` | Lower-case slug of the standard's designation |
| `<edition>` | no | `[A-Za-z0-9.-]+` | Year or revision; SHOULD be present for any standard with editions |
| `<clause>` | no | `[A-Za-z0-9.()_-]+` | Clause, section, control, or requirement id as the standard numbers it |

Full pattern:

```
^std:[a-z0-9][a-z0-9.-]*(:[A-Za-z0-9.-]+)?(#[A-Za-z0-9.()_-]+)?$
```

Examples:

| Citation | Refers to |
|---|---|
| `std:iso-13485:2016` | ISO 13485:2016 as a whole |
| `std:iso-13485:2016#7.3.9` | ISO 13485:2016, clause 7.3.9 |
| `std:iec-62304:2006-a1#5.1` | IEC 62304:2006+A1:2015, clause 5.1 |
| `std:iso-14971:2019#5` | ISO 14971:2019, clause 5 |
| `std:21-cfr-820#820.30` | 21 CFR Part 820, §820.30 |
| `std:hipaa#164.312(d)` | HIPAA Security Rule, 45 CFR 164.312(d) |
| `std:soc2:2017#CC6.6` | SOC 2 (2017 Trust Services Criteria), CC6.6 |
| `std:nist-800-53:r5#SI-4` | NIST SP 800-53 Rev. 5, control SI-4 |

A citation is an identifier, not a resolvable document. Validators check that it is
well-formed; they do not resolve it against any registry. Citing a clause asserts that the
citing rule or concept is meant to address it; it does not assert that it is sufficient.

---

## 4. Where Citations Appear

### 4.1 On an SCD: `cites`

Any SCD MAY carry a top-level `cites` list naming the standards its content addresses.

```yaml
id: scd:project:design-change-control
type: project
title: Design Change Control
version: "1.0.0"
description: Rules for reviewing and approving design changes.
concept: concept:design-controls
cites:
  - std:iso-13485:2016#7.3.9
  - std:21-cfr-820#820.30
content:
  summary: Design changes require a documented review and approval before implementation.
provenance:
  created_by: quality@example-cdmo.com
  created_at: "2026-10-19T00:00:00Z"
```

### 4.2 As a `satisfies` target on an SCD relationship

An SCD relationship of type `satisfies` MAY target a citation:

```yaml
relationships:
  - type: satisfies
    target: std:hipaa#164.312(d)
```

`cites` and `satisfies` relationships carry the same information. `cites` is the compact
form; a relationship can add a `description`.

### 4.3 As a `satisfies` target in a Domain Ontology

A domain manifest concept's `satisfies` list (and `relationships` entries of type
`satisfies`) target citations (`domain-ontology.md` §3):

```yaml
- id: concept:risk-management
  name: Risk Management
  satisfies:
    - std:iso-14971:2019
    - std:iso-13485:2016#7.1
```

---

## 5. Citations in Runtime Context

Citations are traceability metadata. Tools that compile bundles into runtime context MAY
include them in compact form so an agent can name the clause a rule addresses, or MAY omit
them. They MUST NOT be expanded into standard text.

---

## 6. Migration From Standards-Tier SCDs

`scd:standards:` identifiers remain valid in 0.6.0 and produce a deprecation warning.

1. For each standards-tier SCD, find the rules that implement it and add the corresponding
   citation to those SCDs (`cites`), or to the concept that addresses it (`satisfies`).
2. If the standards-tier SCD contains genuine organization rules (not paraphrased standard
   text), move them into a project-tier SCD in a concept bundle of the Domain bundle.
3. Replace `satisfies: scd:standards:...` targets with `std:` citations.
4. Remove the Standards bundle from imports.

---

## 7. Validation

A conformant validator:

1. Checks every citation against the pattern in §3 (error when malformed).
2. Does not attempt to resolve citations.
3. Warns on `scd:standards:` references and `type: standards` bundles (deprecated).

---

## 8. Feedback

Feedback on standard citations should be submitted via GitHub Issues.
