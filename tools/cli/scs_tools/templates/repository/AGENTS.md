# {{ repo_name }}: agent instructions

This repository manages the Structured Context Specification (SCS) context for one Domain,
**{{ domain_name }}**, and its Projects. It holds context: the directives, prohibitions, and facts
that AI services apply to {{ domain_name }}'s work. It does not hold that work.

## What work belongs here

Work in this repository is limited to five operations on SCS context:

1. **Create** workspaces, bundles, and SCDs (`scs new`, `scs add`).
2. **Maintain** them: edit, retire, and re-scope SCDs and bundles (`scs scd write`, `scs bundle`).
3. **Validate** them (`scs-validate`).
4. **Version** bundles (`scs bundle version`); each version is a git tag.
5. **Compile** bundles into runtime artifacts (`scs compile`), written to the workspace's `dist/`.

Application work does not belong here. Do not write, build, or change application code,
infrastructure, or documents other than SCS context in this repository; that work belongs in the
application's own repository. If you are asked for it here, say so and stop.

## Layout

```
{{ repo_name }}/
├── domain/              # the Domain workspace: governance for all of {{ domain_name }}'s work
└── projects/<name>/     # one workspace per Project, independent of the Domain bundle
```

Each workspace has `.scs/config`, `bundles/` (the root bundle and `concepts/`), `context/project/`
(the SCDs), `ontology/domain-manifest.yaml`, and `dist/` (compiled artifacts). `sources/` holds
local source documents and is not committed by default. `plan/`, `test-plan/`, and `qa/` are
reserved for a later SCS release: do not create them.

## Rules

- When the user is working on one workspace, confine your changes to that workspace.
- Write through the `scs` commands rather than editing files by hand, and run them with `--json`
  so you can read the result. Report an operation as done only if the command returned
  `"ok": true`.
- Validate before versioning. Never name an approver yourself: a version is approved by the
  person the user names.
- Do not rewrite, delete, or move version tags.
