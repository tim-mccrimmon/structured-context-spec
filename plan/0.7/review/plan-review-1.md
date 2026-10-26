# Plan review 1: SCS 0.7.0 plan vs RFC 0002

- **Date**: 2026-10-25
- **Inputs read**: `rfcs/RFC-0002-agent-mediated-scs.md`; `plan/0.7/README.md`, `01`-`07`. Nothing else
  (no code, `survey/`, `spec/`, `ISSUES.md`).
- **Format**: ID, severity (blocking / should-fix / minor), location (plan file + heading; RFC
  section), problem, fix.

---

## 1. Coverage: RFC MUST/SHOULD with no home in a WP or acceptance criterion

**R-01** [blocking] `06` WP-00, WP-14 / RFC §11 "Content digest"
The digest algorithm (inputs: versioned manifest, every SCD, each import's `content_digest`;
canonical JSON with sorted keys, no whitespace, non-ASCII unescaped; order manifest, SCDs by id,
imports by id; `sha256:<hex>`; comment/format edits do not change it) has no acceptance criterion.
WP-00 accepts on "CI green" only. Digests written into released manifests are permanent, so a wrong
canonicalization is a format freeze.
Fix: add to WP-00 Accept: "Test vectors in `tests/digest/` (committed, with expected digests
computed independently of the implementation) cover: reordered YAML keys, changed comments and
whitespace (same digest), one changed field value (different digest), non-ASCII text, a bundle with
two pinned imports, and SCD ordering by id. `validation_passed: false` is recorded under
`--no-validate`; `approval_status` reflects the actual run."

**R-02** [blocking] `06` WP-10 Accept / RFC §6.1, §6.5, §6.6, §6.7, §6.8
WP-10 Accept covers §6.1-6.4 and part of §6.8 only. Missing: §6.5 MUST present validation errors in
plain language before proposing fixes; §6.6 SHOULD present `scs bundle diff` summary before
versioning; §6.7 MUST record every advisory finding decision, SHOULD show open findings before
versioning; §6.8 SHOULD give placement advice after compile. Also, a "logging `scs` shim" cannot
observe SCD content edits, which D-08 makes direct file writes by the skill, so "dry run before
every write" and "no writes outside the repo" are untestable for the most common write.
Fix: WP-10 Accept: "Each scripted conversation runs in a temp Domain repo with filesystem
snapshots before and after each turn. Assertions: (a) every filesystem change is preceded by an
assistant turn listing that path and a user turn confirming; (b) no file outside the repo root
changes; (c) after a failing validate, the next assistant turn names each error before any fix;
(d) before every `bundle version`, a `bundle diff` call and its summary appear; (e) every finding
raised has a matching `review_findings` entry via `scs intake record-finding`; (f) after every
compile, the turn names a placement from the guide."

**R-03** [should-fix] `06` WP-10 / RFC §8, §5
§8 MUSTs have no home: items drafted from a document MUST carry `derived_from` naming it (SHOULD
carry a locator); MUST NOT copy standard text into SCDs; source documents MUST NOT be sent anywhere
but the user's AI client. §5 SHOULD (every drafted item records `derived_from`) likewise.
Fix: WP-10 Accept: "Drafting conversation from a fixture source document yields SCD items each
with a `derived_from.source` resolving to `source_documents[].id`, and `locator` on each." Add an
engine test (WP-05): no `scs` command opens a network connection (run under a socket-blocking
fixture). Add a draft-skill instruction plus a test that the fixture's verbatim standard
paragraph does not appear in any SCD.

**R-04** [should-fix] `06` WP-07, WP-10 / RFC §12
Advisory-review rules have no criteria: the four `kind` values; MUST NOT block an operation; MUST
NOT change content without confirmation; MUST name the SCD item and citation; decision is one of
`changed`/`kept` (with rationale)/`deferred` plus who and when; deferred SHOULD be raised again
before the next version.
Fix: WP-07 Accept adds schema tests: `kind` outside the four values fails; `decision: kept` without
`rationale` fails; missing `decided_by`/`decided_at` fails. WP-10 Accept adds: a fixture workspace
with a seeded framework conflict produces a finding naming the item id and the `std:` cite; the
user declining leaves content unchanged and versioning proceeds; a `deferred` finding is raised
again in the next version conversation.

