---
title: "Safety & Risk Brief (Worksheet)"
concept: "safety-risk"
---

## 1. Purpose & Safety Scope
**Team Member Instructions:**  
Define the safety-critical aspects of the system and why safety must be managed.
List categories (patient-facing, clinician-facing, backend processing) included
in the scope.

---

## 2. Safety-Critical Features & Functions
**Team Member Instructions:**  
Identify features that have direct safety implications:

Examples:
- Medication reminder accuracy  
- Adherence event recording  
- Escalation workflows  
- Notification timing  
- Sync with EHR medication data  

Describe why each is safety-critical.


---

## 3. Hazard Identification
**Team Member Instructions:**  
List potential hazards that could cause patient harm or degraded safety.

Types of hazards:
- Incorrect reminders (wrong time, wrong medication)
- Missed reminders due to system failure
- Incorrect adherence status shown to clinicians
- Escalation not triggered when needed
- Escalation triggered incorrectly

For each, describe:
- Hazard description
- Potential impact
- Likelihood (low/medium/high)


---

## 4. Safety Requirements & Guardrails
**Team Member Instructions:**  
Define specific guardrails required to prevent harm.

Examples:
- Never send dosage changes without human oversight  
- Notification timing must never drift by more than X minutes  
- UI must clearly distinguish “confirmed dose” vs “pending”


---

## 5. Failure Modes & Effects (High-Level FMEA)
**Team Member Instructions:**  
For major workflows, list expected failure modes and their effects:

- What can go wrong?
- What happens if it fails?
- What is the user impact?

Include:
- Failure mode
- Effect on user or patient
- Severity
- Detection capability
- Mitigation strategy


---

## 6. Detection & Alerting Requirements
**Team Member Instructions:**  
Define what failures the system must detect, and how the system alerts internal
teams.

Examples:
- Notification queue backlogs
- Delayed reminder dispatch
- Model prediction failures
- EHR sync errors

Specify:
- Detection logic
- Alerting targets (team, severity)
- Time to detection expectations


---

## 7. Mitigation Strategies
**Team Member Instructions:**  
List strategies to mitigate hazards and failure modes:

- Redundancy  
- Retry logic  
- Human review  
- Safe defaults  
- Rollbacks  


---

## 8. Safety Testing Requirements
**Team Member Instructions:**  
Describe testing required to validate safety:

- Negative testing (reminder failures)
- E2E safety flow validation
- Clinical safety review of escalation logic
- Chaos testing for notifications
- Model performance safety checks


---

## 9. Safety Risk Matrix
**Team Member Instructions:**  
Create a simple qualitative risk matrix with severity vs. likelihood.

Example categories:

- Severity: low / moderate / high / critical  
- Likelihood: unlikely / possible / likely / frequent  


---

## 10. Residual Risk Acceptance Criteria
**Team Member Instructions:**  
Explain how the team decides if the remaining risk is acceptable.

Criteria may include:
- Clinical validation sign-off
- Maximum acceptable severity
- Error budgets
- Monitoring coverage


---

## 11. Roles & Responsibilities
**Team Member Instructions:**  
Define who owns safety for:

- Clinical correctness  
- Escalation logic  
- Notification timing  
- Model validation  
- Production safety incidents  


---

## 12. Known Safety Risks (Preliminary)
**Team Member Instructions:**  
List early known risks or concerns.


