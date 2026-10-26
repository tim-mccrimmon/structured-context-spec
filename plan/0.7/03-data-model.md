# 3. Data model

Target state for 0.7. "D-nn" points to a decision in section 7.

## Domain repository layout

```
<domain-name>-context/
├── AGENTS.md                         # agent instructions (D-31)
├── CLAUDE.md                         # pointer to AGENTS.md
├── .github/workflows/scs-validate.yml # full history and tags
├── .gitignore                         # sources/ (D-59)
├── .gitattributes                     # * text eol=lf
├── domain/                           # the Domain workspace
│   ├── .scs/config
│   ├── intake.yaml
│   ├── ontology/domain-manifest.yaml # moved from domain/; 0.6 location still read (D-04)
│   ├── bundles/{domain-bundle.yaml, concepts/}
│   ├── context/project/              # SCDs (D-05)
│   ├── sources/                      # ignored by default (D-59)
│   └── dist/
└── projects/<name>/                  # one per Project, same shape, project-bundle.yaml
```

Reserved at each workspace root, not created, not read: `plan/`, `test-plan/`, `qa/` (D-33).

## Artifacts

| Artifact | Writer | Readers | Schema | 0.7 change |
|---|---|---|---|---|
| `.scs/config` | `scs new` | CLI, validator (workspace marker) | none (line format) | Keys `bundle_type`, `name`, `ontology`, `scs_version` (spec version) plus `tools_version`; old keys still read (D-06) |
| SCD | `scs scd write` or skill file edit (D-08), `scs add` | validator, compiler | `schema/scd/*` | Optional `derived_from[]` on directives, prohibitions, facts: exactly one of `intake` or `source`, optional `locator` (RFC §5). Added as a property; items stay closed (`additionalProperties: false`) |
| Bundle (DRAFT) | `scs new`, `scs add`, `scs bundle pin`, `scs bundle remove-scd` (D-08) | validator, compiler | `schema/bundles/` | Reserved names `plan`, `test-plan`, `qa` rejected (D-33) |
| Bundle snapshot | `scs bundle version` | resolver (pinned refs only, D-17), compiler | bundle schema | `<bundle-dir>/<bundle-name>-v<version>.yaml`, beside the manifest; stem-named 0.6 snapshots still resolve (D-43). Truthful `validation_passed`, `approval_status` (done, uncommitted) |
| Version manifest | `scs bundle version` | validator, compiler, diff | **new** `schema/manifest/version-manifest-schema.json` (D-36) | `content_digest`, `content_inputs` (D-47), `tools_version`; a manifest with a workspace-qualified tag is 0.7 format (D-49); the copy at the tag is authoritative and the working copy must match it (D-39); name `<bundle-name>-v<version>-MANIFEST.yaml` in the bundle's directory (D-02); `approval.approved_by` a person identifier `Name <email>` (D-28) |
| Git tag | `scs bundle version` | diff, validator `--verify-version` | n/a | `<workspace>/<bundle-name>-v<version>` on a commit holding the whole workspace except `dist/` (D-40); the record of the version (D-39). Required: no `--no-git` (D-38) |
| `intake.yaml` | `scs intake` (D-07) | skills, validator | **new** `schema/intake/intake-schema.json` (D-35) | Routing, profile answers, approvers, source documents, review findings. Outside the content digest; in every version commit, so the tag holds the record in force at approval (D-32, D-40) |
| Runtime artifact | `scs compile` | AI services (via person) | `schema/runtime/` | `scs_runtime: "0.7"` (D-47), `source_digest` (uncommitted); written to `dist/<bundle-name>-<version>.yaml` in every mode (D-11); never contains `derived_from` |
| `AGENTS.md`, pointer | `scs new domain` | AI clients | n/a | New |
| CI workflow | `scs new domain` | GitHub Actions | n/a | Runs repo-level `scs-validate --strict` |
| Machine-mode envelope | every `scs --json` command | skills, MCP | **new** `schema/cli/envelope-schema.json` | Section 4 |
| Validator report | `scs-validate --output json` | CLI, CI | **new** `schema/validator/report-schema.json` | `code`, `severity` per finding |
| Diagnostic code registry | WP-04 | engine, spec, CI | `schema/diagnostics/codes.yaml` | New (D-10) |

## Identity and naming rules

- Workspace name: `domain` or the directory name under `projects/`. `.scs/config name` must match;
  the validator reports a mismatch (D-03).
- Bundle name: the part of the id after `bundle:`; one shared function in CLI and validator.
- Working documents are indexed by id; snapshots (recognized by D-43 file name) by (id, version);
  manifests are not bundle documents. `DUPLICATE_ID` applies to working documents only (WP-04).

## Open data questions

Intake schema field shapes for personal and project profiles, answer id convention, and
`answered_by` for inferred-then-confirmed answers are designed in WP-07 and reviewed by the
maintainer before the skills depend on them (D-34).
