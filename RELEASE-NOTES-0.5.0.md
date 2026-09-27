# SCS 0.5.0 Release Notes

**Released:** 2026-09-27 &nbsp;|&nbsp; **Previous stable:** 0.3

---

SCS 0.5.0 is a **breaking change** — expected pre-1.0, per semver. The specification is
still settling and isn't claiming stability yet (see Governance, below). If you have 0.3
content, see [`docs/MIGRATION-0.5.0.md`](docs/MIGRATION-0.5.0.md) before upgrading.

## Theme

**Structured context is the governed context layer for any AI actor** — chat assistants,
autonomous agents, MCP tool invocations, and multi-agent workflows, not just chat. 0.5.0
makes the domain model explicit, resolves the runtime-facing open questions carried over
from `OPEN_QUESTIONS.md`, and hardens the tooling so downstream systems can depend on it.

## What's New

### The Domain Ontology replaces "concern" (anchor change)

The 0.3 model — a domain manifest listing flat `concerns:` — is replaced by the **Domain
Ontology** (RFC-0001): a domain-defined set of **concepts**, with an optional shallow
taxonomy, a small fixed set of typed relationships (`depends-on`, `relates-to`, plus a
`satisfies[]` shorthand for standards), and a mapping from each concept to the standards it
satisfies. Hierarchy becomes `Project → Domain → Concept → SCD`. Bundles of functional areas
now carry `type: concept` (was `type: concern`).

This isn't just a rename — a 0.3 domain manifest's concern list had no relationships between
entries. A 0.5.0 ontology is structured: concepts can depend on and relate to each other,
and each can map to the specific standard it exists to satisfy. See
[`spec/0.5/domain-ontology.md`](spec/0.5/domain-ontology.md) and the worked reference example
at `schema/domain/examples/medical-device-cdmo-domain.yaml`.

Three reference ontologies ship with 0.5.0: **software development** (11 concepts, the
original baseline), **medical-device CDMO** (12 concepts, regulated-manufacturing specific),
and **merchant cash advance / business funding** (16 concepts across MCA-native,
infrastructure, and universal AI-governance clusters).

`scs new project --ontology mca` scaffolds the full MCA ontology directly - 16 concept
bundles, 16 SCDs, and a domain manifest with real `depends-on`/`relates-to` relationships,
not just names. `--ontology sdlc` (the default) is unchanged. CDMO scaffolding isn't wired
up yet (see Deferred, below) even though its reference ontology ships; the software-
development and MCA reference ontologies were both real, existing content this drew from.

### Structured context for any AI actor, not just chat

New normative doc: [`spec/0.5/any-ai-actor-model.md`](spec/0.5/any-ai-actor-model.md).
Covers three things:

- **Context resolved by (agent, intent), not by session.** A session is state — what
  already happened in a specific execution. Context is a decision that holds until someone
  changes it. Resolving context by session conflates the two.
- **Policy-as-context.** A tool or MCP server's permitted operations become governed
  context in their own right, expressed as an ordinary Policy SCD pattern.
- **The checkpoint record.** A small, normative shape any runtime can emit answering
  "which version of which context governed this point in execution?" — not an SCD, generated
  fresh per execution, closer to a structured log line.

### Runtime decisions: immutability, versioning, drift

Three questions carried in `OPEN_QUESTIONS.md` since early SCS are now normative decisions
(§5 of the any-ai-actor model):

- **Immutability** is scoped to a single execution/step, not a whole task or session — a
  multi-step task may re-resolve context at each checkpoint.
- **"In effect"** means the latest *approved* bundle version (never a `DRAFT`); a deployment
  may pin an older version; supersession is immediate for future resolutions and never
  rewrites past checkpoint records.
- **Context drift** is defined mechanically: two checkpoints in the same workflow resolving
  the same concept to different bundle versions. Whether that's acceptable is a runtime
  policy decision, not something SCS rules on.

### Provenance and approval

A bundle's `provenance` must carry `version_approved_by` and `version_approved_at` before it
can carry a real semver version — a `DRAFT` bundle is exempt. This closes the audit-trail
gap RFC-0001 identified: who approved what, and when.

### Tier terminology clarified, not renamed

Some material (`ROADMAP.md`, engagement docs) describes coverage as **Corporate** and
**Project** context, with **Personal** deferred. This is documented shorthand, not a fourth
schema tier: "Corporate" = Meta-Tier + Standards-Tier together, "Project" = Project-Tier,
"Personal" has no schema tier and remains out of scope. See `core-model.md` §5.4.

## Tooling

- **CI**, for the first time: lint (ruff/black/mypy), both regression suites, and a
  wheel-install smoke test, all blocking on `tools-ci.yml`.
- **A real bug fixed**: `scs validate` (the `scs-tools` wrapper) silently reported "not
  installed" even when it was, because of a broken import left behind by an earlier
  refactor — every documented `scs new project; scs validate` workflow was affected. Fixed,
  along with several adjacent scaffolding and packaging defects found while verifying the
  fix (bad `relationships: null` in 28 SCD templates, dangling concept imports on the
  `minimal` project type, `scs add bundle`/`scs bundle list` not recognizing concept
  bundles, a wheel install missing its own rules and schemas entirely).
- **Version bump**: both `scs-tools` and `scs-validator` move to `0.5.0`, matching the spec
  version they implement. A related bug fixed in the same pass: a versioned bundle's
  manifest always recorded `validator_version: "0.1.0"`, regardless of what actually
  validated it — it now reads the real installed version.
- **`rules/v0.1.0/` and `rules/v0.3.0/` retired** — `rules/v0.5.0/` is the only rule set the
  validator ships.

## Migration

No automated `scs migrate` helper ships with 0.5.0 — a deliberate call at RFC-0001
acceptance, not an oversight: manual migration is cheap while 0.3 has one real consumer.
[`docs/MIGRATION-0.5.0.md`](docs/MIGRATION-0.5.0.md) is the full path, including the one step
that isn't mechanical (converting a flat concern list into real ontology structure), and a
trap worth knowing about: SCD content templates can carry an unrelated, free-text
`concerns:` field of their own, which renames to `topics:`, not `concept:`.

## Deferred, Not Forgotten

Cut from 0.5.0 deliberately, not silently dropped — see `ROADMAP.md`, "Beyond 0.5.0," for the
reasoning behind each:

- **Model-routing metadata** and **multi-author provenance** (workstream 4) — neither is
  blocking, and multi-author provenance was conditional from the start on single-source
  approval proving insufficient, which hasn't happened.
- **Publishing `scs-tools`/`scs-validator` to PyPI** — the packages are built, version-bumped,
  and verified; the publish itself waits for real demand from a `pip install`-without-a-clone
  user. Local editable installs cover current use today.
- **CDMO scaffolding** (`scs new project --ontology cdmo`, ISS-029) — the MCA half of this
  shipped (above); CDMO's concept bundles reference SCD content that was never actually
  authored (unlike MCA, there's no existing skeleton to adapt), so it needs real content
  written before the same `--ontology` support can extend to it.

## Governance

Through 0.5.0, the specification is maintained by Tim McCrimmon as sole maintainer; RFCs and
Discussions are informative, not gating. The transition to broader community governance is
deferred to 1.0, which is not scheduled by this release.

## Upgrading

See [`docs/MIGRATION-0.5.0.md`](docs/MIGRATION-0.5.0.md). The validator's own error messages
point here directly when they detect stale `concern` terminology.
