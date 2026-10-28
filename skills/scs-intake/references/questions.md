# Intake Profile Questions

Ask a profile only when the routing answers call for it. Propose answers you can infer and ask
the user to confirm. Each field is saved with `scs intake set FIELD VALUE --workspace <ws>`.

## Personal Domain

When `audience: individual` and `workspace: domain`, usually with the `personal` ontology.

| Field | Ask | Notes |
|---|---|---|
| `owner` | The person's name and email | `Name <email>`. Provenance only; never compiled |
| `boundaries` | What should no AI tool ever do on any of your work? | The source of personal prohibitions. Keep each one absolute |
| `practices` | Habits you want applied everywhere: languages, testing, commit style | Become directives |

A personal Domain is small. A few prohibitions are enough to start.

## Organization

When `audience: organization`, or `regulated: yes`.

| Field | Ask | Notes |
|---|---|---|
| `organization` | Name, products or services, sites | |
| `certifications` | Standards and editions in scope | Citation references such as `std:iso-13485:2016`; they drive `cites`. Never the standard's text |
| `source_documents` | Quality manual, SOPs, policies to draft from | Each with an `id` (`doc-qm`), `title`, and `path` under `sources/`. Documents stay local |
| `approvers` | Who approves new versions of this context | `{person: Name <email>, role: ...}` |
| `boundaries` | What is explicitly out of bounds for AI tools | The main source of prohibitions |

## Project

For each Project.

| Field | Ask | Notes |
|---|---|---|
| `project` | Name, purpose, technology | |
| `risk` | A risk or safety classification, where one applies | For example IEC 62304 software safety class |
| `data` | Categories of data handled | PHI, PCI, PII |
| `boundaries` | Project-specific prohibitions | |

## Answers

Record free-text answers so drafted items can trace to them:

```yaml
id: q-boundaries-1
question: "Is there anything AI tools must never do with design history files?"
answer: "Never edit a released DHF record; drafts only."
answered_by: Jane Doe <jane@acme.example>
```

`answered_at` is filled in when omitted. Giving an existing `id` replaces that answer.

## Choosing an ontology

| Ontology | For |
|---|---|
| `sdlc` | Software teams |
| `cdmo` | Medical device contract development and manufacturing |
| `mca` | Merchant cash advance and similar lending |
| `personal` | One person's own work |

A Project inherits its Domain's ontology unless the user chooses another.
