# SCS Tools

The `scs` command creates, edits, versions, and compiles Structured Context Specification (SCS)
context in a Domain repository.

- **Create** a Domain repository for an organization or a person, and Project workspaces in it
- **Add** concept bundles and SCDs from an ontology's templates, or new concepts of your own
- **Write** SCDs and the intake record through validated commands
- **Version** a bundle as a git tag with a snapshot and an approval manifest
- **Validate** SCDs, bundles, and whole repositories
- **Compile** a Domain or Project bundle into a deterministic runtime artifact

Every command that changes files has `--dry-run` and `--json` (machine mode), so an agent or a
script can drive the tools and read back exactly what changed.

## Packages

SCS ships two packages with distinct commands:

- **`scs-tools`** (this package): the `scs` command
- **`scs-validator`** (`tools/scd-validator`): the `scs-validate` command and the validation
  engine `scs` uses

`scs compile`, `scs bundle validate`, and `scs bundle version` need `scs-validator`. Install
both.

## Installation

Requires Python 3.11 or later and git. The 0.7 tools are not yet on PyPI (the `scs-tools`
package there is an old 0.1.0 release), and they still report version 0.6.0 until the release
candidate.

### From GitHub (no clone)

```bash
pip install \
  "scs-validator @ git+https://github.com/tim-mccrimmon/structured-context-spec.git@0.7-dev#subdirectory=tools/scd-validator" \
  "scs-tools @ git+https://github.com/tim-mccrimmon/structured-context-spec.git@0.7-dev#subdirectory=tools/cli"
```

Use `@v0.6.0` in place of `@0.7-dev` for the released 0.6 tools.

### From source

```bash
git clone https://github.com/tim-mccrimmon/structured-context-spec.git
cd structured-context-spec
pip install -e tools/scd-validator -e tools/cli
```

For development, `pip install -e "tools/scd-validator[dev]" -e tools/cli pytest jsonschema`.

## Quick start

```bash
scs new domain acme-health --author "Jane Doe" --email jane@acme-health.org
cd acme-health-context
scs new project patient-portal

# Edit the SCDs under domain/context/ and projects/patient-portal/context/, then:
scs-validate --strict

cd domain
scs bundle version --version 1.0.0 --approved-by "Jane Doe <jane@acme-health.org>"
scs compile bundles/domain-bundle.yaml --version 1.0.0
```

## The Domain repository