**R-05** [should-fix] `06` WP-07, WP-10 / RFC §4
No criterion for: the first intake step MUST establish the Domain repository; a new repo's Domain
workspace MUST be built before any Project; answers MUST be saved to `intake.yaml` at the
workspace root. WP-07 does not say the validator schema-checks `intake.yaml` (Validation Rules:
"when present, MUST validate").
Fix: WP-07 Accept: "`scs-validate` reports a schema error for an invalid `intake.yaml` in each
workspace." WP-10 Accept: "In the solo and CDMO scripted intakes, the first engine call is
`scs new domain` or a check of an existing repo; no `scs new project` precedes Domain scaffolding;
`domain/intake.yaml` and `projects/<name>/intake.yaml` exist and validate at the end."

**R-06** [should-fix] `01` Boundary, `06` WP-10 / RFC §1, §10
"MUST NOT present itself as providing" out-of-scope functions and "SCS tools MUST NOT [place or
transform renderings]" have no criterion. `01` states it in prose only.
Fix: WP-10 Accept: "Scripted requests to deploy to Claude Enterprise, set up multi-reviewer
approval, or host a registry each get a reply stating it is outside SCS, with no engine call."
WP-05 Accept: "No command accepts an output path outside the repository root; tested for `compile`."

**R-07** [should-fix] `06` WP-06 Accept / RFC §3, §6.2, Validation Rules
"Approver suggestion" and "`--author` required" are in WP-06 scope but not in Accept ("as WP-05,
plus git failure").
Fix: WP-06 Accept: "`bundle version --json` without `--approved-by` exits non-zero with
`VERSION_APPROVER_REQUIRED`, writes nothing, and returns the git email only in
`diagnostics[].suggestion`; with git `user.email` set and no `--approved-by`, no manifest contains
that email. Same for `new`/`add` without `--author`."

**R-08** [should-fix] `06` WP-07, WP-08 / RFC §3
Machine-mode MUSTs (envelope only on stdout, no prompts, `--dry-run` parity) are tested for WP-05/06
commands only. `scs intake set|record-finding` (WP-07) and `scs bundle diff` (WP-08) have no such
criterion. `scs --version` (used by skills per D-27) has no `--json` row in `04` Commands.
Fix: in `06` preamble, define "machine-mode conformance" once (the WP-05 Accept list) and require
it in WP-06, WP-07, WP-08. Add `scs --version --json` to the `04` Commands table and to WP-05.

**R-09** [should-fix] `06` WP-08 / RFC §7
RFC §7 requires: SCDs added, removed, **or retired**; items added/removed/changed; **citations
added or removed**; imports re-pinned. WP-08 omits retired and citations. The `<bundle>` positional
and the defaults for `--from`/`--to` are missing from `04` and WP-08.
Fix: WP-08 scope and Accept list all six change kinds from §7, each with a golden test. Specify:
`scs bundle diff <bundle> [--from V] [--to V|working]`; default `--from` = latest version,
`--to` = `working`. See also R-50 (retired vs removed).

**R-10** [should-fix] `06` WP-03 Accept / RFC §9 "Agent instructions", "Reserved directories",
naming
The MUST content of the agent instructions file (repo manages SCS context for one named Domain
and its Projects; work limited to the five operations; application work belongs elsewhere) is not
checked. The SHOULD `<domain-name>-context` name is in no WP. "Scaffold does not create reserved
dirs" is not checked.
Fix: WP-03 Accept: "Generated `AGENTS.md` contains the Domain name, the five operations, and an
application-work exclusion (asserted by test); `CLAUDE.md` references `AGENTS.md`; `scs new domain
NAME` defaults the directory to `NAME-context`; no `plan/`, `test-plan/`, `qa/` is created."

**R-11** [should-fix] `02` Components (Resolver row), `06` WP-04, WP-14 / RFC §9 "Reserved
directories"
`02` records that the resolver indexes reserved directories and assigns WP-14/WP-04, but neither
WP's text or Accept mentions it. RFC: "the validator and compiler do not read them."
Fix: add to WP-14 scope and Accept: "An SCD or bundle placed under `plan/`, `test-plan/`, or `qa/`
is not indexed, not resolved, not compiled, and produces no diagnostic (test for each)."

**R-12** [minor] `06` WP-04 Accept / RFC Validation Rules (repo mode)
Repo-mode error for zero or more than one Domain workspace, and "reserved dirs reported in no mode",
are in `04` but not in WP-04 Accept. "More than one Domain workspace" is undefined (only one
`domain/` can exist).
Fix: define as "more than one workspace whose `.scs/config bundle_type` is `domain`". Add pass/fail
tests for zero, one, two, and reserved-dir content under `--strict`.

**R-13** [should-fix] `03` Artifacts (Version manifest), `06` WP-04 / RFC §11 Verification, Schema
Changes, Migration Guide
A manifest with no `content_digest` (pre-0.7) MUST produce a warning, while 0.7-written manifests
MUST have it. The D-36 manifest schema cannot express "required when written by 0.7 tools" unless
the manifest records its writer. No WP owns the pre-0.7 warning.
Fix: WP-04: manifest schema uses `if tools_version >= 0.7 then required: [content_digest]` (or
equivalent marker); validator emits `MANIFEST_UNVERIFIABLE` warning for pre-0.7 manifests. Accept:
a 0.6 fixture manifest gives exactly that warning; a 0.7 manifest missing the field fails schema.

**R-14** [minor] `06` WP-14 Accept / RFC §11 "There is no override"
No test that compile has no bypass for a digest mismatch.
Fix: Accept: "`compile` on a mismatched versioned bundle fails with every flag combination,
including `--force`."

**R-15** [should-fix] `06` WP-09 / RFC §10
WP-09 does not name the services covered ("most widely used" in the RFC is not checkable) and omits
the SHOULD that the guide recommend renderings keep bundle id, version, and digest.
Fix: WP-09 names the service list (decided in D-24, e.g. Claude Enterprise, Claude Code, Cursor,
Copilot, ChatGPT Enterprise). Accept: "one page per listed service; each page has `checked:` date,
a source URL per claim, separate Domain and Project placement, and the id/version/digest
recommendation."

**R-16** [minor] `06` (none) / RFC Migration Guide
Legacy `v<version>` tags "keep working" and pre-0.7 versions "validate with a warning" have no
test.
Fix: add to WP-14 Accept a 0.6 fixture repo with `v1.0.0` tags that validates (warnings only) and
compiles.

**R-17** [minor] `01` Starting point, `06` WP-00 / RFC Appendix step 1
ISS-042/043/044 are assumed fixed; no regression criterion protects them through the 0.7 rework
(WP-03, WP-06, WP-14 all touch versioning).
Fix: WP-00 Accept: "regression tests for ISS-042 (both CLIs report package version), ISS-043 (two
concept bundles versioned at the same version keep separate manifests), ISS-044 are present and
green."

