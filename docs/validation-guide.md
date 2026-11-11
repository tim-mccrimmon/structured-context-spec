# Validation

**Version**: 0.7

What `scs-validate` checks, how strict it is at each stage, and what its results mean. The
Agent Skill `scs-validate` runs it and explains the results in plain language before
proposing fixes. Every diagnostic has a registered code; the full list is
[`schema/diagnostics/codes.yaml`](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/schema/diagnostics/codes.yaml).

---

## Running it

```bash
scs-validate --strict                        # every workspace; run at the repository root
scs bundle validate                          # this workspace's root bundle and its imports
scs-validate context/project/security.yaml   # one SCD
scs-validate --verify-version domain/security-v1.0.0   # one version against its tag
scs-validate --domain ontology/domain-manifest.yaml    # a Domain Ontology manifest
```

`--output json` writes a report that validates against
[`schema/validator/report-schema.json`](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/schema/validator/report-schema.json).

| Exit code | Meaning |
|---|---|
| 0 | Valid |
| 1 | Errors |
| 2 | Warnings, in strict mode |
| 3 | Bad arguments |
| 4 | A file could not be read |
| 5 | Internal error |

Each Domain repository's CI workflow runs `scs-validate --strict` on every push.

---

## What is checked

Validation runs in passes; each pass reports what it finds.

| Pass | Checks | Example codes |
|---|---|---|
| Syntax | The file is valid YAML | |
| Schema | Required fields, types, and formats, from [`schema/`](https://github.com/tim-mccrimmon/structured-context-spec/tree/main/schema) | |
| Semantic | The rules that are not structure: binary prohibitions, citation forms, placeholder provenance, empty SCDs | `SCD_PROHIBITION_NOT_BINARY`, `PROVENANCE_PLACEHOLDER`, `SCD_EMPTY` |
| Relationship | Relationship targets exist and are the right kind | `RELATIONSHIP_CITATION_INVALID` |
| Bundle | Imports resolve, each bundle type follows its rules, listed SCDs exist, sections have owners | `BUNDLE_SCD_UNRESOLVED`, `BUNDLE_OWNER_MISSING`, `BUNDLE_OWNER_UNMAPPED` |
| Integrity | Every version tag matches its manifest and content digest; pinned imports match their tags | `CONTENT_DIGEST_MISMATCH`, `VERSION_TAG_MISSING` |

Validation rules are data, declared in the validator's rule files, so a rule can be read and
changed without reading code.

---

## Severity and stage

- **Errors** always fail.
- **Warnings** fail only with `--strict`.
- **Info** never fails, but some become errors at release. An owner role nobody holds is
  info while drafting (`BUNDLE_OWNER_UNMAPPED`) and an error when you version
  (`VERSION_OWNER_UNMAPPED`).

While a workspace is DRAFT, validation is loose: templates still holding TODOs warn, and
empty SCDs are info. A release is strict. `scs bundle release` validates the whole tree and
refuses a version that has errors, an import that is not pinned
(`VERSION_IMPORT_NOT_PINNED`), a section whose owner role nobody holds, or placeholder
provenance (`VERSION_PROVENANCE_PLACEHOLDER`).

---

## Common results and what to do

| Code | What it means | What to do |
|---|---|---|
| `SCD_PROHIBITION_NOT_BINARY` | A prohibition's subject has a condition or hedge (*unless*, *when*, *avoid*, ...) | Narrow the subject until it is always forbidden, or make it a directive |
| `SCD_EMPTY` | An SCD has no prohibitions, directives, or facts | Fill it, or retire it with `scs bundle remove-scd` |
| `PROVENANCE_PLACEHOLDER` | `created_by` is a placeholder, such as an `example.com` address | Name the real author, `Name <email>` |
| `DERIVED_FROM_UNRESOLVED` | A `derived_from` entry names an intake answer or source the intake record does not have | Record the source (`scs intake set source_documents`) or fix the id |
| `BUNDLE_OWNER_UNMAPPED` | A section's owner role has no person | `scs intake set owners '{role: ..., person: ...}'` |
| `BUNDLE_SCD_UNRESOLVED` | A bundle lists an SCD that does not exist | Remove the entry or restore the SCD |
| `CONTENT_DIGEST_MISMATCH` | A version's content no longer matches its recorded digest | A released version was altered; restore it from its tag. Never edit a released version |

Run `scs-validate` with `--output json` for every diagnostic's code, file, and message.

---

## Related

- [Bundle Lifecycle](bundle-lifecycle.md)
- [Validator README](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/tools/scd-validator/README.md)
- [Bundle Format](https://github.com/tim-mccrimmon/structured-context-spec/blob/main/spec/0.7/bundle-format.md) §9: validation rules
