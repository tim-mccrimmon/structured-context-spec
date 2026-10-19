# SCS 0.6.0 — Standards-Tier SCDs (Deprecated)
**Version:** 0.6.0 (Draft)
**Status:** Deprecated in 0.6.0; scheduled for removal in a later release
**Last Updated:** 2026-10-19

---

## 1. What Changed

Through 0.5.0, SCS represented external standards (HIPAA, SOC 2, ISO 13485 and others) as
**Standards-Tier SCDs**, grouped into **Standards bundles** and imported into projects.

In 0.6.0:

- The **Standards tier** (`type: standards`, `scd:standards:` ids) is deprecated.
- The **Standards bundle** type (`type: standards`) is deprecated (`bundle-format.md` §3.3).
- External standards are represented only as **citation references**, strings of the form
  `std:<standard>[:<edition>][#<clause>]`, for example `std:iso-13485:2016#7.3.9`
  (`citations.md`).

Validators continue to accept Standards-Tier SCDs, Standards bundles and `scd:standards:`
relationship targets in 0.6.0, with deprecation warnings. They will be removed in a later
release.

---

## 2. Why

- **Governance is the rules the model obeys.** An AI system acts on an organization's
  rules, such as "design changes require documented review before implementation". A
  restatement of a standard's clause is the reason a rule exists, not a rule in itself.
- **Standard text is licensed.** The text of most standards is sold under license, and only
  the adopter holds it. A bundle cannot reproduce it, and a Standards SCD that paraphrases
  it closely enough to be useful raises the same concern.
- **The interpretation belongs to the adopter.** Standards bodies do not publish SCS
  bundles, so any Standards SCD was someone's interpretation. An organization's quality
  system (its manual and SOPs) already is its interpretation, and the organization is
  accountable for it. Those rules belong in its Domain bundle.

Where an adopter wants AI access to a standard's full text, that text is reference
material for retrieval, held under the adopter's license. It is not governance context and
is outside the scope of SCS bundles.

---

## 3. Migration

1. **Move rules into Domain or Project SCDs.** For each Standards-Tier SCD, identify the
   rules the organization actually follows. Author organization-wide rules as project-tier
   SCDs in the Domain bundle's concept bundles, and project-specific rules in the Project
   bundle.
2. **Cite the standard on the rules that implement it.** Add a `cites` list to each of
   those SCDs, naming the edition and clause, with no standard text:
   ```yaml
   cites:
     - std:iso-13485:2016#7.3.9
   ```
3. **Replace `satisfies` targets.** Change `scd:standards:` targets in SCD relationships
   and in domain-manifest `satisfies` lists to citation references
   (`domain-ontology.md` §3.1).
4. **Remove Standards bundle imports.** Drop `bundle:standards...` imports from Domain and
   Project bundles, then delete the Standards bundles and SCDs.
5. Run `scs-validate` and resolve the remaining deprecation warnings.

---

## 4. Related Documentation

- `citations.md` — citation reference format and where citations may appear
- `bundle-format.md` §3.3 — Standards bundle deprecation
- `core-model.md` §5.2 — tier model

---

## 5. Feedback

Feedback on the deprecation and migration should be submitted via GitHub Issues.
