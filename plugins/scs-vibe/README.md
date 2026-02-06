# SCS Vibe - Structured Context for Vibe Coders

> Stop Claude from coding you into corners. In 15 minutes.

## The Problem

You're vibe coding - moving fast, building something cool. But Claude doesn't know YOUR project. Without context, it makes confident decisions that:

- Conflict with choices you made yesterday
- Don't fit the patterns you've established
- Require rework to integrate
- Add abstractions you don't want

Three weeks in, you're fighting your own codebase.

## The Solution

SCS Vibe is a quick, conversational setup. In 15 minutes, you give Claude enough context to work WITH your system instead of against it.

No PRDs. No architecture docs. Just answer a few questions.

## Installation

```bash
/install scs-vibe
```

## Commands

### `/scs-vibe:init`

Interactive setup that generates structured context for your project.

```
/scs-vibe:init              # Auto-detect and ask questions
/scs-vibe:init healthcare   # Include HIPAA considerations
/scs-vibe:init fintech      # Include SOC2/financial considerations
/scs-vibe:init minimal      # Bare minimum for tiny projects
```

The wizard will:
1. Scan your project to detect tech stack
2. Ask targeted questions about your architecture
3. Push back if answers are too vague
4. Generate a structured CLAUDE.md

### `/scs-vibe:validate`

Check your existing context for completeness and issues.

```
/scs-vibe:validate
```

Checks for:
- Missing critical sections
- Generic/placeholder content
- Stale file references
- Gaps that might bite you later

### `/scs-vibe:explain`

Learn why structured context matters.

```
/scs-vibe:explain
```

## What Gets Generated

A CLAUDE.md file with:

- **What This Is** - What you're building, who uses it
- **Architecture** - How it's structured, key pieces
- **Tech Stack** - Specific technologies and versions
- **Patterns** - What you use, what you avoid, and why
- **Constraints** - Limits Claude must respect
- **Domain Context** - Business concepts and terminology

## Example

**Before** (no context):
```
You: "Add caching to the user lookup"

Claude: "I'll add Redis caching with a 24-hour TTL..."

[You use Memcached with a 1-hour policy and already have a cache utility]
```

**After** (with context):
```
You: "Add caching to the user lookup"

Claude: "I'll use your CacheService in /lib/cache
with a 1-hour TTL per your policy..."

[Claude works WITHIN your system]
```

## Templates

| Template | Use Case |
|----------|----------|
| `minimal` | Small projects, quick start |
| `saas` | Standard SaaS applications |
| `healthcare` | HIPAA considerations (PHI, audit logging) |
| `fintech` | Financial services (SOC2, transactions) |

## Growing Beyond Vibe

When your project gets serious - team members, compliance requirements, real documentation - check out [SCS Team](https://github.com/structuredcontext/scs-team) for the full workflow.

## Links

- Documentation: https://structuredcontext.io
- GitHub: https://github.com/structuredcontext/scs-vibe
- For Teams: https://github.com/structuredcontext/scs-team

## License

Apache 2.0

---

*Built by [Tim McCrimmon](https://github.com/tim-mccrimmon)*
