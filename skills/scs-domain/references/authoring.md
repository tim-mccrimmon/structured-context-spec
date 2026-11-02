# Authoring SCDs

Source: `spec/0.7/runtime-artifact.md` §2 and `spec/0.7/core-model.md` §4.

## An SCD

```yaml
id: scd:project:design-change-control
type: project
title: Design Change Control
version: "1.0.0"
description: Rules for reviewing and approving design changes.
concept: concept:design-controls
content:
  summary: How design changes are reviewed and approved.
  prohibitions:
    - id: DCC-P01
      kind: practice
      subject: marking a design change approved without a recorded human approval
  directives:
    - id: DCC-001
      directive: Draft design change records for human review; do not approve them.
      cites:
        - std:iso-13485:2016#7.3.9
      derived_from:
        - source: doc-qm
          locator: "section 7.3.9"
  facts:
    - id: DCC-F01
      fact: Design changes are approved in the eQMS by the design owner.
      derived_from:
        - intake: q-design-1
provenance:
  created_by: Jane Doe <jane@acme.example>
  created_at: "2026-10-28T00:00:00Z"
```

Only `prohibitions`, `directives`, and `facts` are compiled. `summary` and other content are for
the people who review governance. An SCD with none of the three contributes nothing
(`SCD_EMPTY`); remove it or fill it before a version.

## Prohibitions

| Field | Required | Compiled | Notes |
|---|---|---|---|
| `id` | yes | yes | `^[A-Za-z0-9][A-Za-z0-9._-]*$` |
| `kind` | yes | no | `tool` (a product, service, library, or model) or `practice` (an action) |
| `subject` | yes | yes | A noun phrase. Compiled as `Prohibited: <subject>.` |
| `instead` | no | yes | The approved alternative. Compiled as ` Use instead: <instead>.` |
| `reason` | no | no | Why, for reviewers |
| `cites` | no | yes | Citations |

The validator rejects a subject containing a conditional or advisory word: *unless*, *except*,
*if*, *when*, *where possible*, *avoid*, *prefer*, *should*.

Good: `subject: committing credentials, keys, or tokens to any repository`.
Not a prohibition: "avoid sharing secrets where possible". That is advice; make it a directive,
or narrow it until it is absolute.

A Project cannot lift a Domain prohibition. Changing one needs a new Domain version.

## Directives

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique within the SCD |
| `directive` | yes | One instruction, as the agent should read it |
| `cites` | no | Citations |

## Facts

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique within the SCD |
| `fact` | yes | One short, verifiable statement |
| `cites` | no | Citations |

## `derived_from`

A list on any prohibition, directive, or fact. Each entry has exactly one of:

- `intake: <answer id>` from `intake.yaml` `answers`;
- `source: <document id>` from `intake.yaml` `source_documents`, with an optional `locator`.

It is never compiled. An unknown id is `DERIVED_FROM_UNRESOLVED` (a warning; fails `--strict`).

## Citations

`std:<standard>[:<edition>][#<clause>]`, for example `std:iec-62304:2006-a1#5.1`. A citation
names a clause; it never carries the clause's text.

## Writing an SCD

Pass the YAML on stdin with a heredoc, so no draft file is written anywhere:

```
scripts/scs_engine.py run scs scd write context/project/design-change-control.yaml \
    --from-file - --dry-run <<'EOF'
id: scd:project:design-change-control
...
EOF
```

Then run the same command without `--dry-run`, and list a new SCD in its concept bundle with
`scs bundle add-scd`.
