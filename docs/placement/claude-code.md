---
checked: 2026-10-28
---

# Placement: Claude Code

Claude Code reads instructions from `CLAUDE.md` files and `.claude/rules/` at several levels and
loads them together. That gives a natural place for each artifact. Claims below come from
[How Claude remembers your project](https://code.claude.com/docs/en/memory) (cited as *Memory*)
unless another link is given.

## How Claude Code loads layered context

| Level | Location | Scope |
|---|---|---|
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux and WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md`; or the `claudeMd` key in managed settings | All users on the machine |
| User | `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md` | You, all projects |
| Ancestor directories | `CLAUDE.md` / `CLAUDE.local.md` in each directory above the working directory | Everything below that directory |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md`, `./.claude/rules/**/*.md` | The repository |
| Local | `./CLAUDE.local.md` (gitignored) | You, this project |

All of these are covered in *Memory*:

- **Concatenated, not overridden.** Files are combined rather than one replacing another. They
  load from broadest scope to most specific, so project content appears after user content.
- **Directory order.** Across the directory tree, content runs from the filesystem root down to
  the working directory.
- **Rules.** User rules load before project rules. Rules without `paths` frontmatter load at
  launch with the same priority as `.claude/CLAUDE.md`.
- **Conflicts.** When instructions contradict each other, "Claude may pick one arbitrarily". A
  user rule and a project rule do not override each other.
- **Seeing what loaded.** `/context` shows which `CLAUDE.md` and rules files loaded at launch.

A Domain layer and a Project layer can therefore both be active in one session.

## Domain placement

- **Organization.** Use the managed policy `CLAUDE.md`, distributed by MDM, Group Policy, or
  similar, or the `claudeMd` key in managed settings (*Memory*, "Deploy organization-wide
  CLAUDE.md"). Developers cannot exclude this file with `claudeMdExcludes`. The docs also note
  that a session started with CLAUDE.md loading turned off does not load it.
- **One person, one Domain.** Use `~/.claude/rules/<bundle-name>.md`, which applies to every
  project on the machine.
- **One person, several Domains.** Put each Domain where it covers only that Domain's work. One
  way is a `CLAUDE.md` in the parent directory of that Domain's repositories, for example
  `~/Projects/work/CLAUDE.md`. Ancestor files load for every session started below them
  (*Memory*, "How CLAUDE.md files load").

**Form.** The artifact can stay as YAML. A `CLAUDE.md` can import a file with `@path/to/file`,
and the docs' own examples import non-Markdown files such as `@package.json` (*Memory*, "Import
additional files"). For example, the line `@~/governance/dist/medtech-cdmo-1.0.0.yaml` pulls the
YAML in unchanged. Imports outside the working directory need a one-time approval in project
files, but not in user-scope files (*Memory*). Files in `.claude/rules/` must be `.md`. To use a
rule file, put the YAML in a fenced block, or render it and keep the identity header
([README](README.md#keep-the-identity-in-any-rendering)).

## Project placement

- **Committed with the repository:** `.claude/rules/scs-<bundle-name>.md` with no `paths`
  frontmatter, so it loads at launch. RFC 0002 section 3 uses this example. Alternatively, add
  `@dist/<bundle-name>-<version>.yaml` to the project's `CLAUDE.md`.
- **Personal, not committed:** `CLAUDE.local.md` in the project root.

Avoid `paths:` frontmatter for governance rules. A path-scoped rule loads only when Claude works
with matching files (*Memory*, "Path-specific rules").

## AGENTS.md

Claude Code reads `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md`
exists in the working directory or above it, unless the **Project instructions** setting is
changed. Managed and user `CLAUDE.md` files and `.claude/rules/` still load alongside it. Reading
`AGENTS.md` directly needs v2.1.277 or later (*Memory*, "AGENTS.md"). If several tools share one
repository, an `@AGENTS.md` import in `CLAUDE.md` loads the same file for all of them.

## Known limits

- The docs suggest keeping each `CLAUDE.md` under 200 lines. Imports help organize content but do
  not reduce its context cost (*Memory*, "Write effective instructions").
- Imports recurse at most four hops (*Memory*).
- `CLAUDE.md` is guidance, not enforcement. To block an action, use hooks or managed settings
  such as `permissions.deny` (*Memory*).
- Symlinks into `.claude/rules/` that point outside the working directory need the
  external-import approval. Network paths do not load at all (*Memory*, "Share rules across
  projects with symlinks").
- Whether claude.ai organization instructions also reach Claude Code sessions is not stated in
  the pages checked. See [claude-enterprise.md](claude-enterprise.md).
