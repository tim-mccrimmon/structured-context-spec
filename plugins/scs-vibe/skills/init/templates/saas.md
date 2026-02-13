# [Project Name]

> [One-line description of what this system does]

## System Overview

[2-3 paragraphs describing:
- What the system does and who uses it
- The core problem it solves
- Key user workflows]

## Architecture

### High-Level Design

[Describe the overall architecture]
- **Type**: [Monolith / Microservices / Serverless / Hybrid]
- **Deployment**: [Where and how it runs]
- **Key external dependencies**: [APIs, services it connects to]

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| [Component 1] | [What it does] | `/src/...` |
| [Component 2] | [What it does] | `/src/...` |
| [Component 3] | [What it does] | `/src/...` |

### Data Flow

[Describe how data moves through the system for a typical request]

```
User Request → [Component A] → [Component B] → [Database] → Response
```

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | | |
| Framework | | |
| Database | | |
| Cache | | |
| Queue | | |
| Infrastructure | | |

## Patterns We Use

### [Pattern 1 Name]
- **Where**: [Which parts of codebase]
- **Why**: [Reason for using this pattern]
- **Example**: [File or code reference]

### [Pattern 2 Name]
- **Where**: [Which parts of codebase]
- **Why**: [Reason for using this pattern]
- **Example**: [File or code reference]

## Patterns We Avoid

### [Anti-pattern 1]
- **Why we avoid it**: [Concrete reason]
- **What to do instead**: [Alternative approach]

### [Anti-pattern 2]
- **Why we avoid it**: [Concrete reason]
- **What to do instead**: [Alternative approach]

## Constraints

### Technical Constraints
- [Constraint 1]: [Reason and implications]
- [Constraint 2]: [Reason and implications]

### Business Constraints
- [Constraint 1]: [Reason and implications]

### Performance Requirements
- [Requirement 1]: [Target metrics]

## Code Organization

```
/src
├── /[directory1]     # [Purpose]
├── /[directory2]     # [Purpose]
├── /[directory3]     # [Purpose]
└── /[directory4]     # [Purpose]
```

## Domain Context

### Key Concepts
- **[Term 1]**: [Definition in this system's context]
- **[Term 2]**: [Definition in this system's context]

### Business Rules
- [Rule 1]
- [Rule 2]

## Development Guidelines

### Before Making Changes
- [ ] [Checklist item 1]
- [ ] [Checklist item 2]

### Testing Requirements
- [Requirement 1]
- [Requirement 2]

### Areas Requiring Extra Care
- **[Area 1]**: [Why it needs care, who to consult]
- **[Area 2]**: [Why it needs care, who to consult]

---

*Last updated: [Date]*
*Generated with [SCS](https://structuredcontext.dev)*
