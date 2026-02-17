# SCS Vibe Demo Script

> Target: 3-5 minutes | Audience: Developers + Decision Makers
> Format: Hybrid (separate intro, live demo with narration, outro)

---

## SEGMENT 1: INTRO (Record separately, ~30 seconds)

**[Title card or simple slide: "SCS Vibe — Structured Context for Vibe Coders"]**

> "If you're using Claude Code to build software, you've probably noticed something: Claude is smart, but it doesn't know YOUR project. Without context, it makes confident decisions that conflict with what you've already built. Three weeks in, you're fighting your own codebase.
>
> SCS Vibe fixes this in about 15 minutes. It's a Claude Code plugin that scans your project, asks a few questions, and generates structured context so Claude works WITH your system instead of against it.
>
> Let me show you."

---

## SEGMENT 2: LIVE DEMO (Screen + voice, ~3 minutes)

### Setup context (before recording, have ready):
- Terminal open, in the demo project directory
- The demo project should be clean (just the PRD.md, no CLAUDE.md or .claude/ yet)
- `ls` the directory so viewers can see it's just a PRD

---

### Scene 1: Show the starting point (~20 seconds)

**[Terminal visible, in the demo project directory]**

```bash
ls
```

> "Here's what we're starting with: a single PRD for a care plan tracker — a CLI tool to help patients manage their medications and appointments. That's it. No code, no architecture docs, no CLAUDE.md. Just the idea."

**[Optional: quick `cat PRD.md | head -20` to flash the PRD content]**

---

### Scene 2: Launch Claude Code with the plugin (~15 seconds)

```bash
claude --plugin-dir /path/to/plugins/scs-vibe
```

> "We launch Claude Code with the scs-vibe plugin loaded. This gives us the `/scs-vibe:init` command."

**[Wait for Claude Code to start]**

---

### Scene 3: Run init (~90 seconds — this is the core of the demo)

```
/scs-vibe:init
```

> "Now we run init. Watch what happens — it scans the project, detects the tech signals, and picks up that this is healthcare related from the PRD. It didn't need us to tell it."

**[Claude scans, detects signals]**

> "It asks three questions: what does this do, who uses it, and is this personal or commercial? These matter — the third one triggers the compliance considerations flow."

**[Answer the questions conversationally:]**
- Q1 (What does this do): "A CLI tool that helps patients track their care plans — medications, appointments, and daily check-ins"
- Q2 (Who uses it): "Patients and their caregivers, eventually used in clinical settings"
- Q3 (Personal or commercial): "Commercial — internal tool for a clinic"

> "Because we said commercial AND it detected healthcare keywords, it's now going to surface compliance considerations. This is the part that matters — it's acting as the architect you don't have on your team."

**[Walk through a few considerations — don't need to do all of them]**

> "Look at this — it flagged HIPAA applicability. The PRD never mentions HIPAA. But it knows patient medication data in a clinical setting means HIPAA likely applies. It's forcing us to make a decision now, not after we've shipped."

**[Make quick decisions on 2-3 items to show the flow, then skip ahead if possible]**

---

### Scene 4: Show the generated files (~30 seconds)

> "Now it confirms what it's going to generate, and after we approve..."

**[After files are written, show the results]**

```bash
ls -la
cat CLAUDE.md
```

> "We've got a CLAUDE.md, a CONSIDERATIONS.md with our compliance decisions, and modular rules in .claude/rules."

```bash
ls .claude/rules/
```

> "Tech stack, architecture, patterns, and — because it detected healthcare — PHI handling rules that are path-specific. They only load when Claude is editing files that actually touch patient data."

---

### Scene 5: The payoff (~30 seconds)

> "Now every Claude Code session in this project starts with this context. Claude knows the tech stack, the architecture patterns, the compliance boundaries. When you say 'build the care plan tracker,' it works within YOUR system — not its own invented version of it.
>
> From one PRD to a fully contextualized project in under 15 minutes."

---

## SEGMENT 3: OUTRO (Can be live or recorded separately, ~15 seconds)

> "SCS Vibe is open source. Link in the description. If your project grows into a team effort, check out SCS Team for the full workflow with 11 concern areas, compliance standards, and versioning.
>
> Thanks for watching."

---

## PRODUCTION NOTES

### OBS Setup
- **Scene 1 (Intro)**: Title card + mic audio. Can be a simple text slide or just your voice over the title.
- **Scene 2 (Demo)**: Full screen terminal capture + mic audio. Record together.
- **Scene 3 (Outro)**: Same as intro, or just keep the terminal up.

### Terminal Tips
- Increase font size (16-18pt) so it's readable on small screens
- Use a clean terminal theme (dark background, good contrast)
- Clear the terminal before starting each scene
- If Claude's output is long, don't worry about reading all of it — narrate over it

### Timing Tips
- While Claude is processing/scanning, narrate what it's doing and why
- Don't rush the considerations section — that's the "wow" moment for decision makers
- If something takes too long, you can cut it in post (splice the screen recording)

### Key talking points to hit:
1. **The problem**: Claude doesn't know your project, makes confident wrong decisions
2. **The detection**: Plugin found healthcare signals the PRD didn't explicitly mention
3. **The considerations**: Architect-in-your-pocket moment (HIPAA flagged automatically)
4. **The output**: Structured, modular, path-specific rules
5. **The payoff**: Every future session starts with context

### If something goes wrong:
- Claude asks unexpected questions: Just go with it, narrate what's happening
- Error occurs: Stop recording, fix, restart the segment
- Output looks different than expected: That's fine — you're showing a real tool, not a scripted demo
