# Plan review 2: SCS 0.7.0 plan rev 2 vs RFC 0002

- **Date**: 2026-10-25
- **Inputs read**: `rfcs/RFC-0002-agent-mediated-scs.md`; `plan/0.7/README.md`, `01`-`07`;
  `review/plan-review-1.md`, `review/plan-review-1-disposition.md`. Nothing else.
- **Format**: R2-nn, severity (blocking / should-fix / minor), location, problem, fix.

---

## 1. Disposition check (review 1 findings not fully resolved)

All 68 findings have a landing place. The ones below are claimed resolved but are only partly
resolved in the plan text. Others check out.

| R-1 | Status | Gap | Covered by |
|---|---|---|---|
| R-01 | Partial | WP-00 Accept has `validation_passed: false` but drops "`approval_status` reflects the actual run" | R2-28 |
| R-04 | Partial | WP-10 (h) omits "the finding names the SCD item id and the `std:` cite" (RFC §12 MUST) | R2-28 |
| R-10, R-44 | Partial | WP-03 Accept omits the `NAME-context` default and "reserved names refused at `scs add bundle`"; the second has no owner anywhere | R2-20 |
| R-13 | Partial | D-49 keys on `tools_version >= 0.7`: rc/dev builds compare lower; deleting `tools_version` and `content_digest` downgrades a 0.7 manifest to a warning | R2-02, R2-15 |
| R-28, R-65 | Partial | D-33 stays in section E (WP-01b) but blocks WP-04, which waits only for WP-01a | R2-05 |
| R-33 | Partial | D-39 never verifies roots or any bundle that nothing pins | R2-01 |
| R-34 | Partial | D-41 has no first-version or legacy-tag case, so WP-10 (g) fails on every first version | R2-12 |
| R-35 | Partial | D-40 "every SCD in the tree" contradicts "exactly the digest inputs"; rebuilding from the tag is asserted, not tested | R2-03, R2-11 |
| R-49 | Partial | D-51 names no harness runtime and no pinned model; (a)-(l) are not labeled MUST/SHOULD, but D-51 needs that label to apply its pass rule | R2-16 |
| R-57 | Partial | D-44 lets one confirmation cover a cascade, but later steps cannot be dry-run up front (§6.1, WP-10 (a)) | R2-07 |
| R-58 | Partial | Ownership table exists, but several files have concurrent or unlisted writers | R2-09 |
| R-61 | Partial | `intake_digest` points at an `intake.yaml` state that D-40 never commits | R2-04 |
| R-66 | Partial | WP-02b renders the code table before WP-06/08 add codes | R2-18 |

---

## 2. Versioning content and verification scope (D-39, D-40)

D-39 and D-40 together do not yet establish "versioned bundles are verifiably immutable" or "every
artifact can be rebuilt from its tag". Gaps follow.

**R2-01** [blocking] `07` D-39; `05` Verification scope; `03` Bundle snapshot / RFC §11, Validation
Rules
D-39 verifies "the version pinned by a working bundle in the tree". Nothing pins a root bundle
(Domain or Project), and an unreferenced concept is pinned by nothing too. So CI never verifies a
root version: editing a Project bundle's own SCDs after 1.0.0 stays green until someone compiles.
The plan also never says what the working bundle file holds after `bundle version`: the released
version (in place, as built, which `05` Resolution implies) or `DRAFT`. That choice decides
whether a working file counts as "versioned", what D-17 resolves an unpinned ref to, and how the
next edit cycle starts. WP-14 cannot be built without guessing.
Fix: new D-52, which makes two choices. (1) The state of the working bundle after versioning; rec.:
it keeps the released version, and the first edit (`scd write`, `pin`, `remove-scd`, `add`) sets it
back to `DRAFT`. (2) The verification set, which D-39 restates as {every version pinned by a working
bundle} ∪ {every working bundle whose `version` is not `DRAFT`, against its own snapshot and
manifest}. WP-14 Accept: "version a Project root, edit one of its SCDs: repository-mode validation
reports `CONTENT_DIGEST_MISMATCH`."

