# Performance & Reliability Context Brief
Project: Medication Adherence Platform
Domain: Performance & Reliability
Version: 1.0
Status: Draft
Phase: Intent

This brief describes the performance and reliability expectations for the
Medication Adherence Platform. It informs targets for response time, availability,
fault tolerance, and scalability.

---

## 1. Purpose and Scope
The platform must be fast and reliable where it matters most:

- Delivering reminders on time
- Capturing adherence check-ins
- Providing clinicians a current view of adherence
- Ensuring escalation workflows run correctly

Scope includes all patient-facing and clinician-facing flows, plus backend
pipelines for notifications, adherence ingestion, and escalations.

---

## 2. Critical User Journeys & Workflows

1. **Patient views today’s medication schedule**  
   - Patient opens the app to see medications due now and later today.

2. **Patient submits a check-in (“I took this dose”)**  
   - Patient taps to confirm ingestion; event must be recorded reliably.

3. **Clinician views patient adherence summary**  
   - Clinician opens a dashboard to review adherence before or during a visit.

4. **Care coordinator reviews escalations**  
   - Coordinator views list of high-risk patients and drills into recent events.

5. **Notification pipeline sends upcoming reminders**  
   - System sends reminders before doses; delays degrade effectiveness.

These journeys drive the main response-time and availability requirements.

---

## 3. Response Time Targets

**Patient App**
- View today’s schedule:  
  - Target: < 1.5 seconds P95 for main screen load.  
- Submit a check-in:  
  - Target: < 500 ms P95 API latency, with UI confirmation within 1 second.

**Clinician Dashboard**
- Load patient adherence summary:  
  - Target: < 2.0 seconds P95.  
- Load cohort / panel view:  
  - Target: < 3.0 seconds P95 (100–500 patients).

**Admin / Program Config**
- Program configuration pages:  
  - Target: < 2.0 seconds P95; this is less critical than patient flows.

---

## 4. Throughput & Load Expectations

- **Patients:**  
  - 50k–250k active patients in early rollouts.  

- **Notifications:**  
  - Peak windows around 7–9am and 7–9pm local time.  
  - 2–5 notifications per patient per day.  

- **Adherence Events:**  
  - Up to several hundred thousand events per day.  
  - Bursts aligned with notification windows.

- **Clinician Loads:**  
  - Fewer total users, but usage spikes during business hours.

These patterns require smoothing via queues and auto-scaling.

---

## 5. Availability & Uptime Requirements

- **Overall API availability:**  
  - 99.9% monthly (error budget ~43.8 minutes/month).  

- **Notification pipeline availability:**  
  - Effective availability of timely delivery ≥ 99.5%.  

- **Clinician dashboard availability:**  
  - 99.5% (slightly less stringent than core patient flows, but still high).

Planned maintenance should be zero-downtime for patient-critical services.

---

## 6. Error Budgets & SLOs

**SLOs**
- Patient schedule API: 99.9% success rate, P95 latency < 1.5s.  
- Check-in API: 99.9% success rate, P95 latency < 500ms.  
- Notification dispatch: ≥ 99.5% of scheduled notifications sent within ±5 minutes.

**Error Budgets**
- Downtime and degraded performance draw from the error budget.  
- Once the monthly error budget is exhausted, feature rollouts pause until stability improves.

---

## 7. Fault Tolerance & Degradation Strategies

- If the **notification provider** is down:  
  - Queue messages and retry with exponential backoff.  
  - If outage persists beyond a threshold, fail over to secondary provider.  
  - App can show “reminder pending” state but should not block check-ins.

- If the **EHR** is unavailable:  
  - Existing MedicationPlans continue to function.  
  - New plan creation or updates may be delayed but core adherence tracking continues.

- If the **primary database** slows down:  
  - Read replicas or caching used to serve read-heavy endpoints.  
  - Non-critical features may be temporarily disabled (e.g., heavy analytics queries).

- If the **escalation engine** is delayed:  
  - Escalations are processed with some delay but never dropped; queues ensure eventual processing.

---

## 8. Redundancy & Failover

- **AZ Redundancy:**  
  - All production services run across at least 2 availability zones.  

- **Regional Redundancy:**  
  - Primary region (us-east-1) with warm standby in us-west-2.  

- **Data Replication:**  
  - Database replication across AZs; cross-region replication for DR.  

- **Failover:**  
  - Initial design: manual region failover runbook; future automation planned.  

---

## 9. Retry, Backoff & Idempotency

- **Notification Dispatch:**  
  - Retries with exponential backoff; cap on total attempts.  
  - Idempotent notification IDs to avoid duplicate sends.

- **EHR API Calls:**  
  - Retries for transient failures (timeouts, 5xx).  
  - Circuit breaker for persistent failures to avoid thrashing.

- **AdherenceEvent Creation:**  
  - Idempotency keys per scheduled dose + timestamp to prevent duplicates from flaky networks.

---

## 10. Scalability Strategy

- **Horizontal Scaling:**  
  - Backend services on ECS scale out based on CPU usage and SQS queue depth.  

- **Async Processing:**  
  - Notification scheduling and escalation evaluation done via queues and workers.  

- **Database:**  
  - Read replicas added for reporting and clinician dashboards.  
  - Partitioning strategies considered for very large cohorts.

- **Cache:**  
  - Patient schedule and clinician views cached where safe to reduce DB load.

---

## 11. Performance Testing & Validation

- **Load Testing:**  
  - Pre-launch and quarterly tests on staging.  
  - Simulate notification peaks and high check-in volumes.

- **Stress Testing:**  
  - Push beyond expected traffic to understand breakpoints.

- **Soak Testing:**  
  - Multi-hour runs to identify memory leaks or performance degradation.

Success criteria:

- System maintains SLOs under 2× projected peak load.  
- No unbounded resource usage over long-duration tests.

---

## 12. Performance & Reliability Risks

- Third-party notification provider outages may impact adherence behavior.
- Misconfigured auto-scaling may lead to under- or over-provisioning.
- EHR slowness could impact initial plan provisioning for new patients.
- Complex queries for clinician dashboards may strain the database if not tuned.

Mitigations include: provider redundancy, performance tuning, indexing, caching,
and clear SLO/error budget policies.

---

## 13. Provenance
created_by: "Platform Lead – Medication Adherence"
created_at: "2025-11-27T21:00:00Z"
source: "Intent Phase – Performance & Reliability Domain"
notes: "Initial performance and reliability envelope; subject to refinement post pilot."