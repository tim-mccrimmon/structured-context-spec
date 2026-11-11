# SCS 0.7.0 Release Notes

**Status:** release candidate `0.7.0rc6`, not yet released &nbsp;|&nbsp; **Previous stable:** 0.6.0

---

SCS 0.7.0 changes the tools more than the format. SCDs and bundles written for 0.6.0 remain
valid; scripts that call the tools need updating. See
[`docs/MIGRATION-0.7.0.md`](docs/MIGRATION-0.7.0.md) before upgrading.

## Theme

**Context an AI assistant can maintain for you, under your approval.** SCS is versioned
context for generative AI: the guidance, guardrails, and supporting facts an organization
stands behind, changed only by a new version. 0.7.0 implements
[RFC 0002](rfcs/RFC-0002-agent-mediated-scs.md), so an assistant can run the intake
conversation, draft rules, review them, and release and compile versions, while every change
is confirmed by a person and every version can be verified afterwards.

## What's New

### Domain repositories

Context now lives in its own git repository, `<name>-context/`, rather than inside an
application's codebase. The Domain workspace (`domain/`) holds organization-wide context, and
each Project has a workspace under `projects/<name>/`. `scs new domain` creates the repository
with a CI workflow, `AGENTS.md`, and an initial commit; `scs new project` adds a Project inside
it. Both take `--title`, the display name used in titles and descriptions. `scs-validate` at the repository root checks every workspace. See
[`spec/0.7/bundle-format.md`](spec/0.7/bundle-format.md) §8.

### Versions you can verify

A version is an annotated git tag, `<workspace>/<bundle-name>-v<version>`, on a commit holding
the whole workspace. Its manifest records the approver, always a named person
(`Name <email>`), and a `content_digest` over the bundle's resolved content. Validation checks
every tag against its digest, so a version edited after release is detected, and
`scs compile --version` compiles from the tag rather than the working tree. Released versions
are never overwritten.

### A machine interface for agents

Every `scs` and `scs-validate` command accepts `--json` and prints one result envelope
([`schema/cli/envelope-schema.json`](schema/cli/envelope-schema.json)) with the `changes` it
made, coded `diagnostics`, and a `result`. Commands that write accept `--dry-run` and report
the same changes without making them. Every diagnostic code is registered in
[`schema/diagnostics/codes.yaml`](schema/diagnostics/codes.yaml). New engine commands let an
agent maintain a workspace without editing files: `scs scd write`, `scs bundle pin`,
`add-import`, `add-scd`, `remove-scd`, and `scs add bundle --new`. `scs bundle release`
versions a root bundle and the concept bundles it needs in one command: each changed concept
bundle is versioned and pinned, then the root, with one approver. Its dry run rehearses the
whole release and lists every snapshot, manifest, pin, commit, and tag; a failed release undoes
every step.

### Intake and provenance

Each workspace records its intake conversation in `intake.yaml`: the answers, the source
documents drafted from, and the decisions on review findings. SCD items can say where they
came from with `derived_from`, which validation checks and the compiler never emits. See
[`spec/0.7/agent-interface.md`](spec/0.7/agent-interface.md) §5-§6 and
[`spec/0.7/core-model.md`](spec/0.7/core-model.md) §4.1.

### Change summaries and stacks

`scs bundle diff` reports what changed since the last version: SCDs, prohibitions,
directives, and facts, citations, and imports. `scs stack` previews several compiled artifacts
loaded together, such as a personal, an organization, and a Project artifact, and reports
repeated bundles, duplicated rules, and prohibitions that another layer directs. It reads only;
it never merges or drops a rule. See
[`spec/0.7/runtime-artifact.md`](spec/0.7/runtime-artifact.md) §5.

### Agent Skills

Four skills in the open Agent Skills format, in [`skills/`](skills/README.md), operate SCS
through the tools. `scs-domain` and `scs-project` each take one workspace from setup through
source documents and intake to a draft of every rule in one pass, a draft review package,
advisory review until the rules settle, and a version and a compiled artifact. Section owners
are settled before the draft review package, so it names each section's owner; the person who
releases is asked at release. They resume or update a workspace from `scs status`.
Drafting is written for the assistant as reader: each directive says what the assistant does
when it meets the case; before review, items that repeat across sections are merged and reference
material moves to the uncompiled `summary`, and the sources are swept for uncovered clauses
before review settles. In a regulated workspace, review checks for a rule against presenting
invented content as fact. `scs-validate` checks and fixes, and `scs-explain`
answers questions. They share one set of rules: write only through the engine, show a dry run
and get an explicit yes before every change and commit, never choose an approver, and stay
inside the Domain repository. One yes may cover a batch of writes once every change in it is
shown; commits, versions, and tags keep their own. They install in Claude Code and in Claude
(claude.ai).

### The agent interface, specified

New normative document: [`spec/0.7/agent-interface.md`](spec/0.7/agent-interface.md), covering
machine mode, intake, provenance, human confirmation, change summaries, drafting from source
documents, and advisory review. [`spec/0.7/rfc-0002-trace.md`](spec/0.7/rfc-0002-trace.md)
traces every requirement in RFC 0002 to the specification text that states it.

### Section owners

