# Bundle Lifecycle

**Version**: 0.7

How a Domain or Project bundle goes from a first draft to a released, compiled version, and
how it changes after that. The normative rules are in
[Bundle Format](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/bundle-format.md) §5 and §8.

---

## The repository

One **Domain repository** (a git repository) holds one Domain and its Projects:

```
acme-context/
├── AGENTS.md, CLAUDE.md            # how an assistant works in this repository
├── .github/workflows/              # CI: scs-validate --strict
├── domain/                         # the Domain workspace
│   ├── bundles/domain-bundle.yaml  # bundle:acme: imports meta + its concept bundles
│   ├── bundles/concepts/*.yaml     # one per concept, each with an owner role
│   ├── context/project/*.yaml      # the SCDs
│   ├── intake.yaml                 # answers, owners, approvers, sources, review findings
│   ├── sources/                    # source documents (kept local, not committed)
│   └── dist/                       # compiled artifacts and review packages
└── projects/
    └── portal/                     # a Project workspace, the same shape
```

Each workspace is versioned and compiled on its own. A Project does not import its Domain;
at runtime both artifacts apply, Domain first.

---

## 1. Draft

A new workspace is **DRAFT**: every bundle has `version: "DRAFT"`, and nothing is approved.

1. **Profile and sources.** Who the context is for, the Ontology Model, and the source
   documents. Answers go into `intake.yaml`.
2. **Draft every SCD in one pass**, from the sources outward, recording where each rule came
   from (`derived_from`). The ontology's templates are a coverage check: keep the ones that
   apply, retire the rest (`scs bundle remove-scd`), and add concepts the templates lack
   (`scs add bundle <name> --new`).
3. **Consolidate.** Merge items that say the same thing in different sections, and move
   reference material (document lists, administration, names where a role is enough) out of
   the compiled lists into `summary`.

Validation is loose while DRAFT: templates with TODOs warn, they do not fail. Commit as you
go with `scs commit`.

## 2. Owners and review

Each concept bundle names the role accountable for it (`owner: quality`), and the intake
record names the person who holds the role (`scs intake set owners`). Owners are the primary
reviewers.

`scs view <bundle> --allow-draft` writes an HTML **review package**: every prohibition,
rule, and fact by section, with its owner and its source. Owners review it; each finding and
the decision on it is recorded (`scs intake record-finding`). Fix, regenerate, and repeat
until a round produces no changes.

## 3. Release

`scs bundle release` releases a workspace in one step, with one approver:

1. Each concept bundle that is new or changed gets a version (`--concept NAME=VERSION`).
2. The root bundle's imports are pinned to those versions (`bundle:security:1.0.0`).
3. The root bundle gets its version.

Every version is:

- a **git tag**, `<workspace>/<bundle-name>-v<version>` (`domain/acme-v1.0.0`), on a commit
  made by the engine;
- a **snapshot** of the root bundle (`bundles/acme-v1.0.0.yaml`) and a **manifest**
  (`bundles/acme-v1.0.0-MANIFEST.yaml`) recording the approver, the validation result, the
  digest of every bundle and SCD, and the **content digest** of the whole tree.

A release needs every section's owner role held, an approver given as `Name <email>` (never
taken from git config), and no placeholder provenance. The dry run (`--dry-run`) performs the
whole release on a scratch copy and lists everything it would do. If a step fails, every
completed step is undone.

A released version is never overwritten. The tag, the snapshot, and the digest stay as they
are; a change means a new version.

## 4. Compile

```bash
scs compile bundles/domain-bundle.yaml --version 1.0.0
```

compiles the released version from its tag, not from the working copy, into
`dist/<name>-<version>.yaml`: an identification rule, prohibitions, the meta rules,
directives, then facts. The artifact carries the content digest as `source_digest`, so it
can be matched to its approved version. The same source always produces the same bytes.
See [Runtime Artifact](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/runtime-artifact.md).

`scs stack <outer> ... <inner>` previews artifacts loaded together, for example a Domain and
a Project. Where the artifact goes next is the owner's decision; see
[Placement](placement/README.md).

## 5. Change after release

After a release the working copy is DRAFT again. To change it:

1. Edit, add, or retire SCDs, and commit. `scs status` shows what changed since the last
   version; `scs bundle diff` shows what changed since a version, or between two.
2. Review the changes with the owners (`scs view`, as before).
3. Release a new version. Only the concept bundles that changed need new versions; the rest
   stay pinned where they are.

Versions are semantic versions (`1.0.0`). SCS does not say which part to increase; one
workable convention is a patch for wording that changes no behavior, a minor version for a new
or tightened rule, and a major version for a restructuring.

Formal approval in a quality system stays in that system. Its approval record should cite
the version and the content digest, so anyone can check which content was approved.

---

## Related

- [Quick Start](quick-start-guide.md)
- [Validation](validation-guide.md)
- [Bundle Format](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/bundle-format.md)
- [Governance & Compliance](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/governance-and-compliance.md)
- [Example repository](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/examples/medtech-cdmo)
