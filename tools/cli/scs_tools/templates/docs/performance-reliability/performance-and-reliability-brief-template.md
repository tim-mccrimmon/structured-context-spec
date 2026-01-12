---
title: "Performance & Reliability Brief (Template)"
domain: "performance-reliability"
version: "1.0"
status: "Template"
scs_version: "0.2.0"
structure_hash: "sha256:d9ad4454a856cfbc"
---

## 1. Purpose and Scope
**Team Member Instructions:**  
Summarize which parts of the system need to be fast, reliable, and resilient,
and why. Focus on user-facing interactions and critical backend workflows
(notification delivery, data ingestion, etc.).

**AI Mapping →** response-time.scope, availability.scope
---

## 2. Critical User Journeys & Workflows
**Team Member Instructions:**  
List the most important flows from a performance/reliability perspective.
Examples: patient viewing today’s meds, sending a check-in, clinician viewing
adherence for a patient, escalation creation.

For each, briefly describe the flow and why it matters.

**AI Mapping →** response-time.critical_flows, availability.critical_flows

---

## 3. Response Time Targets
**Team Member Instructions:**  
Define response time expectations for each critical workflow. Use concrete,
user-centered targets (e.g., “Dashboard loads in < 2 seconds in 95% of cases”).

Include:

- API-level targets (backend)
- End-to-end perceived latency (front-end + backend)

**AI Mapping →** response-time.targets[*]

---

## 4. Throughput & Load Expectations
**Team Member Instructions:**  
Describe the expected volume and patterns over time:

- Requests per second (or per minute) for key APIs
- Notification volume patterns (morning/evening peaks)
- Adherence event volume

Note seasonality or spikes (e.g., post-surgery cohorts).

**AI Mapping →** scalability.load_profile

---

## 5. Availability & Uptime Requirements
**Team Member Instructions:**  
Define the availability expectations:

- Overall uptime target (e.g., 99.9%)
- Any stricter targets for specific components (e.g., notification pipeline)
- Allowed maintenance windows

**AI Mapping →** availability.targets

---

## 6. Error Budgets & SLOs
**Team Member Instructions:**  
Document high-level SLOs and error budgets for critical services:

- SLOs (success rate, latency, etc.)
- Error budget (e.g., allowed downtime per month/quarter)

**AI Mapping →** availability.slos, availability.error_budgets

---

## 7. Fault Tolerance & Degradation Strategies
**Team Member Instructions:**  
Describe what happens when things go wrong and how the system degrades:

- How do we handle:
  - notification provider outages?
  - partial EHR unavailability?
  - database slowness?
- Which features can degrade or be disabled safely?
- What “graceful degradation” looks like for patients and clinicians.

**AI Mapping →** fault-tolerance.degradation_strategies

---

## 8. Redundancy & Failover
**Team Member Instructions:**  
Describe redundancy and failover strategies:

- Region-level or AZ-level redundancy
- Active-active vs. active-passive
- Failover triggering (manual vs. automatic)
- Data replication strategy

**AI Mapping →** fault-tolerance.redundancy

---

## 9. Retry, Backoff & Idempotency
**Team Member Instructions:**  
Explain:

- Where retries are used (notifications, EHR calls, queue workers)
- Backoff strategies (exponential, max attempts)
- Idempotency guarantees for critical operations (e.g., adherence event creation)

**AI Mapping →** fault-tolerance.retry_policies

---

## 10. Scalability Strategy
**Team Member Instructions:**  
Describe how the system scales with increased load:

- Vertical vs. horizontal scaling
- Auto-scaling rules/triggers
- Use of queues and async processing to smooth spikes

**AI Mapping →** scalability.strategy

---

## 11. Performance Testing & Validation
**Team Member Instructions:**  
Define your approach to validating performance:

- Types of tests (load, stress, soak)
- Environments used
- What “pass” means for key SLOs

**AI Mapping →** response-time.testing, scalability.testing

---

## 12. Performance & Reliability Risks
**Team Member Instructions:**  
List known risks related to performance and reliability:

- Single points of failure
- High-risk dependencies
- Areas where targets are aspirational

**AI Mapping →** response-time.risks, availability.risks, fault-tolerance.risks, scalability.risks

---

## 13. Provenance
created_by: "{{ NAME }}"
created_at: "{{ ISO8601 }}"
source: "Intent Phase – Performance & Reliability Domain"
notes: "Initial performance and reliability context."