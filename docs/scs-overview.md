# Structured Context Specification (SCS) — One-Page Overview

## The Problem

AI systems are increasingly embedded in professional work — writing code, drafting contracts, analyzing data, supporting clinical decisions. But they operate without an explicit understanding of the environment they're working in: your architecture, your compliance obligations, your business rules, your constraints.

The result is familiar: AI that produces confident output that doesn't fit. Not because the model is inadequate, but because the context it needs is scattered across documents, wikis, emails, tribal knowledge, and chat history. It drifts. It conflicts. It can't be validated or versioned.

## What SCS Is

The **Structured Context Specification** is an open, community-driven specification for representing agent context as structured, versioned artifacts. It defines a standard format for capturing professional knowledge — rules, boundaries, constraints, domain concepts, compliance requirements — in a way that is:

- **Concise** — focused, atomic definitions (not walls of text)
- **Precise** — structured YAML (not ambiguous prose)
- **Non-conflicting** — explicitly composed and validated
- **Versionable** — git-native, reviewable, auditable
- **Reusable** — composable across projects, teams, and organizations

SCS is not a prompt engineering framework, a RAG system, or an agent runtime. It is a specification for making context a first-class artifact — alongside code, tests, and infrastructure.

## Core Concepts

**Structured Context Documents (SCDs)** are the atomic building blocks. Each SCD captures a single concern — an architecture decision, a compliance obligation, a business rule — in a structured YAML format with independent versioning and provenance tracking.

**Bundles** organize SCDs into composable packages. Five bundle types form a hierarchy:

| Bundle Type | Purpose | Who Owns It |
|---|---|---|
| **Meta** | Universal SCS vocabulary | SCS maintainers |
| **Standards** | External compliance (HIPAA, SOC2, etc.) | Standards bodies |
| **Concern** | Functional area (Security, Architecture, etc.) | Department leads |
| **Domain** | Organization-wide aggregator | CTO / CIO |
| **Project** | Individual initiative | Product / Project managers |

A project bundle imports a domain bundle, which imports concern bundles, which reference standards — giving every AI interaction access to the full organizational context through a single entry point.

## Who It's For

- **Development teams** building with AI-assisted tools (Cursor, Claude Code, Copilot)
- **Standards organizations** packaging compliance requirements for machine consumption
- **Enterprises** governing AI behavior across teams and projects
- **Any industry** — healthcare, finance, legal, government, software

## Current Status

SCS is at **version 0.3** with working tooling (CLI, validators, schema definitions), examples, and templates. It is open source under the Apache 2.0 license and actively seeking community contributors.
