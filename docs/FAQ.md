
# Structured Context Specification — FAQ (Version 0.3)

Medium‑length, complete (but not deep‑dive) answers.
Expanded set: ~20 questions.

---

## 1. What is "context" in AI-assisted development?

Context is the information an AI system uses to understand what you are asking it to do and the environment in which it must operate.
For humans, context lives in shared mental models, documents, architecture, conversations, and experience. For an LLM, context only exists in the text it is given in the moment.
If essential intent, constraints, and boundaries are missing, the model improvises—leading to drift, rework, and misalignment.

---

## 2. What is Structured Context?

Structured Context (SCS) is a compact, standardized, machine-readable representation of the essential environment in which development occurs.
It encodes intent, constraints, architecture boundaries, domain rules, and organizational expectations into a form that fits inside an LLM's context window.
SCS ensures that humans and AI share the same foundational understanding before any code is generated.

---

## 3. Why do we need Structured Context?

Modern AI-assisted development fails not because the models are inadequate, but because **the environment they operate in is undefined**.
Teams rely on implicit context—tribal knowledge, scattered documents, personal assumptions—that AI cannot access.
SCS makes this environment explicit, structured, and shareable. As a result, AI and humans behave consistently, and development becomes predictable rather than improvisational.

---

## 4. What problems does SCS solve?

SCS addresses key failure modes in AI-assisted development:

- Misaligned or inconsistent AI output
- Requirements and architectural drift
- Rework caused by unclear constraints
- Conflicting interpretations across tools and developers
- Lack of traceability or governable context
- Inability to automate compliance or architectural checks

By defining the environment up front, SCS stabilizes downstream work.

---

## 5. What do we expect SCS to achieve?

SCS is designed to produce:

- Reliable AI-assisted Build Phase behavior
- Clear alignment between humans and AI
- Reduced rework and fewer corrections
- Stronger architectural and compliance consistency
- Portable organizational knowledge
- A foundation for future autonomic governance

SCS does not solve every development challenge, but it eliminates the biggest source of unpredictability: missing or inconsistent context.

---

## 6. Is Structured Context the application?

No.
SCS is not the application—it is the **environment** that governs how the application is built.
The application includes code, architecture, runtime behavior, and infrastructure.
SCS simply defines the intent, rules, boundaries, and constraints that guide development.

---

## 7. How is SCS different from requirements documents or architecture diagrams?

Traditional documentation is written for humans—often verbose, ambiguous, and scattered across many tools.
SCS is a **minimal, structured, versioned contract** that LLMs can interpret consistently.
It distills what matters most into a machine-readable form, without replacing richer human-readable documentation.

---

## 8. Why are SCDs inflexible?

SCDs are intentionally inflexible because they function as contractual elements of the project's environment.
Each SCD defines exactly one concept—business rule, architectural constraint, domain definition—and must remain stable once versioned.
This rigidity prevents silent drift and ensures humans and AI always operate from the same authoritative definition.

---

## 9. What is an SCD?

An **SCD (Structured Context Document)** is the atomic unit of structured context.
Each SCD is written in YAML or JSON and expresses one essential idea: a definition, rule, constraint, requirement, boundary, or domain concept.
Hundreds of SCDs across multiple categories build the operating environment for the project.

---

## 10. What are Meta, Standard, and Project SCDs?

**Meta SCDs** define how SCS itself works—schemas, rules, semantics.
**Standard SCDs** encode organizational or domain best practices (e.g., security, UX, compliance).
**Project SCDs** express system-specific rules and intent.
Together, they allow organizations to build reusable libraries while customizing context for each project.

---

## 11. What is a Bundle?

A **Bundle** is a versioned manifest of versioned SCDs.
Bundles assemble SCDs into a complete operating environment used by AI tools during the Build Phase.

**The 4 Bundle Types:**

1. **Project Bundle** (type: `project`)
   Top-level orchestrator that imports all other bundles. Contains imports only, no SCDs directly.

