---
checked: 2026-10-28
---

# Placement: ChatGPT Enterprise

**Verification note.** OpenAI's Help Center (`help.openai.com`) returned HTTP 403 to every fetch
on the checked date. Claims sourced to it below come from search-result excerpts of those pages,
not from reading the pages. Each one is marked *(unconfirmed)*. Claims marked *(fetched)* come
from OpenAI pages that were read in full. Read the linked pages yourself before acting on an
unconfirmed claim.

## How ChatGPT loads layered context

| Level | Where | Status |
|---|---|---|
| Workspace instructions | Workspace settings > General, set by owners and admins | *(unconfirmed)*: release notes and admin quickstart excerpts ([release notes](https://help.openai.com/en/articles/10128477-chatgpt-enterprise-and-edu-release-notes), [admin quickstart](https://help.openai.com/en/articles/20001264-chatgpt-enterprise-admin-quickstart)) |
| Custom instructions (personal) | Each user's personalization settings | *(fetched)*: "preferences you want ChatGPT to follow across chats" ([Personalize](https://learn.chatgpt.com/codex/personalize)) |
| Project instructions and sources | Inside a project | *(fetched)*: "Project instructions apply across its chats". Files sit in the project's Sources ([Projects and chats](https://learn.chatgpt.com/codex/projects)) |
| `AGENTS.md` (Codex) | `~/.codex/AGENTS.md`, then each directory from the project root down to the working directory | *(fetched)*: concatenated root-down. Later files override earlier ones ([AGENTS.md](https://learn.chatgpt.com/codex/agent-configuration/agents-md)) |

What could and could not be confirmed:

- **Workspace and project instructions.** No page we could read describes how workspace
  instructions combine with personal or project instructions.
- **Project instructions may override personal ones.** A search excerpt of the official Projects
  article says project instructions "will override your global custom instructions"
  *(unconfirmed)*. If that is current, a Domain placed only in personal custom instructions may
  not hold inside a project. The workspace-instructions route may avoid this, but its behaviour
  inside projects is also unconfirmed.
- **Codex.** Within Codex, a global `AGENTS.md` and a repository `AGENTS.md` are both loaded
  *(fetched)*.

## Domain placement

- **Organization.** Use **workspace instructions**, if your workspace has them *(unconfirmed)*.
  Paste the artifact or a rendering with the identity header
  ([README](README.md#keep-the-identity-in-any-rendering)). Then ask, both in a plain chat and
  inside a project, which governance bundles are active, to see where it applies.
- **One person.** Use personal **custom instructions** *(fetched, as a feature)*. Bear in mind the
  possible project override above.
- **Codex.** Put the Domain artifact in `~/.codex/AGENTS.md` *(fetched)*. For several Domains,
  place each in an `AGENTS.md` at the root of that Domain's repositories. Codex reads only from
  the project root down, so an `AGENTS.md` above the Git root is not read. That means one copy per
  repository *(fetched)*.

## Project placement

- **ChatGPT.** Put the artifact in the project's **instructions**. That keeps it in force across
  the project's chats *(fetched)*. Adding it to the project's Sources as a file is an option, but
  the pages read do not say whether files are always read in full.
- **Codex.** Put it in the repository's `AGENTS.md` *(fetched)*.

## GPTs

An aggregator of OpenAI's release notes reports that new custom GPT creation was disabled in
Enterprise workspaces other than FedRAMP on 2026-10-26, with plugins as the replacement. This is
a secondary source ([releases.sh](https://releases.sh/openai/chatgpt-enterprise-edu-release-notes)),
*(unconfirmed)* against OpenAI's own page. Admins control who can create GPTs and how they are
shared ([GPTs and sharing](https://learn.chatgpt.com/codex/enterprise/gpts-and-sharing),
*fetched*). We do not suggest GPTs as a new placement.

## Known limits

- Codex stops adding `AGENTS.md` content once the combined size reaches `project_doc_max_bytes`,
  32 KiB by default ([AGENTS.md](https://learn.chatgpt.com/codex/agent-configuration/agents-md),
  *fetched*).
- We could not confirm from official pages the character limits for custom instructions,
  workspace instructions, or project instructions, or per-plan file limits for projects.
  Third-party figures conflict.
- We could not confirm whether workspace instructions are available on ChatGPT Business as well
  as Enterprise.
