# Safety & Risk

The Safety & Risk concept defines safety requirements, risk assessment, hazard analysis, and risk mitigation strategies. It ensures the system operates safely and that risks are identified and managed appropriately.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new project` scaffolds
one concept bundle for it, `bundles/concepts/safety-risk.yaml`, with these
template SCDs:

| Workspace | Template SCDs |
|---|---|
| Project (`projects/<name>/`) | `risk-assessment`, `safety-checklist` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: quality` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Engineering team (technical risks)
- Business team (business impact of failures)
- Compliance team (safety regulations)
- Industry standards (safety best practices)

[`safety-and-risk-brief-template.md`](safety-and-risk-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
