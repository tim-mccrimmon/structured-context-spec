# Compliance & Governance

The Compliance & Governance concept defines regulatory compliance requirements, audit trails, governance policies, and how standards are satisfied. It ensures the system meets legal, regulatory, and organizational requirements.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/compliance-governance.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `soc2-controls`, `audit-requirements`, `policy-enforcement` |
| Project (`projects/<name>/`) | `soc2-controls` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: compliance` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Legal team (regulatory requirements)
- Security team (technical controls)
- Business team (organizational policies)
- External auditors (audit requirements)

[`compliance-and-governance-brief-template.md`](compliance-and-governance-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