---

## 2. Contradictions

**R-18** [should-fix] `04` Commands (`bundle version` row) / RFC Appendix step 1, Migration Guide
RFC removes the git-config approver default from `scs bundle version` in all modes ("no longer
takes the approver from `git config`; pass `--approved-by` explicitly"). Plan requires
`--approved-by` "in machine mode" only, leaving human mode free to default. Not flagged.
Fix: `04` row: "`--approved-by` required in every mode." Add to WP-06 Accept. If human-mode
default is intended, add a D-item marked RFC.

**R-19** [should-fix] `04` Exit codes / RFC §3
RFC: `4` = file error. Plan: `4` = "Schema directory not found". Narrowing unflagged; missing input
files, unreadable SCDs, and write failures have no specified code.
Fix: `4` = "File error (missing, unreadable, or unwritable file, including schema directory)".

**R-20** [should-fix] `04` Envelope / RFC §3
Plan envelope differs from RFC: `suggestion` is a string (RFC: object keyed by field,
`{"approved_by": ...}`); `changes` git entries use `ref` instead of `path` (D-09 adds the actions
but not the shape); paths are repo-relative (RFC example is workspace-relative). The example itself
pairs snapshot `domain-bundle-v1.0.0.yaml` with tag `domain/company-v1.0.0` (different bundle
names).
Fix: publish `schema/cli/envelope-schema.json` in WP-05 (envelope, `changes[]` with `action` enum
`create|modify|delete|git-init|git-commit|git-tag`, `path` or `ref`, `diagnostics[]` with
`suggestion` as object). Keep RFC's object form. Fix the example. WP-05 Accept: every test envelope
validates against it.

**R-21** [should-fix] `07` D-04, `03` layout / RFC §9 layout, RFC header "no breaking changes"
D-04 moves the ontology manifest to `ontology/` in every workspace, changing the RFC §9 layout and
existing 0.6 workspaces, but is not marked RFC and does not say whether tools still read the old
location.
Fix: mark D-04 "RFC"; add "tools read `domain/domain-manifest.yaml` (0.6 location) with a
deprecation warning" and a WP-03 test for it.

**R-22** [minor] `03` Artifacts (Version manifest, Runtime artifact) / RFC Schema Changes, §11
Unflagged additions: `content_inputs` in manifests; `scs_runtime: "0.7"` in the artifact. RFC adds
only `source_digest` and says it does not disturb runtime-artifact §3.5 stability. A runtime
version bump may affect consumers keyed on `scs_runtime`.
Fix: record both as D-items; state whether `scs_runtime` changes and why.

**R-23** [should-fix] `07` D-15, `05` Failure handling / RFC §9 "Versioning"
The plan retains a `--no-git` mode ("`--force --no-git` rewrites", "in git mode"). RFC: "Bundle
versions MUST be recorded as git tags." No decision covers whether `--no-git` survives in 0.7.
Fix: add D-38: remove `--no-git` from `bundle version`, or keep it as non-conforming and have the
validator warn on manifests with no matching tag.

**R-24** [should-fix] `04` Commands (`compile`), `07` D-11, `06` WP-03 and WP-05 / RFC §9 "Compiled
output"
`04`/D-11 say compile writes `dist/` "with `--json`"; WP-03 says "compile default to `dist/`";
WP-05 says "compile with `--json` writes `dist/`". Human-mode output target is ambiguous and two
WPs own the same change.
Fix: one rule: "`scs compile` writes `dist/<bundle-name>-<version>.yaml` in every mode; `--stdout`
prints instead (human mode only)." Assign to WP-05 only; drop it from WP-03.

**R-25** [should-fix] `06` WP-08 vs Dependency graph vs Parallel groups
WP-08 text: depends WP-06, WP-14. Mermaid: WP-06 to WP-08 only (no WP-14 edge). Groups: WP-08 in D,
parallel with WP-06.
Fix: add `WP14 --> WP08` to the graph; move WP-08 to a group after WP-06, or drop the WP-06
dependency if diff does not need machine-mode `version`.

**R-26** [should-fix] `06` WP-09, Parallel groups A / `07` D-24
WP-09 "Depends: D-24 only", but D-24 is decided in WP-01; group A starts WP-09 "now" and the graph
has no WP-01 edge.
Fix: add `WP01 --> WP09` (or decide D-24 now and record it), and move WP-09 to group B.

**R-27** [minor] `06` Parallel groups
Group E omits WP-11a (a WP-10 dependency). Group D omits WP-14 (a WP-06 dependency). Group F puts
WP-13 alongside WP-11 although WP-13 depends on WP-11. Group C "WP-05 (lead), then WP-03" implies
WP-03 waits on WP-05, which the graph does not say. "Lead ship" is undefined.
Fix: regenerate the groups table from the graph; define "lead" or delete it.

**R-28** [minor] `06` WP "Depends" lines vs `07` "Blocking" column
Disagreements: WP-03 omits D-01, D-21, D-23 (D-23 is cited in its body); WP-04 omits D-02; WP-06
lists no D-items though D-01, D-02, D-08, D-13 block it; WP-07 omits D-20, D-32; WP-10 omits D-08,
D-19, D-30. An agent reading its WP misses decisions that bind it.
Fix: make section 7's Blocking column the single source; each WP Depends line lists exactly the
D-items whose Blocking column names it.

**R-29** [minor] `06` Critical path
Lists WP-00 and WP-01 in sequence (they are parallel roots); omits WP-14, which WP-06 depends on;
omits the WP-07 maintainer schema-approval gate, which also precedes WP-10.
Fix: "Critical path: max(WP-00, WP-01) -> WP-04 -> WP-05 -> WP-03 -> WP-06 -> WP-10 -> ...;
parallel near-critical: WP-01 -> WP-14 -> WP-06; WP-07 + schema approval -> WP-10."

**R-30** [should-fix] `06` WP-04 Depends / `03` Version manifest row
WP-04 writes the version manifest schema, but the manifest fields (`content_digest`,
`content_inputs`) come from WP-00's uncommitted code. WP-04 does not depend on WP-00.
Fix: add `WP00 --> WP04`.

**R-31** [minor] `07` D-18 vs D-20
D-20 defines "error in strict" as warning with exit 2; D-18 says "Warning, error under strict"
without saying which.
Fix: D-18: "Warning; exit 2 under `--strict`," matching D-20.

**R-32** [minor] `05` Bundle states / RFC §11 "In the artifact"
The state diagram allows Compiled only from Versioned; RFC defines `DRAFT` compiles
(`DRAFT+<digest>`, no `source_digest`).
Fix: add `Draft --> CompiledDraft: scs compile (no source_digest)`.

---

## 3. Ambiguity (an implementing agent would have to guess)

**R-33** [blocking] `05` Bundle states, `07` D-19, `04` Validator repository mode / RFC §11
Verification
SCDs are not snapshotted; the digest is recomputed from the working tree. Once a concept is edited
for its next version, every earlier version of it mismatches permanently. The plan does not say
which manifests the validator verifies: all historical manifests (CI red forever after the first
edit), only the latest per bundle, or only versions pinned by a working bundle. `05` says Drifted
returns to Versioned "at a new version" without saying the old version stops being checked.
Fix: add D-39 and state it in `05`/WP-04/WP-14: e.g. "Repo-mode validation verifies, per bundle,
the version pinned by the working root bundle(s); older versions are verified only on explicit
request (`scs-validate --version V`), against the tagged commit's content." Accept test: edit an
SCD, version again, CI is green.

**R-34** [blocking] `06` WP-08 / RFC §7
`scs bundle diff --from <version>` needs the old SCD content, which exists only at the git tag
(SCDs are not snapshotted). The plan does not say diff reads from git, or what happens without
git.
Fix: WP-08: "Old-version content is read from the tagged commit (`git show <tag>:<path>`);
`--from` with no tag is an error `DIFF_VERSION_NOT_FOUND`." Make WP-08 depend on the tag format
decision (D-02/D-03).

**R-35** [blocking] `05` Failure handling, `04` `changes` (D-09) / RFC §9 "every artifact can be
rebuilt from its tag", §11
The commit made by `scs bundle version` is unspecified: does it commit the whole working tree,
only the snapshot and manifest, or refuse on a dirty tree? If uncommitted SCD edits are left out,
the tag does not contain the content the digest covers and the artifact cannot be rebuilt from
the tag.
Fix: add D-40: "`bundle version` refuses with `VERSION_DIRTY_TREE` if any file in the digest inputs
is uncommitted, or commits exactly the digest inputs plus snapshot and manifest." WP-06 Accept: the
tagged commit's files recompute to the manifest's `content_digest`.

**R-36** [blocking] `04` Commands / RFC §9
In a multi-workspace repo, the plan does not say how a command selects its workspace (cwd,
`--workspace` flag, bundle path) or what paths in `changes`/`diagnostics` are relative to.
Agents will issue commands from the repo root.
Fix: `04`: "Commands resolve the workspace from `--workspace <domain|name>` or, if absent, the
nearest `.scs/config` above cwd; at repo root without `--workspace`, workspace-scoped commands fail
with `WORKSPACE_REQUIRED`. All envelope paths are POSIX, relative to the Domain repo root."

**R-37** [should-fix] `04` Commands (`validate` row), `06` WP-04 Accept / RFC §3
Unclear whether `scs-validate --json` emits the envelope (with the report in `result`) or the
existing report (`--output json`). WP-04 Accept says "validates against a published report
schema"; WP-05 puts `--json` on `validate`. The report schema's location is not in `03`.
Fix: "`scs-validate --output json` keeps the report format (schema `schema/validator/report-schema.json`,
owned by WP-04); `scs validate --json` and `scs-validate --json` emit the envelope with that report
in `result` unchanged and findings in `diagnostics`." Add the report schema to the `03` table.

