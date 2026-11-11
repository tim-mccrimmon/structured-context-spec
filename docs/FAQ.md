# Structured Context Specification: FAQ (0.7)

---

## What is "context" for an AI assistant?

The information the assistant uses to understand what it is asked to do and the environment it
works in. For a person, context lives in experience, documents, and conversations. For a
language model, it exists only in the text it is given. When the rules, boundaries, and facts
that matter are missing, the model fills the gap with plausible guesses.

## What is structured context?

Context an organization or a person stands behind: rules, boundaries, and facts, authored
deliberately, reviewed by the people accountable for them, and changed only by a new version.
That separates it from retrieved context, which changes with every query. SCS gives it a
format (SCDs and bundles), a review and versioning process, and a compiled form an AI service
can be given.

## What problems does SCS solve?

- Governance that lives in PDFs and procedures the assistant never sees
- Rules that differ from one chat, tool, or team to the next
- No record of which rules were in force when a piece of work was done
- Rules that nobody owns, so nobody reviews or updates them
- Context that is too long, repetitive, or vague to change what an assistant does

## What is an SCD?

A Structured Context Document: one YAML file about one topic, holding **prohibitions**
(things the assistant must never do, with no conditions), **directives** (rules), and
**facts** (what the assistant should know). Each carries provenance, and may cite the
standard it traces to (`std:iso-13485:2016#7.3.9`). Only those three lists are compiled; the
rest of the SCD is for reviewers. See [Understanding SCDs](scd-guide.md).

## What is a bundle?

A manifest that groups SCDs. A **Domain** bundle holds the governance for all of an
organization's or a person's work; a **Project** bundle holds one project's own rules. A
Domain's rules are grouped into **concept** bundles (security, risk management, client work,
...), each with an owner. The **meta** bundle, published with the spec, tells the assistant
how Domain and Project rules combine and how to treat citations.

## Does a Project import its Domain?

No. Domain and Project bundles are versioned and compiled separately, and either can exist
without the other. At runtime both apply, Domain first. A Project can add rules; it cannot
override the Domain's prohibitions.

## Do I write the YAML myself?

You can, but most people use the Agent Skills: an AI assistant drafts the SCDs from your
documents and answers, shows you each change, and runs the engine to validate, version, and
compile. See the [Quick Start](quick-start-guide.md).

## What is an ontology, and which one do I pick?

An Ontology Model is the starting set of concepts and template SCDs for a type of business:
`sdlc` (software development, the default), `cdmo` (medical-device contract manufacturing),
`mca` (merchant cash advance), and `personal` (one person). Pick the nearest one, keep what
applies, retire the rest, and add your own concepts.

## How are standards and regulations handled?

By citation only. A rule cites `std:<standard>[:<edition>][#<clause>]`, for regulations as
well (`std:21-cfr-820`, `std:eu-ai-act-2024-1689`). Standard text is never copied into SCS,
and the compiled artifact tells the assistant not to present wording from memory as the text
of a cited standard. See [Citations](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/citations.md).

## How does versioning work?

Each workspace is DRAFT until it is released. A release versions every changed concept
bundle and then the Domain or Project bundle. Each version is a git tag, on a commit with a
snapshot and a manifest naming the approver and the content digest (a SHA-256 of the
content). A version is never overwritten; a change means a new version. The compiled artifact
carries the digest as `source_digest`, so anyone can check which approved version an AI
service was given. See [Bundle Lifecycle](bundle-lifecycle.md).

## Who reviews and approves the context?

Each section (concept bundle) names an owner role, such as `quality` or `regulatory`, and the
intake record names the person who holds it. Owners review the draft through an HTML review
package (`scs view`). The person who releases a version is recorded as its approver. Formal
approval in a quality system stays there: the approval record cites the version and digest.

## How big is the compiled artifact?

Small by design: prohibitions, rules, and facts, with no commentary. A Domain drafted from a
policy and a standards list is typically around a hundred lines. Consolidation before review
merges duplicates and moves reference material out of the rules.

## How does the artifact reach an AI service?

That is the owner's decision; SCS ends at the compiled artifact and does not place it. The
non-normative [placement guide](placement/README.md) describes what common services (Claude,
Claude Code, Cursor, Copilot, and others) can load and their size limits.

## Can SCS work with RAG?

Yes. Retrieval supplies documents relevant to a query; SCS supplies the rules that apply to
every query. A runtime can deliver both.

## What does SCS not do?

- It is not a prompt framework, a RAG system, or an agent runtime.
- It does not place artifacts in AI services or transform them for a vendor.
- It does not provide multi-user approval workflows or a hosted registry.
- It does not select or stream context at request time. That is a runtime's job, built on
  the artifacts SCS produces.

---

## Version

This FAQ describes SCS 0.7.0. Normative definitions are in
[Terminology](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/terminology.md).
