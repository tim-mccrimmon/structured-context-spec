---
name: explain
description: Learn why structured context matters. Quick explanation for skeptics and the curious.
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-vibe:explain`. Never auto-invoke based on project state or conversation context.

---

# Why Structured Context Matters (For Vibe Coders)

You're explaining the value of structured context to a developer who may be skeptical or just curious.

## The Core Message

Keep it practical and relatable. Don't oversell. The message is:

> "Claude is smart but doesn't know YOUR system. Without explicit context, it makes confident decisions based on general knowledge - which often codes you into corners. Structured context gives Claude a 'world' to operate in."

## Key Points to Cover

### 1. The Problem (Make It Relatable)

Share scenarios they've probably experienced:

- "Claude suggested a perfectly reasonable solution... that conflicted with a design decision you made 3 months ago"
- "Claude built a feature that works in isolation but doesn't fit your existing patterns"
- "Every new session, you're re-explaining your architecture"
- "Claude invented an abstraction you now have to maintain, when a simpler approach would have worked"

**The root cause:** Claude has vast general knowledge but zero knowledge of YOUR specific system. It fills the gaps with reasonable-sounding guesses.

### 2. The Solution (Keep It Simple)

Structured context = telling Claude about your system BEFORE it starts making decisions.

It's like onboarding a new developer:
- Here's what we're building
- Here's how it's structured
- Here are the patterns we use (and avoid)
- Here are the constraints you need to know

**The key insight:** This isn't about making Claude smarter. It's about giving it the information it needs to apply its intelligence appropriately.

### 3. What Goes in Structured Context

The essentials:
- **System Overview**: What does this do? Who uses it?
- **Architecture**: How is it structured? What are the key components?
- **Tech Stack**: What specific technologies and why?
- **Patterns**: What patterns do we use? What do we avoid?
- **Constraints**: What limits must Claude respect?

### 4. Before/After Example

**Without structured context:**
```
User: "Add a caching layer for the user lookup"

Claude: "I'll add Redis caching using the popular redis-om library
with a 24-hour TTL..."

[Problem: You use Memcached, you have a 1-hour max TTL policy,
and you have an existing caching utility Claude didn't know about]
```

**With structured context:**
```
CLAUDE.md:
- Cache: Memcached via /lib/cache utility
- Constraint: Max TTL 1 hour (compliance requirement)
- Pattern: All caching goes through CacheService

User: "Add a caching layer for the user lookup"

Claude: "I'll add caching using your existing CacheService in /lib/cache.
Based on your 1-hour max TTL constraint, I'll set TTL to 3600 seconds.
Here's the implementation following your existing patterns..."

[Claude works WITHIN your system instead of inventing a new one]
```

### 5. How to Get Started

1. Run `/scs-vibe:init` - 15 minute setup
2. Review and tweak - Add anything specific
3. Commit it - Version control your context
4. Run `/scs-vibe:validate` occasionally - Keep it fresh

### 6. Address Common Objections

**"I already have a CLAUDE.md"**
Great! Run `/scs-vibe:validate` to check if it's still accurate. Context gets stale fast.

**"This seems like a lot of work"**
15 minutes. That's it. `/scs-vibe:init` does most of the work - you're just confirming and adding detail.

**"Will Claude actually use this?"**
Yes. Claude reads CLAUDE.md at the start of every session. The more specific you are, the better it works.

**"What if my project grows?"**
When you have a real team, PRDs, architecture docs - check out [SCS Team](https://github.com/structuredcontext/scs-team) for the full workflow.

## Tone Guidelines

- Be helpful, not salesy
- Use concrete examples
- Acknowledge skepticism is reasonable
- Don't promise magic - promise better-aligned assistance
- Keep it brief

## Resources to Mention

- Documentation: https://structuredcontext.dev
- Commands: `/scs-vibe:init`, `/scs-vibe:validate`
- For teams: [SCS Team](https://github.com/structuredcontext/scs-team)
