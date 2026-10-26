# Plan review 3: SCS 0.7.0 plan rev 3 vs RFC 0002

- **Date**: 2026-10-25
- **Inputs read**: `rfcs/RFC-0002-agent-mediated-scs.md`; `plan/0.7/README.md`, `01`-`07`;
  `review/plan-review-2.md`, `review/plan-review-2-disposition.md`. Nothing else.
- **Scope**: final round. Only issues that would make an agent build the wrong thing or stall.
  The integrity model (D-39, D-40, D-53, D-54) is taken as decided; findings on it are about how
  section 5 and WP-14 implement it.
- **Format**: R3-nn, severity (blocking / should-fix / minor), location, problem, fix.

---

## 1. Review 2 disposition check

All 29 findings are reflected in the text. Most are resolved as claimed. These are only partly
resolved:

| R2 | Gap | Covered by |
|---|---|---|
| R2-01 | Roots' tags are verified (check 1), but the WP-14 test the disposition cites (edit a versioned root's SCD, expect `CONTENT_DIGEST_MISMATCH`) is not produced by any D-39 check | R3-02 |
| R2-02 | The field-deletion downgrade is closed, but the same downgrade now happens through a missing tag, including in every default CI checkout | R3-03 |
| R2-03 | The commit scope is decided, but `changes` cannot express files swept into the commit, and staged files outside the workspace are not addressed | R3-04 |
| R2-11 | Rebuild is defined and tested, but there is no defined way to compile a released version (the working file is `DRAFT`), so the rebuild test cannot run as written | R3-01 |
| R2-17 | D-55 fixes the commit identity, but not the tag's (annotated tags need a tagger) | R3-05 |
| R2-19 | D-54 contradicts RFC Validation Rules and Migration Guide (pre-0.7 versions "validate with a warning"), and is missing from the amendments list | R3-09 |

---

## 2. Findings