**R2-02** [blocking] `07` D-39, D-49, D-18 / RFC Summary, §11 "verifiably unchanged"
The working-tree manifest certifies itself. Normal validation recomputes the digest and compares
it with the `content_digest` in the working manifest, which is outside the digest and freely
editable. Three edits go undetected:
- Edit an SCD, then edit `content_digest` to match: green.
- Delete `tools_version` and `content_digest`: the manifest becomes "pre-0.7" under D-49, gives a
  `MANIFEST_UNVERIFIABLE` warning, and WP-14 says such bundles still compile.
- Delete the manifest: `MANIFEST_MISSING` warning; compile proceeds without `source_digest`.

`approved_by` can also be rewritten after the fact, and nothing checks it. Only `--verify-version`
against the tag catches any of this, and only on request. Git is now mandatory (D-38), so the
check is cheap.
Fix: D-39 adds: "For each version in the verification set, the validator reads that version's
manifest from its tag. The working manifest's `content_digest`, `approval`, and
`validation_passed` must equal the tagged values (`MANIFEST_ALTERED`, error). A version with a
0.7-format qualified tag (`<workspace>/<name>-v…`) whose working manifest is missing or lacks
`content_digest` is an error, not a warning. A verified version with no tag is an error
(`VERSION_TAG_MISSING`)." State in the spec that the guarantee is against unrecorded change, not
against someone who rewrites both the manifest and the tag; RFC §11 already treats tags as a
locator.

**R2-03** [blocking] `07` D-40; `05` What a version is, Transition guards / RFC §9 "rebuilt from its
tag", §11
(a) D-40 says both "exactly the digest inputs" and "every SCD in the tree". The latter sweeps
unrelated work-in-progress SCDs, including other workspaces', into the tag. That contradicts
"other working-tree changes are left alone" and the RFC §9 SHOULD to confine changes to one
workspace. (b) The commit holds only this bundle's inputs, so rebuilding the resolved tree from the
tag requires the imports' snapshots, manifests, and SCDs at that commit to match the imports'
digests. Nothing ensures this. A pinned import whose SCDs were edited after it was versioned is
caught only by validation, which `--no-validate` skips (`05` guard: "Validation passes (unless
`--no-validate`)"). With `--no-validate`, the root's tag holds a drifted import tree, and its
artifact cannot be rebuilt. (c) "Manifest-relevant bundle files" is undefined. (d) Deleted SCD
files (`remove-scd`) are not mentioned.
Fix: rewrite D-40 as follows.
- Before any write, and regardless of `--no-validate`, `bundle version` verifies every pinned
  import's digest against working content (`CONTENT_DIGEST_MISMATCH`). It refuses with
  `VERSION_DIRTY_TREE` if any file in an import's resolved tree differs from HEAD.
- The commit is a pathspec commit of the working bundle file, the SCD files the bundle includes
  (with deletions), the snapshot, the manifest, and `intake.yaml` (R2-04). Nothing else is staged
  or unstaged.
- Add `VERSION_DIRTY_TREE` to the `04` registry seed. Move the import check into the `05` guard
  as independent of validation. WP-14 Accept: "`--no-validate` on a root whose pinned import
  drifted fails with `CONTENT_DIGEST_MISMATCH`"; "an uncommitted edit in another workspace is not
  in the version commit."

