# SCS Agent Skills

Seven skills in the open [Agent Skills](https://agentskills.io/specification) format that let an
AI assistant operate SCS for a user: build and maintain a Domain repository, validate it, version
it, and compile it, with the user confirming every change. They follow
[`spec/0.7/agent-interface.md`](../spec/0.7/agent-interface.md). Every write goes through the SCS
tools (`scs`, `scs-validate`) in machine mode; the skills carry the conversation and the judgment.

| Skill | Does |
|---|---|
| [`scs-intake`](scs-intake/SKILL.md) | The intake conversation; creates the Domain repository and its workspaces; records `intake.yaml` |
| [`scs-draft`](scs-draft/SKILL.md) | Writes and maintains prohibitions, directives, and facts, from conversation or source documents |
| [`scs-review`](scs-review/SKILL.md) | Advisory review; records the user's decision on each finding |
| [`scs-validate`](scs-validate/SKILL.md) | Runs the validator and explains the results before proposing fixes |
| [`scs-version`](scs-version/SKILL.md) | Change summary, approver, and bottom-up versioning |
| [`scs-compile`](scs-compile/SKILL.md) | Compiles a version, previews stacks, and advises on placement |
| [`scs-explain`](scs-explain/SKILL.md) | Explains a workspace, a rule's origin, an artifact, or a message |

Status: draft for 0.7. The behaviour tests (scripted conversations, D-51) are not yet run.

## Installing the skills

Checked 2026-10-28 against [Claude Code: skills](https://code.claude.com/docs/en/skills) and
[Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

- **Claude Code:** copy each skill directory to `~/.claude/skills/<skill-name>/` (all your work)
  or to `.claude/skills/<skill-name>/` in the Domain repository.
- **Claude (claude.ai):** zip each skill directory and upload it under **Customize > Skills**
  (**+**, **Create skill**, **Upload a skill**). Code execution must be on. On Team and
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
`scs-intake`), `scs-validate/references/diagnostics.md` (from `schema/diagnostics/codes.yaml`),
and `scs-compile/references/placement/` (from `docs/placement/`). After changing a source, run:

```bash
python skills/sync.py          # requires PyYAML
python skills/sync.py --check  # what CI runs
```

`tools/cli/tests/test_skills.py` checks the format, the shared rules, the copies, and that every
engine command and flag a skill names exists.
