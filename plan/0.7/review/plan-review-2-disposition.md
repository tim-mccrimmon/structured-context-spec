# Plan review 2: disposition

Revision 3, 2026-10-25. All findings accepted. The blocking findings were settled by the
maintainer's integrity-model decisions (D-39, D-40, D-53, D-54), which replace the review's
proposed patches with a simpler model: the git tag is the record of a version.

| Finding | Disposition |
|---|---|
| R2-01 roots never verified; working file state | D-39 check 1 verifies every version tag, roots included; D-52 working file stays DRAFT; WP-14 Accept (Project root edit) |
| R2-02 working manifest vouches for itself | D-39 check 2 (`MANIFEST_ALTERED`); D-49 keyed on tag form; D-18 rewritten; WP-14 Accept (three tamper tests) |
| R2-03 commit scope; drift under `--no-validate` | D-40 whole workspace except `dist/`; D-53 integrity checks always run; WP-14 Accept |
| R2-04 `intake_digest` not committed; writer conflict | D-32: `intake.yaml` is in the version commit; `intake_digest` dropped |
| R2-05 D-33 in wrong batch | Moved to section C (WP-01a) |
| R2-06 D-27 cycle | WP-01b excludes D-27; fallback order recorded; WP-11a decides per client |
| R2-07 cascade vs dry-run | D-44 cascade plan, then per-step dry-run checked against the plan; WP-10 (a) |
| R2-08 re-scope; temp file | D-08 option 1 adds `add-scd`, `add-import`; `scd write` reads stdin |
| R2-09 ownership conflicts | Ownership table rebuilt: check registry (WP-04), command discovery (WP-05), per-WP fragments for codes and migration notes, ordered owners for `bundle.py`, `add.py`, pyproject; maintainer updates `ISSUES.md` |
| R2-10 `--verify-version` and D-39 unowned | WP-14 scope paragraph; D-39 blocks WP-14 only |
| R2-11 rebuild undefined, untested | Section 5 defines rebuild and lists compiler inputs; WP-14 rebuild test |
| R2-12 diff on first or legacy version | D-41; WP-08 Accept; WP-10 (g) |
| R2-13 strict CI red after migration | D-54 (legacy versions not reported); `info` severity never affects exit (D-10); WP-14 Accept under `--strict` |
| R2-14 person vs role | D-28: `role:<name>` vs `Name <email>`; WP-04, WP-07 Accept |
| R2-15 rc version comparison | D-56; D-49 keyed on tag form; WP-11rc Accept |
| R2-16 harness runtime; MUST/SHOULD | D-51 names the Agent SDK and a pinned model; WP-10 table labels each assertion |
| R2-17 git identity in sandboxes | D-55; WP-14 Accept; WP-11a rows; WP-13 `git bundle` archive |
| R2-18 trace gaps; code table timing | WP-02b trace includes Schema Changes and Validation Rules; code table generated at docs build (WP-15) |
| R2-19 RFC amendments list | D-39, D-40, D-44, D-08 §1 added |
| R2-20 reserved names at `add`; `NAME-context` | WP-05 and WP-03 Accept |
| R2-21 `changes` on failure | D-09; `04` failure example |
| R2-22 lead wording | "before any other engine package starts" |
| R2-23 release notes timing | README and release notes in WP-11rc; WP-15 is the docs site only |
| R2-24 closed schemas | `03`: property added, items stay closed |
| R2-25 conformance for no-dry-run commands; `--allow-draft` | `04` conformance item 3; compile row |
| R2-26 byte-identical `.git` | "working tree, index, and refs" |
| R2-27 code seed | Seeded in `04` |
| R2-28 review-1 remainders | WP-00 Accept; WP-10 h1, m |
| R2-29 pyproject ownership | WP-11a uses a throwaway branch; ownership table |
