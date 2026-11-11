# Usability & Accessibility

The Usability & Accessibility concept defines user experience principles, interface design approach, accessibility requirements, and human-computer interaction patterns. It ensures the system is usable by all intended users including those with disabilities.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/usability-accessibility.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `ux-principles`, `accessibility-compliance` |
| Project (`projects/<name>/`) | `ux-principles`, `accessibility-compliance`, `error-handling-ux` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: product` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Product team (user research, personas)
- Design team (UX patterns, design system)
- Compliance team (accessibility requirements)
- User feedback and research

[`usability-and-accessibility-brief-template.md`](usability-and-accessibility-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
