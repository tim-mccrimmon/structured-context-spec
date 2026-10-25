# SCS Roadmap

Current stable: **0.6.0** (tagged `v0.6.0`, 2026-10-19). In development: **0.7.0**, on branch
`0.7-dev`.

Granular backlog: `ISSUES.md`. Design proposals: `rfcs/`.

## Previous releases

- **0.5.0:** the Domain Ontology replaced "concerns" (RFC 0001); structured context reframed
  for any AI actor; runtime decisions on immutability, versioning, and drift. See
  `RELEASE-0.5.0.md`.
- **0.6.0:** Domain (Global) and Project bundles as independent trees; standards as citations
  only; prohibitions, directives, and facts compiled into a deterministic runtime artifact by
  `scs compile`; the packaged meta bundle. See `RELEASE-NOTES-0.6.0.md`.

## SCS 0.7.0: theme

**Approved, versioned context as the source of truth for AI, produced through conversation.**
Through 0.6.0, using SCS means learning the spec. 0.7.0 makes an AI assistant the intended way
to create, maintain, validate, version, and compile bundles, with the spec as the authority,
the validator as the gate, and a named person approving every version. It also makes versioned
bundles verifiably immutable.

Design: `rfcs/RFC-0002-agent-mediated-scs.md`, accepted 2026-10-25. 0.7.0 is additive: no
breaking changes to SCDs or bundles.

**Scope.** SCS ends at a validated, versioned bundle and its compiled artifact. Placing
artifacts where AI services read them, multi-user review and approval workflows, registries,
hosting, and runtime serving stay outside SCS.

## Workstreams

In the RFC's implementation order. Each is usable on its own.

### 1. Hardening

Make the lifecycle dependable before an agent drives it.

- ISS-042: `scs --version` reports the wrong version
- ISS-043: version manifests and tags collide when several bundles share a version
- ISS-044: cdmo templates carry a misleading profile header
- ISS-045: versioned bundles are not verifiably immutable (content digest, verified by the
  validator and compiler, carried in the artifact)
- ISS-047: no approver taken silently from `git config`

### 2. Domain repositories (ISS-048)

One git repository per Domain, holding the Domain workspace and its Projects, with agent
instructions and a CI workflow. A `personal` Domain profile for individual developers.

### 3. Machine mode (ISS-049)

`--json` and `--dry-run` across the CLI, a single result envelope, no prompts.

### 4. Intake, provenance, and review findings (ISS-050)

The intake record schema, item-level `derived_from`, and recorded decisions on advisory review
findings.

### 5. Agent Skills (ISS-051)

The primary interface: intake, draft, review, validate, version, compile, and explain, in the
open Agent Skills format.

### 6. Change summary (ISS-052)

`scs bundle diff`: a deterministic summary of what an approver is approving.

### 7. Placement guide (ISS-053)

Non-normative docs on where Domain and Project artifacts typically go for common AI services.

### 8. Release engineering

- Publish `scs-tools` and `scs-validator` to PyPI at 0.7.0. PyPI currently holds `scs-tools`
  0.1.0 and no `scs-validator`, so `pip install` from PyPI does not give a working toolchain.
  Skills running in hosted chat sandboxes depend on a working `pip install` (RFC 0002,
  Unresolved Question 3). This revisits the publish deferred in ISS-014.
- GitHub releases for each tag, starting with `v0.6.0`.

### 9. MCP server (ISS-054)

A local stdio adapter over the engine. Lowest priority; started when there is demand.

### 10. Acceptance (ISS-055)

Onboard Omarchy entirely through a chat client using the skills, compared against a baseline
run with the 0.6 tools.

## Governance

The specification is maintained by Tim McCrimmon as sole maintainer. RFCs and Discussions
inform decisions; the maintainer may shorten an RFC's comment period, as was done for RFC 0002.
The transition to broader community governance is deferred to 1.0, which this roadmap does not
schedule.

## Beyond 0.7.0

Not scheduled:

- **Review profiles** (RFC 0003, stub): declarative, citable checks per framework (for example
  CHAI, HIPAA, ISO 13485) that structure the advisory review.
- **Model-routing metadata** (ISS-010): routing is runtime behavior, kept out of scope for now.
- **Multi-author provenance** (ISS-011): conditional on single-source approval proving
  insufficient. Multi-user approval workflows are outside SCS under RFC 0002.
- Carried from the 0.3 roadmap: a domain registry or marketplace; expert-authored domains
  (legal, clinical, financial); cross-domain dependency management; a public working group.

Resolved by 0.7.0: the **personal tier** deferred since 0.5.0 becomes the personal Domain
(RFC 0002).
