# SCS 0.7.0 Plan

- **Status**: Draft rev 4 (2026-10-25), revised after `review/plan-review-3.md`. WP-01a decided
  (section 7 A to D); WP-01b (section E) open. Not yet approved.
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
