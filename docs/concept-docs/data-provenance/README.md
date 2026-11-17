# Data & Provenance

The Data & Provenance concept defines data models, data flow, data governance, provenance tracking, and data lifecycle management. It establishes what data the system manages, how it flows, and how lineage is tracked.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/data-provenance.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `provenance-tracking`, `retention-policy` |
| Project (`projects/<name>/`) | `data-model`, `provenance-tracking`, `retention-policy` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: data` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Business team (data requirements, entities)
- Architecture team (data storage approach)
- Compliance team (data retention, privacy)
- Existing systems (current data models)

[`data-and-provenance-brief-template.md`](data-and-provenance-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