SCS 0.7 keeps an owner's context in one git repository, `<name>-context/`. It holds one Domain
workspace (governance that applies to all of the owner's work) and one workspace per Project
(governance for one project). The two kinds of bundle are independent: a Project bundle does not
import the Domain bundle, and a runtime applies the two side by side.

```
acme-health-context/
├── AGENTS.md                      # How an agent works in this repository (CLAUDE.md points here)
├── CLAUDE.md
├── .github/workflows/scs-validate.yml   # CI: scs-validate --strict
├── domain/                        # The Domain workspace
│   ├── bundles/
│   │   ├── domain-bundle.yaml     # The Domain bundle; imports the concept bundles
│   │   └── concepts/              # One concept bundle per ontology concept
│   ├── context/project/           # SCD files
│   ├── ontology/                  # The ontology manifest
│   ├── docs/
│   ├── intake.yaml                # Intake record, once `scs intake` writes it
│   └── .scs/config
└── projects/
    └── patient-portal/            # A Project workspace, same layout,
        └── bundles/project-bundle.yaml   # with a Project bundle in place of the Domain bundle
```

`dist/` in a workspace holds compiled artifacts. It is not part of a version.

## Commands

Run `scs <command> --help` for the full options of any command.

### `scs new` - Domain repositories and Project workspaces

```bash
scs new domain acme-health                   # sdlc ontology (default)
scs new domain acme-funding --ontology mca   # merchant cash advance
scs new domain acme-cdmo --ontology cdmo     # medical-device CDMO
scs new domain jdoe --ontology personal      # a person: boundaries only

scs new project patient-portal               # run inside the Domain repository
scs new project my-funder --ontology mca     # default: the Domain's ontology
```

`scs new domain` creates the repository, AGENTS.md, the CI workflow, and an initial commit.
`scs new project` adds `projects/<name>/` to the repository that contains the current directory
(or `--dir`).

Each ontology supplies one template set for a Domain and one for a Project; remove what does not
apply. A Domain gets organization-wide policy and standards (for sdlc: tech stack, security,
compliance, retention, engineering practices, operations, AI use), plus `company` and
`prohibited`. SCDs that describe one system, such as system context, threat model, and the risk
register, are scaffolded only for a Project. A personal Domain gets only boundaries (the
`prohibited` concept); its other concepts are defined with the user.

Without `--no-interactive`, missing information is prompted for. The author comes from
`--author` and `--email` or the prompt; it is never invented.

### `scs add` - Concept bundles and SCDs

```bash
scs add bundle security                       # a concept bundle from the ontology's templates
scs add bundle groceries --new --title "Groceries"   # a concept with no template
scs add scd threat-model                      # one SCD from a template
scs add scd tech-stack --workspace domain     # into a named workspace
```

`--new` creates the concept bundle, a first empty SCD, its ontology entry, and the root bundle's
import of it. `scs bundle list --available` lists the templates.

### `scs scd write` - Write an SCD

```bash
scs scd write context/project/release-gates.yaml --from-file draft.yaml
scs scd write context/project/release-gates.yaml --from-file - < draft.yaml --dry-run
```

The content is validated against the SCD schema and rules first; an invalid SCD is not written.

### `scs intake` - The intake record

```bash
scs intake set audience organization
scs intake set certifications '[std:iso-13485:2016, std:iec-62304:2006-a1]'
scs intake set approvers '{person: Jane Doe <jane@acme-health.org>, role: QA Lead}'
scs intake record-finding --help
```

`intake.yaml` holds a workspace's intake answers, approvers, source documents, and review
findings. It is not an SCD and is never compiled.

### `scs bundle` - Inspect, edit, and version bundles

```bash
scs bundle list                         # bundles in the workspace
scs bundle info security
scs bundle validate                     # the root bundle and everything it imports
scs bundle add-import bundle:security
scs bundle add-scd --help
scs bundle remove-scd --help            # retire an SCD
scs bundle pin --help                   # pin an import to a released version
scs bundle version --version 1.0.0 --approved-by "Jane Doe <jane@acme-health.org>"
```

`scs bundle version` releases a bundle as the git tag `<workspace>/<bundle-name>-v<version>` on
a commit holding the workspace, with a snapshot and a manifest. The commit's author is the
approver, who must be named with `--approved-by` (it is never taken from git config). Every
import must be pinned to a released version that still matches its tag. A version is never
overwritten.

### `scs validate` and `scs-validate` - Validation

```bash
scs-validate --strict                          # every workspace, at the repository root
scs-validate --verify-version domain/security-v1.0.0
scs validate context/project/tech-stack.yaml   # one or more SCDs
scs validate --bundle bundles/domain-bundle.yaml --strict --output json
```

`scs validate` uses the `scs-validator` engine. Validation runs in passes: syntax, schema,
semantic, relationship, bundle and completeness, and, in a repository, integrity (digests, tags,
and manifests). Every finding has a registered diagnostic code and a severity; `info` findings
never change the exit code.

### `scs compile` - Runtime artifacts

```bash
scs compile bundles/domain-bundle.yaml --version 1.0.0     # from the tag
scs compile bundles/project-bundle.yaml --allow-draft      # working tree; version DRAFT+<digest>
scs compile bundles/project-bundle.yaml --version 1.0.0 --stdout --format json
```

The artifact is one self-contained file of the bundle's prohibitions, directives, and facts,
written to `dist/<bundle-name>-<version>.yaml`. It has no timestamps, so the same source always
gives the same bytes. With `--version`, the released content is compiled from its tag and the
artifact carries its `source_digest`. See `spec/0.7/runtime-artifact.md`.

## Machine mode

`--json` writes one JSON result envelope to stdout: `ok`, the files and git effects in
`changes`, and diagnostics with codes. `--dry-run` reports the same changes and writes nothing.
On failure, the run rolls back and `changes` lists what remains (normally nothing). See
`plan/0.7/04-interfaces.md` until the 0.7 agent-interface spec is published.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Errors found |
| 2 | Warnings, with `--strict` |
| 3 | Invalid arguments |
| 4 | File not found or permission error |
| 5 | Internal error |

## CI

`scs new domain` writes `.github/workflows/scs-validate.yml`, which runs `scs-validate --strict`
at the repository root on every push and pull request. It installs `scs-validator` from PyPI, so
it works once 0.7.0 is published.

## Resources

- [SCS specification](../../spec/0.7/)
- [Migration guide, 0.6 to 0.7](../../docs/MIGRATION-0.7.0.md)
- [Validator](../scd-validator/)
- [Examples](../../examples/)
- [Contributing](../../CONTRIBUTING.md)

## License

Apache 2.0
