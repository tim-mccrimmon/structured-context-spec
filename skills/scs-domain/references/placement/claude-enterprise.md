---
checked: 2026-10-28
---

# Placement: Claude Enterprise (claude.ai)

In the Claude apps, organization instructions give an organization-wide place for a Domain
artifact. Projects give a place for a Project artifact. For Claude Code, see
[claude-code.md](claude-code.md).

## How Claude loads layered context

| Level | Where | Who sets it | Source |
|---|---|---|---|
| Organization instructions | Organization settings > Organization and access > Organization instructions | Owners and Primary Owners | [Set organization instructions](https://support.claude.com/en/articles/14546867-set-organization-preferences) |
| Instructions for Claude (personal) | Account settings, applied to all of a user's conversations | Each user | [Personalization features](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features) |
| Project instructions and knowledge | Inside a project: "Set project instructions", and the knowledge panel | Project owner or editors | [Create and manage projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects) |
| Organization skills | Organization settings > Plugins & skills | Owners | [Provision skills](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization) |

What the docs say about how these combine:

- Organization instructions take precedence over a user's own instructions when the two directly
  conflict. User instructions still apply to anything the organization does not address
  ([Set organization instructions](https://support.claude.com/en/articles/14546867-set-organization-preferences)).
- Project instructions "only apply to chats within that project"
  ([Personalization features](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)).
- The pages checked do not say how organization instructions and project instructions rank
  against each other. They imply that both are in effect in a project chat: organization
  instructions apply to "every conversation across your organization", and project
  instructions apply to that project's chats. A Domain layer and a Project layer can therefore
  both be active. Precedence between them is not documented.

## Domain placement

- **Organization.** Paste the artifact into **Organization instructions**. This field is
  limited to 3,000 characters, and changes can take up to an hour to apply "across Claude
  products" ([Set organization instructions](https://support.claude.com/en/articles/14546867-set-organization-preferences)).
  Many Domain artifacts will be longer than that. For example, the two-tier example's Domain
  artifact is about 3,300 bytes. If yours does not fit, render a compact form that keeps the
  identity header, the identity rule, and every prohibition and directive with its id. Do not
  drop rules silently. If the result still does not fit, the Domain bundle may be larger than
  this placement can carry. That is a decision for the bundle's owner, not for the rendering.
- **One person.** A personal Domain fits **Instructions for Claude**, which applies to all of
  that user's conversations
  ([Personalization features](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)).
  The pages checked give no character limit for it.

**Skills are a poor fit for governance that must always apply.** The provisioning article
describes Claude choosing a skill based on its description. Users can also switch provisioned
skills off for themselves
([Provision skills](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization)).

## Project placement

Put the Project artifact in **project instructions** for the project that holds the work
([Create and manage projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)).
That article gives no character limit for project instructions.

Instructions are a better home than project knowledge:

- For paid plans, knowledge switches to retrieval (RAG) when it nears the context limit, so a
  knowledge file may not be read in full
  ([Create and manage projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)).
- The upload article lists JSON and TXT as document types but does not list YAML or Markdown
  ([Upload files](https://support.claude.com/en/articles/8241126-upload-files-to-claude)). To
  attach the artifact as a file, compile it as JSON or upload it as `.txt`.

Team and Enterprise projects can be shared with named members or the whole organization, unless
an admin has turned project sharing off
([Create and manage projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)).

**Form.** Project instructions take text, so the YAML can be pasted as-is, which keeps every
field. If you render it, keep the identity header
([README](README.md#keep-the-identity-in-any-rendering)).

## Known limits

- Organization instructions: Team and Enterprise plans only. 3,000 characters. Only Owners and
  above can view or edit them. They cannot override Claude's safety behaviour. The article
  warns that behaviour may vary when instructions directly contradict each other
  ([Set organization instructions](https://support.claude.com/en/articles/14546867-set-organization-preferences)).
- Projects are on every plan. Free accounts are limited to five
  ([Create and manage projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)).
- Project knowledge files are limited to 30 MB each. The number of files is unlimited, but the
  total content must fit the context window
  ([Upload files](https://support.claude.com/en/articles/8241126-upload-files-to-claude)).
- The organization-instructions article does not list which surfaces honour the setting, such as
  web, desktop, mobile, or Claude Code. It says only "across Claude products"
  ([Set organization instructions](https://support.claude.com/en/articles/14546867-set-organization-preferences)).
  To confirm, ask the agent which governance bundles are active.
