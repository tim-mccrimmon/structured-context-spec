# Security

The Security concept captures authentication, authorization, data protection, threat modeling, and security controls. It defines how the system protects sensitive data, authenticates users, prevents unauthorized access, and mitigates security threats.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/security.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `authn-authz`, `data-protection`, `data-handling` |
| Project (`projects/<name>/`) | `authn-authz`, `data-protection`, `data-handling`, `threat-model` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: security` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Compliance team (regulatory requirements: HIPAA, SOC2)
- Architecture team (trust boundaries, integration points)
- Organizational security policies
- Industry threat intelligence

[`security-context-brief-template.md`](security-context-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
