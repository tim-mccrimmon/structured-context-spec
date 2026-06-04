# Medical-Device CDMO — Context Intake Template

> **Generic.** This template defines what *concrete* context a medical-device CDMO must supply for
> each of the 12 concerns before its context can be authored into SCS bundles. It contains no
> organization-specific values — a specific CDMO records its readiness and its actual rules in its
> own private workspace, against this template.

---

## 1. The bar: what "good context" is

A unit of context is usable in a bundle only if it is all three:

1. **Concrete** — it stipulates an actual limit, rule, value, or boundary. "Use appropriate tools"
   is not concrete; "Client-confidential data may go only to the highest-tier tools" is.
2. **Terminal** — it is self-contained. It does not dangle to a document you don't have. "Per the
   approved-tool register" is a pointer; the register's actual contents are terminal.
3. **Agent-relevant** — it shapes what an AI assistant may, must, or must not do. If no agent
   operates in it, it is not a concern in this domain.

### Readiness states

| State | Meaning | The follow-up |
|---|---|---|
| ✅ **Have it** | Concrete and terminal — ready to author into an SCD | none |
| 🟡 **Pointer** | The rule exists but dangles to an absent artifact | **Retrieve** the artifact |
| ❌ **Gap** | No concrete limit was ever stipulated | **Decide** it — name the decision + an owner |
| ⚪ **N/A** | No agent operates here | record the rationale, move on |

The 🟡-vs-❌ split is the point: **🟡 is a fetch; ❌ is a decision.** Separating them keeps a
"get us better context" request from stalling on the items nobody has decided yet.

### Generic worked example

- ✅ **Good:** a documented, ordered source-precedence hierarchy with explicit conflict-resolution
  rules. Concrete, terminal, near-executable — *the target shape for every SCD.*
- ❌ **Gap:** "outputs must be reviewed for potential bias," with no method, threshold, or trigger.
  Unfalsifiable — an agent can't act on it and an auditor can't check it.

---

## 2. The 12 concerns — what to stipulate

For each concern: its purpose, the concrete items to stipulate, and a generic good-vs-pointer cue.

### 1. `compliance-governance`
**Stipulate:** the data-class → permitted-AI-tool/tier mapping; autonomy rules (what an assistant may
do without named sign-off, by workflow type); the hard "never" prohibitions; which specific regulatory
clauses bind the work (→ standards tier).
**Good:** "Client-confidential → highest-tier tools only; consumer chat prohibited." **Pointer:** "per the approved-tool register."

### 2. `data-provenance`
**Stipulate:** the data-classification scheme with examples; source-precedence / conflict-resolution
rules; source→target lineage + reconciliation / ALCOA+ integrity criteria (for migrations); permitted
sources per client program (segregation).
**Good:** "an ordered 5-level source-precedence hierarchy with explicit conflict rules." **Pointer:** "data mapping per the migration spec."

### 3. `security`
**Stipulate:** the access-control model (who/what reaches which systems); validated-system boundaries
(assistant read-only? writes gated?); DLP / data-handling at the AI boundary.
**Good:** "assistants read-only to the QMS; no controlled-record writes without qualified, gated approval." **Pointer:** "per IT-security review."

### 4. `business-context`
**Stipulate:** program objectives & business case; explicit in/out scope; measurable success criteria;
client program(s) served and their constraints.
**Good:** "migrate System A → System B across 3 sites by [date]; success = all controlled records migrated & validated." **Pointer:** "see the project charter."

### 5. `system-architecture`
**Stipulate:** target system architecture/configuration; integration topology; target data/object
model; architectural constraints the assistant must not drift from.
**Good:** "approved target objects X/Y/Z; integration to System C via interface A; no unapproved custom objects." **Pointer:** "per the solution design."

### 6. `verification-validation`
**Stipulate:** validation approach (GAMP category; IQ/OQ/PQ); requirements (URS) with stable IDs;
quantitative acceptance criteria; qualification protocols & evidence.
**Good:** "URS-014 → OQ-22 → accept at 100% record-count match." **Pointer:** "per the validation plan."

### 7. `risk-management`
**Stipulate:** the risk register (probability × severity + controls); risk → requirement →
controlling-deliverable traceability; data-integrity risk controls; risk-acceptability criteria.
**Good:** "Risk-14, P×S, control = X, traces to URS-Y, residual acceptable." **Pointer:** "per the risk file."

### 8. `implementation-cutover`
**Stipulate:** cutover plan & sequence; multi-site rollout specifics (role/licensing differences);
rollback triggers & procedure; hypercare / go-live criteria.
**Good:** "wave 1 [site/date]; rollback if reconciliation < 99%." **Pointer:** "per the cutover plan."

### 9. `ai-accountability`
**Stipulate:** the concrete human sign-off gates (what requires named-human review); the non-decision
principle (AI never decides); accountability assignment (who owns AI-assisted output); a bias /
limitation handling **method**.
**Good:** "AI output to a controlled record requires named-engineer sign-off + independent reproduction." **Gap:** "review for bias" (no method).

### 10. `training-competency`
**Stipulate:** the role → required-competency matrix; the definition of a qualified reviewer (who may
approve AI output); training-completion gates on access; site/role competency differences.
**Good:** "only Part 11-trained engineers may approve migrated controlled records." **Pointer:** "per the training plan."

### 11. `qms-records`
**Stipulate:** the document hierarchy & control rules; record-retention rules; CAPA triggers; which
records are authoritative systems of record (AI output never is).
**Good:** "AI contribution log retained [lifecycle + N yr]; AI output is a working artifact until transferred to the SoR." **Pointer:** "per the record-retention procedure."

### 12. `supplier-qualification`
**Stipulate:** AI-vendor qualification criteria & current status; platform supplier qualification (GAMP
supplier assessment); per-tier vendor approval; re-qualification triggers.
**Good:** "Vendor V — tier-2 approved, tier-3 conditional, SOC 2 Type II, BAA available, confirmed [date]." **Pointer:** "see the vendor register."

---

## 3. How to use it

1. **Walk the 12 concerns**, not your source documents. For each, ask: is there a concrete, terminal
   stipulation? Mark ✅ / 🟡 / ❌ / ⚪.
2. **For every 🟡 — retrieve the artifact.** It exists; collect it.
3. **For every ❌ — name the decision and an owner.** No one has set this limit; someone must. Park
   what can't be decided yet; don't let it stall the rest.
4. **A concern is bundle-ready when its items are all ✅.** That is the gate into authoring its SCDs.
