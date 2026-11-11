# Ethics & AI Accountability

The Ethics & AI Accountability concept defines ethical considerations, AI/ML governance, bias mitigation, explainability, and accountability mechanisms. It ensures AI systems are used ethically and responsibly with appropriate human oversight.

A concept of the Software Development (`sdlc`) Ontology Model. `scs new domain` and `scs new
project` scaffold one concept bundle for it, `bundles/concepts/ethics-ai-accountability.yaml`, with these
template SCDs (Domain and Project templates):

| Workspace | Template SCDs |
|---|---|
| Domain (`domain/`) | `ai-usage-policy`, `audit-trail`, `model-bias` |
| Project (`projects/<name>/`) | `ai-usage-policy`, `audit-trail`, `model-bias` |

Keep the templates that apply, fill them from your sources, and retire the rest
(`scs bundle remove-scd`). A concept bundle with no SCDs left is removed. The skills do this
with you; see [What to Gather](../../what-to-gather.md).

## Owner

The concept bundle names the role accountable for it, `owner: ai-governance` by default. Change it
with `scs bundle set-owner`, and name the person who holds it in the intake record
(`scs intake set owners`). A section cannot be versioned until its role is held.

## What to gather

- ML/AI team (models, algorithms, training data)
- Product team (AI use cases, user impact)
- Legal/Compliance team (AI regulations)
- Ethics committee (ethical guidelines)

[`ethics-and-ai-accountability-brief-template.md`](ethics-and-ai-accountability-brief-template.md) is an optional worksheet for collecting this. A filled-in worksheet
is a source document like any other: put it in the workspace's `sources/` and draft from it.
