# Open Questions — Structured Context Specification (SCS)

This document captures **unresolved questions** the community is actively invited to debate.
None of these are settled. If you think the framing is wrong, that itself is valuable input.

---

## Foundational

- What *must* be explicit for reliable AI behavior?
- What information should **never** be considered “context”?
- Is context descriptive, prescriptive, or both?
- Is context something an AI *uses* or something it must *conform to*?

---

## Boundaries

- Where does **context** end and **memory** begin?
- What belongs in context vs prompt vs tool schema vs RAG payload?
- Should retrieved documents ever be treated as first-class context artifacts?
- Can context reference other context dynamically, or must it be static?

---

## Structure & Scope

- How much structure is enough before usability suffers?
- What is the smallest “Core” spec most teams could agree on?
- Should context be hierarchical, graph-based, or both?
- What invariants must always hold true?

---

## Lifecycle

- Should context be immutable per execution? per task? per session?
- How should context versioning interact with runtime behavior?
- What constitutes “context drift” and how can it be detected?

---

## Validation & Tooling

- What can realistically be validated automatically?
- What must remain human-reviewed?
- Where is schema validation sufficient, and where is semantic validation required?

---

If you want to propose a concrete change, open a Discussion or RFC.
If you want to add a question, submit a PR to this file.
