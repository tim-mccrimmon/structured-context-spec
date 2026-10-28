# SCS 0.7.0 Release Notes

**Status:** release candidate `0.7.0rc1`, not yet released &nbsp;|&nbsp; **Previous stable:** 0.6.0

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
it. `scs-validate` at the repository root checks every workspace. See
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
`add-import`, `add-scd`, `remove-scd`, and `scs add bundle --new`.

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

Seven skills in the open Agent Skills format, in [`skills/`](skills/README.md), operate SCS
through the tools: intake, drafting, advisory review, validation, versioning, compiling, and
explaining. They share one set of rules: write only through the engine, show a dry run and get
an explicit yes before every change, never choose an approver, and stay inside the Domain
repository. They install in Claude Code and in Claude (claude.ai).

### The agent interface, specified

New normative document: [`spec/0.7/agent-interface.md`](spec/0.7/agent-interface.md), covering
machine mode, intake, provenance, human confirmation, change summaries, drafting from source
documents, and advisory review. [`spec/0.7/rfc-0002-trace.md`](spec/0.7/rfc-0002-trace.md)
traces every requirement in RFC 0002 to the specification text that states it.

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
- **Exit codes.** 0 success, 1 errors, 2 warnings under `--strict`, 3 usage error, 4 file
  error, 5 internal error.
- **Deprecated.** The `scs-vibe` and `scs-team` plugins, removed in 0.8.

## Testing the release candidate

`0.7.0rc1` is published to TestPyPI only:

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ "scs-tools==0.7.0rc1"
```

The `--extra-index-url` supplies dependencies such as click and PyYAML from PyPI. Claude
(claude.ai) cannot reach TestPyPI; there, use the skill ZIPs with the wheels bundled
(`python skills/package.py --wheels <dir>`). Results per client are recorded in
[`docs/install-matrix.md`](docs/install-matrix.md).

## Known Gaps

- **Skill behaviour tests.** The scripted-conversation tests of the skills (plan decision
  D-51) have not run. The skills' structure is tested; their behaviour with a model is
  specified but not yet demonstrated.
- **Install matrix.** Claude Code and Claude are recorded; Cursor, Codex, and GitHub Copilot
  are not yet tried.
- **Generated CI.** The workflow `scs new domain` writes installs `scs-validator` 0.7.x from
  PyPI, so it fails until 0.7.0 is published there.
- **`BUNDLE_SCD_UNRESOLVED`** stays a warning; whether it should be an error is open.
- **Examples** have not yet been rebuilt as Domain repositories.

## Governance

RFC 0002 was accepted on 2026-10-25 by the maintainer, with the comment period waived. The
decisions made while building it are recorded in the RFC's amendments and in
`plan/0.7/07-decisions-and-gaps.md`. The specification is maintained by Tim McCrimmon as sole
maintainer until the transition to community governance planned for 1.0.

## Upgrading

See [`docs/MIGRATION-0.7.0.md`](docs/MIGRATION-0.7.0.md).