**R2-04** [should-fix] `07` D-32 vs D-40; `06` WP-07, WP-14, File ownership / RFC Motivation
(review record)
`intake_digest` hashes `intake.yaml` "at versioning time", but D-40 does not commit `intake.yaml`.
The linked record may never exist in history, so the link cannot be checked. The hash is also
unspecified (raw bytes or canonical form per §11). WP-07 scope ("`intake_digest` in manifests") and
WP-14 Depends (D-32) both claim the manifest writer in `bundle.py`. WP-07 and WP-14 run in
parallel (group 5), and the ownership table gives `bundle.py` to WP-14/WP-06 only.
Fix: D-32 option 1 adds: "canonical digest as §11; `intake.yaml` is included in the version
commit." Give manifest writing of `intake_digest` to WP-14 only; WP-07 provides the schema field.

**R2-11** [should-fix] `05` What a version is; `06` WP-14 Accept / RFC §9 "every artifact can be
rebuilt from its tag"
"Rebuild" is undefined and untested. WP-14 tests only "tagged commit's files recompute to the
digest". The compiler may also read inputs outside the digest: `.scs/config`, the
`ontology/domain-manifest.yaml`, and the meta bundle shipped with the tools (D-21). A rebuild with
other tools can differ.
Fix: define "rebuild" as "with the manifest's `tools_version`, compiling at a checkout of the tag
yields an artifact with the same `source_digest` and the same content as the original, apart from
fields §3.5 declares variable". List every compiler input and state for each whether it is in the
tag. WP-14 Accept: "`git worktree add` at the tag, `scs compile`, artifact equals the `dist/`
artifact compiled at versioning time."

---

## 3. Dependencies and ownership

**R2-05** [should-fix] `07` D-33 (section E); `06` WP-04 Depends, graph, groups
WP-04 Depends lists D-33 under WP-01a, but D-33 sits in section E (WP-01b). The graph has no
`WP01b --> WP04`; group 3 waits for WP-00 and WP-01a only. Either the lead starts with an undecided
item, or it waits for all of WP-01b.
Fix: move D-33 to section A or C (WP-01a), as R-65 proposed.

**R2-06** [should-fix] `07` D-27; `06` WP-01b Accept, graph
WP-01b is done when "every item in section E has a recorded outcome". D-27 is "decide after
WP-11a", but WP-11a depends on WP-01b. WP-01b therefore cannot finish, and WP-02a, WP-03, and
WP-09 wait for it.
Fix: WP-01b Accept excludes D-27. Record D-27's fallback order now; the final choice becomes a
WP-11a output that gates WP-10.