**R-38** [should-fix] `03` Artifacts (Bundle snapshot) / RFC §9
Snapshot file name and location are unspecified (`04` example shows
`domain/bundles/domain-bundle-v1.0.0.yaml`); D-17 resolution and WP-08 depend on it.
Fix: add to `03`: "`<bundle-dir>/<bundle-name>-v<version>.yaml`, beside the manifest."

**R-39** [should-fix] `07` D-10, `06` WP-02, WP-04, WP-05
The diagnostic code registry is "in the spec" (WP-02) and "in rule YAML" (WP-04), and WP-05/06/07/14
each mint codes in parallel. No initial list exists, so codes will drift between spec and code.
Fix: one machine-readable `schema/diagnostics/codes.yaml` owned by WP-04; WP-02 renders the spec
table from it; CI checks every emitted code is registered. Seed it in `04` with codes the plan
already uses (`VERSION_APPROVER_REQUIRED`, `CONTENT_DIGEST_MISMATCH`, plus those added in R-13,
R-34-R-36).

**R-40** [should-fix] `06` WP-10, WP-11a, WP-13
"Each target chat client" and "a chat client" are undefined. WP-11a results, D-27, and WP-13 pass/fail
depend on the list.
Fix: name the clients in D-27 (e.g. Claude.ai, Claude Code, Cursor, Codex, Copilot, matching RFC
§2) and the one used for WP-13.