Every section, a concept bundle or a Project bundle that lists SCDs directly, names the role
accountable for it in its `owner` field, and the workspace's `intake.yaml` `owners` list maps
each role to a person, by name (an email is optional). Scaffolded concepts come with a
default role. Validation reports a
missing or unmapped owner as information while a section is being drafted, versioning refuses
a section without one, and a released section whose role no one holds now is a warning. The
person is kept in the intake record, outside the content digest, so a change of person needs no
new version. `scs bundle set-owner` sets the role. See
[`spec/0.7/bundle-format.md`](spec/0.7/bundle-format.md) §5.1.

### Review packages (preview)

`scs view` renders one released bundle as a single self-contained HTML file for people who
review and approve it without using git: every rule verbatim with the exact line the AI
receives, the section owners, the rules a Project inherits from its Domain, and the content
digest checked against the release. The same release always produces the same file. The
package format is a preview and is expected to change in 0.8.

### Released by, not approved by

The person named when a version is released authorizes it into the repository; the engine
records them as the approver (`--approved-by`, `version_approved_by`). That is not the
organization's formal approval: where context is certified, that happens afterwards in the
organization's own review or quality system, outside SCS. The review package and the skills
say "released by", and the package states that certification is not part of it. The field
names are unchanged in 0.7. An approval record in the organization's own system SHOULD cite
the version and its content digest, which the compiled artifact carries as `source_digest`
([`spec/0.7/governance-and-compliance.md`](spec/0.7/governance-and-compliance.md) §8); after a
release, the skills say what to cite.

### Examples and documentation

[`examples/`](examples/README.md) holds two Domain repositories built through the engine: a
fictional medical-device CDMO with one Project, and a personal Domain, each released and
compiled. `examples/build.py` rebuilds them from a recipe, and CI checks they are current. The
documentation site ([`docs/`](docs/README.md)) is rewritten for 0.7: a quick start with the
skills or the engine, an FAQ, a glossary, and guides to SCDs, the bundle lifecycle, and
validation; `docs/concern-docs/` is now `docs/concept-docs/`.

### Placement guidance (provisional)

[`docs/placement/`](docs/placement/README.md) describes where a compiled artifact can be
placed in five AI services. Each page carries the date it was checked. Placement itself stays
outside SCS, and this guidance is expected to change in 0.8.

## Tooling

- **Packages.** `scs-tools` and `scs-validator` move to 0.7.0, and `scs-tools` depends on the
  validator, so one install gives both `scs` and `scs-validate`. Python 3.11 or later and git
  are required.
- **Ontologies.** `--ontology personal` is new, for one person's context; `sdlc`, `cdmo`, and
  `mca` scaffold their full concept set for the workspace kind.
- **Removed.** `scs init`, `scs new --type`, and `scs bundle version --force` / `--no-git`.
- **Reproducible builds.** When `SOURCE_DATE_EPOCH` is set, every timestamp the engine writes
  uses it, so a scripted build produces the same bytes.
- **Validator messages.** An SCD relationship to a `concept:` id now says that concept links
  belong in the domain manifest's ontology.
- **Exit codes.** 0 success, 1 errors, 2 warnings under `--strict`, 3 usage error, 4 file
  error, 5 internal error.
- **Removed.** The `scs-vibe` and `scs-team` plugins; the Agent Skills in `skills/` replace
  them. The examples `two-tier-governance`, `med-adherence`, and `chai-standards-bundle`
  (still at the `v0.6.0` tag).

## Testing the release candidate

`0.7.0rc6` is published to TestPyPI only:

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ "scs-tools==0.7.0rc6"
```

The `--extra-index-url` supplies dependencies such as click and PyYAML from PyPI. Claude
(claude.ai) cannot reach TestPyPI; there, use the skill ZIPs with the wheels bundled
(`python skills/package.py --wheels <dir>`). Results per client are recorded in
[`docs/install-matrix.md`](docs/install-matrix.md).

## Known Gaps

- **Skill behaviour tests.** The scripted-conversation tests of the skills (plan decision
  D-51) run against a simulated user; pacing (at most three questions per message) is held to
  4 of 5 runs, not 5 of 5. On rc6 every assertion passed, pacing included, in the six
  scenarios the rc6 changes touched, after fixes and reruns; the other seven were last run on
  rc5. Acceptance with a real user (WP-13) passed on rc5, and again on rc6 with the skill
  changes since (2026-11-11); the approval-record guidance has not been run.
- **Install matrix.** Claude Code and Claude are recorded; Cursor, Codex, and GitHub Copilot
  are not yet tried (planned for 0.8).
- **Generated CI.** The workflow `scs new domain` writes installs `scs-validator` 0.7.x from
  PyPI, so it fails until 0.7.0 is published there.
- **`BUNDLE_SCD_UNRESOLVED`** stays a warning (decided): a bundle that lists a missing SCD
  fails `--strict`, a release, and `scs compile`, while a draft still validates.

## Governance

RFC 0002 was accepted on 2026-10-25 by the maintainer, with the comment period waived. The
decisions made while building it are recorded in the RFC's amendments and in
`plan/0.7/07-decisions-and-gaps.md`. The specification is maintained by Tim McCrimmon as sole
maintainer until the transition to community governance planned for 1.0.

## Upgrading

See [`docs/MIGRATION-0.7.0.md`](docs/MIGRATION-0.7.0.md).
