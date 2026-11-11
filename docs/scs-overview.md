# Structured Context Specification (SCS) — One-Page Overview

## The Problem

AI systems are increasingly embedded in professional work — writing code, drafting contracts, analyzing data, supporting clinical decisions. But they operate without an explicit understanding of the environment they're working in: your architecture, your compliance obligations, your business rules, your constraints.

The result is familiar: AI that produces confident output that doesn't fit. Not because the model is inadequate, but because the context it needs is scattered across documents, wikis, emails, tribal knowledge, and chat history. It drifts. It conflicts. It can't be validated or versioned.

## What SCS Is

The **Structured Context Specification** is an open specification for the context an
organization or a person stands behind when AI does their work: rules, boundaries, and facts,
authored deliberately, reviewed by the people accountable for them, and changed only by a new
version. It is designed to be:

- **Concise**: focused, atomic statements, not walls of text
- **Precise**: structured YAML, validated against schemas and rules
- **Reviewable**: each section has an owner who reviews and approves it
- **Versioned**: every version is a git tag with an approver and a content digest
- **Portable**: compiled into one artifact any AI service can be given

SCS is not a prompt engineering framework, a RAG system, or an agent runtime. It ends at a
validated, versioned bundle and its compiled artifact; placing that artifact where an AI
service reads it is the owner's decision.

## Core Concepts

**Structured Context Documents (SCDs)** are the building blocks. An SCD holds
**prohibitions** (binary, never conditional), **directives** (rules), and **facts** about one
topic, with provenance and citations to the standards they trace to (`std:iso-13485:2016#7.3.9`).
Standard text is never copied into SCS.

**Bundles** group SCDs:

| Bundle | Purpose | Who owns it |
|---|---|---|
| **Domain** | Governance for all of an organization's or a person's work (often called Global) | The organization's governance or quality team, or the person |
| **Project** | One project's own rules | The project team |
| **Concept** | One concept of the Domain Ontology (security, risk management, ...) | The role named as its owner |
| **Meta** | Universal SCS vocabulary, published with the spec | SCS maintainers |

A Domain bundle imports the meta bundle and its concept bundles. A Project bundle never imports
the Domain: the two are versioned and compiled separately, and at runtime a Project inherits
its Domain's rules. Each is compiled into a **runtime artifact**, a short YAML file of rules
and facts.

A **Domain repository** holds one Domain and its Projects, in git. Industry **Ontology Models**
(software development, medical-device CDMO, merchant cash advance, personal) supply the
starting concepts and template SCDs.

## How It Is Used

Most people use SCS through the **Agent Skills** (`scs-domain`, `scs-project`,
`scs-validate`, `scs-explain`): an AI assistant drafts the context from your documents and
your answers, walks the owners through review, and releases and compiles a version, with you
confirming each change. The skills run the SCS engine (`scs`, `scs-validate`), which can
also be used directly.

## Who It's For

- **Regulated organizations** that need AI to follow their quality system, and need to show
  which rules were in force
- **Teams** using AI assistants (Claude, Cursor, Copilot, Codex) on governed work
- **Individuals** who want their own boundaries and preferences applied consistently
- **Any industry**: healthcare, medical devices, finance, legal, software

## Current Status

SCS **0.7** is in development: agent-mediated authoring through the Agent Skills, Domain
repositories with git-tag versions, section owners, and review packages. 0.6.0 is the latest
release. Open source under the Apache 2.0 license.
