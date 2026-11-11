# Deployment & Operations

The Deployment & Operations concept defines deployment strategy, operational procedures, monitoring, incident response, and maintenance. It establishes how the system is deployed, monitored, and maintained in production.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/deployment-operations.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `infrastructure-definition`, `observability`, `incident-response` |
| Project (`projects/<name>/`) | `infrastructure-definition`, `observability`, `incident-response` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: operations` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Engineering team (deployment practices)
- Infrastructure team (platform capabilities)
- Security team (security monitoring requirements)
- Business team (uptime requirements, maintenance windows)

[`deployment-and-operations-brief-template.md`](deployment-and-operations-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
