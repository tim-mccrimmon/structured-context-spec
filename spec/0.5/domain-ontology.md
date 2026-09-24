# SCS 0.5.0 — Domain Ontology
**Version:** 0.5.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-09-22
**Design rationale:** `rfcs/RFC-0001-domain-ontology.md` (accepted 2026-09-21)

---

## 1. Purpose

This document is the **normative specification** for the Domain Ontology: the structure a
domain uses to organize its concepts, and the rules that govern it. It replaces the flat
`concerns` list from SCS 0.3.

RFC-0001 records the design discussion, alternatives considered, and rationale. This
document states the rules definitively, for implementers and tools.

---

## 2. Why This Exists

SCS 0.3's `concerns` list did two things at once, without being structured for either:

- it was the domain's table of contents (which concept bundles exist)
- it was, implicitly, the domain's conceptual model (what matters, and how those things
  relate)

The second job was never given real structure — no relationships between concepts, no
taxonomy, no mapping from a concept to the regulatory clause it exists to satisfy. In a
regulated domain, that mapping is the whole point: "does our context cover IEC 62304 §5.1?"
needs to be a machine-answerable question, not something answered by reading prose.

**Field evidence.** The original "concerns" list was never domain-neutral — it was one
ontology (Software Development / SDLC) wearing a generic name; its shape maps directly onto
a conventional product plan's chapters. Two engagements broke that assumption in different
ways: a **Medical-Device CDMO** (Nextern) needed risk management, design controls, and
supplier qualification — concepts the SDLC list has no home for — and lost the regulatory
mapping that mattered most in that market when forced into the SDLC shape. A **Business
Funding** engagement (Everest) is a third, distinct market with no obvious existing
framework to align to; it is now modeled as the **MCA** ontology (§4). A single fixed ontology
cannot serve every business type SCS is used in.

---

## 3. The Domain Ontology

A **Domain Ontology** is a domain's model of the concepts that structure its work. It lives
in the **domain manifest**, in an `ontology` block, and has three parts:

1. **Concepts** — named categories of domain knowledge. `concept:risk-management`,
   `concept:design-controls`, `concept:verification-validation`. Replaces "concerns".
2. **Taxonomy** — an optional parent/child hierarchy. `concept:iso-14971-risk-analysis` MAY
   have `parent: concept:risk-management`.
3. **Relationships** — an optional, small, fixed set of typed edges between concepts:
   `depends-on`, `relates-to`, `satisfies`.

Each concept MAY also carry a `satisfies` mapping to standards-tier SCDs — the regulatory
requirements it exists to address. In a regulated domain, this is what makes framework
coverage machine-answerable.

**Depth is optional.** The smallest valid Domain Ontology is a flat list of concept names —
exactly what "concerns" was, minus the name. A domain adds taxonomy and relationships
incrementally as it matures. This is not OWL, not RDF, not description logic, and there is
no reasoner — it is a typed graph you can read.

### 3.1 Domain Manifest Schema

```yaml
domain:
  id: domain:medical-device-cdmo
  name: Medical Device CDMO
  version: 0.1.0
  description: >
    Context domain for contract design & manufacturing of medical devices under
    ISO 13485, IEC 62304, and FDA 21 CFR 820.

  ontology:
    concepts:
      - id: concept:risk-management
        name: Risk Management
        description: Hazard analysis, risk controls, and residual-risk evaluation.
        relationships:
          - type: relates-to
            target: concept:verification-validation
        satisfies:
          - scd:standards:iso-14971
          - scd:standards:iso-13485-clause-7.1
        bundle: bundle:risk-management:0.1.0

      - id: concept:iso-14971-risk-analysis
        name: ISO 14971 Risk Analysis
        parent: concept:risk-management
        satisfies:
          - scd:standards:iso-14971-clause-5

      - id: concept:verification-validation
        name: Verification & Validation
        description: Computer-system validation (GAMP category; IQ/OQ/PQ).
        relationships:
          - type: depends-on
            target: concept:risk-management

    relationship_types: [depends-on, relates-to, satisfies]

  schemas:
    meta:
      content_schema: "../../scd/meta-scd-content-schema.json"
    standards:
      content_schema: "../../scd/standards-scd-content-schema.json"
    project:
      content_schema: "../../scd/project-scd-content-schema.json"
```

(`concept:risk-management` has no `parent` — the field is simply omitted, not set to
`null`; the schema types it as a string, and an absent field means "no parent," not an
explicit null.)

| Field | Req | Notes |
|---|---|---|
| `concepts[]` | yes | ≥ 1 |
| `concepts[].id` | yes | `^concept:[a-z][a-z0-9-]*$` |
| `concepts[].name` | yes | human-readable |
| `concepts[].description` | recommended | |
| `concepts[].parent` | no | a `concept:` id in the same domain; forms the taxonomy; MUST be acyclic |
| `concepts[].relationships[]` | no | `{ type, target }`; `type ∈ {depends-on, relates-to, satisfies}`; `target` a `concept:` id (for `depends-on` / `relates-to`) or `scd:standards:` id (for `satisfies`) |
| `concepts[].satisfies[]` | no | shorthand list of `scd:standards:` ids (sugar for `relationships` of type `satisfies`) |
| `concepts[].bundle` | no | the concept bundle realizing this concept |
| `relationship_types[]` | no | domain may restrict the allowed set |

