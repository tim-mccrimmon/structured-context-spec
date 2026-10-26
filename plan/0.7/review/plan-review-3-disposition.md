# Plan review 3: disposition

Revision 4, 2026-10-25. All findings accepted. The maintainer decided D-57, D-58, D-59, and the
narrowing of D-39 check 2 the same day. Per the review's verdict, no further full review round;
the maintainer checks the patched WP-14 Accept list.

| Finding | Disposition |
|---|---|
| R3-01 no way to compile a released version | D-57 `compile --version V` (decided); `04`, `05`, WP-14 scope and rebuild test |
| R3-02 WP-14 test asserted a check the model lacks | Test replaced: root edit passes, `--verify-version` passes, `compile --version` gives tagged content; root-tag tamper test added |
| R3-03 shallow CI checkout verifies nothing | WP-03 workflow `fetch-depth: 0` with tags; `GIT_HISTORY_INCOMPLETE`, `VERSION_TAG_MISSING` in D-39, `04`, WP-14 |
| R3-04 swept and staged files in the commit | D-09 `git-commit` carries `paths`; D-40 `git commit --only` with workspace pathspec; `04` example; WP-14 staged-edit test |
| R3-05 tagger identity; user git config | D-58 (decided): annotated tag, fixed tagger, signing/hooks/autocrlf overridden; WP-14 test with global gpgsign and a failing hook |
| R3-06 snapshots trip `DUPLICATE_ID` | `03` indexing rule; D-43 blocks WP-04; WP-04 Accept |
| R3-07 check 2 red after legitimate removal | D-39 check 2 narrowed to versions in use (decided); WP-14 test |
| R3-08 WP-04 schema cannot apply D-49 | D-49 moved to WP-14; WP-04 schema keeps fields optional |
| R3-09 D-54 contradicts RFC | D-54 marked RFC; amendments list |
| R3-10 `.gitignore`; `sources/` in history | D-40 implementation note, `VERSION_INPUT_UNTRACKED`; D-59 (decided) ignores `sources/` by default |
| R3-11 forged import manifest in a root tag | D-39 check 1 compares import manifests with their own tags; WP-14 test |
| R3-12 byte identity vs CRLF | Compare by git blob id; scaffold `.gitattributes` |
| R3-13 unborn HEAD | `scs new domain` makes an initial commit; WP-03 Accept |
| R3-14 ownership of shared bundle-name function | WP-04 listed first |