2. **Meta Bundle** (type: `meta`)
   Provides SCS foundational vocabulary and semantic structure. Imported from the SCS specification.

3. **Standards Bundle** (type: `standards`)
   Captures compliance and regulatory requirements. May import other standards bundles.

4. **Domain Bundle** (type: `domain`)
   Organizes project-tier SCDs by concern area. Projects require 11 prescribed domain bundles (minimum).

Every project uses all 4 bundle types to express everything needed for consistent AI-assisted development.

---

## 12. What are Domain Bundles and why are they important?

**Domain Bundles** organize project-tier SCDs by concern area, with patterns derived from established frameworks such as TOGAF, Zachman, FEAF, ISO/IEC 25010, and NIST RMF.

**The 11 Prescribed Domains:**

1. Architecture
2. Security
3. Performance & Reliability
4. Usability & Accessibility
5. Compliance & Governance
6. Data & Provenance
7. Testing & Validation
8. Deployment & Operations
9. Safety & Risk
10. Ethics & AI Accountability
11. Business Context

Every production project must include all 11 domain bundles (minimum) to ensure comprehensive coverage of all major concern areas. Instead of inventing new categories, SCS mirrors well-known enterprise frameworks—ensuring completeness and credibility.

---

## 13. How does SCS fit inside an LLM context window?

Structured Context is intentionally compact—typically 25–35% of the model's window.
This leaves room for task instructions, code, debugging, and conversation.
Compact, structured data is far more salient to LLMs than large narrative documents, resulting in more stable and reliable behavior.

---

## 14. What is the difference between Task Context and Project Context?

**Task Context** is the immediate instruction (e.g., "Create a new API endpoint").
**Project Context** is the durable environment (intent, constraints, definitions, boundaries) that governs how tasks must be completed.
AI failures almost always stem from missing **Project Context**, not unclear instructions.
SCS provides the missing project environment.

---

## 15. How does SCS make the Build Phase reliable?

When a project bundle is loaded into an IDE or AI agent:

- The model knows the constraints
- The model applies domain and architectural rules
- Output becomes consistent across sessions and developers
- Rework decreases significantly

The reference implementation demonstrated a dramatic improvement:
**With a bundle: stable, aligned behavior. Without a bundle: drift and inconsistency.**

---

## 17. Does SCS replace Agile, Scrum, XP, or DevOps?

Not at all.
SCS operates **upstream** of all methodologies. It defines the environment in which those methods run.
Teams continue using Agile ceremonies, DevOps pipelines, CI/CD, and testing practices—but with far clearer boundaries and constraints.

---

## 18. Can SCS work with RAG or documentation retrieval?

Yes, but RAG cannot substitute for SCS.
RAG retrieves unstructured information—useful for reference but not for governance or consistent application of constraints.
SCS provides the authoritative project environment, while RAG supplements it with supporting materials.

---

## 19. How does versioning work in SCS?

Each SCD and Bundle has an explicit version.
Once versioned, an SCD becomes part of the project contract and should not change except through deliberate version increments.
Versioning enables reproducibility, traceability, and stable Build Phase behavior.

---

## 20. Is Structured Context required for autonomic governance?

Yes.
Autonomic (future AI-driven) governance requires an explicit, machine-readable environment.
Without structured context, AI systems cannot validate architectural choices, enforce compliance, or detect drift.
SCS provides the substrate that future governance tools will rely upon.

---

## 21. Does SCS make development slower?

No—SCS shifts work **upstream**, reducing far more downstream rework, drift, and correction cycles.
Teams report smoother Build Phases, fewer misunderstandings, more consistent AI behavior, and faster onboarding.
The time saved over the life of a project is significant.

---

## 22. What does SCS *not* do?

SCS does **not**:

- Build the system
- Replace engineering practice
- Replace architecture documentation
- Specify implementation details
- Replace your backlog or roadmap
- Dictate process or methodology

SCS defines **the environment**, not the implementation.

---

## Version

Version **0.3** — Technical accuracy updates for launch
Updated: 2025-12-09
