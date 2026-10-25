# RFC 0003: Review Profiles

- **Start Date**: 2026-10-25
- **RFC PR**: (leave blank, will be filled by maintainer)
- **Tracking Issue**: (leave blank, will be filled when RFC is accepted)
- **Author(s)**: Tim McCrimmon (@tim-mccrimmon)
- **Status**: Stub (not yet open for review)
- **Target**: SCS 0.8.0 or later (additive)
- **Depends on**: RFC 0002 (advisory review, section 12)

---

## Summary

RFC 0002 gives the agent interface an advisory review: while drafting, the agent raises
problems for the user to decide on, and the decisions are recorded. In RFC 0002 that review
runs on the agent's own judgment. This RFC proposes **review profiles**: declarative sets of
checks, each tied to a framework citation, that an agent runs during review. A profile
expresses a framework (for example CHAI, HIPAA, ISO 13485, or an organization's own policy) as
conditions and expectations ("if the project handles PHI, expect a prohibition on sending PHI
to unapproved services"), without carrying the framework's text. The spec defines the profile
format and ships one small example; profiles themselves come from the community, from
vendors, or from organizations.

---

## Motivation

- **Consistency.** Two agents reviewing the same workspace with only their own judgment will
  raise different findings. A profile gives them the same checklist.
- **Auditability of the review itself.** A finding that cites "profile `chai-genai` 1.0.0,
  check GA-07" can be traced and questioned. "The AI thought so" cannot.
- **Frameworks without the burden.** Organizations want to know their context addresses
  frameworks such as CHAI's Assurance Standards Guide or HIPAA. Putting those frameworks into
  the core spec would make SCS responsible for tracking every revision, would have the spec
  defining what "correct" governance is, and may raise licensing questions. A profile format
  lets that content live outside the spec, maintained by whoever is best placed to maintain it.
- **Coverage questions.** With profiles and the ontology's framework mappings (RFC 0001), an
  agent can answer "which parts of this framework does our context not address yet?"

---

## Guide-level Explanation (sketch)

A user, or their organization, chooses the profiles that apply to a workspace. The intake can
propose them: a regulated healthcare Domain might get `hipaa-privacy` and `chai-genai`. During
review, the agent evaluates each check against the workspace and raises any that fail as
findings, citing the profile and check. The user decides on each one, exactly as in RFC 0002.
Profiles never block and never change content.

---

## Reference-level Explanation (sketch)

Illustrative only; the format is the main open question.

```yaml
id: profile:hipaa-privacy
version: "1.0.0"
title: HIPAA Privacy Rule, AI context checks
maintainer: example-org
applies_when:
  intake.data: [PHI]
checks:
  - id: HP-01
    kind: missing-protection
    expect:
      prohibition_about: "sending PHI to services without a business associate agreement"
    cites: [std:hipaa-privacy:45-cfr-164.502]
    guidance: "Projects that handle PHI should prohibit sending it to unapproved services."
  - id: HP-02
    kind: technical-risk
    flag_if:
      directive_about: "disabling access logging"
    cites: [std:hipaa-security:45-cfr-164.312-b]
```

Points to settle:

- How checks match content: structured selectors over SCD fields, natural-language
  expectations the agent judges, or both. Structured selectors are reproducible; natural
  language covers more.
- Where profiles are declared: Domain bundle, Project bundle, or the intake record.
- How profiles are versioned, pinned, and distributed, and whether they get a content digest
  like bundles (RFC 0002 section 11).
- How findings reference profiles in `review_findings` (profile id, version, check id).

---

## Drawbacks

- Another artifact type to specify, validate, and maintain.
- A profile can be wrong or out of date, and a finding that cites a profile may look more
  authoritative than it is.
- Natural-language checks keep some of the variability profiles are meant to remove.

---

## Alternatives

- **Ship frameworks in the core spec.** Rejected for the maintenance, neutrality, and
  licensing reasons in the Motivation.
- **Agent judgment only (RFC 0002 as is).** Workable, but inconsistent across clients and
  harder to audit.
- **Validator rules.** The validator's rules are already data (`rules/v0.6.0/*.yaml`). Many
  checks need judgment the deterministic validator cannot make, but structured checks could
  share its rule format. Worth considering when designing the selector syntax.

---

## Unresolved Questions

1. Profile format and matching model (see Reference-level sketch).
2. Whether the spec ships any real profile, or only a worked example.
3. Licensing of source frameworks. CHAI's checklists were described as open access at their
   June 2024 draft release; current terms and the status of the final guide need checking
   before any CHAI profile is built.
4. Governance for community profiles: naming, trust, and how a user knows who maintains one.
5. Whether structured checks run in the validator as well as in agent review.

---

## Future Possibilities

- Coverage reports per framework, built from profiles and ontology mappings.
- Organization-authored profiles that encode internal policy and apply to every Project in a
  Domain.

---

## Related RFCs

- RFC 0001: Domain Ontology (framework mappings).
- RFC 0002: Agent-Mediated SCS (advisory review, intake record, content digest).
