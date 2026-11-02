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
  On its own that does not prove an import loaded; see [Check the placement](#check-the-placement).

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
files, but not in user-scope files (*Memory*). Until approved, the import does not load and
nothing reports it: the session starts normally and exits 0 (observed in Claude Code 2.1.301,
2026-10-30). The workspace trust prompt comes first, and `claude -p` cannot show the approval
prompt, so a scripted or CI session never loads an unapproved import. Approval appears to be
per project.

This matters for the several-Domains layout above. If the artifact lives in the Domain's
context repository and that repository is a sibling of the code repositories, the parent
`CLAUDE.md` import is external from every one of them, and each needs its own approval. Start
one interactive session in each repository and approve the import before relying on it, then
[check the placement](#check-the-placement).

Files in `.claude/rules/` must be `.md`. To use a
rule file, put the YAML in a fenced block, or render it and keep the identity header
([README](README.md#keep-the-identity-in-any-rendering)).

## Project placement

- **Committed with the repository:** `.claude/rules/scs-<bundle-name>.md` with no `paths`
  frontmatter, so it loads at launch. RFC 0002 section 3 uses this example. Alternatively,
  import the artifact from the project's `CLAUDE.md`. `scs compile` writes it to the context
  repository, at `<name>-context/projects/<project>/dist/<bundle-name>-<version>.yaml`, not to
  the code repository. Import it from there (an external import, which needs approval), or
  copy it into the code repository and import the copy.
- **Personal, not committed:** `CLAUDE.local.md` in the project root.

Avoid `paths:` frontmatter for governance rules. A path-scoped rule loads only when Claude works
with matching files (*Memory*, "Path-specific rules").

## Check the placement

`/context` lists the `CLAUDE.md` and rules files that loaded, but a file can be listed while an
import inside it did not load. A placement passes when both hold in a new session started in
the code repository:

1. `/context` lists the artifact itself: the `.yaml` path for an import, or the rule file.
2. Asked which governance bundles are active, the session returns the exact text of each
   self-identification rule (`<bundle-name>/identity`) without using tools.

The second check matters because a session can name the bundles and versions just by reading
the import paths in `CLAUDE.md`. Only the exact rule text shows the content was loaded.

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
