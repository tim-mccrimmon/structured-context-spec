# SCS 0.5.0 — The "Any AI Actor" Model
**Version:** 0.5.0 (Draft)
**Status:** Work in Progress
**Last Updated:** 2026-09-22
**Tracking:** `ISSUES.md` ISS-006 (ROADMAP.md workstream 2)

---

## 1. Purpose

This document defines how structured context applies to **any AI runtime** — a chat
assistant, an autonomous agent, an MCP tool invocation, a step in a multi-agent workflow —
with chat as one case among several, not the model everything else is described relative to.

It covers three things: how context gets *selected* for a given actor (§2), how a tool or
MCP server's permitted operations become governed context in their own right (§3), and how
a workflow records which context version actually governed a given step (§4).

---

## 2. Context Scoped to Agent + Intent

### 2.1 Why Not "Session"

A session is a record of what has happened so far in a particular execution — a
conversation history, an in-progress agent's scratchpad, a workflow's current step. That is
**state**, not context (see §2.2): it is produced at runtime, it is specific to one
execution, and there is no decision behind it worth preserving once the session ends.

Resolving *which governed context applies* by keying off the session would conflate the two
categories the rest of this document depends on keeping separate. A session tells you what
already happened. It does not tell you what rules should apply next.

### 2.2 Context vs. State

This distinction is normative for how SCS content should be reasoned about, though it is
not itself a schema element:

| | Context (SCS) | State (not SCS) |
|---|---|---|
| **What it is** | A decision: someone chose it, and it holds until someone deliberately changes it | A fact about right now: nobody decided it, it just is |
| **Test** | Meaningful to ask "was this true yesterday, and who decided it?" | The question doesn't apply — "yesterday's balance" is just a different fact |
| **Lifecycle** | Versioned, approved, governed (RFC-0001) | Looked up fresh; not versioned because there is no decision history |
| **Trigger** | Present for every prompt in the domain, regardless of wording | Present only because the specific prompt's wording demanded a lookup |
| **Owner** | SCS defines it | The runtime / a tool call resolves it (paepae, MCP, application code) |

A prompt is a third, distinct thing from both: it is the literal ask, word for word, as
entered. Context does not answer the prompt; it bounds what an answer is allowed to look
like. State is what a *specific* prompt's wording forces the runtime to go fetch.

### 2.3 The Resolution Key

Given the above, structured context is resolved by **(agent, intent)** — which kind of
actor is asking, doing what kind of task — not by session, and not by the literal wording
of the prompt. This is a request-level classification, made *before* anything about the
specific prompt's content is examined:

1. **Agent** — a `role:` (meta-tier vocabulary, already defined) or an equivalent actor
   identity: which agent, running under which capabilities, is making this call.
2. **Intent** — which task or workflow step is being performed. Scoped to a `concept:` (or
   a set of concepts) in the active domain's ontology, since a concept is already the unit
   a domain organizes its guardrails around.

`(agent, intent)` resolves to a set of concept bundles — the governed context that applies
regardless of what the specific prompt says, as long as the agent+intent classification
holds. This is the same key used for the checkpoint record in §4 — recording which context
applied is the same lookup as selecting it, just performed after the fact.

---

## 3. Policy-as-Context

### 3.1 What This Is

A tool or MCP server's permitted operations are themselves governed context, not a runtime
implementation detail. "This role may fetch data from the risk register, read-only" is a
decision with the same shape as any other guardrail — it should be authored, versioned, and
approved the same way.

### 3.2 Why a Policy SCD, Not a Relationship

A concept's `relationships[]` (RFC-0001) carries only a type and a target — enough for
`depends-on`/`relates-to`/`satisfies`, not enough for a real permission, which needs *who*
(a role), *what scope* (which resource), and often a condition (read-only, requires
approval). That is exactly the shape an SCD already carries. Policy-as-context is therefore
a **project-tier SCD content pattern** — a new named pattern alongside Architecture,
Security, and the others in `project-tier.md` §5 — not a new relationship type.

```yaml
id: scd:project:policy-risk-management-readonly
type: project
title: "Risk Management — Read-Only Access Policy"
version: "DRAFT"
concept: concept:risk-management
description: >
  Defines which roles may access risk-management data, and under what constraints.

content:
  applies_to_roles:
    - role:quality-engineer
  permitted_operations:
    - capability: fetch-data
      resource: risk-register
    - capability: write-data
      resource: risk-register
      requires_approval: true

provenance:
  created_by: jane@nextern.com
  created_at: "2026-09-22T00:00:00Z"
```

`concept:` (already an optional field on every SCD, RFC-0001) is what answers "for what
purpose" — the concept a policy is attached to *is* the purpose. `applies_to_roles`
answers "for who," reusing the meta-tier `role:` vocabulary that already exists. Neither
needed a new field.

### 3.3 Tool Identity: Capability Class, Not Endpoint

