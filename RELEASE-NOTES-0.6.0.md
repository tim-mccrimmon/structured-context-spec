# SCS 0.6.0 Release Notes

**Released:** 2026-10-19 &nbsp;|&nbsp; **Previous stable:** 0.5.0

---

SCS 0.6.0 is a **breaking change**, expected pre-1.0 under semver. If you have 0.5.0 content,
see [`docs/MIGRATION-0.6.0.md`](docs/MIGRATION-0.6.0.md) before upgrading.

## Theme

**Governance context that a runtime can deliver as-is.** 0.5.0 made the domain model
explicit. 0.6.0 separates organization-wide governance from project governance, removes
standards text from SCS entirely, and adds a compile step that turns a governance bundle into
one small, deterministic file a gateway or agent runtime can inject with every request and
identify by hash.

## What's New

### Two independent governance bundles

- A **Domain bundle** holds an organization's governance, the rules that apply to all of its
  work. Deployments often call it the Global or organization bundle; it is the same bundle
  type described for a different audience. It pins the published meta bundle and imports
  concept bundles.
- A **Project bundle** holds one project's governance. It imports concept bundles (or lists
  project SCDs) directly, and MUST NOT import meta, domain, standards, or other project
  bundles.

The two are compiled separately and applied side by side. A Project bundle no longer imports
the Domain bundle, so neither has to be re-released when the other changes. An industry
ontology (software development, medical-device CDMO, merchant cash advance) is the template
an organization's Domain bundle is scaffolded from; the organization's approved copy is
its own. See [`spec/0.6/bundle-format.md`](spec/0.6/bundle-format.md).

### Standards become citations

Standards bundles and the Standards tier are deprecated. A standard now appears in SCS only
as a **citation reference**, `std:<standard>[:<edition>][#<clause>]`, such as
`std:iso-13485:2016#7.3.9`. SCDs carry them in `cites`, and `satisfies` relationships and
domain-ontology concepts target them. A citation never carries standard text.

Two observations drove this. The text of most standards is licensed to the adopter, not to
the specification or a vendor. And the authoritative interpretation of a standard is the
adopter's own quality system; SCS holds that interpretation as rules and keeps the standard as
the reference. Where an adopter wants AI systems to consult a standard's full text, that
belongs in retrieval, not in governance. See [`spec/0.6/citations.md`](spec/0.6/citations.md).

### The runtime artifact and `scs compile`

New normative document: [`spec/0.6/runtime-artifact.md`](spec/0.6/runtime-artifact.md).
`scs compile` turns a Domain or Project bundle into a runtime artifact holding three kinds of
SCD content, and nothing else:

- **Prohibitions** (`content.prohibitions`): tools or practices that are forbidden. They are
  binary by construction: the author states only the subject, the compiler writes
  `Prohibited: <subject>.`, and validation rejects a subject containing a qualifier such as
  "unless", "except", or "where possible". Prohibitions are listed first.
- **Directives** (`content.directives`): rules an agent is expected to follow.
- **Facts** (`content.facts`): statements an agent should know, such as what the company does
  and where its records are kept. They compile into a separate `facts` list.

Every rule and fact has a stable identifier, `<bundle>/<scd-name>/<id>`, unique across Domain
and Project artifacts, so an agent can name the rule it applied and an audit log can record
it. The artifact begins with a self-identification rule, so asking an agent which governance
is active returns each bundle and its version.

The artifact contains no timestamps, authors, or paths: the same approved source always
produces the same bytes and the same SHA-256. Compiling a `DRAFT` bundle requires
`--allow-draft` and yields a version of `DRAFT+<digest>`, so two different drafts never
report the same version.

### The meta bundle is published with the specification

`bundle:meta:0.6.0` lives at `meta/` and ships inside `scs-validator`, so a Domain bundle's
meta import resolves wherever the tools are installed. Its directives tell an agent how
Domain and Project rules combine, how to treat facts, to name the rule behind any refusal or
change, and that a citation does not contain the cited standard's text.

### The Project tier, clarified

Organization-wide rules in a Domain bundle are `scd:project:*` SCDs. The tier identifies who
authors an SCD (the adopter), not where it applies; scope comes from the bundle that
includes it. The name is kept so SCD identifiers stay stable. See
[`spec/0.6/project-tier.md`](spec/0.6/project-tier.md) §1 and ISSUES.md ISS-041.

## Tooling

- **`scs new domain`** scaffolds an organization's Domain workspace from an ontology. Every
  Domain workspace gets `company` (facts) and `prohibited` concept bundles. For the sdlc and
  cdmo ontologies it uses a **Global profile**: only SCDs that state organization-wide policy
  or standards. SCDs that describe one system (problem definition, system context, threat
  model, risk register, cutover) are scaffolded only by `scs new project`.
- **`scs new project`** scaffolds the Project bundle and its concept bundles only; it no
  longer generates meta, standards, or domain bundles.
- **`--ontology cdmo`**: the medical-device CDMO ontology is now scaffoldable, with one
  skeleton template for each of its 48 SCD slots. Each skeleton says whether its content
  compiles as directives, facts, or prohibitions.
- **`scs compile`**: new command (needs `scs-tools[validator]`).
- **Validation resolves the whole bundle tree** for every bundle type, checking import types,
  version mismatches, and cycles. An unresolved import is now an error; an unresolved SCD
  stays a warning, since an ontology template may list SCD slots not yet written.
- **`scs bundle validate` and `scs bundle version`** find a workspace's Domain or Project
  bundle. `scs add bundle <domain>` now explains that a Domain bundle is its own workspace.
- `scs bundle version` no longer adds a hard-coded co-author trailer to the commit it creates.
- **Version bump**: `scs-tools` and `scs-validator` move to `0.6.0`, and the validator ships
  `rules/v0.6.0/`.

## Migration

[`docs/MIGRATION-0.6.0.md`](docs/MIGRATION-0.6.0.md) covers splitting organization rules from
project context, rewriting Project bundle imports, pinning the meta bundle, replacing
standards with citations, and writing directives, prohibitions, and facts for compilation.
As in 0.5.0, there is no automated migration helper. `scd:standards:` references and
`type: standards` bundles still validate in 0.6.0, with deprecation warnings.

## Deferred, Not Forgotten

- **Delivering artifacts at runtime.** SCS defines the artifact format; how a runtime stores,
  selects, and injects artifacts is outside the specification.
- **Renaming the Project tier** is an open question (ISS-041), to revisit only if the name
  proves confusing in practice.
- **Publishing to PyPI** still waits for demand from users installing without a clone.
- **Open documentation and example issues** (ISS-030, ISS-031, ISS-038, ISS-040) are tracked
  in `ISSUES.md` and do not affect the 0.6.0 format.

## Governance

The specification is maintained by Tim McCrimmon as sole maintainer. The changes in 0.6.0
were decided by the maintainer without an RFC; the design and its reasoning are recorded in
the specification documents and the migration guide. RFCs and Discussions remain
informative, not gating, until the transition to community governance planned for 1.0.

## Upgrading

See [`docs/MIGRATION-0.6.0.md`](docs/MIGRATION-0.6.0.md) and the worked example in
[`examples/two-tier-governance/`](examples/two-tier-governance/): a Domain and a Project
bundle with their compiled artifacts.
