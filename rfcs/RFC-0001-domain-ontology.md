# RFC 0001: Domain Ontology (replaces "Concern")

- **Start Date**: 2026-08-28
- **RFC PR**: (leave blank, will be filled by maintainer)
- **Tracking Issue**: (leave blank, will be filled when RFC is accepted)
- **Author(s)**: Tim McCrimmon (@tim-mccrimmon)
- **Status**: Draft
- **Target**: SCS 2.0 (breaking change)

---

## Summary

SCS 0.3 defines **concerns** as a per-domain list of functional areas (Architecture,
Security, Testing … for Software Development; Risk Management, QMS Records, Supplier
Qualification … for the medical-device CDMO domain), each packaged as a **concern bundle**.
In practice this list is not just an organizing convenience — it *is* the domain's model of
what matters. This RFC promotes it to a first-class, explicit artifact: the **Domain
Ontology**, a domain-defined set of **concepts** with a shallow taxonomy and a small set of
typed relationships, plus a mapping from each concept to the standards it satisfies. The
`Concern` bundle type and the term "concern" are retired. The bundle hierarchy becomes
`Project → Domain → Concept → SCD`.

---

## Motivation

**The concern list is doing ontology work without being named or structured as one.**
When the medical-device CDMO domain replaced the Software-Development concern list with its
own, that was not a cosmetic change — it swapped the domain's conceptual vocabulary, and
everything downstream (which SCDs exist, how they group, how a consumer reasons about
coverage) changed with it. SCS today treats that list as `concerns: [bundle:architecture:1.0.0, …]`
— an unordered array of bundle references in the domain manifest, with:

- **no relationships between concepts** — nothing expresses that "Verification & Validation"
  depends on "Design Controls", or that "CAPA" relates to "Complaint Handling";
- **no hierarchy** — the list is flat, so there is no "Risk Management" with sub-concepts;
- **no framework mapping** — nothing connects a concept to the ISO 13485 / IEC 62304 /
  21 CFR 820 clauses it exists to satisfy, even though that mapping is the whole point in a
  regulated domain;
- **a name collision** — "concern" is an established term from aspect-oriented / separation-
  of-concerns design, where it means a cross-cutting *implementation* aspect. SCS concepts
  are domain knowledge categories, a different thing. The overload causes confusion.

**Why this matters now — structured context is for any AI actor, not just chat.** SCS 2.0
reframes structured context as the governed context layer for any AI actor: chat
assistants, autonomous agents, MCP tool invocations, and multi-agent workflows. Consumers
in that world do more than prepend text to a prompt — a control plane traverses a graph to
select the right context for an agent + intent; a tool-call gate checks a policy expressed
as context; a workflow engine pins a context version at a checkpoint. All of that is much
stronger when the domain's concepts, their relationships, and their framework mappings are
**explicit and machine-readable** rather than implied by a flat list of bundle names.

Expected outcome: a domain can state its ontology once, in the domain manifest; SCDs attach
to concepts; consumers reason over concepts and their relationships; and, in regulated
domains, coverage against a framework is answerable from the ontology.

> **[Tim to augment]** Prior art / supporting evidence on ontology-grounded context
> (knowledge-graph-grounded retrieval, semantic layers, ontology-driven RAG, enterprise
> context modeling). Drop references and the argument here.

---

## Guide-level Explanation

### The Domain Ontology

A **Domain Ontology** is a domain's model of the concepts that structure its work. It
lives in the **domain manifest** and has three parts:

1. **Concepts** — named categories of domain knowledge. `concept:risk-management`,
   `concept:design-controls`, `concept:verification-validation`. Replaces "concerns".
2. **Taxonomy** — an optional parent/child hierarchy. `concept:iso-14971-risk-analysis`
   MAY have `parent: concept:risk-management`.
3. **Relationships** — an optional, small, fixed set of typed edges between concepts:
   `depends-on`, `relates-to`, `satisfies`. (`depends-on` and `satisfies` already exist in
   the SCS relationship vocabulary; `relates-to` is new and deliberately weak.)

