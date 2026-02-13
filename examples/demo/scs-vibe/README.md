# SCS Vibe Demo - Care Plan Tracker

A demo project for testing the `scs-vibe` Claude Code plugin.

## Scenario

You're a solo developer with an idea: a CLI tool to help patients track their care plans. You've written a PRD. That's it. No code, no architecture docs, no CLAUDE.md. Just the idea.

## Prerequisites

- Claude Code installed and working
- This directory open as your project root

## Demo

### 1. Launch Claude Code with the plugin

```bash
claude --plugin-dir /path/to/plugins/scs-vibe
```

### 2. Run init

```
/scs-vibe:init
```

Answer the questions conversationally. The plugin will generate:
- `CLAUDE.md` - Project context
- `.claude/rules/` - Modular rules files
- `CONSIDERATIONS.md` - Compliance, security, and legal items to think about

### 3. Check what was generated

Look at what scs-vibe created. Pay attention to:
- Did it pick up the healthcare domain from the PRD?
- Did it flag HIPAA as a consideration? (The PRD never mentions it)
- Does the generated context reflect the project's intent?

### 4. Ask Claude to build it

With context now in place, try:

```
Build the care plan tracker from the PRD
```

Watch how Claude approaches it with structured context vs without. Does it consider data sensitivity? Does the architecture match what scs-vibe captured?

## What's in this project

| File | Purpose |
|------|---------|
| `PRD.md` | Product requirements (mentions patients, care plans, medications) |

That's it. One file. The plugin does the rest.
