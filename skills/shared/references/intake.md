# Intake

How to ask the intake questions and record the answers. The engine is the only writer of
`intake.yaml`; every field is saved with `scs intake set FIELD VALUE --workspace <ws>`.

## Pacing

- Ask at most three questions in one message, and wait for the answers before going on. A
  request to confirm proposed answers counts as one of the three; a person's name, email,
  and role together count as one. Ask only for what this stage needs: a detail needed
  later, such as a person's email for the people answer, waits for that stage.
- Propose answers you can infer, from the source documents or the conversation, and ask the
  user to confirm them. A proposal is not an answer until the user confirms it. Put a value
  the documents do not give into the same confirmation as an invitation ("confirm or correct
  these, and add any products or sites"), not as a question of its own.
- Ask the people questions only once the profile answers are recorded, in a message of their
  own.
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

Ask for documents before the profile questions: they answer many of them. Give the full path
of the workspace's `sources/` folder, absolute, in the message that asks for the documents
(the repository root plus `scs status` `path`), ask the user to copy the
documents there, and wait until they say it is done. Then run `scs status` again: the
`sources.files` it lists are the documents to record. Record each one:

```
scripts/scs_engine.py run scs intake set source_documents '{id: doc-ai-policy, title: AI Usage Policy, path: sources/ai-usage-policy.pdf}' --workspace domain --dry-run
```

Read each document in the conversation, then propose the profile answers it supports. Never
copy a document anywhere else. The documents stay local: `sources/` is ignored by git, except
its README.

In the same message, ask one optional question: is there a website whose pages should inform the
answers (the organization's site for a Domain, the product's or client's for a Project)? If the
user gives one, read the pages they name with your web-reading tool (WebFetch in Claude Code),
not a shell command such as `curl`; the home page and an About page are usually enough.
Save the text of each page as a dated Markdown copy in `sources/`, named
`website-<host>-<page>-<YYYY-MM-DD>.md`, starting with the URL and the date it was read; show
the file names and get a yes first, as for any write. Record each copy like a document, with its
`path` only: the copy, not the live page, is what the answers came from. If you cannot read web
pages here, say so and ask the user to save the pages into `sources/` themselves.

If the user has no documents and no website, say that is fine and go on with the questions.

## People

Ask who is involved, and record them as an answer, `q-people-1`, so drafted items can cite
it. Record each person by name and role; ask for an email only from whoever releases versions,
unless the user offers it. Propose names and roles you find in the
documents, and ask the user to confirm or correct them. Ask who owns each section once the
draft is done, before the draft review package: the draft decides which sections there are, and
the section owners are its primary reviewers, so the package names them. Ask who releases
versions at release. The engine refuses a version until both are recorded.

- **Domain:** leadership roles that set or own the rules: for example CEO, CTO, CISO, quality,
  regulatory, legal.
- **Project:** the team: lead, developers, quality or regulatory reviewer, and the business
  owner.

### Section owners

Every section (concept bundle) has an owner role: the person accountable for that section,
who reviews and approves it. The templates give each concept a default role; `scs status`
lists them under `owners.sections`, with `unmapped_roles` for roles no one holds yet. Propose
a person for every role yourself, from the people already recorded (the people answer in
`intake.yaml`, usually `q-people-1`, and the source documents), as one table (role, the
sections it owns, the person, their title), and ask the user to confirm or correct it: that is
one question. Do this even when there is one role. Never ask who holds a role, and never list
the roles with blanks for the user to fill in. A person may hold
several roles; a small organization often merges them.

Record each role with its person's name and title. Do not ask for owners' emails; record one
only if the user gives it (`Jane Doe <jane@acme.example>`):

```
scripts/scs_engine.py run scs intake set owners '{role: quality, person: Jane Doe, title: VP Quality}' --workspace domain --dry-run
```

If the user wants a section owned by a different role than its default, change the bundle's
role, then map the new role:

```
scripts/scs_engine.py run scs bundle set-owner regulatory --bundle bundles/concepts/compliance-governance.yaml --workspace domain --dry-run
```

A personal Domain has one role, `owner`: map it to the person. Versioning a section fails until
its role is mapped (`VERSION_OWNER_UNMAPPED`), so settle owners after drafting, before the
draft review package; at release, check that every section, including any added in review,
still has one. A
change of person later is an intake change only and needs no new version; a change of role
changes the bundle and needs one.

### Who releases versions

At release, ask who releases new versions of this workspace's context, and record each person (the
engine calls them approvers):

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
| `certifications` | Standards, regulations, and editions in scope | Citation references in the form in [authoring.md](authoring.md) ("Citations"), such as `std:iso-13485:2016`, `std:21-cfr-820` or `std:hipaa`; they drive `cites`. Never the standard's text |
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
| `owners` | `{role: ..., person: Name, title: ...}` (email optional), one per call, replacing the entry with the same `role` |
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
omitted. Giving an existing `id` replaces that answer. The person answering is the author
named when the workspace was created, unless the user says otherwise; do not ask again.
A record for a public repository may name roles (`role:quality-manager`) instead of people,
but whoever releases a version is always a named person.
