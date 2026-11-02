# SCS Agent Skills

Four skills in the open [Agent Skills](https://agentskills.io/specification) format that let an
AI assistant operate SCS for a user: build and maintain a Domain repository, validate it, version
it, and compile it, with the user confirming every change. They follow
[`spec/0.7/agent-interface.md`](../spec/0.7/agent-interface.md). Every write goes through the SCS
tools (`scs`, `scs-validate`) in machine mode; the skills carry the conversation and the judgment.

| Skill | Does |
|---|---|
| [`scs-domain`](scs-domain/SKILL.md) | The Domain, from setup to a compiled version: welcome, source documents, intake, people, drafting, review, versioning, compiling; resumes or updates from `scs status` |
| [`scs-project`](scs-project/SKILL.md) | One Project, the same way, once the Domain has a released version; reviews the Project with the Domain and records Domain conflicts as questions for the Domain owner |
| [`scs-validate`](scs-validate/SKILL.md) | Runs the validator and explains the results before proposing fixes |
| [`scs-explain`](scs-explain/SKILL.md) | Explains where the work stands, a workspace, a rule's origin, an artifact, or a message |

Run the Domain and each Project in separate sessions. Each session starts from `scs status`, so
work can stop at any point and resume later.

Status: 0.7 release candidate 2. The rc1 skills (`scs-intake`, `scs-draft`, `scs-review`,
`scs-version`, `scs-compile`) passed the behaviour tests (D-51); rc2 reorganizes them by workspace
(D-81), and its behaviour tests (WP-10b) are not yet run. Earlier reports are in
[`tools/skill-harness/results/`](../tools/skill-harness/results/).

## Installing the skills

Checked 2026-10-28 against [Claude Code: skills](https://code.claude.com/docs/en/skills) and
[Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

- **Claude Code:** copy each skill directory to `~/.claude/skills/<skill-name>/` (all your work)
  or to `.claude/skills/<skill-name>/` in the Domain repository.
- **Claude (claude.ai):** upload each skill as a ZIP under **Customize > Skills**
  (**+**, **Create skill**, **Upload a skill**). `python skills/package.py --out <dir>` builds
  the ZIPs; add `--wheels <dir>` to bundle the scs-tools and scs-validator wheels, since
  Claude's sandbox may not reach the package index you need. Code execution must be on. On Team and
  Enterprise plans an owner enables code execution and skills, and can upload skills for the
  whole organization.

## Installing the SCS tools

Each skill's `scripts/scs_engine.py check` reports whether the tools are installed and new
enough, and `install-plan` gives the command to show the user, in the D-27 order: PyPI, a GitHub
tag, then wheels bundled with the skill or uploaded to the chat. The skill installs nothing
without the user's agreement. What works in each client is recorded in
[`docs/install-matrix.md`](../docs/install-matrix.md).

## Maintaining the skills

Some files are copies, so each skill stays self-contained: `scripts/scs_engine.py` (from
`shared/scs_engine.py`), the stage procedures in `scs-domain/references/` and
`scs-project/references/` (from `shared/references/`, edited there only),
`references/placement/` in the same two skills (from `docs/placement/`), and
`scs-validate/references/diagnostics.md` (from `schema/diagnostics/codes.yaml`). After changing a source, run:

```bash
python skills/sync.py          # requires PyYAML
python skills/sync.py --check  # what CI runs
```

`tools/cli/tests/test_skills.py` checks the format, the shared rules, the copies, and that every
engine command and flag a skill names exists.
