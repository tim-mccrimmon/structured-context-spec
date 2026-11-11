# Architecture

The Architecture concept defines the system's structure, components, boundaries, and technical design. It establishes how the system is organized, what technologies are used, how components interact, and how the system integrates with external systems.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/architecture.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `tech-stack`, `integration-map` |
| Project (`projects/<name>/`) | `system-context`, `tech-stack`, `integration-map`, `component-model` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: engineering` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Engineering team (technical capabilities)
- Infrastructure team (platform constraints)
- Security team (security requirements)
- Existing systems (integration needs)

[`architecture-context-brief-template.md`](architecture-context-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
