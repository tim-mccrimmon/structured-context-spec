# Testing & Validation

The Testing & Validation concept defines testing strategy, validation approach, quality assurance processes, and verification methods. It establishes how the system is tested to ensure correctness, reliability, and quality.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/testing-validation.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `test-coverage`, `qa-procedures`, `engineering-practices` |
| Project (`projects/<name>/`) | `test-coverage`, `validation-plan`, `qa-procedures` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: quality` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- Engineering team (current testing practices)
- Product team (acceptance criteria)
- Security team (security testing requirements)
- Compliance team (validation requirements)

[`testing-and-validation-brief-template.md`](testing-and-validation-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