A permitted operation is named at the **capability-class** level — `fetch-data`,
`execute-code`, `query-db`, `write-data`, `send-communication` — not by a specific MCP
server or endpoint name. A specific tool binding (which MCP server, which exact function)
is an implementation detail that can change per deployment or vendor without the underlying
decision changing at all; naming it directly in a policy SCD would tie a governance
decision to something closer to state than to context, the same category error as baking a
live account balance into a guardrail.

**Default capability classes:** `fetch-data`, `execute-code`, `query-db`, `write-data`,
`send-communication`. A domain MAY extend this set (e.g., a CDMO domain adding
`dispose-controlled-substance`) — the same mechanism as `ontology.relationship_types[]`
restricting or extending the default relationship set (RFC-0001).

### 3.4 Enforcement Is Not SCS's Job

A policy SCD is a declaration, not an enforcement mechanism. Something specific to the
runtime — a compiler, the same kind of function that turns SCDs into `.claude/rules/*.md`
(`scs-team`'s recompile step) — reads the policy SCD and produces whatever the actual tool
registry needs: a LangChain tool allow-list, an MCP gateway's permission gate, an OPA
policy. The registry, once populated, enforces the permission the moment an agent tries to
call a tool. **SCS defines what is permitted. It never enforces it directly, and it does
not need to know which specific mechanism will.**

If the runtime changes — a new orchestration framework, a different MCP gateway — only the
compilation step changes. The policy SCD, and the decision it records, does not.

---

## 4. Context Pinned at a Workflow Checkpoint

### 4.1 Scope: SCS Does Not Model Workflows

Steps, transitions, which agent runs when, how a payload moves between agents — this is
orchestration, and it belongs to the runtime (paepae, or an equivalent orchestrator), not
to SCS. SCS has no artifact type for "workflow" and does not need one.

### 4.2 What SCS Does Define: the Checkpoint Record

What SCS defines is the **shape of a record** answering, after the fact: "which version of
which context governed this point in execution?" This makes an audit trail possible without
requiring SCS to understand or model the workflow that produced it.

A checkpoint record is not an SCD. It is not authored once and referenced repeatedly the
way a bundle is — it is generated fresh on every execution, potentially in high volume, and
carries none of an SCD's authoring ceremony (no content schema, no tier, no relationships).
It is closer to a structured log line than a document: a small, normative shape any runtime
can emit and any auditor or tool can read, regardless of which orchestrator produced it.

```yaml
checkpoint:
  bundle: bundle:risk-management:1.2.0
  concept: concept:risk-management
  agent: role:quality-engineer
  intent: hazard-analysis-review
  timestamp: "2026-09-23T10:00:00Z"
  workflow_ref: "workflow:release-review/run-4821/step-3"
```

| Field | Req | Notes |
|---|---|---|
| `bundle` | yes | The exact bundle id + version that was in effect (`bundle:<name>:<version>`) |
| `concept` | recommended | Which concept's context this checkpoint reflects |
| `agent` | yes | The `role:` (or equivalent actor identity) this checkpoint applies to — §2.3 |
| `intent` | yes | The task/step being performed — §2.3. Same field, same value, as what was used to *select* this context in the first place |
| `timestamp` | yes | ISO-8601, when this checkpoint was recorded |
| `workflow_ref` | no | Opaque, orchestrator-defined. SCS does not interpret this — it exists so the record can be traced back to whatever the runtime calls "the workflow," without SCS needing a model of what a workflow is |

`agent` and `intent` are deliberately the same two fields used to resolve context in §2.3.
Selecting context and recording which context was selected are the same lookup, performed
at two different times.

### 4.3 What This Enables

Given a store of checkpoint records, a question like "which version of the risk-management
context governed step 3 of run #4821?" has a real, machine-answerable answer — the same
auditability instinct behind `version_approved_by` (RFC-0001), applied to *use* of a bundle
rather than to its authoring.

---

## 5. Consumers, Not Targets

Claude Code's `.claude/rules/` is one consumer of SCS content — a composition step that
turns governed context into the shape one specific tool expects. It is not the model SCS is
designed around. The same governed content composes just as validly into:

- An MCP server's permission gate, driven by a policy SCD (§3.4)
- A LangGraph node's system prompt, or any other orchestrator's per-step context injection
- A checkpoint record in an audit trail (§4.2)

Each of these is a *composer*: a function, specific to one consumer, that reads governed
SCS content and produces whatever that consumer needs. SCS's job stops at the governed
content. Composition is always the consumer's job, and there is always more than one
consumer.

---

## 6. Open Questions

- **Capability-class taxonomy governance** — whether the default set (§3.3) should live in
  a formal registry SCS maintains, or purely as spec-documented convention that domains
  extend informally.
- **Checkpoint record storage and validation** — whether `scs validate` should gain formal
  support for checking a checkpoint record against its schema (a lightweight addition,
  given the shape is intentionally small), or whether validation of these records is
  entirely the runtime's responsibility since they're generated, not authored.

---

## 7. Feedback

Feedback on the Any AI Actor model should be submitted via GitHub Issues, referencing
ISS-006.
