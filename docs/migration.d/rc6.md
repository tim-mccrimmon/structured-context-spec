## Release candidate 6

- **`scs bundle release` versions a root and its concept bundles in one command.** It versions
  each concept bundle that is unpinned or changed since its pinned version, pins it in the root,
  then versions the root, with one approver (`--version` for the root, `--concept NAME=VERSION`
  for each concept bundle). Run it without `--concept` to see which concept bundles need a
  version: `RELEASE_VERSION_REQUIRED` lists them in `suggestion.concepts`. Its `--dry-run`
  rehearses the release on a scratch copy of the repository and lists every snapshot, manifest,
  pin, commit, and tag, the root's included. If a step fails, every completed step is undone.
  `scs bundle version` and `scs bundle pin` are unchanged.
- **The scs-domain and scs-project skills put content first.** After the documents and the
  profile, they draft every SCD in one pass from the sources, using the ontology's templates as
  a coverage check, then offer a draft review package (`scs view --allow-draft`), and review
  and fix until the rules settle. Section owners and who releases versions are asked at
  release, where the engine enforces them. A Project session assesses the Domain and the
  Project together; Domain issues become questions for the Domain owner.
- **Drafting guidance for the assistant as reader.** The skills write each directive as what
  the assistant does when it meets the case, keep administration and detection patterns out of
  compiled content (or in the uncompiled `summary`, if the user wants them kept), state planned
  processes as planned, and sweep the sources for uncovered clauses before the review settles.
- **One confirmation may cover a batch of writes** (`agent-interface.md` §7). An agent shows
  every planned change in the batch first and asks again if a dry run differs. Commits,
  versions, and tags keep their own confirmation.
- **`scs bundle remove-scd` suggests the full id** when given a bare SCD name that matches one
  listed SCD (`SCD_NOT_LISTED`, `suggestion.scd_id`).
- **The intake error for a citation containing `+` names the slug form**
  (`std:iec-62304:2006-a1`). The citation grammar is unchanged.