`concerns` is not a valid domain manifest field in 0.5.0 — see §9, Migration.

### 3.2 Relationship Semantics

| Type | Between | Meaning |
|---|---|---|
| `depends-on` | concept → concept | the source concept's context assumes the target's is established |
| `relates-to` | concept → concept | a weak, non-directional association; navigational only |
| `satisfies` | concept → `scd:standards:` | this concept exists to address that requirement |

This is a deliberately small set, distinct from — and smaller than — the SCD-to-SCD
relationship set in `core-model.md` §6.1 (`depends-on`, `constrains`, `satisfies`,
`refines`, `extends`, `conflicts-with`, `implements`). `constrains`, `refines`, `extends`,
`conflicts-with`, and `implements` are not part of the concept-level ontology; they remain
available for SCD-to-SCD relationships.

### 3.3 The `concept` Field on SCDs

An SCD MAY declare which concept it realizes:

```yaml
id: scd:project:hazard-analysis-procedure
type: project
title: Hazard Analysis Procedure
version: "0.5.0"
concept: concept:risk-management
content:
  ...
```

Optional at the schema level (`project-tier.md` §4.2), but expected for an SCD that lives
in a concept bundle.

---

## 4. Ontology Models

A Domain Ontology is authored once per **type of business** (a market/industry vertical),
not once per company. So far there are three:

- **SDLC** — the original "concerns" list (architecture, security, testing, …), for
  software development businesses.
- **CDMO** — risk management, design controls, verification & validation, supplier
  qualification, …, for regulated medical-device contract manufacturers.
- **MCA** — merchant cash advance / business funding: origination, underwriting and decisioning,
  contract characterization, disclosure compliance, servicing and collections, and more that
  neither the SDLC nor the CDMO shape has a home for. 16 concepts in three clusters
  (industry-native, infrastructure, and the AI-governance layer). Best-practice AI governance,
  not a compliance mapping, so it carries relationships but no `satisfies`. Reference manifest:
  `schema/domain/examples/merchant-cash-advance-domain.yaml`.

The first step in adopting SCS is choosing your business's ontology, not writing one from a
blank page: **use an existing model if one fits your market, or create a new one by
adapting the nearest existing model** rather than starting from nothing. A company's domain
manifest instantiates a model — it declares which concepts it uses and how they relate —
but the model itself (the reusable shape) is the thing worth naming, versioning, and
sharing across companies in the same market.

This is also the answer to a question SCS 0.3 got wrong: 0.3 said concerns were "reusable
across domains" (a shared Security concern). **Concepts are domain-scoped, not shared
across domains** (RFC-0001, parked indefinitely — no cross-domain import mechanism is
planned). Two CDMO companies each instantiate the CDMO Ontology Model rather than importing
one another's concepts. What is reusable is the model, not the concept bundle.

How an Ontology Model is packaged, versioned, and referenced independently of a specific
domain manifest is not yet specified — open, see §10.

---

## 5. Concept Bundles

`type: concept` replaces `type: concern` (`bundle-format.md` §3.4). Structural rules are
unchanged from 0.3's concern bundles:

- MUST NOT import other bundles (`imports: []`)
- MUST contain ≥ 1 SCD
- Domain bundles import concept bundles; the domain-bundle rules (MUST import ≥1 concept
  bundle, MUST contain no direct SCDs) carry over unchanged with the rename.

A concept's `bundle` field (§3.1) is what connects the ontology entry to the concept bundle
realizing it — matched by bundle name, ignoring the version suffix.

---

## 6. Bundle Validity Properties

Beyond the structural rules above, a concept bundle is expected to have four properties.
Only the first is validator-enforced as of 0.5.0; the rest are stated intent for future
validator work:

1. **Reflects the ontology** — every SCD's `concept` resolves to a real concept in the
   active domain. **Enforced** (§8, rule 6).
2. **Approved, not just authored** — see §7, Provenance and Approval. **Enforced** for
   non-`DRAFT` versions.
3. **Consistent version to version** *(not yet enforced)* — a concept cannot be renamed or
   removed, and a relationship's meaning cannot change, without a major version bump. No
   version-diff/compatibility check exists yet; this needs its own design (what "breaking"
   means for a concept bundle).
4. **Compact and non-conflicting** *(not yet enforced)* — no redundant or duplicate
   concepts, and no contradictory relationships beyond the acyclic checks in §8. SCS's
   default validation philosophy is permissive (structure, not content completeness);
   compactness/non-conflict checking would be new, opt-in-first the same way completeness
   checking is today.

Content **accuracy or coverage completeness is explicitly out of scope for the validator**
— SCS cannot verify that domain content is true or sufficient, only that someone with
standing has attested to it (§7).

---

## 7. Provenance and Approval

A bundle's `provenance` block records **authorship** unconditionally
(`created_by`/`created_at`, optionally `updated_by`/`updated_at`/`rationale`) — this is
unchanged from 0.3.

