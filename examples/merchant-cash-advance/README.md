# Merchant Cash Advance (MCA) Reference Skeletons

A customer-neutral starting point for a merchant cash advance / business-funding provider: one
**skeleton SCD** for each of the 16 concepts in the MCA Domain Ontology
(`schema/domain/examples/merchant-cash-advance-domain.yaml`), packaged as concept bundles under one
domain bundle.

**These are skeletons, not guardrails.** Every substantive field is a `TODO`. Nothing here is a
decision; it becomes one when the person with standing over a concept decides something and writes it
in. Some `TODO`s carry an `e.g.` hint drawn from how this industry typically works.

## What is here

```
merchant-cash-advance/
├── domains/merchant-cash-advance.yaml   # domain bundle: imports the 16 concept bundles (DRAFT)
├── concepts/<concept>.yaml              # one concept bundle per concept, holding its skeleton SCD (DRAFT)
└── scds/project/<concept>.yaml          # the skeleton SCD for each concept
```

Everything validates with `scs-validate` (SCDs, bundles, and the ontology manifest with
`--domain`). All bundles are `DRAFT`, so no approval is recorded yet.

## The 16 concepts

The ontology has three clusters. The first is what makes this a business-funding ontology and not a
relabeled software or medical-device one.

| Cluster | Concepts |
|---|---|
| MCA-native | origination, underwriting-decisioning, contract-characterization, disclosure-compliance, security-interest-management, servicing-collections, capital-funding, portfolio-risk-management, broker-partner-management |
| Infrastructure | data-provenance, data-security, systems-integration |
| Universal AI governance | governance, ai-accountability, training-competency, adoption-rollout |

`data-security` is named that way, not `security`, because in this business "security" natively
means the lien on receivables (`security-interest-management`).

## Who typically owns each concept (a suggestion)

Someone with standing has to decide each concept; the skeleton cannot say who. These are the
functions that usually hold it, to start the conversation:

| Concept | Typical owning function |
|---|---|
| origination, broker-partner-management | Sales |
| underwriting-decisioning | Underwriting |
| contract-characterization, disclosure-compliance | Legal (a review gate; often no single department owns it) |
| security-interest-management | Legal or Finance |
| servicing-collections | Collections |
| capital-funding | Treasury / Finance |
| portfolio-risk-management | Finance / data science |
| data-provenance, data-security, systems-integration | IT / technology leadership |
| governance, ai-accountability, adoption-rollout | Executive leadership (with department heads for pacing) |
| training-competency | HR |

## Using it

1. Copy the SCDs and bundles into your project and replace each `TODO` with a real decision.
2. Expect each concept to split into several small, atomic SCDs once real decisions exist; keep one
   decision per SCD and add them to the concept bundle.
3. Add concepts of your own if your business needs them. The ontology is the industry baseline: add
   to it, do not remove from it.
4. Validate, then version and approve a bundle when it is ready (`scs bundle version`).

Links between concepts (`depends-on`, `relates-to`) live in the **ontology**, not on the SCDs: an
SCD relationship must point at another SCD, so a `concept:` target is not valid there.

## What this is not

Best-practice AI governance, not a compliance program. Regulatory obligations (state disclosure
regimes, and so on) belong to your own legal and compliance function; the ontology deliberately
carries no statute-by-statute mapping.
