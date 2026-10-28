# Install Matrix (WP-11a)

Whether the SCS tools can be installed where an agent runs, for each chat client in D-50. The
packages tried are the pre-releases on TestPyPI, built from branch `testpypi/0.7.0rc0`
(`0.7-dev` at `daf5c8c` with the versions bumped):

- https://test.pypi.org/project/scs-validator/0.7.0rc0/
- https://test.pypi.org/project/scs-tools/0.7.0rc0/

D-27 records the fallback order for installing in a chat sandbox: PyPI, then a GitHub tag, then
a wheel bundled with the skill. The last column is the method each client should use. This
matrix is run again against WP-11rc.

| Client | Install method tried | Success | PyPI reachable | GitHub reachable | Python | git | git identity | `scs --version --json` (result) | Date | D-27 choice |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Code (macOS, local) | `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ scs-tools==0.7.0rc0` in a new venv | yes | yes | yes | 3.12.13 | 2.54.0 | configured | `{"scs_version": "0.7.0", "tools_version": "0.7.0rc0"}` | 2026-10-28 | PyPI |
| Claude Code (macOS, auto mode) | Same command, run by the agent | no: refused by the auto-mode safety check ("Code from External") before it ran | yes | yes | 3.14.6 | 2.54.0 | configured | not run | 2026-10-28 | User runs the install (`! pip install ...`) or adds a permission rule (note 1) |
| Claude.ai | Same command, run by the agent after the user confirmed the package is theirs (note 2) | no: `test.pypi.org` does not resolve in the sandbox (`NameResolutionError`); pip found only `scs-tools` 0.1.0 on PyPI (note 4) | yes (200) | no: 403 from the sandbox proxy unless the repository is added to the session (note 3) | 3.13.18 | 2.43.0 | configured | not run | 2026-10-28 | PyPI once 0.7.0 (or a pre-release) is on PyPI; bundled wheel works now (next row) |
| Claude.ai (bundled wheel) | Both wheels uploaded to the chat, copied to their original file names, `pip install` from the files; dependencies from PyPI (note 5) | yes; `scs new domain`, `scs-validate --strict`, `scs compile --allow-draft`, and `scs stack` all ran (git init and commit work) | yes | no (note 3) | 3.13.18 | 2.43.0 | configured | `{"scs_version": "0.7.0", "tools_version": "0.7.0rc0"}` | 2026-10-28 | bundled wheel |
| Cursor | deferred: not yet run (Tim, later; Claude clients first) | | | | | | | | | |
| Codex | deferred: not yet run (Tim, later; Claude clients first) | | | | | | | | | |
| GitHub Copilot | deferred: not yet run (Tim, later; Claude clients first) | | | | | | | | | |

## Running a row

Paste this into the client's agent, in a new chat or session, and copy its answers into the row:

```text
Please run these steps in your code execution or terminal environment and report each result
exactly. Do not change any settings or install anything other than what is listed.

1. python3 --version
2. git --version
3. git config --global user.email  (report only whether it prints a value: "configured" or
   "not configured"; do not show the value)
4. curl -s -o /dev/null -w "%{http_code}" https://pypi.org/simple/   (or report that the
   network is blocked)
5. curl -s -o /dev/null -w "%{http_code}" https://github.com
6. python3 -m venv /tmp/scs-venv && /tmp/scs-venv/bin/pip install --index-url
   https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ scs-tools==0.7.0rc0
   (if venv is unavailable, use: pip install --user with the same arguments)
7. /tmp/scs-venv/bin/scs --version --json   (or `scs --version --json` if installed with --user)

If step 6 fails, report the full error message, then stop.
```

If the install from TestPyPI fails because the network is blocked, the next fallback (a GitHub
tag, then a bundled wheel) is tried in WP-10, once the skills exist.

## Notes

1. **Claude Code in auto mode** blocks an agent from installing packages from an index it has
   not been told to trust; the safety check is working as intended. Whether an install from
   the real PyPI is also blocked is not known until 0.7.0 is published. For WP-10:
   a skill should not rely on installing the tools itself, and should give the user the command
   to run. That session's Python, 3.14.6, is newer than CI tests (3.11 and 3.12).
2. **Claude.ai's agent** declined to install from TestPyPI without confirmation, for reasons it
   stated: TestPyPI is an open index, and `--extra-index-url` with PyPI allows dependency
   confusion. It offered to continue once told the package is the user's own pre-release, to
   inspect the package first, or to install from the real PyPI. For WP-10: skills should say
   where the package comes from (the PyPI project and the repository), so the agent and user can
   check it.
3. **GitHub from Claude.ai.** `curl https://github.com` returned 400, and a specific release
   archive (`pypa/pip` tag 24.0) returned 403. The sandbox proxy's response says GitHub access to
   a repository is not enabled for the session until the repository is added (`add_repo`). The
   D-27 second fallback, a GitHub tag, therefore needs the SCS repository added to the session
   first; it was not tried.
4. **Claude.ai cannot reach TestPyPI.** The sandbox resolves `pypi.org` but not
   `test.pypi.org`, so a pre-release on TestPyPI cannot be tested there. PyPI itself works: pip
   listed `scs-tools` 0.1.0, the old release. An unpinned `pip install scs-tools` would install
   0.1.0 until 0.7.0 is published, so skills must pin the version.
5. **Bundled wheels in Claude.ai.** Uploaded files are renamed with a hash prefix (for example
   `a6975716-scs_validator-0.7.0rc0-py3-none-any.whl`), and pip refuses a wheel whose name is not
   in the standard format. The agent copied both, unchanged, to `/tmp/scs-wheels/` under their
   original names and installed from there. For WP-10: a skill that bundles wheels must install
   them under their standard names. Dependencies installed from PyPI without trouble.