**New in 0.5.0:** once a bundle's `version` is a real semantic version (not `DRAFT`), its
provenance MUST also include:

| Field | Description |
|---|---|
| `version_approved_by` | Email or identifier of the person who approved this bundle version |
| `version_approved_at` | ISO-8601 timestamp of version approval |

```yaml
provenance:
  created_by: jane@nextern.com
  created_at: "2026-09-20T00:00:00Z"
  version_approved_by: sam@nextern.com
  version_approved_at: "2026-09-21T00:00:00Z"
  rationale: "Added ISO 14971 clause mapping for risk-management concept"
```

**A `DRAFT` bundle does not require these fields** — there is nothing yet to approve. This
is a deliberate schema conditional (not an oversight): unconditionally requiring approval
on every bundle, including fresh working copies, would make every newly-scaffolded project
fail validation immediately. Approval only becomes meaningful once you're cutting an actual
version.

`version_approved_by` names **one accountable person per bundle version** — a deliberate
single-source MVP, not the final shape. Regulated use will likely need a **per-perspective**
model instead — the owner of risk management attesting the risk-management concept,
compliance attesting the compliance concept, etc. Tracked as multi-author provenance
(SCS backlog `ISS-011`); revisit once real usage shows whether a single approver is
actually insufficient.

Approval is a **bundle-level event, not a per-SCD one**. An SCD's own `provenance` is
unchanged — authorship only, regardless of whether the bundle containing it is `DRAFT` or
versioned.

---

## 8. Validation Rules

A conformant validator applies these rules to a domain manifest's `ontology` block (and,
where noted, to SCDs and bundles from the same domain):

1. Every `concepts[].id` matches `^concept:[a-z][a-z0-9-]*$` and is unique within the
   domain.
2. `parent` references resolve to a concept in the same domain; the parent graph is
   acyclic.
3. `relationships[].type` (and each `satisfies[]` entry, treated as an implicit
   `relationships` entry of type `satisfies`) is in the allowed set — default
   `{depends-on, relates-to, satisfies}`, or the domain's `relationship_types`.
4. `relationships[].target`: a `concept:` id in the same domain for `depends-on` /
   `relates-to`, must resolve; an `scd:standards:` id for `satisfies` — well-formedness is
   checked, but resolving it against real SCDs needs project-level context a
   domain-manifest-only validation pass doesn't have, so an unresolved `satisfies` target is
   a warning, not an error, in that context.
5. `depends-on` among concepts is acyclic.
6. An SCD's `concept` (if present) resolves to a concept in the active domain.
7. A concept bundle's SCDs SHOULD all declare the same `concept` as the bundle's concept
   (warning, not error) — best-effort; needs both the bundle and its SCDs loaded.
8. `concerns` (on a domain manifest) or `type: concern` (on a bundle) is an error, with a
   migration hint pointing at §9.

---

## 9. Migration from 0.3

1. **Rename** `type: concern` → `type: concept` in every concern bundle; the directory
   `concerns/` → `concepts/` by convention.
2. **Domain manifest**: replace
   `concerns: [bundle:x:1.0.0, …]`
   with
   `ontology: { concepts: [ { id: concept:x, name: X, bundle: bundle:x:0.5.0 }, … ] }`.
   This alone is a valid (flat) Domain Ontology.
3. **Add depth incrementally**: set `parent` where a taxonomy exists; add `depends-on` /
   `relates-to`; add `satisfies` pointing at your standards-tier SCDs.
4. **SCDs**: add `concept: concept:<id>` to each SCD in a concept bundle (optional but
   recommended).
5. **Provenance**: add `version_approved_by` / `version_approved_at` to any bundle that
   isn't `DRAFT`.
6. Run `scs validate` against the 0.5.0 rules; fix reported `concern` residue.

No automated `scs migrate` helper is planned for 0.5.0 — this is a guide-only migration.
Revisit if a third party has real 0.3 content to migrate.

---

## 10. Open Questions

Carried over from RFC-0001, not yet resolved:

- **Ontology Model packaging** — how a model (§4) is packaged, versioned, and referenced
  independently of a specific domain manifest.
- **Approval model** — whether the single-source `version_approved_by` (§7) is sufficient
  long-term, or regulated domains need per-perspective/per-concept attestation.

---

## 11. Future Extensions

- **Ontology-aware context selection** — a runtime selects context by walking `depends-on`
  from the concepts a task touches, not just by tier.
- **Coverage reports** — `scs coverage --framework iso-13485` answered from the ontology's
  `satisfies` edges.
- **Richer concept relationships** (`constrains`, `conflicts-with`) promoted from SCD-level
  to concept-level, if demand appears.
- **Ontology Model library** — package SDLC / CDMO / future models as reusable, versioned
  artifacts a domain manifest instantiates.
- **Per-perspective attestation** — extend `version_approved_by` to a per-concept or
  per-perspective approval list, if single-source approval proves insufficient.
- **Ontology diff** — show what changed between two versions of a domain's ontology, as
  part of domain versioning.

---

## 12. Feedback

Feedback on the Domain Ontology should be submitted via GitHub Issues, referencing
RFC-0001.
