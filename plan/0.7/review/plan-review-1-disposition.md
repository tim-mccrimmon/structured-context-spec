# Plan review 1: disposition

Revision 2 of the plan, 2026-10-25. Every finding in `plan-review-1.md` is accepted; this table
records where each one landed. "D-nn" is a section 7 decision (new ones are D-38 onward).

## Blocking

| Finding | Disposition |
|---|---|
| R-01 digest format has no conformance test | WP-00 Accept: independent test vectors in `tests/digest/` |
| R-02 WP-10 misses §6.5-6.8; shim cannot see file writes | WP-10 Accept (a)-(l): filesystem snapshot per turn, one assertion per RFC rule; harness in D-51 |
| R-33 which versions are verified after drift | D-39; `05` Verification scope; WP-04, WP-14 Accept |
| R-34 diff needs old content | D-41; WP-08 reads from the tag |
| R-35 version commit contents | D-40; `05` What a version is; WP-14 Accept |
| R-36 workspace selection, path base | D-42; `04` Workspace selection and envelope paths |
| R-64 release before acceptance | WP-11 split into WP-11rc, WP-13, WP-11 |

## Should-fix and minor

| Finding | Disposition |
|---|---|
| R-03 §8, §5 MUSTs | WP-10 Accept (b), (k); WP-05 Accept: no network |
| R-04 §12 advisory review | WP-07 Accept (schema); WP-10 Accept (h) |
| R-05 §4 intake order | WP-07 Accept (intake validated); WP-10 Accept (j) |
| R-06 out-of-scope requests | WP-10 Accept (l); WP-05 Accept: no output outside repo |
| R-07 WP-06 Accept gaps | WP-06 Accept |
| R-08 machine mode for intake, diff, `--version` | Conformance defined once in `04`; required in WP-05 to WP-08; `scs --version --json` |
| R-09 diff change kinds, defaults | WP-08; `04` defaults; retired per D-08 |
| R-10 AGENTS.md content, naming, reserved dirs | WP-03 Accept |
| R-11 reserved dirs indexed | WP-14 Accept; `05` Resolution row |
| R-12 repo mode "more than one Domain" | `04` definition; WP-04 Accept |
| R-13 pre-0.7 manifest warning | D-49; WP-04 Accept |
| R-14 no compile bypass | WP-14 Accept |
| R-15 placement services | D-24 names services; WP-09 Accept |
| R-16 legacy tags | WP-14 Accept |
| R-17 hardening regressions | WP-00 Accept |
| R-18 approver in every mode | D-13; `04`; WP-06 Accept |
| R-19 exit code 4 | `04` Exit codes; D-12 |
| R-20 envelope shape | `04` envelope schema, object `suggestion`, example fixed |
| R-21 D-04 not marked RFC | D-04 marked RFC; legacy location read; WP-03 Accept |
| R-22 `content_inputs`, `scs_runtime` | D-47 |
| R-23 `--no-git` | D-38 |
| R-24 compile output | D-11; owned by WP-05 only |
| R-25 WP-08 dependencies | Graph and groups regenerated |
| R-26 WP-09 needs D-24 | WP-09 depends on WP-01b |
| R-27 groups table | Regenerated from the graph; "lead" defined |
| R-28 WP depends vs section 7 | Section 7 Blocks column is the single source; WP depends lines match |
| R-29 critical path | Rewritten |
| R-30 WP-04 needs WP-00 | Added |
| R-31 D-18 wording | D-18: exit 2 under strict |
| R-32 DRAFT compile state | `05` state diagram |
| R-37 validator JSON vs envelope | `04` Validator output |
| R-38 snapshot naming | D-43; `03` |
| R-39 code registry | D-10: `schema/diagnostics/codes.yaml`; seed list in `04` |
| R-40 target clients | D-50 |
| R-41 "Domain built" | `DOMAIN_WORKSPACE_MISSING`; WP-03 Accept |
| R-42 envelope versions | `scs_version` and `tools_version` |
| R-43 to R-54 acceptance rewrites | Applied to WP-02a/b, WP-03, WP-04, WP-06, WP-07, WP-08, WP-10, WP-11a, WP-13, WP-13a, WP-15, WP-12, WP-14, WP-05, WP-11 |
| R-55 D-08 retire, MCP | D-08 rewritten with two options; rec. engine commands |
| R-56 role-only approver | D-28 limited to `intake.yaml` |
| R-57 cascade approval | D-44; D-01 notes the cost |
| R-58 versioning code ownership | File ownership table in `06` |
| R-59 `--force` | D-15: removed |
| R-60 placement copy drift | D-24: skill states `checked:` date |
| R-61 intake outside digest | D-32 option 1: `intake_digest` |
| R-62 install fallback | D-27: bundled wheel |
| R-63 missing decisions | D-38 to D-51 |
| R-65 37 decisions up front | WP-01a / WP-01b split |
| R-66 spec before shapes | WP-02a / WP-02b split |
| R-67 install test layout | WP-11a uses final layout; re-run on rc |
| R-68 schema approval gate | M-07 milestone in graph |

## Changes in judgment

- **Lead package moved from WP-05 to WP-04.** WP-05 needs WP-04's code registry and structured
  validator API, so WP-04 is first on the critical path.
- **WP-00 no longer waits on the versioning decisions.** It commits the code as built;
  D-38 to D-43 change behavior in WP-14 before anything is released.
