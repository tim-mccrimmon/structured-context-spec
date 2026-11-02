# Review

The validator checks structure, completeness, and integrity. It cannot judge whether a rule is
sound. You do that, as an adviser: you raise findings, the user decides, and the decision is
recorded. You never block anything.

## What to look for

Read the workspace's SCDs and `intake.yaml` (`scs bundle info`, or the files themselves; reading
is fine, writing is not). Check:

| `kind` | Look for |
|---|---|
| `framework-conflict` | A rule that contradicts a framework the workspace cites. Example: a directive that lets the assistant mark records approved, where 21 CFR 820 is cited and approval is a human sign-off |
| `missing-protection` | Something the intake says is present (PHI, payment data, safety-class C software, client confidential data) with no prohibition or directive covering it |
| `technical-risk` | A rule that weakens security, auditability, or traceability: disabling logging, sharing credentials, skipping review. Also a rule so broad that it blocks the work the context is for, such as a prohibition that forbids what the Project must build |
| `ethical-risk` | A rule that could cause harm, deception, or unfair treatment of people |
| `layer-conflict` | A rule that contradicts one in another layer loaded with it: in a Project, the Domain (see below) |

Look both ways: for rules that are too loose, and for rules too tight to let the AI tool be
useful. Base framework findings on what a citation names and on what you know of the
framework; say when you are unsure, and never quote a standard's text as if you had it.

## Presenting a finding

Present findings a few at a time, most serious first. For each, in plain language:

1. name the SCD item (`scd:project:design-history#DC-004`) and, where relevant, the citation it
   rests on (`std:21-cfr-820`);
2. say what the problem is and why it matters, without alarm;
3. offer the choices: **changed** (you propose the edit, shown and confirmed as any other
   write), **kept** (the user gives a reason), or **deferred**.

Do not change content to resolve a finding unless the user confirms that change. If the user
keeps a rule, leave the content as it is; versioning goes ahead. Push back once on keeping
something serious, then respect the decision.

## Recording the decision

Record every finding you raise, whatever the decision:

```
scripts/scs_engine.py run scs intake record-finding --workspace <ws> \
    --kind framework-conflict --target scd:project:design-history#DC-004 \
    --finding "Lets the assistant mark DHR records approved" --cites std:21-cfr-820 \
    --decision kept --rationale "<the user's reason>" \
    --decided-by "<Name <email> of the user deciding>" --dry-run
```

Show the change, confirm, then run it. `kept` needs a rationale. When the decisions are
recorded, commit them with `scs commit`: show its dry run, get a yes, then commit. Do this
before any version is planned, not as a step inside the version plan. Ask who is deciding; do not
assume. To decide a `deferred` finding later, pass its `--id` (`rf-3`) to replace it.
`scs status` counts findings by decision and lists the deferred ones.

## The Domain in a Project review

A Project is reviewed with its Domain, because the Domain's rules apply to the Project too.
Read the Domain's latest released version: its compiled artifact,
`domain/dist/<bundle-name>-<version>.yaml`, where `<version>` is `domain_latest_version` from
`scs status`; if there is none, read the Domain's SCD files under `domain/context/`. Never
read a Domain draft as if it were released.

Check the Project's rules against the Domain's, and check the Domain's rules against what the
Project must do. When a Domain rule conflicts with the Project, or blocks it:

- record a `layer-conflict` finding **in the Project** (`--workspace <project>`), targeting the
  Domain item, with the decision `deferred` and the finding phrased as a question for the
  Domain owner;
- do not change anything in `domain/`, and do not draft a Project rule that lifts or loosens
  the Domain's. A Domain rule changes only by a new Domain version, in a Domain session.

## Several artifacts together

When the user loads several compiled artifacts together (a personal Domain, an organization's
Domain, a Project), preview them:

```
scripts/scs_engine.py run scs stack <outermost.yaml> ... <innermost.yaml>
```

`STACK_PROHIBITION_DIRECTED` marks a directive that mentions what another layer prohibits. It
is a text match: judge whether the two really conflict, and look for conflicts it misses. SCS
defines no precedence between layers; do not tell the user one layer overrides another.
