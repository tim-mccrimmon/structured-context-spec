# Intake

How to ask the intake questions and record the answers. The engine is the only writer of
`intake.yaml`; every field is saved with `scs intake set FIELD VALUE --workspace <ws>`.

## Pacing

- Ask at most three questions in one message, and wait for the answers before going on. A
  request to confirm proposed answers counts as one of the three; a person's name, email,
  and role together count as one. Ask only for what this stage needs: a detail needed
  later, such as a person's email for the people answer, waits for that stage.
- Propose answers you can infer, from the source documents or the conversation, and ask the
  user to confirm them. A proposal is not an answer until the user confirms it.
- Ask the ontology; never assume it, even when the Domain's ontology seems to fit.
- After each group of answers, record them, then say what comes next.

## Routing (always)

| Field | Values |
|---|---|
| `audience` | `individual` or `organization` |
| `regulated` | `true` or `false`. The frameworks are recorded later, with the profile, as `certifications` |
| `ontology` | `sdlc`, `cdmo`, `mca`, or `personal` |

| Ontology | For |
|---|---|
| `sdlc` | Software teams |
| `cdmo` | Medical device contract development and manufacturing |
| `mca` | Merchant cash advance and similar lending |
| `personal` | One person's own work |

A Project's ontology describes the Project's own work, which may differ from the Domain's. A
software Project inside a medical device company is usually `sdlc`; it is `cdmo` only if the
Project's work is itself device development or manufacturing. Ask which, and explain the
difference.

## Source documents

Ask for documents before the profile questions: they answer many of them. Give the exact path
of the workspace's `sources/` folder (from `scs status`, `path`), ask the user to copy the
documents there, and wait until they say it is done. Then run `scs status` again: the
`sources.files` it lists are the documents to record. Record each one:

```
scripts/scs_engine.py run scs intake set source_documents '{id: doc-ai-policy, title: AI Usage Policy, path: sources/ai-usage-policy.pdf}' --workspace domain --dry-run
```

Read each document in the conversation, then propose the profile answers it supports. Never
copy a document anywhere else. The documents stay local: `sources/` is ignored by git, except
its README.

If the user has no documents, say that is fine and go on with the questions.

## People

Ask who is involved, and record them as an answer, `q-people-1`, so drafted items can cite
it. Propose names and roles you find in the documents, and ask the user to confirm or correct
them. Take the people in two messages: first who is involved and in which role; then, once
that is settled, who owns which concept (for a Domain) and who approves versions.

- **Domain:** leadership roles that set or own the rules: for example CEO, CTO, CISO, quality,
  regulatory, legal. Ask who owns each concept the ontology covers.
- **Project:** the team: lead, developers, quality or regulatory reviewer, and the business
  owner.

Then ask who approves new versions of this workspace's context, and record each person:

```
scripts/scs_engine.py run scs intake set approvers '{person: Jane Doe <jane@acme.example>, role: Quality Manager}' --workspace domain --dry-run
```

## Personal Domain

When `audience: individual`, usually with the `personal` ontology.

| Field | Ask | Notes |
|---|---|---|
| `owner` | The person's name and email | `Name <email>`. Provenance only; never compiled |
| `boundaries` | What should no AI tool ever do on any of your work? | The source of personal prohibitions. Keep each one absolute |
| `practices` | Habits you want applied everywhere: languages, testing, commit style | Become directives |

A personal Domain is small. A few prohibitions are enough to start.

## Organization Domain

When `audience: organization`, or `regulated: true`.

| Field | Ask | Notes |
|---|---|---|
| `organization` | Name, products or services, sites | |
| `certifications` | Standards, regulations, and editions in scope | Citation references such as `std:iso-13485:2016` or `std:hipaa`; they drive `cites`. Never the standard's text |
| `boundaries` | What is explicitly out of bounds for AI tools | The main source of prohibitions |

## Project

| Field | Ask | Notes |
|---|---|---|
| `project` | Name, purpose, technology | |
| `risk` | A risk or safety classification, where one applies | For example IEC 62304 software safety class |
| `data` | Categories of data handled | PHI, PCI, PII |
| `boundaries` | Project-specific prohibitions | Narrower than the Domain's; never a lift of one |

## Value shapes

The engine validates each value against the intake schema. Pass YAML in these shapes:

| Field | Shape |
|---|---|
| `organization` | `{name: ..., products: [...], services: [...], sites: [...]}` |
| `project` | `{name: ..., purpose: ..., technology: [...]}` |
| `risk` | `{classification: ..., cites: [std:...], rationale: ...}` |
| `certifications`, `data`, `boundaries`, `practices` | lists of strings; a new list replaces the old one |
| `approvers`, `source_documents`, `answers` | one entry per call: added, or replacing the entry with the same `person` or `id` |
| `owner` | `Name <email>` |

## Answers

Free-text answers go in `answers`, so drafted items can trace to them:

```
scripts/scs_engine.py run scs intake set answers - --workspace domain --dry-run <<'EOF'
id: q-boundaries-1
question: "Is there anything AI tools must never do with design history files?"
answer: "Never edit a released DHF record; drafts only."
answered_by: Jane Doe <jane@acme.example>
EOF
```

Pass the YAML on stdin with a heredoc, as above, so no file is written. `answered_at` is filled in when
omitted. Giving an existing `id` replaces that answer. Ask who is answering; do not assume.
A record for a public repository may name roles (`role:quality-manager`) instead of people,
but a version's approver is always a person.