Each concept also carries a **`satisfies` mapping to standards-tier SCDs** — the regulatory
requirements it exists to address. In a regulated domain this is what makes "does our
context cover IEC 62304 §5.1?" answerable.

**Depth is optional.** The smallest valid Domain Ontology is a flat list of concept names —
exactly what "concerns" is today, minus the name. A domain adds taxonomy and relationships
incrementally as it matures. SCS does not require a fully modeled graph.

**It is deliberately lightweight.** The Domain Ontology is expressed in the same
YAML/schema style as the rest of SCS. It is not OWL, not RDF, not description logic, and
there is no reasoner. It is a typed graph you can read.

### How you use it

You author a domain manifest with an `ontology` block. You create SCDs and attach each to a
concept via `concept: concept:<id>` (replacing the current implicit "this SCD is in the
architecture concern bundle" grouping). A concern *bundle* becomes a **concept bundle** —
same idea, renamed — collecting the SCDs for one concept.

A consumer (a runtime, a validator, an agent) reads the ontology to know: what concepts
this domain has, how they relate, which SCDs realize each, and which frameworks each
satisfies.

### How to think about it

The Domain Ontology is the **table of contents and the wiring diagram** for a domain's
context. "Concerns" gave you the table of contents (a flat list). The Domain Ontology adds
the wiring — hierarchy, dependencies, and the line back to the regulations — and gives the
whole thing a name that says what it is.

---

## Reference-level Explanation

### Terminology changes

| 0.3 | 2.0 |
|---|---|
| Concern | **Concept** |
| Concern bundle (`type: concern`) | **Concept bundle** (`type: concept`) |
| Domain manifest `concerns: [bundle:…]` | Domain manifest `ontology: { concepts: [ … ] }` |
| Hierarchy: Project → Domains → Concerns → SCDs | Project → Domain → **Concept** → SCD |

### Domain manifest schema changes

Replace the flat `concerns` array with an `ontology` object. Sketch:

```yaml
domain:
  id: domain:medical-device-cdmo
  name: Medical Device CDMO
  version: 2.0.0
  description: >
    Context domain for contract design & manufacturing of medical devices under
    ISO 13485, IEC 62304, and FDA 21 CFR 820.

  ontology:
    concepts:
      - id: concept:risk-management
        name: Risk Management
        description: Hazard analysis, risk controls, and residual-risk evaluation.
        # taxonomy (optional)
        parent: null
        # typed relationships (optional; type ∈ depends-on | relates-to | satisfies)
        relationships:
          - type: relates-to
            target: concept:verification-validation
        # framework mapping (optional but expected in regulated domains):
        # standards-tier SCDs this concept exists to satisfy
        satisfies:
          - scd:standards:iso-14971
          - scd:standards:iso-13485-clause-7.1
        # the concept bundle realizing this concept (optional until SCDs exist)
        bundle: bundle:risk-management:2.0.0

      - id: concept:iso-14971-risk-analysis
        name: ISO 14971 Risk Analysis
        parent: concept:risk-management
        satisfies:
          - scd:standards:iso-14971-clause-5

      - id: concept:design-controls
        name: Design Controls
        relationships:
          - type: depends-on
            target: concept:risk-management
        satisfies:
          - scd:standards:cfr-820-30

    # optional: constrain which relationship types this domain uses
    relationship_types: [depends-on, relates-to, satisfies]
```

New `domain.ontology` object:

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

`concerns` is removed. `domain.schemas` (meta/standards/project content schemas) is
unchanged.

### SCD changes

An SCD in a concept bundle SHOULD declare its concept:

```yaml
id: scd:project:hazard-analysis-procedure
type: project
title: Hazard Analysis Procedure
version: "2.0"
concept: concept:risk-management        # NEW — replaces implicit concern-bundle grouping
content:
  ...
```

The existing `relationships` block on SCDs is unchanged. The new `concept` field is
optional at the schema level but expected for SCDs that live in a concept bundle.

### Bundle changes

- `type: concern` → `type: concept`.
- A concept bundle MUST NOT import other bundles (`imports: []`) and MUST contain ≥ 1 SCD —
  same structural rules concern bundles have today.
- Domain bundles import concept bundles instead of concern bundles; the "MUST import ≥ 1
  concern bundle, MUST contain no direct SCDs" rule carries over unchanged with the rename.

### Relationship semantics

Reuse the existing vocabulary where it fits, keep the concept-level set small:

| Type | Between | Meaning |
|---|---|---|
| `depends-on` | concept → concept | the source concept's context assumes the target's is established |
| `relates-to` | concept → concept | a weak, non-directional association; navigational only |
| `satisfies` | concept → `scd:standards:` | this concept exists to address that requirement |

`constrains`, `refines`, `extends`, `conflicts-with`, `implements` remain available for
SCD-to-SCD relationships; they are **not** part of the concept-level ontology set in 2.0
(may be added later — see Future Possibilities).

### Validation rules

1. Every `concepts[].id` matches `^concept:[a-z][a-z0-9-]*$` and is unique within the
   domain.
2. `parent` references resolve to a concept in the same domain; the parent graph is
   acyclic.
3. `relationships[].type` is in the allowed set (default `{depends-on, relates-to,
   satisfies}` or the domain's `relationship_types`).
4. `relationships[].target`: `concept:` id in the same domain for `depends-on` /
   `relates-to`; `scd:standards:` id for `satisfies`. Targets must resolve.
5. `depends-on` among concepts is acyclic.
6. An SCD's `concept` (if present) resolves to a concept in the active domain.
7. A concept bundle's SCDs SHOULD all declare the same `concept` as the bundle's concept
   (warning, not error).
8. `concerns` / `type: concern` in a 2.0 bundle is an error (with a migration hint).

---

## Drawbacks

- **It is a breaking change.** "Concern" appears in the spec, both validator rule sets
  (`rules/v0.1.0`, `rules/v0.3.0`), the schemas, ~a dozen example domains and bundles, the
  `scs-tools` templates (`templates/bundles/concerns/…`), and both Claude Code plugins.
  Everything that consumes SCS 0.3 breaks on the rename alone.
- **Migration cost** for anyone with existing bundles (see Migration Guide).
- **Risk of scope creep.** "Ontology" invites OWL, reasoners, inference. This RFC
  deliberately bounds it to a typed graph in YAML; that boundary has to be held in review
  and in future RFCs.
- **Two ways to say "satisfies a framework"** (`satisfies[]` sugar vs a `relationships`
  entry). Convenience vs one-way-to-do-it. Resolvable — see Unresolved Questions.
- Domains that never model relationships get slightly more manifest ceremony (an `ontology:
  { concepts: [...] }` wrapper) for no immediate gain over the old flat list.

---

## Alternatives

### Alternative 1: Keep "concern", add relationships and framework mapping to it

Add `relationships` and `satisfies` to concern bundles without renaming. Less churn.
Rejected because it leaves the name collision with separation-of-concerns in place, and
"concern" never signals "this is the domain's conceptual model" — which is the point.

### Alternative 2: Full ontology stack (OWL / RDF / SKOS)

Adopt an established ontology language and tooling. Rejected: enormous complexity increase,
a reasoner dependency, and a barrier to the "author it in YAML, read it by eye" property
that makes SCS approachable. The 90% of value (named concepts, taxonomy, a few typed edges,
framework links) does not need it.

### Alternative 3: Model the ontology as SCDs (meta-tier)

Express concepts as meta-tier SCDs with relationships, rather than a manifest block. Keeps
one mechanism. Rejected for now: the ontology is domain-definition data (it belongs with
the domain manifest, versioned with the domain), not per-project context; putting it in
SCDs blurs that line. Revisit if the manifest block grows unwieldy.

> **[Tim to augment]** Any other approaches you've evaluated, and prior art from other
> specs/standards.

### Do Nothing

Concerns stay a flat list of bundle names. Regulated domains keep expressing
framework coverage informally in prose SCDs. Graph-based consumers (control planes,
workflow engines) keep inferring structure from import edges and naming. The "SCS is for
any AI actor, not just chat" reframe lands with a weaker foundation.

---

## Unresolved Questions

- **Naming**: `concept` confirmed. Confirm `type: concept` (vs `type: concept-bundle`) for
  the bundle type.
- **`satisfies[]` sugar**: keep the shorthand list, or require the `relationships` form
  only?
- **Relationship set**: is `{depends-on, relates-to, satisfies}` the right minimal set, or
  do we also need `part-of` distinct from `parent` taxonomy?
- **Cross-domain concepts**: 0.3 says concerns are "reusable across domains" (a shared
  Security concern). Do concepts stay domain-scoped (this RFC assumes yes) or can a concept
  be defined once and imported by multiple domains? If shared, where does the canonical
  definition live?
- **Migration tooling**: ship an automated `scs migrate 0.3→2.0` for the concern→concept
  rename, or guide-only?
- **`concept` on SCDs**: optional (this RFC) or required for SCDs in a concept bundle?

---

## Future Possibilities

- **Ontology-aware context selection**: a runtime selects context by walking `depends-on`
  from the concepts a task touches, not just by tier.
- **Coverage reports**: `scs coverage --framework iso-13485` answered from the ontology's
  `satisfies` edges.
- **Richer concept relationships** (`constrains`, `conflicts-with`) promoted from
  SCD-level to concept-level if demand appears.
- **Shared/importable concept libraries** across domains (depends on the cross-domain
  question above).
- **Ontology diff**: show what changed between two versions of a domain's ontology as part
  of domain versioning.

---

## Appendix

### Implementation Notes

- Schema: edit `schema/domain/domain-manifest-schema.json` (replace `concerns`, add
  `ontology`); add a concept-id pattern; extend the SCD schema with optional `concept`.
- Validator: new rules module for ontology validation (rules 1–8 above); rename all
  `concern` handling; converge on a single `rules/v2.0.0/` set (retire v0.1.0 / v0.3.0 —
  tracked separately in the SCS 2.0 backlog).
- `scs-tools`: rename `templates/bundles/concerns/` → `.../concepts/`; `scs new concept`;
  domain-manifest scaffolding emits an `ontology` block.
- Docs: `spec/2.0/` rewrite of core-model / terminology / bundle-format; new
  `spec/2.0/domain-ontology.md`.
- Plugins (`scs-vibe`, `scs-team`): update skill prompts and templates.

### Migration Guide (0.3 → 2.0)

1. **Rename** `type: concern` → `type: concept` in every concern bundle; the directory
   `concerns/` → `concepts/` by convention.
2. **Domain manifest**: replace
   `concerns: [bundle:x:1.0.0, …]`
   with
   `ontology: { concepts: [ { id: concept:x, name: X, bundle: bundle:x:2.0.0 }, … ] }`.
   This alone is a valid (flat) Domain Ontology.
3. **Add depth incrementally**: set `parent` where a taxonomy exists; add `depends-on` /
   `relates-to`; add `satisfies` pointing at your standards-tier SCDs.
4. **SCDs**: add `concept: concept:<id>` to each SCD in a concept bundle (optional but
   recommended).
5. Run `scs validate` against the 2.0 rules; fix reported `concern` residue.

A migration script for steps 1–2 is an open question (above).

### Related RFCs

- None yet. The broader SCS 2.0 changes (the "any AI actor" reframe, runtime open-question
  resolutions, model-routing metadata, multi-author provenance, tooling CI) are tracked in
  `ISSUES.md` / `ROADMAP.md` and may spawn their own RFCs.
