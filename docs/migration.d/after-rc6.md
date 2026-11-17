## Since release candidate 6

- **The examples are Domain repositories.** `examples/medtech-cdmo/` (a CDMO Domain on the
  `cdmo` ontology, with one Project) and `examples/personal/` (a personal Domain) are built
  through the engine by `examples/build.py` from a `recipe.yaml`, released, and compiled; CI
  checks they are current. `python examples/build.py --keep <dir>` gives each with its git
  history and version tags. `examples/two-tier-governance/`, `examples/med-adherence/`, and
  `examples/chai-standards-bundle/` are removed; links to them break. They remain at the
  `v0.6.0` tag. `examples/medical-device-cdmo/` and `examples/merchant-cash-advance/` (the
  reference ontologies) are unchanged.
- **`docs/concern-docs/` is `docs/concept-docs/`.** Links to the old path break. Each page now
  describes one Software Development ontology concept: the template SCDs the engine scaffolds
  for it and its default owner role. The 0.2 brief templates are kept as optional worksheets
  without their AI-mapping fields, and `docs/concern-docs/med-adherence-examples/` is removed.
  The quick start, FAQ, glossary, bundle lifecycle, SCD guide, and validation guide are
  rewritten for 0.7.
- **The engine honors `SOURCE_DATE_EPOCH`.** When it is set, every timestamp the engine writes
  (provenance, intake answers, version manifests) uses it, so a scripted build can be
  reproduced byte for byte. Without it, nothing changes.
- **An SCD relationship to a `concept:` id says where concept links go.** The schema error now
  points to the domain manifest's ontology (`concepts[].relationships`) and the SCD's
  `concept` field (`spec/0.7/domain-ontology.md` §3.3). The rule is
  unchanged: SCD relationships target SCDs or citations.
- **Owners are settled before the draft review package.** The scs-domain and scs-project skills
  propose section owners from the intake's people once the draft is done, so the review package
  names each section's owner; at release they check that every section still has one and ask
  who releases.
- **Drafting consolidates before review.** The skills merge items that say the same thing
  across sections and move reference material (document lists, administration, names where a
  role is enough) to the uncompiled `summary`, showing the counts before and after, and repeat
  the check after each review round. A prohibition is something the assistant itself must
  never do; a rule only a person can break becomes a reminder directive. In a regulated
  workspace, review flags a missing rule against presenting invented content as fact.
- **Citation forms.** `std:` is the only prefix, for laws and regulations too
  (`std:21-cfr-820`, `std:eu-ai-act-2024-1689`); an amendment uses a hyphen
  (`std:iec-62304:2006-a1`), never `+`.
- **An external approval cites the version and the content digest.** Where an organization
  approves its context in its own system of record, the approval record SHOULD cite the version
  and its `content_digest`, which the compiled artifact carries as `source_digest`
  (`spec/0.7/governance-and-compliance.md` §8). After a
  release, the skills say what to cite.