**R-41** [minor] `06` WP-03 / RFC §4 "Domain workspace MUST be built before any Project"
"Built" is undefined (scaffolded? versioned?) and the engine's enforcement is unstated.
Fix: "`scs new project` refuses with `DOMAIN_WORKSPACE_MISSING` unless `domain/.scs/config` exists."

**R-42** [minor] `04` Envelope / `07` D-06
Envelope `scs_version` means spec version or tools version? D-06 separates the two for
`.scs/config`.
Fix: envelope carries `scs_version` (spec) and `tools_version`.

---

## 4. Acceptance criteria quality

**R-43** [should-fix] WP-02 Accept
"A reviewer agent ... finds no contradiction" is not objective.
Rewrite: "`spec/0.7/rfc-0002-trace.md` lists every RFC 0002 MUST/SHOULD (numbered) with the spec
section that states it; the maintainer signs off the table; `grep -r 'spec/0.6\|0\.6\.0' spec/0.7
rfcs/RFC-0002*` returns only intentional historical references, listed in the trace file."

**R-44** [should-fix] WP-03 Accept
"Passes repository-mode validation in CI" requires a GitHub run and does not say strict; "tags
take the form" is a versioning behavior WP-03 does not own (see R-58).
Rewrite: "`scs new domain` then `scs new project a` then `scs-validate --strict` at repo root exits
0 locally; the generated workflow file runs that same command (asserted by test); D-04 legacy
location read; `.scs/config name` mismatch reported; reserved names refused at `scs add bundle`."

