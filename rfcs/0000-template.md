# RFC 0000: [Title]

- **Start Date**: YYYY-MM-DD
- **RFC PR**: (leave blank, will be filled by maintainer)
- **Tracking Issue**: (leave blank, will be filled when RFC is accepted)
- **Author(s)**: Your Name (@github-username)

---

## Summary

> One paragraph explanation of the proposed change.

---

## Motivation

> Why are we doing this? What use cases does it support? What is the expected outcome?

> This section should clearly explain why the existing specification is inadequate to address the problem that the RFC solves. Include concrete examples if helpful.

---

## Guide-level Explanation

> Explain the proposal as if it were already implemented and you were teaching it to another SCS user.

> - Introduce new named concepts
> - Use examples to show how users will interact with this feature
> - Explain how SCS users should *think* about this feature
> - If applicable, show how this feature compares to similar features in other specifications or standards

> This section should be approachable for someone familiar with SCS but not necessarily an expert. After reading this section, a user should:
> - Understand what the feature is
> - Understand how it benefits them
> - Know when they would use it

---

## Reference-level Explanation

> This is the technical portion of the RFC. Provide enough detail that:
> - The feature's interaction with existing SCS components is clear
> - The proposal is precise enough to serve as specification text
> - Corner cases are addressed

> This section should include:
> - Changes to schemas (JSON/YAML)
> - Changes to required or optional fields
> - New SCD types or tier structures
> - New relationship types or semantics
> - Validation rules
> - Examples showing the feature in action

### Schema Changes

> Show proposed schema modifications (if applicable)

```yaml
# Example schema changes
```

### SCD Examples

> Provide concrete examples of SCDs using this feature

```yaml
# Example SCD showing the feature
id: scd:example:feature-demo
type: project
title: Example demonstrating new feature
version: "1.0"
description: Shows how the proposed feature works

content:
  # ... example content ...
```

### Validation Rules

> Define how validators should handle this feature

---

## Drawbacks

> Why should we *not* do this?

> Consider:
> - Implementation cost (in complexity, maintenance, etc.)
> - Whether this fits well with the SCS philosophy
> - Integration challenges with existing SCDs
> - Cost of migrating existing bundles (if breaking change)
> - Potential for misuse or confusion

---

## Alternatives

> What other designs have been considered? What is the impact of not doing this?

> This section could also include prior art from other specifications or standards that solve similar problems.

### Alternative 1: [Description]

> Explain the alternative approach and why it was not chosen

### Alternative 2: [Description]

> Explain another alternative approach

### Do Nothing

> What happens if we don't implement this RFC?

---

## Unresolved Questions

> What parts of the design are still TBD? What questions should be resolved through the RFC process?

> Examples:
> - What naming should we use for new fields?
> - Should this be required or optional?
> - How does this interact with feature X?
> - Should we provide migration tooling?

---

## Future Possibilities

> Think about what the natural extension of your proposal would be and how it could evolve in future versions of SCS.

> This is a good place to "dump ideas" that are related but out of scope for this RFC. Note that this section should focus on related future work that would build on this RFC, not alternative approaches.

---

## Appendix (Optional)

### Implementation Notes

> If you have thoughts on implementation approaches (for validators, tools, etc.), include them here

### Migration Guide

> If this is a breaking change, provide guidance on how existing SCD bundles should be migrated

### Related RFCs

> List any related or dependent RFCs
