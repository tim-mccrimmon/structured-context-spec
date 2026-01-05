# Usability & Accessibility Domain

## Overview
The Usability & Accessibility domain defines user experience principles, interface design approach, accessibility requirements, and human-computer interaction patterns. It ensures the system is usable by all intended users including those with disabilities.

## Domain Owner
**Typical Role:** Product Manager / UX Designer
**Responsibilities:**
- Define UX principles and design philosophy
- Establish accessibility requirements (WCAG compliance)
- Define interface patterns and user workflows
- Ensure inclusive design for all user populations
- Define usability testing approach

## Generated SCDs
This domain produces 3-4 SCDs:
1. **scd:project:ux-principles** - User experience approach and design philosophy
2. **scd:project:accessibility-requirements** - WCAG compliance, screen readers, keyboard navigation
3. **scd:project:interface-patterns** - UI patterns, interaction models, navigation
4. **scd:project:user-workflows** (optional) - Key user journeys and workflows

## Templates to Complete
- **usability-and-accessibility-brief-template.md** - Complete UX and accessibility context

## How to Complete
1. **Prerequisite:** Review business-context domain to understand:
   - Who the users are (primary and secondary)
   - User needs and pain points
   - Accessibility requirements for user populations

2. **Gather information from:**
   - Product team (user research, personas)
   - Design team (UX patterns, design system)
   - Compliance team (accessibility requirements)
   - User feedback and research

3. **Define UX approach:**
   - UX principles (simplicity, clarity, efficiency)
   - Accessibility standards (WCAG 2.1 AA, etc.)
   - Interface patterns and components
   - User workflows for key tasks

4. **Move to completed:**
   - Place finished template in `../../intent/completed/usability-accessibility/`

## Dependencies
- **Prerequisite domains:**
  - business-context (understand users and their needs)
- **Provides context to:**
  - architecture (interface layer design)
  - testing-validation (usability and accessibility testing)
  - compliance-governance (accessibility compliance requirements)

## Workflow Position
**SECOND WAVE** - Can begin after business-context is complete. Often completed by Product Manager early to establish user-facing direction.

## What Happens Next
Your completed template generates 3-4 usability and accessibility SCDs that guide interface design and testing.

## Template Version
- Version: 0.2.0
- Last Updated: 2025-01-26

## Need Help?
- **Review example:** `../med-adherence-examples/usability-accessibility/usability-and-accessibility-brief.md`

---

*This domain is part of the 11 prescribed SCS domains required for production projects.*
