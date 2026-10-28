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
| Claude.ai | | | | | | | | | | |
| Cursor | | | | | | | | | | |
| Codex | | | | | | | | | | |
| GitHub Copilot | | | | | | | | | | |

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
