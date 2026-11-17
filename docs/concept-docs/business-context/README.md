# Business Context

The Business Context concept captures the foundational "what/why/who" of the project: the problem being solved, the stakeholders involved, business objectives, market opportunity, constraints, and success criteria. This concept provides the essential business rationale that all other concepts depend on.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new project` scaffolds
one concept bundle for it, `bundles/concepts/business-context.yaml`, with these
template SCDs:

| Workspace | Template SCDs |
|---|---|
| Project (`projects/<name>/`) | `problem-definition`, `stakeholders`, `business-objectives`, `opportunity-analysis`, `constraints-and-assumptions`, `success-criteria` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: product` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Executive leadership (strategic objectives)
- Product team (user needs and market analysis)
- Sales/Customer success (customer pain points)
- Finance (budget and ROI expectations)
- Operations (organizational constraints)

[`business-context-opportunity-brief-template.md`](business-context-opportunity-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
