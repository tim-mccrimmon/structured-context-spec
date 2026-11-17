## Housekeeping

- **`scs init` is removed.** In 0.7 an owner's context lives in its own Domain repository, so
  there is no workspace to add to an existing codebase. Create the repository with
  `scs new domain` and add Projects with `scs new project`. `scs add` still works in a
  workspace made by 0.6 `scs init`, and still applies its recorded `--type`.
- **Unreadable YAML files are reported.** A YAML file in a workspace that does not parse, or is
  not UTF-8, used to be skipped without a word, so an SCD in it silently dropped out. It is now
  `WORKSPACE_FILE_UNREADABLE` (warning; exit 2 under `--strict`), naming the file and the line
  of the parse error, from `scs-validate`, `scs bundle validate`, and `scs compile`. Fix the file
  or delete it. If a bundle lists an SCD in that file, `BUNDLE_SCD_UNRESOLVED` is reported as
  well, and `scs compile` names the unreadable file alongside its error. The root bundle, the
  ontology manifest, and `intake.yaml` are not reported twice; their own checks cover them.
- **Rule files no longer declare severities nothing reads.** Each code's severity is declared in
  `schema/diagnostics/codes.yaml`. A rule file names a severity only where a check can be set to
  warn: completeness rules, the bundle `xor_constraint`, and the ontology `concern_residue` and
  `concept_bundle_agreement`. The unused `validation_modes` and `scd_uniqueness` blocks are
  gone. No finding changes severity.
- **`scs bundle list` and `scs bundle info` have `--json` and `--workspace`.** Under `--json`,
  `list` returns the root and concept bundles (path, kind, id, type, version, and SCD count for
  concepts), or the available templates by ontology with `--available`; `info` returns the whole
  bundle and whether it came from the workspace or a template. `info` on an unknown name is
  `BUNDLE_NOT_FOUND`. `list` no longer shows versioned snapshots and manifests in
  `bundles/concepts/` as concept bundles.
