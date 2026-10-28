---
name: scs-intake
description: Sets up Structured Context (SCS) for a person or an organization. Runs the intake conversation, creates the Domain repository and its Domain and Project workspaces with the SCS tools, and records the answers in intake.yaml. Use when someone wants to start using SCS, create governance or AI guardrails for their work, add a Project to an existing Domain, or revisit their intake.
license: Apache-2.0
compatibility: Needs Python 3.11+, git, and the SCS tools (scs-tools 0.7.0 or later); scripts/scs_engine.py checks and plans the install.
metadata:
  scs-spec: "0.7.0"
  scs-minimum-tools-version: "0.7.0"
---

# SCS Intake

You help the user set up Structured Context: versioned guidance, guardrails, and supporting
facts for the AI tools they use. You gather what is needed in conversation, and the SCS tools
(the engine) do every write. You never write workspace files yourself.

## Rules for every SCS skill

1. Call the engine only through `scripts/scs_engine.py run scs ...` (or `run scs-validate ...`).
   Never edit workspace files directly, and never reimplement validation, versioning, or
   compiling.
2. Before any write, run the command with `--dry-run`, show the user the planned `changes`
   (each path, and any git commit or tag) in plain language, and get an explicit yes. Then run
   it for real.
3. Report success only when the envelope says `"ok": true`. Otherwise say what failed, using
   the diagnostics.
4. Never pass `--force`, `--no-validate`, or `--allow-draft` unless the user asked for that
   behaviour in this conversation.
5. Never choose an approver, take one from git config or the environment without asking, or
   record yourself or the model as one. Approvers are people the user names: `Name <email>`.
6. Write nothing outside the Domain repository. Source documents go nowhere but this
   conversation.
7. Placing artifacts in AI services, multi-person review or approval workflows, hosted or
   shared registries, and runtime serving are outside SCS. If asked, say so plainly, and do
   not run anything for it.
8. When the user is working on one workspace (`domain` or one Project), change no other.

## 0. Check the engine

Run `scripts/scs_engine.py check`. If `ok` is false, run `scripts/scs_engine.py install-plan`
and show the user the command and where the package comes from. Install only once the user
agrees, or let them run it. If the user uploaded wheel files, run `stage-wheels` on them first
and pass the staged paths to `install-plan`.

## 1. Establish the Domain repository first

The first step of every intake decides the Domain repository: an existing one the user names,
or a new one. A Domain is one owner's governance: an organization, or one person.

- **Existing:** confirm the path, then work inside it. A repository holds `domain/` and
  `projects/<name>/`, each with `.scs/config`.
- **New:** propose the name `<domain-name>-context` (for example `acme-cdmo-context`,
  `jdoe-context`). Build the Domain workspace before any Project.

## 2. Routing questions (always)

Infer what you can from the conversation, then ask the user to confirm in one message rather
than asking each question separately:

| Field | Values |
|---|---|
| `audience` | `individual` or `organization` |
| `domain` | the existing repository, or `new` |
| `workspace` | `domain`, or a Project name |
| `regulated` | yes or no; if yes, which frameworks |
| `ontology` | `sdlc`, `cdmo`, `mca`, or `personal`, proposed from the above |

Then ask the profile questions that apply. They are in
[references/questions.md](references/questions.md).

## 3. Create the workspace

Ask for the author's name and email; never take them from git config without confirming.

```
scripts/scs_engine.py run scs new domain <name> --ontology <ontology> \
    --author "<Name>" --email "<email>" --no-interactive --dry-run
```

Show the planned changes (the repository, `AGENTS.md`, CI workflow, templates, the initial
commit), get a yes, then run it without `--dry-run`. For a Project, run
`scs new project <name> --dir <repository> ...` the same way, only after the Domain exists.

The scaffold supplies every template for the ontology. Go through them with the user and remove
what does not apply with `scs bundle remove-scd` (see the scs-draft skill). A `personal`
Domain gets only boundaries; define the person's other concepts with them using
`scs add bundle <name> --new`.

## 4. Record the intake

Save every answer with the engine; it is the only writer of `intake.yaml`:

```
scripts/scs_engine.py run scs intake set audience organization --workspace domain --dry-run
scripts/scs_engine.py run scs intake set approvers '{person: Jane Doe <jane@acme.example>, role: Quality Manager}' --workspace domain
scripts/scs_engine.py run scs intake set answers - --workspace domain < answer.yaml
```

Free-text answers go in `answers` with an id (`q-boundaries-1`), the question, the answer,
and `answered_by`. Those ids are what drafted items cite in `derived_from`. A record for a
public repository may name roles (`role:quality-manager`) instead of people, but a version's
approver is always a person.

Show the field-by-field change before each write, as for any other write. For a workspace
made before 0.7, offer to reconstruct an intake record by asking; it is optional.

## 5. Finish

Run `scripts/scs_engine.py run scs-validate --strict` at the repository root and explain the
result. Then suggest the next step: drafting the rules (scs-draft).
