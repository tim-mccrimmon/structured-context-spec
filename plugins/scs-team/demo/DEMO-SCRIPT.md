# SCS Team Demo Script

> Target: 3-5 minutes | Audience: Developers + Decision Makers
> Format: Hybrid (separate intro, live demo with narration, outro)

---

## SEGMENT 1: INTRO (Record separately, ~30 seconds)

**[Title card or simple slide: "SCS Team — Structured Context for Teams"]**

> "Your team has PRDs, architecture docs, security requirements. Claude doesn't know any of it. So every session, it makes decisions that conflict with what's already been decided.
>
> SCS Team takes your existing documentation and transforms it into structured context that Claude actually uses. It organizes it into 11 concern areas — from architecture to compliance to business context — and compiles it into Claude Code rules automatically.
>
> Here's a team project with real docs. Let's see what happens."

---

## SEGMENT 2: LIVE DEMO (Screen + voice, ~3-4 minutes)

### Setup context (before recording, have ready):
- Terminal open, in the scs-team demo project directory
- Project should be clean (no .scs/ or .claude/ directories)
- `ls` to show the project structure

---

### Scene 1: Show the starting point (~20 seconds)

**[Terminal visible, in the demo project directory]**

```bash
ls
ls docs/
```

> "This is a patient portal — a FastAPI app built by a team. We've got a PRD from the product manager, an architecture doc from the CTO, and security requirements from the CISO. Real code in src/. But no structured context — Claude doesn't know any of this exists."

---

### Scene 2: Launch and initialize (~30 seconds)

```bash
claude --plugin-dir /path/to/plugins/scs-team
```

**[Wait for Claude Code to start]**

```
/scs-team:init
```

> "Init scans the project and scaffolds the .scs directory with all 11 concern bundles. It detects Python, FastAPI, finds our three docs, and spots HIPAA keywords. Watch the recommendations it gives us."

**[Show the output — it should recommend adding the docs and using HIPAA]**

> "It found our docs and is telling us exactly what to do next. Let's follow its lead."

---

### Scene 3: Process existing documentation (~60 seconds)

```
/scs-team:add docs/PRD.md
```

> "We feed it the PRD. It analyzes the document, extracts structured information — problem definition, stakeholders, success criteria — and maps it to the right concern areas. Then it compiles to Claude Code rules automatically."

**[Show the output summary — what SCDs were created, what concerns were updated]**

```
/scs-team:add docs/architecture.md
```

> "Same thing with the architecture doc. System context, tech stack, component model — all extracted and organized."

**[If time is tight, you can skip showing the full output and just narrate]**

---

### Scene 4: Add compliance standards (~30 seconds)

```
/scs-team:use hipaa
```

> "Now the powerful part. The plugin ships with pre-built compliance standards. One command, and we get HIPAA requirements — PHI handling rules, security controls, administrative safeguards. These aren't templates — they're real requirements that Claude will follow."

**[Show the output — 3 HIPAA SCDs added, what they contain]**

> "Notice it tells us what we still need to customize — which data in OUR system is PHI, our specific retention period, our business associates."

---

### Scene 5: Check the big picture (~30 seconds)

```
/scs-team:status
```

> "Status shows us the full picture across all 11 concerns. Architecture and business context are covered from our docs. Compliance is partially covered from HIPAA. But look — security, performance, testing, deployment — all missing. The plugin doesn't pretend those gaps don't exist. It surfaces them."

**[Show the coverage table — some Covered, some Partial, most Missing]**

> "For a team, this is the conversation starter. Which gaps matter? Who owns them? That's how structured context becomes a team process, not just a tool."

---

### Scene 6: Show the compiled output (~20 seconds)

```bash
ls .claude/rules/
```

> "Everything compiled automatically to Claude Code rules. Architecture, business, compliance — all with managed markers so the plugin knows which files it owns. Your custom rules stay untouched."

**[Quick peek at one file]**

> "Every Claude Code session in this project now starts with the full picture. Architecture decisions, compliance boundaries, business context — all from docs that already existed."

---

## SEGMENT 3: OUTRO (Can be live or recorded separately, ~15 seconds)

> "SCS Team is open source. It supports HIPAA, SOC2, PCI, GDPR, and CHAI out of the box, with 11 concern areas that cover everything from architecture to ethics. Link in the description.
>
> If you're a solo dev, start with SCS Vibe — same idea, 15-minute setup, no docs required.
>
> Thanks for watching."

---

## PRODUCTION NOTES

### OBS Setup
- Same as scs-vibe: terminal capture + mic for demo, title card + mic for intro/outro

### What to skip if running long:
- The second `/scs-team:add` (architecture.md) — can narrate "and we'd do the same for the architecture doc" while skipping
- The detailed HIPAA output — just hit the key points
- Don't try to do `/scs-team:draft` — that's a conversation and will blow the time budget

### Key talking points to hit:
1. **The problem**: Team has docs, Claude doesn't know about them
2. **The workflow**: init → add docs → use standards → status
3. **The 11 concerns**: This is a taxonomy, not a checklist — use what's relevant
4. **Pre-built standards**: One command for HIPAA compliance context
5. **Gap surfacing**: The plugin tells you what's MISSING, not just what exists
6. **Dual-layer output**: Source in .scs/, compiled to .claude/rules/

### Commands NOT to demo (save for a longer video):
- `/scs-team:draft` — too conversational for 3-5 min
- `/scs-team:validate` — important but not visually exciting
- `/scs-team:version` — save for a "full workflow" video

### If something goes wrong:
- Claude asks for confirmation: Say yes and narrate what it's doing
- Output is too long: Narrate over it, "you can see it's extracting..."
- Unexpected behavior: Roll with it — real tools have personality