**R2-07** [should-fix] `07` D-44; `04` Skill-to-engine contract; `06` WP-10 (a), (c) / RFC §6.1, §6.2
In a cascade, the root's `pin` and `version` dry-runs depend on the concept versions written
earlier in the same cascade, so the engine cannot produce their `changes` before the one
confirmation. Either (a) fails, or the skill confirms each step, which contradicts D-44.
Fix: D-44 adds: "the skill shows, before the single confirmation, a cascade plan listing every
snapshot, manifest, pin edit, and tag (all deterministic from names and versions); it runs each
step's `--dry-run` and stops if the result differs from the plan." Alternatively, add `bundle
version --cascade --dry-run`. Amend WP-10 (a) to accept the plan listing.

**R2-08** [should-fix] `07` D-08; `04` Commands / RFC §1 Maintain, §6.8
(a) Re-scoping is in the D-08 question but not in either option. No command adds an existing SCD
to another bundle or adds an import to a bundle. (b) Option 2 drops "retired" from RFC §7 without
saying what retire is (file delete? remove from `scds`?). (c) Option 1's `scd write PATH --from-file
F` makes the skill write `F` somewhere. In a sandbox that is usually `/tmp`, which breaks WP-10 (b)
"no file outside the repo root changes" and RFC §6.8.
Fix: option 1 adds `scs bundle add-scd` and `scs bundle add-import` (or states that `scs add`
covers them), and `scd write` reads stdin (`--from-file -`). Option 2 defines retire. "RFC
amendments implied" lists §1 if retire maps to removal.

**R2-09** [should-fix] `06` File ownership
Writers missing from the table, or running concurrently:
- `scs_tools/cli.py` (WP-05 only): WP-06 (`pin`, `remove-scd`), WP-07 (`intake`), and WP-08
  (`diff`) all register commands. WP-06 and WP-07 can run at the same time (WP-06 does not wait
  for WP-07).
- `add.py` (WP-05 only): WP-06 must add the `--author` requirement (D-13).
- `bundle.py`: WP-05 must switch versioning to the in-process validator (D-37; WP-05 Accept "no
  subprocess call remains"), but the first owner is WP-14. WP-07 writes `intake_digest` (R2-04).
- `schema/diagnostics/codes.yaml` (WP-04, then WP-07): WP-05, WP-06, WP-08, and WP-14 all add
  codes, and WP-07 and WP-14 run in parallel.
- Validator code: WP-03 Accept requires the D-03 name mismatch and the D-04 legacy-location read
  in validation, but the validator belongs to WP-04 and then WP-07.
- `docs/MIGRATION-0.7.0.md` and `ISSUES.md`: the preamble requires every WP to edit them, which
  contradicts "two WPs never edit the same file at the same time".
- `schema/runtime/` (`source_digest`, `scs_runtime`, D-47): no owner.

Fix: add these rows. Use per-WP fragments for migration notes and the code registry
(`docs/migration.d/WP-nn.md`, `schema/diagnostics/codes.d/WP-nn.yaml`), assembled in WP-15 and
WP-04's build step. Move the D-03/D-04 validator work to WP-04, adding D-03 and D-04 to its Blocks
column.

**R2-10** [should-fix] `06` WP-04, WP-14; `04` Validator output
`--verify-version` (validator reads git objects, a new capability) and the D-39 verification set
have no owning scope line. WP-04 is blocked by D-39 but has neither scope nor Accept for it. WP-14
tests it but has no scope paragraph at all, only Accept.
Fix: give WP-14 a scope paragraph naming D-39 verification-set selection, `--verify-version`,
resolver changes, D-16/D-18 compiler changes, versioning guards, and commit scope. Remove D-39
from WP-04's Blocks, or state what WP-04 builds for it.

---

## 4. Other decision and section-consistency issues

**R2-12** [should-fix] `07` D-41; `04` `bundle diff` defaults; `06` WP-10 (g) / RFC §6.6, Migration
Guide
The default `--from` is "latest version". Two cases fail with `DIFF_VERSION_NOT_FOUND`: a bundle's
first version, which has no prior version, and a bundle migrated from 0.6, whose only tags are
`v1.0.0` or were renamed by `filter-repo`. WP-10 (g) requires a diff before every version, so
every first-version conversation either fails the assertion or the skill skips the diff.
Fix: D-41 adds: "no prior version: diff from empty (everything added); legacy version: read the
`v<version>` tag if it exists, else the stem-named snapshot plus `DIFF_LEGACY_BASELINE` warning."
WP-08 golden test for each case.

**R2-13** [should-fix] `07` D-18, D-49, D-04; RFC §9 CI / Migration Guide
CI runs `--strict`, and warnings exit 2. A migrated repo with pinned pre-0.7 versions
(`MANIFEST_UNVERIFIABLE`), or still on the 0.6 ontology location (deprecation warning), is red on
every push. It stays red until every bundle is re-versioned, and D-15 forbids rewriting. WP-14
Accept "validates (warnings only)" does not say under which mode.
Fix: a decision states whether these warnings escalate under `--strict`. Rec.: they do not
(informational class in the registry); the generated CI then stays green for migrated repos.
WP-14 Accept names the mode.

**R2-14** [should-fix] `07` D-28, D-36; `06` WP-07 Accept / RFC Validation Rules
WP-07 requires "a manifest with a role-only `approved_by` fails", but no rule says how a role
("Quality Manager") differs from a person ("Jane Doe").
Fix: D-28 defines the forms. Rec.: role-only entries in `intake.yaml` use `role:<name>`, and the
manifest schema rejects the `role:` prefix and empty strings. Otherwise define a person
identifier as a name with an email.

**R2-15** [should-fix] `07` D-45, D-49; `06` WP-11rc, WP-13
Version comparison is unspecified. Under PEP 440, `0.7.0rc1 < 0.7.0`. A skill with a minimum of
`0.7.0` refuses the rc engine in WP-13, and D-49's `>= 0.7` treats rc and dev manifests as
pre-0.7.
Fix: D-45 and D-49 state PEP 440 comparison with pre-releases counted as meeting the base version
(or minimum `0.7.0rc0`). D-49 keys on the presence of `tools_version`, not its value (and see
R2-02).

**R2-16** [should-fix] `07` D-51; `06` WP-10 Accept
"The WP-13 client's default model" is Claude.ai's, which changes over time and cannot be run in a
local harness with a filesystem snapshot per turn. The harness runtime (API plus a local skill
loader? Claude Code? replay?) is not named. Assertions (a)-(l) are not marked MUST or SHOULD, yet
D-51's 5/5 vs 4/5 rule depends on that. (g), (i), the second half of (h), and the `locator` in (k)
are SHOULD in the RFC.
Fix: D-51 names the runtime and a pinned model id. Label each of (a)-(l) MUST or SHOULD in WP-10.

**R2-17** [should-fix] `04` `bundle version`; `07` D-38, D-50; `06` WP-11a, WP-13
Versioning now always commits. Hosted sandboxes (Claude.ai, the WP-13 client) typically have no
git identity configured, and the engine may not take one from the environment (D-13). `git commit`
then fails, and WP-13 cannot pass. The install matrix records neither git presence nor identity.
WP-13 does not say how the repo, with tags and `.git`, leaves the sandbox to be archived.
Fix: a decision on the committer identity. Rec.: author = `--approved-by`, committer = fixed
`scs-tools <noreply>`, both passed with `-c` and listed in `changes`. WP-11a rows add git version
and identity. WP-13 Accept: "repo archived as a `git bundle` including tags."

**R2-18** [should-fix] `06` WP-02a, WP-02b Accept / RFC Validation Rules, Schema Changes
(a) The trace splits RFC sections 1-12 between WP-02a and WP-02b. The unnumbered Validation Rules
and Schema Changes sections, which carry most of the testable MUSTs, belong to neither. (b) WP-02b
renders the code table from `codes.yaml` and CI checks they match. WP-06 and WP-08 (groups 6-7)
add codes after WP-02b may be done, so either their CI goes red or they edit `spec/0.7/`, which
WP-02b owns.
Fix: assign Validation Rules and Schema Changes to WP-02b's trace. Generate the code table at docs
build (WP-15) instead of committing it, or make WP-02b depend on WP-08.

**R2-19** [should-fix] `07` D-39; "RFC amendments implied" / RFC Validation Rules
RFC: "A versioned bundle's recomputed content digest MUST match … error in every mode." D-39
limits normal validation to a subset, but is not marked RFC and is missing from the amendments
list. D-44 (§6.2 reading) and D-08 option 1 (§1 "retire") are missing too.
Fix: mark D-39 "RFC (Validation Rules)". Add D-39, D-44 (if a reading is recorded), and D-08 §1 to
"RFC amendments implied".

**R2-20** [should-fix] `04` Commands (`scs add`); `06` WP-03, WP-05
"Reserved bundle names refused" at `scs add` has no owning WP. WP-04 owns only the validator rule,
and neither the WP-05 nor the WP-03 scope mentions it. The `NAME-context` default is in WP-03's
scope but not its Accept.
Fix: WP-05 scope and Accept: "`scs add bundle plan` fails with `RESERVED_BUNDLE_NAME`". WP-03
Accept adds the `NAME-context` default.

**R2-21** [should-fix] `04` Envelope example and `changes` rule; `06` WP-06 Accept
The example is a failed run (`ok: false`, approver missing) listing four changes, while WP-06
requires that the same failure "writes nothing", and `changes` is "every effect of the run".
Skills will misreport what happened on failure.
Fix: define `changes` on `ok: false` as the effects that remain after rollback (normally empty),
and fix the example. Optionally add `planned` for dry-run.

---

## 5. Minor

**R2-22** [minor] `06` Lead package. "Inspected closely before any others run" contradicts groups 1-2
(WP-01b, WP-02a, WP-09, WP-11a, WP-13a), which run before or alongside WP-04. Fix: "before any other
engine package starts".

**R2-23** [minor] `06` WP-15 after WP-11. 0.7.0 is published with the old README as its PyPI
description and a GitHub release without release notes. Fix: README and release notes move to
WP-11rc or WP-11 scope. WP-15 keeps the docs site.

**R2-24** [minor] `03` SCD row "Requires opening the closed item schemas". This can be read as
dropping `additionalProperties: false`. Fix: "add `derived_from` as a property; items stay closed."

**R2-25** [minor] `04` Machine-mode conformance item 3 applies to commands with `--dry-run` n/a
(`diff`, `validate`, `--version`). Fix: "for commands that take `--dry-run`". Also add
`--allow-draft` to the `compile` row (`05` uses it).

**R2-26** [minor] `06` WP-06 Accept "repo byte-identical". This is impossible for `.git` (loose
objects, reflog). Fix: "working tree, index, and refs identical".

**R2-27** [minor] `04` Diagnostic codes seed. Codes the plan already needs are missing:
`.scs/config` name mismatch (D-03), legacy ontology location (D-04), duplicate id (WP-04), git
missing (D-38), output path outside repo (WP-05), `VERSION_DIRTY_TREE` (R2-03). Fix: seed them.

**R2-28** [minor] `06` WP-00, WP-10 (h). These are the review-1 remainders. WP-00 Accept adds
"`approval_status` reflects the actual run". WP-10 (h) adds "each finding names the SCD item id and,
where relevant, the `std:` cite (§12)" using a seeded framework-conflict fixture. Also add a WP-10
assertion for RFC §9's SHOULD to confine changes to the named workspace.

**R2-29** [minor] `06` WP-11a. It publishes with the final package layout (pyproject edits) while
WP-05 edits the same pyproject (mypy). Fix: WP-11a builds from a throwaway branch, or the table
lists pyproject ownership.

---

## Verdict

**Not ready for maintainer decisions as written; one more focused revision.** The revision fixes
most of review 1. The dependency graph, groups, and Depends lines agree apart from D-33 (R2-05) and
the D-27 cycle (R2-06). The remaining blockers are all in section A, the core claim of the release:

- D-39 never verifies roots, and leaves the state of the working bundle after versioning undefined
  (R2-01).
- The working manifest certifies itself, and a downgrade to "pre-0.7" bypasses verification
  (R2-02).
- D-40's commit scope contradicts itself, and `--no-validate` lets a drifted import tree into a tag
  (R2-03).

Together these mean "verifiably immutable" holds only for pinned concepts when nobody edits the
manifest, and "rebuild from its tag" is asserted but never tested (R2-11).

Next steps:
1. Fix R2-01 to R2-03 (rewriting D-39 and D-40, and adding D-52).
2. Move D-33 and resolve D-27.
3. Add the missing decisions: commit identity (R2-17), version comparison (R2-15),
   person-identifier form (R2-14), and strict CI on migrated repos (R2-13).

With those done, section 7 is ready for decision. After the decisions, agents can build the
engine WPs without re-deriving intent once the ownership table is corrected (R2-09, R2-10). WP-10
still needs D-51's runtime and the MUST/SHOULD labels (R2-16).

| Severity | Count |
|---|---|
| Blocking | 3 |
| Should-fix | 18 |
| Minor | 8 |
