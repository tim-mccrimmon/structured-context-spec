---
checked: 2026-10-28
---

# Placement: Cursor

Cursor has Team Rules for an organization, User Rules for one person, and project rules and
`AGENTS.md` for a repository. All claims below come from the Cursor
[Rules](https://cursor.com/docs/context/rules) page.

## How Cursor loads layered context

| Level | Where | Notes |
|---|---|---|
| Team Rules | Cursor dashboard ([team content](https://cursor.com/dashboard/team-content)) | Team and Enterprise plans. Created by team administrators. A rule can be enforced, so members cannot turn it off |
| Project rules | `.cursor/rules/*.mdc` in the repository | Version-controlled. Frontmatter `description`, `globs`, `alwaysApply` |
| `AGENTS.md` | Project root and any subdirectory | Nested files combine with parents. More specific ones take precedence |
| User Rules | Customize > Rules | Apply across all of a user's projects |

- **Merged.** "All applicable rules are merged; earlier sources take precedence when guidance
  conflicts". The order is Team Rules, then Project Rules, then User Rules. A Domain layer
  (Team or User Rules) and a Project layer (project rules or `AGENTS.md`) can both be active.
- **Agent only.** Rules apply to Agent (Chat). The page says "Rules do not impact Cursor Tab or
  other AI features".

## Domain placement

- **Organization.** Use a **Team Rule** that is enforced and applies always (no globs). Paste the
  artifact or a rendering that keeps the identity header
  ([README](README.md#keep-the-identity-in-any-rendering)). Enforcement means members cannot
  disable it in Customize.
- **One person, one Domain.** Use **User Rules**, which apply across all projects.
- **One person, several Domains.** The Rules page documents no level between User Rules and a
  single project. To keep a Domain from covering other Domains' work, include the Domain
  artifact as a project rule in each repository that belongs to that Domain, for example
  `.cursor/rules/scs-domain-<bundle-name>.mdc`. Copies can drift, so check each copy's
  `version` and `source_digest` against the versioned bundle.

## Project placement

Add `.cursor/rules/scs-<bundle-name>.mdc` with `alwaysApply: true`:

````markdown
---
description: SCS Project governance, bundle:<name> <version>
alwaysApply: true
---

```yaml
<the compiled artifact, unchanged>
```
````

The file must use `.mdc`. A plain `.md` file in `.cursor/rules` is ignored by the rules system.
If the repository already uses `AGENTS.md` for other agents, the artifact can go there instead.
Cursor reads `AGENTS.md` at the project root.

Avoid the "Apply Intelligently" and "Apply to Specific Files" types for governance. Those types
include a rule only when the agent judges it relevant or a matching file is involved.

## Known limits

- Team Rules need a Team or Enterprise plan.
- The page suggests keeping rules under 500 lines. It gives no hard size limit.
- Rules do not apply to Cursor Tab or other AI features outside Agent.
- Files referenced from a rule are not inlined into context. The page says this is the same in
  the editor, the CLI, and Cloud Agents. Place the artifact's text in the rule itself, not a
  link to it.