**R3-01** [blocking] `05` Bundle states and Compiler inputs; `04` `compile` row; `07` D-52, D-11;
`06` WP-14 Rebuild, WP-13
After `bundle version` the working bundle file stays `DRAFT` (D-52, which `03` and `05` already
treat as settled). `scs compile BUNDLE` resolves the working file, so it gives a DRAFT compile, which
needs `--allow-draft` and has no `source_digest`. No command compiles a released version. The
state diagram's `Versioned --> Compiled` has no command behind it. The WP-14 rebuild test has the
same problem: the working file at the tag is also `DRAFT`. WP-13 ("a `dist/` artifact whose
`source_digest` equals the manifest's `content_digest`") cannot pass.
Fix: add a decision paired with D-52 (call it D-57). Rec.: `scs compile BUNDLE --version V`
compiles the snapshot `<bundle-name>-v<V>.yaml` after the D-39 checks for that version. Without
`--version` it compiles the working file, which is DRAFT and needs `--allow-draft`. Update the `04`
compile row, the `05` diagram (`Versioned --> Compiled: scs compile --version V`), the WP-14 rebuild
test ("compile `--version V` at the tag"), WP-05 and WP-14 scope, and WP-10 (i). If the
maintainer chooses the other D-52 option (working file keeps the released version), this
becomes "the first edit resets it to `DRAFT`". Either way, D-52 and D-57 are decided together.

**R3-02** [blocking] `06` WP-14 Accept ("Version a Project root, edit one of its SCDs ... gives
`CONTENT_DIGEST_MISMATCH`"); `05` What validation verifies; `05` diagram `Drifted`
None of the three D-39 checks fires on this test. The tagged content is unchanged (check 1), the
working manifest and snapshot are unchanged (check 2), and nothing pins a root (check 3). Under the
decided model this edit is normal work toward the next version: the working root is `DRAFT`, and
`05` defines drift only for "content a pinned version covers". An agent will either add an
undecided fourth check, which turns every post-version edit of a Domain or Project red under
strict CI, or fail the test.
Fix: replace the test with what the model guarantees: "version a Project root, edit one of its
SCDs: repository-mode validation passes; `--verify-version` on the root's tag passes; compiling
`--version V` (R3-01) gives the tagged content, not the edit." Add a tamper test for roots: "move
the root's tag to a commit with an edited SCD and an unchanged manifest: check 1 gives
`CONTENT_DIGEST_MISMATCH`." If the maintainer wants unversioned root edits reported, record it as
a decision with `info` severity.

**R3-03** [blocking] `06` WP-03 (CI workflow); `07` D-49, D-54; `05` What validation verifies
Every D-39 check reads tags. `actions/checkout` defaults to a depth-1 clone without tags. In that
clone, check 1 sees no tags, check 3 cannot read tagged content, and D-49/D-54 classify every
manifest as pre-0.7 history, "not verified, not reported". So the generated CI is green whatever
the content. Locally, deleting a qualified tag does the same thing to one version, which brings
back the R2-02 downgrade.
Fix: (1) WP-03: the workflow template uses `fetch-depth: 0` and fetches tags. WP-03 Accept checks
this. (2) In repository mode the validator errors on a shallow clone (`GIT_HISTORY_INCOMPLETE`).
(3) A manifest that carries `content_digest`, which no pre-0.7 manifest has, but has no qualified
tag is an error (`VERSION_TAG_MISSING`). D-54 is unaffected because pre-0.7 manifests lack the
field. Seed both codes in `04` and add a WP-14 test for each.

**R3-04** [should-fix] `04` Envelope example and `changes` rule; `07` D-09, D-40; `06` WP-06,
WP-14
The whole-workspace commit sweeps in uncommitted edits the run did not write. The `04` example
reports one as `{"action": "modify", ...}`. Conformance item 3 ("changes equals the effects of the
real run") and the §6.1 confirmation need a rule that separates "written by this run" from
"committed by this run". Also, a plain `git commit` commits the whole index, so a file staged in
another workspace would enter the version commit. The WP-14 test covers only an unstaged edit.
Fix: D-09: `git-commit` carries `paths: [{path, status: A|M|D}]`; `modify` means only files the
run wrote. Fix the `04` example. The skill shows `paths` before confirming. The commit is limited
to `<workspace>/` minus `<workspace>/dist/` (`git commit --only -- <pathspec>`). Rollback restores
the index. The WP-14 test adds "a staged edit in another workspace is not in the commit".

**R3-05** [should-fix] `07` D-55; `06` WP-14 Accept
D-55 fixes the commit identity, but an annotated tag needs a tagger identity, which sandboxes lack
(the R2-17 failure, now at `git tag`). The user's global git config can also break or alter the
commit: `commit.gpgsign`, `tag.gpgSign`, hooks, and `core.autocrlf`.
Fix: D-55 states the tag type. Rec.: an annotated tag with the same fixed identity, or a
lightweight tag. It also lists which git settings the engine overrides with `-c`. The WP-14
identity test also runs with `commit.gpgsign=true` set globally.

**R3-06** [should-fix] `03` Identity and naming rules; `06` WP-04 (duplicate ids); `07` D-43
A snapshot has the same bundle id as its working file. WP-04's new `DUPLICATE_ID` rule, built by
the lead agent before D-43 naming exists in code, will flag every versioned workspace unless the
indexer tells snapshots and manifests apart from working documents. The plan never says how.
Fix: `03`: working documents are indexed by id. Snapshots, recognized by D-43 file name or
non-`DRAFT` `version`, are indexed by (id, version). Manifests are not bundle documents.
`DUPLICATE_ID` applies to working documents only. Add D-43 to WP-04 Depends. WP-04 Accept: "a
workspace with snapshots and manifests of two versions has no `DUPLICATE_ID`."

**R3-07** [should-fix] `05` check 2; `06` WP-14 ("Delete a working manifest whose tag has one:
`MANIFEST_ALTERED`")
Check 2, driven from tags as that test requires, makes CI permanently red after any legitimate
removal. Examples: deleting a concept bundle with its snapshots and manifests, renaming a Project
directory, or removing a Project. Tags persist, and D-15 forbids rewriting them.
Fix: check 2 requires a working manifest only for versions still in use: those pinned by a working
bundle, plus the latest version of each working bundle that exists. A versioned bundle whose
working file is gone is history, and its tags are still checked by check 1. Add a WP-14 test:
"delete a versioned concept that nothing pins: strict validation passes."

**R3-08** [should-fix] `06` WP-04 Accept ("rejects ... a 0.7 manifest without `content_digest`");
`07` D-49
D-49 identifies a 0.7 manifest by its tag, and reading tags is WP-14's work. A JSON schema owned by
WP-04 cannot tell a 0.7 manifest from a pre-0.7 one, so this criterion cannot be built or checked
in WP-04.
Fix: WP-04's schema keeps `content_digest` and `tools_version` optional and the `approved_by` rules
strict. Move "a manifest with a qualified tag lacks `content_digest`/`tools_version`: error" into
WP-14's check module and Accept.

**R3-09** [should-fix] `07` D-54, "RFC amendments implied"; RFC Validation Rules, Migration Guide
The RFC says a manifest without `content_digest` "produces a warning that the bundle cannot be
verified" (Validation Rules) and that pre-0.7 versions "validate with a warning" (Migration Guide).
D-54 says not reported. WP-02a's trace will hit a contradicting MUST.
Fix: add D-54 to the amendments (Validation Rules, Migration Guide). Mark D-54 "RFC".

**R3-10** [should-fix] `07` D-40; `06` WP-03 (`.gitignore` line); RFC §8
(a) "`.gitignore` keeps `dist/` out of version commits but lets the user decide whether to track
it" contradicts itself. Ignoring and tracking are exclusive. (b) Whether the commit honors
`.gitignore` is undefined. If it does, an ignored file under `context/` silently breaks "rebuild
from the tag". If it does not, ignored secrets get committed. (c) `sources/` (quality manuals,
SOPs) enters history on the first version and leaves the machine on the user's next push. RFC §8
expects source documents to stay local.
Fix: D-40 implementation note: `dist/` is excluded by pathspec, not by `.gitignore`. Other ignored
files are not added. `bundle version` refuses (`VERSION_INPUT_UNTRACKED`) if any digest or compiler
input is ignored or untracked after staging. The scaffold `.gitignore` leaves `dist/` to the user.
`AGENTS.md` and the intake skill tell the user that `sources/` is committed unless they ignore it.

**R3-11** [minor] `05` check 1; RFC §11 (import digests)
Check 1 recomputes a root's digest from the import `content_digest` stored in the import manifest
at the root's commit. Nothing checks that manifest against the import's own tag, so a hand-made
root tag can embed a forged import record.
Fix: check 1 also requires each pinned import's manifest at the root's commit to equal that
import's tagged manifest.

**R3-12** [minor] `05` check 2 ("identical")
Byte identity fails on CRLF checkouts and editor re-saves.
Fix: compare git blob ids, and have the scaffold write `.gitattributes` with `* text eol=lf`. Or
compare canonical form (§11) for snapshots and byte-compare manifests. State which.

**R3-13** [minor] `06` WP-06 rollback tests; WP-03
If `scs new domain` makes no initial commit, the first `bundle version` runs on an unborn HEAD.
There, "refs as they were" means deleting the branch ref, not resetting it.
Fix: WP-03 states whether `new domain` makes an initial commit (rec.: yes, with the D-55
identity). WP-06 adds an unborn-HEAD failure-injection test if it does not.

**R3-14** [minor] `06` File ownership
WP-04's shared bundle-name function changes `bundle.py` and `digest.py`, but WP-04 is not listed as
their first owner. No conflict in practice because WP-04 runs first, but agents follow the table.
Fix: list WP-04 first on both rows.

---

## Verdict

Review 2's blockers are resolved in substance by the decided integrity model. The dependency
graph, groups, Depends lines, and ownership table now agree. Three blocking gaps remain, all in how
WP-14 and its neighbors implement the model:

- No command compiles a released version once the working file stays `DRAFT` (R3-01).
- A WP-14 test asserts a check the model does not have (R3-02).
- In the generated CI, and after a deleted tag, verification passes vacuously (R3-03).

**Section 7: ready for the maintainer after a short patch.** Add D-57 (how a released version is
compiled, decided together with D-52), the tag type in D-55 (R3-05), and D-54's RFC marking
(R3-09). Nothing else in sections A to E needs re-drafting.

**Buildable by agents after those decisions: yes,** once R3-01 to R3-03 are folded into
`04`/`05`/WP-03/WP-14. The should-fix items are local edits to one decision or one WP each and can
land in the same pass. No further full review round is needed; a maintainer check of the patched
WP-14 Accept list is enough.

| Severity | Count |
|---|---|
| Blocking | 3 |
| Should-fix | 7 |
| Minor | 4 |
