---
checked: 2026-10-28
---

# Placement: GitHub Copilot

Copilot reads instructions from several places. Which ones a session uses depends on the
surface: GitHub.com, an IDE, or the CLI. Check the support table before choosing. Sources:

- [About custom instructions](https://docs.github.com/en/copilot/concepts/prompting-and-context/custom-instructions)
  (*Concepts*)
- [Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)
  (*Support*)
- [Repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
  (*Repository*)
- [Organization instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-organization-instructions)
  (*Organization*)
- [Personal instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-personal-instructions)
  (*Personal*)
- [Copilot CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
  (*CLI*)
- VS Code [custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
  (*VS Code*)

## How Copilot loads layered context

| Level | Where | Read by |
|---|---|---|
| Organization | Org Settings > Copilot > Custom instructions (*Organization*) | GitHub.com Chat, cloud agent, and code review (*Support*) |
| Personal | GitHub.com Copilot Chat > profile picture > Personal instructions (*Personal*); `~/.copilot/copilot-instructions.md` and `~/.copilot/instructions/*.instructions.md` (*CLI*, *VS Code*) | GitHub.com Chat, JetBrains Chat, and Copilot CLI (*Support*); VS Code local sessions (*VS Code*) |
| Repository-wide | `.github/copilot-instructions.md` (*Repository*) | Every surface in the support table except Eclipse code review, which supports no custom instructions (*Support*) |
| Path-specific | `.github/instructions/**/*.instructions.md` with `applyTo` (*Repository*) | Most surfaces; not GitHub.com Chat, Eclipse Chat, or VS Code and Visual Studio code review (*Support*) |
| Agent files | `AGENTS.md` anywhere (nearest wins), or a root `CLAUDE.md` / `GEMINI.md` (*Repository*) | Cloud agent, code review, VS Code Chat (`AGENTS.md` only), and CLI (*Support*) |

How the levels combine:

- **Copilot Chat on GitHub.com.** Personal instructions rank highest, then repository
  instructions, then organization instructions. "All sets of relevant instructions are provided
  to Copilot" (*Personal*, *Concepts*).
- **CLI, VS Code, and Visual Studio.** These clients "combine applicable instruction files
  without defining a general precedence order" (*Concepts*). The CLI removes identical
  duplicates (*CLI*). VS Code calls its sources "additive" (*VS Code*).
- **Both layers.** A Domain layer (organization or personal) and a Project layer (repository) can
  both be active, but only on surfaces that read both levels.

## Domain placement

- **Organization.** Use **organization custom instructions**. They require Copilot Business or
  Enterprise (*Concepts*) and are set by organization owners (*Organization*). The GitHub support
  table lists them for GitHub.com surfaces only, not IDE or CLI sessions (*Support*). The VS Code
  docs say supported sessions can use them when
  `github.copilot.chat.organizationInstructions.enabled` is on (*VS Code*). The two pages
  disagree, so check in your editor by asking which governance bundles are active.
- **One person.** Use `~/.copilot/copilot-instructions.md`, which the CLI and VS Code read, plus
  **Personal instructions** on GitHub.com for Chat there. These cover all of your work, so they
  suit a single personal Domain. For several Domains, the CLI also reads directories listed in
  `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (*CLI*). Setting that per Domain workspace is one way to
  keep each Domain to its own work.

**Form.** Organization and GitHub.com personal instructions are text boxes, so paste the YAML or
a rendering. The `~/.copilot` files are Markdown, so a fenced YAML block works. Keep the identity
header either way ([README](README.md#keep-the-identity-in-any-rendering)).

## Project placement

Use **`.github/copilot-instructions.md`**, the file the most surfaces read: every surface in the
support table except Eclipse code review, which supports no custom instructions (*Support*). Put the artifact in a fenced YAML block, or render it with the identity header.

If the repository already standardizes on `AGENTS.md` for several agents, that file also works on
the surfaces that read it. GitHub.com Chat, Visual Studio, JetBrains Chat, and Xcode Chat do not
(*Support*).

A path-specific file with `applyTo: "**"` is an option for the surfaces that read path-specific
files. It loads only when Copilot works with a matching file (*Repository*).

## Known limits

- Organization instructions: Copilot Business or Enterprise, and GitHub.com surfaces only, per
  *Concepts* and *Support*. See the VS Code exception above.
- GitHub.com personal instructions apply only to Copilot Chat on GitHub.com (*Personal*).
- Code review reads instruction files from the pull request's head branch, not the base branch
  (*Repository*). A change to the Project artifact in a pull request affects that pull request's
  own review.
- The pages checked state no character limit for instruction files. Some third-party sources
  cite a 4,000-character limit for code review. We could not find it in the official pages
  fetched on the checked date, so treat it as unconfirmed.
- In VS Code, nested `AGENTS.md` discovery needs `chat.useNestedAgentsMdFiles`. The docs call it
  experimental and off by default (*VS Code*).