**R-45** [should-fix] WP-04 Accept
"Published report schema" has no path; "snapshot test of JSON shape" duplicates it.
Rewrite: per R-37, plus R-12 tests, plus "every diagnostic in the test corpus has a registered
`code`."

**R-46** [should-fix] WP-06 Accept
Rewrite to include R-07, R-35, and: "`bundle pin` updates exactly one import and appears in
`changes`; a failure injected after each of snapshot, manifest, commit, tag leaves the repo
byte-identical to before (four tests)."

**R-47** [should-fix] WP-07 Accept
Missing: tests for `scs intake` commands, `derived_from` resolution (warning loose, exit 2 strict),
`oneOf` (both keys fails), personal and project profile fixtures, role-only attribution (D-28).
"Maintainer approves the schema" is a gate, not a criterion of done.
Rewrite: add those tests; move approval to a named milestone "M-07 schema approved", shown in the
graph before WP-10.

**R-48** [minor] WP-08 Accept
"Byte-identical output" is good; add per R-09/R-34: one golden per §7 change kind including
retired and citations, and `--from` reading from the tag.

**R-49** [should-fix] WP-10 Accept
Scripted conversations against a model are non-deterministic; no model, run count, or pass rate
is set.
Rewrite: "Each scripted conversation runs N=5 times against <named model/client>; every run must
satisfy every assertion in R-02 (no pass-rate below 100% for MUSTs)." State whether a replay or
mock-model harness is used instead.

