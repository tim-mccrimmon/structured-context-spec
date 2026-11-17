# SCS 0.7.1 Release Notes

**Status:** released &nbsp;|&nbsp; **Spec version:** 0.7.0 (unchanged)

A tools-only release. SCS is distributed as GitHub releases with the wheels attached, not on
PyPI ([ISS-014](ISSUES.md)); 0.7.1 makes every install path match.

## Changed

- **Install from the GitHub release.** Install both wheels in one command:

  ```bash
  U=https://github.com/tim-mccrimmon/structured-context-spec/releases/download/v0.7.1
  pip install $U/scs_validator-0.7.1-py3-none-any.whl $U/scs_tools-0.7.1-py3-none-any.whl
  ```

  The `scs-tools` package on PyPI is an old, unrelated release; don't install it.
- **Generated CI.** The workflow `scs new domain` writes installs the `scs-validator` wheel from
  the GitHub release matching the tools version, so it works without PyPI. Repositories created
  with 0.7.0 install from PyPI and fail that step: replace the `pip install` line in
  `.github/workflows/scs-validate.yml` with

  ```yaml
      - run: pip install "scs-validator @ https://github.com/tim-mccrimmon/structured-context-spec/releases/download/v0.7.1/scs_validator-0.7.1-py3-none-any.whl"
  ```

- **Skills.** The install plan recommends bundled or uploaded wheels first, then the GitHub
  release wheels, then a GitHub tag. PyPI is no longer offered.
- **Release workflow.** `release.yml` replaces `publish.yml`: pushing a `v*` tag builds both
  packages, smoke-tests them, and attaches them with `SHA256SUMS` to the GitHub release.

No format, schema, or diagnostic changes. Content digests of released bundles are unchanged.
