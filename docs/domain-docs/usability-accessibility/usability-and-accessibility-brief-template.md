---
title: "Usability & Accessibility Brief (Template)"
domain: "usabiliity-accessibility"
version: "1.0"
status: "Template"
scs_version: "0.2.0"
structure_hash: "sha256:8779bcbc8537d7e0"
---

## 1. Purpose & UX Scope
**Team Member Instructions:**  
Describe the users, use cases, and core usability goals of the system. Identify
which experiences must be frictionless, safe, and easy for diverse users.

**AI Mapping →** ux-principles.scope
---

## 2. User Personas & Cognitive/Physical Considerations
**Team Member Instructions:**  
Define the user groups and their needs, including:

- Elderly adults  
- Adults with chronic conditions  
- Clinicians and care coordinators  
- Users with visual, motor, or cognitive impairments  

Describe specific constraints: low vision, tremors, reading difficulty,
limited tech literacy, etc.

**AI Mapping →** ux-principles.personas

---

## 3. Core UX Principles
**Team Member Instructions:**  
Define the principles guiding UX decisions. Examples:

- Simple, clear, low-burden interactions  
- Large touch targets  
- Predictable navigation  
- Clear hierarchy and labeling  
- Minimal cognitive load  
- Accessible color contrast  

**AI Mapping →** ux-principles.principles[*]

---

## 4. WCAG / Accessibility Requirements
**Team Member Instructions:**  
Specify which accessibility standards must be met (e.g., WCAG 2.1 AA). Include:

- Color contrast  
- Font sizing  
- Screen reader compatibility  
- Focus order  
- Touch target minimums  
- Support for reduced motion  
- VoiceOver / TalkBack support  

**AI Mapping →** accessibility-compliance.standards, accessibility-compliance.criteria

---

## 5. UX for Critical Workflows
**Team Member Instructions:**  
List workflows that require extra clarity, simplicity, and accessibility:

- Checking today’s medications  
- Submitting dose confirmation  
- Reviewing reminders  
- Handling missed doses  
- Reading escalations or alerts  
- Adjusting notifications  

Describe desired UX outcomes and constraints for each.

**AI Mapping →** ux-principles.critical_flows[*]

---

## 6. Readability, Language & Cognitive Load
**Team Member Instructions:**  
Define:

- Reading level targets (e.g., 6th grade)  
- Use of plain language  
- Avoiding medical jargon  
- Microcopy guidelines  
- Preferred tone (supportive, non-judgmental)  

**AI Mapping →** ux-principles.readability, accessibility-compliance.cognitive_support

---

## 7. Visual Design & Interaction Requirements
**Team Member Instructions:**  
Document requirements for:

- Font sizes (preferred minimums)  
- Color palette constraints  
- Contrast ratios  
- Iconography  
- Gestures  
- Motion/animation rules (e.g., reduced motion setting)  

**AI Mapping →** accessibility-compliance.visual_design

---

## 8. Multi-Device Considerations (Mobile First)
**Team Member Instructions:**  
Describe requirements for:

- iOS/Android accessibility features  
- Responsive layout  
- Offline behavior  
- Touch vs. mouse interactions  

**AI Mapping →** ux-principles.device_requirements

---

## 9. Error Handling & User Feedback
**Team Member Instructions:**  
Describe how errors should appear:

- Clear, human-readable language  
- No blame or judgment  
- Persistent but unobtrusive notifications  
- Inline error guidance (“How to fix this”)  
- Accessibility-friendly error summaries  

Define:

- Visual patterns  
- Timing  
- Tone  
- Assistive technologies compatibility  

**AI Mapping →** error-handling-ux.patterns[*]

---

## 10. Empty States, Success States & Loading States
**Team Member Instructions:**  
Describe:

- What users see when data is missing  
- How success messages should appear  
- Loading animations (and their accessible alternatives)  
- Guidance to reduce confusion  

**AI Mapping →** ux-principles.system_states

---

## 11. User Input & Form Requirements
**Team Member Instructions:**  
Define:

- Touch target minimum sizes  
- Input validation rules  
- Keyboard navigation  
- Required labels  
- Inline help  

**AI Mapping →** accessibility-compliance.forms

---

## 12. Usability Testing Requirements
**Team Member Instructions:**  
Describe:

- Required usability testing  
- Test participant demographics (elderly, low vision, limited tech literacy)  
- Key tasks to validate  
- Success criteria  
- Accessibility testing process  

**AI Mapping →** validation.usability_tests, accessibility-compliance.testing

---

## 13. Known Usability & Accessibility Risks
**Team Member Instructions:**  
List risks such as:

- Low contrast medication colors  
- Confusing multi-step flows  
- Cognitive overload  
- Screen reader mislabeling  

**AI Mapping →** ux-principles.risks, accessibility-compliance.risks

---

## 14. Provenance
created_by: "{{ NAME }}"
created_at: "{{ ISO8601 }}"
source: "Intent Phase – Usability & Accessibility Domain"
notes: "Initial UX and accessibility requirements."