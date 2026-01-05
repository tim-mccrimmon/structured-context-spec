# SCS RFCs (Requests for Comments)

This directory contains RFCs for significant changes to the Structured Context Specification (SCS).

## What is an RFC?

An RFC (Request for Comments) is a design document that proposes a major change to SCS. RFCs provide a structured way for the community to:
- Propose significant features or changes
- Discuss tradeoffs and alternatives
- Build consensus before implementation
- Document the reasoning behind design decisions

## When to Write an RFC

You should write an RFC for:
- **New SCD tiers or types**
- **Changes to core schemas** (breaking or significant additions)
- **New required fields** (breaking change)
- **Significant changes to relationship semantics**
- **Major additions to the specification**

You do NOT need an RFC for:
- Typo fixes or documentation improvements
- Small clarifications
- Additional examples
- Bug fixes in schemas

When in doubt, open a GitHub Discussion first to gauge whether an RFC is needed.

## RFC Process

### 1. Discuss the Idea

Before writing an RFC:
- Open a GitHub Discussion in the "Ideas" category
- Describe the problem and potential approaches
- Get initial feedback from the community
- The maintainer will indicate if an RFC is appropriate

### 2. Write the RFC

If the idea has merit:
- Copy `rfcs/0000-template.md` to `rfcs/0000-my-feature.md`
- Fill in all sections thoughtfully
- Provide concrete examples
- Address alternatives and drawbacks honestly

### 3. Submit the RFC

- Open a pull request adding your RFC to the `rfcs/` folder
- The maintainer will assign an RFC number (e.g., 0001, 0002)
- Rename your file to use the assigned number
- Title the PR: "RFC: [Your Title]"

### 4. Community Review

- The RFC will be open for at least 2 weeks for community feedback
- Participate in the discussion on the PR
- Be open to revising the RFC based on feedback
- The maintainer will indicate when discussion is winding down

### 5. Decision

Within 4 weeks of the RFC PR being opened, the maintainer will:
- **Accept**: RFC is merged, implementation can proceed
- **Reject**: RFC is closed with explanation (file is NOT merged)
- **Defer**: Good idea but not the right time; revisit later
- **Request Changes**: Needs modification before decision

### 6. Implementation

If accepted:
- The RFC is merged into the `rfcs/` folder
- A tracking issue is created in GitHub Issues
- Implementation work can begin (updating spec, schemas, examples)
- When implementation is complete, the spec is updated and versioned

## RFC Lifecycle

```
Idea Discussion → RFC Written → PR Submitted → Community Review (2+ weeks)
                                                       ↓
                                        Accepted / Rejected / Deferred
                                            ↓
                                        (if accepted)
                                            ↓
                                   Implementation → Spec Updated
```

## Active RFCs

### Under Review

| Number | Title | Author | Status | PR |
|--------|-------|--------|--------|----|
| (None currently) | | | | |

### Accepted (Pending Implementation)

| Number | Title | Author | Accepted Date | Tracking Issue |
|--------|-------|--------|---------------|----------------|
| (None currently) | | | | |

### Implemented

| Number | Title | Author | Implemented In | PR |
|--------|-------|--------|----------------|----|
| (None currently) | | | | |

### Rejected/Deferred

| Number | Title | Author | Status | Reason |
|--------|-------|--------|--------|--------|
| (None currently) | | | | |

## Tips for Writing Good RFCs

### Be Specific
Don't just identify a problem—propose a concrete solution with examples.

### Consider Alternatives
Show that you've thought through multiple approaches and explain why you chose this one.

### Be Honest About Drawbacks
Every design has tradeoffs. Acknowledging them builds trust and leads to better discussions.

### Provide Examples
Concrete examples make abstract proposals much easier to understand and evaluate.

### Keep Scope Focused
One RFC should address one coherent change. If you're proposing multiple independent features, write multiple RFCs.

### Engage with Feedback
Be open to revising your proposal based on community input. The best RFCs evolve through discussion.

## Questions?

- Review the [GOVERNANCE.md](../GOVERNANCE.md) for the full RFC process
- Open a GitHub Discussion if you're unsure whether to write an RFC
- Look at accepted RFCs as examples (once some exist)

## Acknowledgments

The SCS RFC process is inspired by:
- [Rust RFCs](https://github.com/rust-lang/rfcs)
- [Python PEPs](https://peps.python.org/)
- [IETF RFCs](https://www.ietf.org/standards/rfcs/)

We're grateful to these communities for pioneering effective specification governance.
