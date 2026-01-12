---
title: "Business Context, Opportunity & Requirements Brief"
version: "1.0"
status: "Draft"
owner: "Product Management"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
project: "PROJECT NAME"
scs_version: "0.2.0"
structure_hash: "sha256:cb2d88a9b0309db8"
---

# Business Context, Opportunity & Requirements Brief

This document provides the unified upstream context for a new product initiative,
combining business framing, opportunity analysis, and high-level requirements.
It establishes **why** the initiative exists, **for whom** it matters, and
**what** success looks like—without prematurely defining architecture or design.
It is the single source of truth used by downstream SCD templates in the Intent
phase.

---

## 1. Problem Overview
The initiative exists because a significant and escalating problem affects users,
operations, compliance posture, or competitive standing. Existing workflows,
tools, or technologies no longer meet organizational needs and create measurable
friction, inefficiency, or risk.

This section describes:
- The nature of the problem  
- Who is impacted  
- Consequences of inaction  
- Strategic relevance to the organization  

---

## 2. Target Users & Stakeholders
The product serves a primary user group and intersects with multiple secondary
stakeholders.

This section identifies:
- Primary users (motivations, pain points, constraints)
- Secondary users (support, operations, partners)
- Internal stakeholders (compliance, engineering, legal, finance)
- Alignment with broader organizational or customer needs

---

## 3. Why Now
Environmental, market, regulatory, or strategic catalysts make this initiative
time-sensitive.

Include:
- Market trends or competitive threats  
- Regulatory or compliance requirements  
- New opportunities (technology, partnerships, capabilities)
- Internal priorities or leadership mandates  
- Risks of delay  

---

## 4. Opportunity Summary
The initiative unlocks meaningful strategic or operational value. It fills a gap
in the portfolio, improves key performance indicators, or opens new market
segments.

This section provides:
- The strategic upside  
- Commercial potential  
- User value and differentiation  
- Why this initiative is the right investment  

---

## 5. Desired Business Outcomes
Expected outcomes should be **measurable** and tied to organizational goals.

Examples include:
- Reduced operational cost  
- Improved user engagement  
- Compliance improvements  
- Increased retention or revenue  
- Lower error rates  
- Improved clinical outcomes (if applicable)

---

## 6. Guiding Principles & Vision
This section expresses the defining characteristics and aspirations for the
product.

Include:
- Vision statement (what the product should ultimately be)
- What the product is / is not
- Experience and behavioral principles
- Non-negotiable values (e.g., safety, privacy, simplicity)

---

## 7. Key Assumptions
Capture assumptions that support early planning but require validation.

Examples:
- User behavior expectations  
- Integration feasibility  
- Customer interest or adoption  
- Technical capabilities  
- Cost or resourcing assumptions  

These guide discovery and define early risks.

---

## 8. Constraints
Document any known boundaries or limitations:

- Regulatory requirements  
- Timeline and budget  
- Architecture/platform dependencies  
- Organizational constraints  
- Contractual obligations  

---

## 9. Target Personas & Key Use Cases
Personas provide human grounding for the opportunity. Use cases describe how
those personas will interact with the product.

### Personas
Brief descriptions of:
- Primary persona(s)
- Secondary persona(s)
- Situational attributes relevant to the solution

### Use Cases
Scenario-focused narratives describing:
- User intentions
- Triggers and workflows
- Expected outcomes  

These are not functional requirements but context for them.

---

## 10. High-Level Solution Direction
At this stage, the solution direction is conceptual and directional—not a design
specification.

Include:
- The role the product will play  
- The general approach to solving the problem  
- The intended modes of value delivery  
- Alignment with existing systems or portfolio strategy  
- Out-of-scope elements  

This helps focus downstream exploration.

---

## 11. High-Level Functional Requirements
Document the essential behaviors the system must support to address the problem
and deliver user value.

Each requirement should:
- Describe user-facing or system-facing behavior
- Identify the user/stakeholder affected
- Provide expected outcomes  
- Avoid dictating implementation  

This section includes only the most essential requirements; detailed behavior is
captured later in domain-specific SCDs.

---

## 12. UX Considerations
Directional guidance for early discovery and design work, including:

- Accessibility expectations
- Interaction models and complexity limits
- Tone, readability, and clarity
- Mobile/web parity expectations
- Information hierarchy and task prioritization

(Deep UX requirements live in the Usability & Accessibility domain.)

---

## 13. Technical Considerations
High-level technical factors that shape feasibility:

- Required integrations  
- Performance or reliability needs  
- Data considerations  
- Deployment environment assumptions  
- Security, privacy, and compliance expectations  

(Technical details belong in Architecture, Data, Security, and Operations domains
— not here.)

---

## 14. Data Requirements
Document high-level data needs:

- Key entities involved  
- What data the product consumes or produces  
- Analytics and instrumentation needs  
- Governance or retention requirements  
- Critical metrics needed for success measurement  

(Deep data modeling lives in the Data-Provenance domain.)

---

## 15. Edge Cases & Error Themes
This section identifies “families of edge cases” and error categories without
specifying low-level UX or logic.

Examples:
- Offline usage  
- Network issues  
- Partial failures from external systems  
- User error or invalid inputs  

(Specific UX patterns live in Usability & Accessibility; error handling logic is
captured later in domain SCDs.)

---

## 16. Dependencies & External Factors
Document anything outside the team’s control:

- Third-party services  
- Internal platform dependencies  
- Cross-team alignments  
- Regulatory drivers  
- Contractual or partner-based obligations  

These shape planning and risk.

---

## 17. Measurement & Success Metrics
Define how success will be measured.

Metrics may include:
- Business KPIs  
- Adoption and engagement  
- Error/latency rates  
- Compliance results  
- Satisfaction and usability metrics  

This ensures alignment on how impact will be evaluated post-launch.

---

## 18. Open Questions
Highlight unresolved questions or decision points requiring additional research,
leadership input, or dependency alignment.

---

## 19. Appendices (Optional)
- Research findings  
- Discovery summaries  
- Market or competitive analysis  
- Early concept sketches  
- Regulatory notes  
- Supporting artifacts  

---