**R-50** [should-fix] WP-11a Accept
"A recorded result per client" has no fields.
Rewrite: "`docs/install-matrix.md` row per client in R-40: install method tried, success y/n,
network access to PyPI/GitHub, Python version, `scs --version --json` output, date."

**R-51** [should-fix] WP-13 Accept
"Completed with no CLI use and no spec reading; friction log compared" has no pass condition and
no independent check.
Rewrite: "Transcript and repo archived. Pass if: transcript has no user-typed `scs` command and no
spec link opened; `scs-validate --strict` at repo root exits 0; three bundles (Domain + two
Projects) each have a tag, a manifest with a user-named `approved_by`, and a `dist/` artifact whose
`source_digest` equals the manifest's `content_digest`; each workspace has a valid `intake.yaml`;
placement advice given per artifact; friction log has no unresolved blocker absent from WP-13a's
log."

**R-52** [should-fix] WP-13a, WP-15 (no Accept); WP-12 (no scope)
Rewrite: WP-13a Accept: "friction log committed at a named path with step, time, blocker per
entry." WP-15 Accept: "`mkdocs build --strict` passes; nav contains the 0.7 spec, migration guide,
placement guide; release notes list every ISS closed." WP-12: add one line, "when activated, must
meet RFC §2 (stdio only, no behavior beyond machine mode)."

**R-53** [should-fix] WP-14 Accept
"A test for each probe in `survey/cli-engine.md`" makes done depend on a working file outside the
plan.
Rewrite: list the probes inline (DRAFT import versioning, unpinned import versioning, rewrite of an
existing version, DRAFT-root compile with versioned imports, versioned bundle without manifest,
unpinned import resolution, digest-mismatch message content) with expected outcome for each.

**R-54** [minor] WP-05, WP-11 Accept
WP-05: add one test per exit code 0-5 (including 4 and 5). WP-11: add "`scs --version` and
`scs-validate --version` print 0.7.0; `pip install scs-validator==0.7.0` alone works."

---

## 5. Decisions in section 7

**R-55** [should-fix] D-08 / RFC §7, §6.1, §2 Layer 3
(a) "Retire = remove from the bundle's `scds`" makes retired indistinguishable from removed, but
RFC §7 diff reports them separately. (b) SCD edits as skill file writes bypass `--dry-run`, so
§6.1 relies on skill discipline with no engine record. (c) The MCP layer exists for clients
"without ... shell access"; with no engine write command they cannot edit SCDs at all.
Fix: either add `scs scd write <path> --from-file` and `scs scd retire <id>` (with `--dry-run`,
retire recorded as a status or in the manifest), or keep D-08 and amend RFC §7 to drop "retired"
and RFC §2 to note MCP cannot edit content in 0.7. Mark which.

**R-56** [should-fix] D-28 / RFC Summary, §6.2, Validation Rules (`approved_by`)
Role-only attribution "for `answered_by` and approvers" may extend to the version manifest's
`approved_by`, weakening the RFC's core claim ("what a named person approved").
Fix: limit role-only to `intake.yaml` (`answered_by`, `decided_by`, `approvers`); version manifest
`approval.approved_by` stays a person identifier. State it in D-28.

**R-57** [should-fix] D-01, D-19 / RFC UQ5, §6.2
RFC UQ5 leans toward per-workspace versioning ("fits agent use better"). D-01 recommends per
bundle, and D-19 adds a bottom-up cascade, so one Domain change may need several `bundle version`
calls. The plan does not decide whether one user-named approver in the conversation covers the
whole cascade or each call needs confirmation (§6.2 says "in the current conversation").
Fix: D-01 states the cascade cost and adds: "one confirmation naming the approver and listing all
bundles in the cascade covers that cascade; the skill passes the same `--approved-by` to each call."

**R-58** [should-fix] (missing decision) Ownership of `bundle version` code
WP-00, WP-03 (tags), WP-06 (machine mode, pin, cleanup), WP-14 (guards) all change versioning; WP-03
and WP-14 can run concurrently. Not a section 7 item, but agents will collide.
Fix: assign tag/manifest naming to WP-14 (or WP-06), remove it from WP-03; record file ownership per
WP in `06`.

