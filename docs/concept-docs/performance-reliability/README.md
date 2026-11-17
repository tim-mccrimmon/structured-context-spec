# Performance & Reliability

The Performance & Reliability concept defines performance requirements, reliability targets, scalability approach, availability expectations, and system resilience. It establishes how the system performs under load and recovers from failures.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new project` scaffolds
one concept bundle for it, `bundles/concepts/performance-reliability.yaml`, with these
template SCDs:

| Workspace | Template SCDs |
|---|---|
| Project (`projects/<name>/`) | `response-time`, `availability`, `fault-tolerance`, `scalability` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: engineering` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Business team (SLA commitments, user expectations)
- Architecture team (scalability approach)
- Operations team (current performance baselines)
- Product team (acceptable response times)

[`performance-and-reliability-brief-template.md`](performance-and-reliability-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
