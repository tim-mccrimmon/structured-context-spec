## Status, commits, and source documents (rc2)

- **New command, `scs status`.** Reads only. Works out where each workspace stands from the
  repository: the intake record, documents in `sources/` and whether they are recorded, SCDs
  with template placeholders left, review findings by decision, versions and changes since the
  latest, uncommitted files, compiled artifacts, and, for a Project, the Domain's latest
  released version (D-83).
- **New command, `scs commit`.** Commits one workspace's changes and nothing else, with the
  author you name (`--author "Name <email>"`, never taken from git configuration) and
  `scs-tools` as committer. `COMMIT_AUTHOR_REQUIRED` and `COMMIT_AUTHOR_INVALID` are new (D-84).
- **`scs new project` commits the new workspace**, as `scs new domain` already did (D-91).
- **`sources/` is scaffolded** in every new workspace, with a README saying what goes there. The
  generated `.gitignore` now ignores `**/sources/*` except that README (D-86). An existing
  repository keeps its `.gitignore`; to track the README there too, change `sources/` to the
  two new lines.
- **The sdlc scaffold leaves out the healthcare templates** (`hipaa-compliance`,
  `chai-adherence`, `tefca-participation`); add one with `scs add scd <name>` (D-91).