**R-59** [minor] D-15 / `05` Failure handling
D-15 limits `--force` to "clears leftovers of a failed run", while WP-06 makes versioning clean up
after itself. When `--force` applies is unclear.
Fix: drop `--force` from `bundle version`, or define the leftover case it handles.

**R-60** [minor] D-24 / RFC §10
Skills shipping a copy of the placement guide can drift from the "checked against current docs"
requirement.
Fix: the copy carries its `checked:` date and the skill tells the user that date when advising.

**R-61** [minor] D-32 / RFC Motivation ("bundle records ... what was flagged ... and what the
approver decided")
With `intake.yaml` outside the digest, a version has no link to the review record in force when it
was approved.
Fix: manifest records the git commit (or a hash of `intake.yaml`) at versioning time; or document
the gap in the spec, as D-32 proposes.

**R-62** [minor] D-27
Fallback "install from the GitHub tag" fails the same way as PyPI in sandboxes without network.
Fix: include the RFC UQ3 option of a skill-bundled wheel as the second fallback.

**R-63** [minor] Missing decisions summary
Decisions an agent will hit with no D-item: `--no-git` (R-23), historical-version verification
scope (R-33), diff source of old content (R-34), version commit scope (R-35), workspace selection
and path base (R-36), snapshot naming (R-38), cascade approval (R-57), how skills declare and check
a minimum engine version (D-27 mentions it without a mechanism).
Fix: add D-38 to D-45 with these.

---

## 6. Sequencing risk

**R-64** [blocking] `06` WP-11, WP-13
Acceptance (WP-13) runs after release (WP-11) publishes 0.7.0 to PyPI. PyPI versions cannot be
re-uploaded, so a failed acceptance ships anyway or needs 0.7.1.
Fix: WP-11 split: WP-11-rc publishes `0.7.0rcN` to PyPI; WP-13 runs on the rc; WP-11-final
depends on WP-13 pass.

**R-65** [should-fix] `06` WP-01
One maintainer must decide 37 items before WP-02/03/04/05/07/14 start. Group E decisions (D-21 to
D-27, D-31, D-33) do not block engine work.
Fix: split WP-01a (sections A, B, C, D-36, D-33: blocks engine) and WP-01b (rest), so WP-04/14
start sooner.

**R-66** [should-fix] `06` WP-02 vs WP-04/05/07
WP-02 writes the spec (including the code registry and agent-interface text) in parallel with the
WPs that define codes, the envelope, and the intake schema. The spec will be written against
undecided shapes.
Fix: WP-02 in two parts: WP-02a (layout, scope, terminology) after WP-01; WP-02b (envelope, codes,
intake, `derived_from`) after WP-05, WP-07 schema approval.

**R-67** [should-fix] `06` WP-11a
WP-11a publishes "0.7 pre-releases" before any 0.7 engine work exists and before WP-11 fixes the
dependency set (validator as hard dependency). The D-27 result may not hold for the shipped
packages.
Fix: WP-11a tests installability with the final package layout (both packages, hard dependency)
early, and is re-run against the rc in WP-11-rc.

**R-68** [minor] `06` WP-07 / D-34
The maintainer's schema approval gate is on the path to WP-10 but not in the graph.
Fix: add a milestone node `M07[Schema approved]` between WP-07 and WP-10.

---

## Verdict

**Not ready for maintainer decisions as written.** Section 7 is complete for the questions it asks,
but several decisions an agent will hit early are missing: which versions the validator verifies
after drift (R-33), where diff reads old content (R-34), what a version commit contains (R-35), and
how commands choose a workspace (R-36). Without them, WP-04, WP-06, WP-08, and WP-14 cannot be
built without guessing. The digest format has no conformance criterion (R-01). WP-10, where RFC §4,
§6, §8, and §12 MUSTs land, cannot be verified as written (R-02). Release precedes acceptance
(R-64). Fix the seven blocking items and add D-38 to D-45 (R-63); then section 7 is ready for
decisions. The should-fix items can follow in the same revision.

| Severity | Count |
|---|---|
| Blocking | 7 |
| Should-fix | 41 |
| Minor | 20 |
