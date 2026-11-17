# SCS Quick Start (0.7)

From nothing to a released, compiled Domain: the context that governs all of an
organization's or a person's AI-assisted work. There are two ways to do it:

- **With the Agent Skills** (most people): an AI assistant drafts the context from your
  documents and answers, and you confirm each change.
- **With the engine directly**: the same steps as `scs` commands.

Either way the result is a **Domain repository**: a git repository with the Domain workspace
in `domain/` and, later, one workspace per Project in `projects/<name>/`.

---

## Before you start

- Python 3.11 or later, and git.
- Your source material: policies, procedures, a standards list, and the people who own each
  area. [What to Gather](what-to-gather.md) lists what helps.
- The SCS tools:

  ```bash
  pip install "scs-tools==0.7.0"        # installs scs and scs-validate
  ```

  Until 0.7.0 is on PyPI, see [`tools/cli/README.md`](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/tools/cli/README.md) for the release
  candidate. The skills can also install the tools for you.

---

## Path 1: with the Agent Skills

1. **Install the skills.** In Claude Code, copy them into your skills directory:

   ```bash
   git clone https://github.com/tim-mccrimmon/structured-context-spec.git
   cp -R structured-context-spec/skills/scs-* ~/.claude/skills/
   ```

   For Claude (claude.ai) and other clients, see [`skills/README.md`](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/skills/README.md)
   and the [install matrix](install-matrix.md).

2. **Start the Domain.** In a new session, in the directory where the repository should go,
   ask: *"Set up our SCS Domain."* `scs-domain` takes it from there:

   | Stage | What happens |
   |---|---|
   | Profile | Who the context is for, the industry ontology, and the source documents |
   | Draft | Every SCD drafted in one pass from your sources, each rule traced to where it came from, then consolidated |
   | Owners and review package | You confirm who owns each section; the assistant writes an HTML review package for them |
   | Review | Findings and your decisions, round by round, until it settles |
   | Release | You name who releases; the version is tagged and compiled |

   You can stop at any point. The next session starts from `scs status` and picks up where
   you left off.

3. **Add a Project** once the Domain has a released version: in a new session, ask
   *"Add a Project for <name>."* `scs-project` works the same way and reviews the Project
   against the Domain's rules.

4. **Ask questions any time.** `scs-explain` answers "where are we?", "where did this rule
   come from?", or "what does this message mean?". `scs-validate` runs the validator and
   explains the results.

---

## Path 2: with the engine

The engine's commands are what the skills run. Every command that changes files takes
`--dry-run`, and `--json` for machine mode.

### 1. Create the repository

```bash
scs new domain acme --ontology cdmo --title "Acme Medical" \
    --author "Jane Doe" --email jane@acme-medical.com
cd acme-context/domain
scs status
```

The ontology (`sdlc`, `cdmo`, `mca`, or `personal`) supplies the concept bundles and
template SCDs. A `personal` Domain gets only boundaries; define its other concepts with
`scs add bundle <name> --new`.

### 2. Fill in the SCDs you need, retire the rest

Each template in `context/project/` says what goes in it. Write the content as
`prohibitions`, `directives`, or `facts`:

```yaml
content:
  summary: "Design changes follow the QMS design change procedure."
  directives:
    - id: DOC-001
      directive: "Design changes require documented review and approval before implementation."
      cites:
        - std:iso-13485:2016#7.3.9
```

Edit the files, or write them through the validator:

```bash
scs scd write context/project/document-control.yaml --from-file draft.yaml
scs bundle remove-scd scd:project:supplier-assessment scd:project:vendor-tier-approval
```

[Understanding SCDs](scd-guide.md) covers how to write rules that work.

### 3. Name the owners and approvers

Each concept bundle names an owner role (`owner: quality`). Record who holds each role, and
who approves versions:

```bash
scs intake set owners '{role: quality, person: Jane Doe <jane@acme-medical.com>, title: VP Quality}'
scs intake set approvers '{person: Jane Doe <jane@acme-medical.com>, role: VP Quality}'
scs commit -m "Draft the Domain" --author "Jane Doe <jane@acme-medical.com>"
```

### 4. Validate and review

```bash
scs bundle validate                                  # this workspace
(cd .. && scs-validate --strict)                     # every workspace, as CI runs it
scs view bundles/domain-bundle.yaml --allow-draft    # an HTML review package in dist/
```

Send the review package to the section owners. Fix what they find, and repeat.

### 5. Release and compile

```bash
scs bundle release --version 1.0.0 --concept company=1.0.0 --concept prohibited=1.0.0 ... \
    --approved-by "Jane Doe <jane@acme-medical.com>" --dry-run
```

Run it without `--concept` first to see which concept bundles need a version, then without
`--dry-run`. Each version is a git tag (`domain/acme-v1.0.0`) on a commit with a snapshot
and a manifest recording the approver and the content digest. Then compile:

```bash
scs compile bundles/domain-bundle.yaml --version 1.0.0    # dist/acme-1.0.0.yaml
```

The compiled artifact is a short YAML file: prohibitions first, then rules, then facts, with
the content digest as `source_digest`. [Placement](placement/README.md) describes how
common AI services can be given it. That step is yours; SCS does not place artifacts.

### 6. Add a Project

```bash
cd ..
scs new project portal --author "Jane Doe" --email jane@acme-medical.com
cd projects/portal
```

The Project has its own templates and bundle and is released and compiled the same way. It
does not import the Domain; at runtime both artifacts apply, Domain first.

---

## See it finished

[`examples/medtech-cdmo/`](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/examples/medtech-cdmo) is a complete Domain repository with
one Project, built by these commands, and [`examples/personal/`](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/examples/personal) is a
personal Domain.

## Next

- [Bundle Lifecycle](bundle-lifecycle.md): versions, pins, changes after release
- [Validation](validation-guide.md): what each check means
- [FAQ](FAQ.md)
