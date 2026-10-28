# SCS 0.7.0 Plan

- **Status**: Rev 5 (2026-10-26). Decisions recorded (section 7) except D-27, which WP-11a
  settles. RFC 0002 amended for WP-01a, WP-01b, and section 7 G.
- **Source of design**: `rfcs/RFC-0002-agent-mediated-scs.md` (accepted 2026-10-25)
- **Backlog**: `ISSUES.md` ISS-042 to ISS-055; workstreams in `ROADMAP.md`

RFC 0002 says what 0.7.0 is and why. This plan says how it gets built: the system as it
stands, the target, the work packages, and how each is accepted. It is retrofitted from the RFC
and the code on `0.7-dev`, then reviewed and approved before any build work is handed to
agents. Test plan, QA plan, and the SCDs that govern the build agents derive from it.

## Contents

| # | Section | What it fixes |
|---|---|---|
| 1 | [System context](01-system-context.md) | What SCS 0.7 is, its boundary, actors, and what is out of scope |
| 2 | [Component model](02-component-model.md) | Engine, validator, compiler, schemas, skills, MCP: responsibilities and boundaries |
| 3 | [Data model](03-data-model.md) | Schemas and files: SCDs, bundles, manifests, intake record, runtime artifact, digests |
| 4 | [Interfaces](04-interfaces.md) | CLI machine mode, result envelope, skill-to-engine contract, validator output |
| 5 | [Lifecycle](05-lifecycle.md) | Bundle and workspace states, transitions, and the guards on each |
| 6 | [Work breakdown](06-work-breakdown.md) | Work packages, dependencies, critical path, acceptance criteria |
| 7 | [Decisions and gaps](07-decisions-and-gaps.md) | RFC gaps, RFC vs code conflicts, open questions to decide before build |

Derived, after approval: `test-plan/`, `qa/`, `context/` (build-agent SCDs).

Working material: `survey/` holds the as-built surveys the plan was drafted from; `review/`
holds the QA reviews of the plan and their disposition.

## Baseline rules

- The plan changes before the code does. A work package that needs a design change stops and
  raises it against the relevant section.
- Each work package names the plan sections it implements and the acceptance criteria it must
  meet.
- RFC 0002 remains the authority on intent. Where this plan and the RFC disagree, section 7
  records it and the maintainer decides.

## Build progress

Updated 2026-10-26. Branch `0.7-dev`; CI green on every commit below.

| WP | State | Commit |
|---|---|---|
| WP-01a, WP-01b | Done: decisions recorded, RFC 0002 amended (D-27 waits for WP-11a) | `938483d` |
| WP-00 | Done: validator version from package metadata, digest test vectors | `99ee08c` |
| WP-04 | Done: check registry, repository mode, diagnostic codes, report schema | `3e7c7a4` |
| WP-05 | Done: `--json` envelope, exit codes 0-5, `--dry-run`, `scd write`, `compile` to `dist/` | `476e542` |
| WP-03 | Done: `new domain` creates the Domain repository (AGENTS.md, CI, initial commit), `new project` inside it, `ontology/`, D-06 config keys; templates by ontology and kind (D-64), `personal` ontology with boundaries only (D-61, D-62, D-72), `created_by` as `Name <email>` | `3d36d97` |
| WP-14 | Done: tag-based versioning, D-39 checks, `--verify-version`, `compile --version`, D-17 resolution, D-70 `SCD_EMPTY`, D-71 `PROVENANCE_PLACEHOLDER` | `2bb34c0` |
| WP-06 | Done: author and approver rules (D-13, D-71), D-74 ontology inheritance, `--dry-run` on `new`, `bundle pin`/`add-import`/`add-scd`/`remove-scd`, `add bundle --new` (D-68, D-75, D-76), full rollback | `0e16628` |
| WP-07 | Done, M-07 approved 2026-10-26: `schema/intake/intake-schema.json`, `scs intake set`/`record-finding` (D-77, D-78), `derived_from` in SCD items, `DERIVED_FROM_UNRESOLVED`, intake checks per workspace | `e5da021` |
| WP-02a, WP-08, WP-09, WP-11a, WP-13a | Unblocked, not started | |

Known gaps carried forward:

- An unreadable SCD YAML file is skipped by the index without a diagnostic. (Bundle mode now
  schema-validates the SCDs it resolves, WP-07.)
- Rule-severity housekeeping item from WP-04 is still open.
- The generated CI workflow installs `scs-validator>=0.7.0,<0.8` from PyPI; that works once
  0.7.0 is published (D-27, WP-11rc). The packages still report version 0.6.0.
- `scs init` still makes a standalone 0.6-style workspace with `--type`; it is not
  repository-aware.
- The 0.5 presentation docs still show `scs new project --type`.
- The exit-2 (`--strict` warnings) machine-mode test fakes the validator report. A placeholder
  `created_by` (`PROVENANCE_PLACEHOLDER`) is now a real warning-only input in bundle and
  repository mode; the test could use it.
- `scs compile` writes to `dist/`, which is untracked by default and shows in `git status`; the
  generated `.gitignore` leaves the choice to the user.
- The examples' `created_by` values use `.example` domains and now warn as
  `PROVENANCE_PLACEHOLDER`; they are fictional organizations and are left as they are.
- Validator messages for drift (`CONTENT_DIGEST_MISMATCH` from bundle validation) print
  absolute paths in human output; machine mode normalizes them to the repository root.

Working notes:

- Change sets per WP: code, tests, `schema/diagnostics/codes.d/WP-NN.yaml` (then
  `python tools/scd-validator/scripts/build_codes.py`), and `docs/migration.d/WP-NN.md`.
- Before committing: both test suites; `ruff check`; `black --check` run from inside each
  package directory (never from `tools/`, which falls back to 88 columns); `mypy src` and
  `mypy scs_tools`; `build_codes.py --check`; `sync_schemas.py --check`.
- Dev environment: a venv with `pip install -e "tools/scd-validator[dev]" -e tools/cli pytest
  jsonschema`.
