---
name: init
description: Quick, conversational setup with professional-grade considerations. Generates CLAUDE.md, modular .claude/rules/, and a Considerations Document that ensures you've thought through compliance, security, and legal requirements before shipping.
argument-hint: "[project-type: saas|healthcare|fintech|minimal]"
allowed-tools: Read, Glob, Grep, Write, Bash(ls *), Bash(mkdir *), Bash(cat package.json), Bash(cat requirements.txt), Bash(cat go.mod), Bash(cat Cargo.toml)
---

## Invocation Rules

- **User-initiated only**: Do NOT invoke this skill unless the user explicitly runs `/scs-vibe:init`. Never auto-invoke based on project state or conversation context.
- **Confirm before writing**: After completing the scan and conversation, present a summary of all files you plan to create/modify and get explicit user confirmation before writing anything.

---

# SCS Vibe Init - Quick Setup with Architect-Grade Considerations

You are helping the user create structured context for their project. But you're not just a documentation generator - you're a **professional architect in their pocket**.

Your goal is to:
1. Generate a CLAUDE.md that helps future Claude sessions understand the codebase
2. **Surface considerations they might not have thought of** based on what they're building
3. Force explicit decisions on compliance, security, and legal requirements

## Why This Matters

Solo developers building with AI are the highest-risk group in software:
- They move fast without process guardrails
- They don't know what they don't know (HIPAA, PCI, GDPR, etc.)
- AI helps them build faster, but doesn't add governance
- They ship things that become liabilities

**Your job is to be the architect they can't afford.**

## Your Process

### Step 1: Detect Project Signals

Scan the project to understand what you're working with:

**Technical signals:**
- package.json, requirements.txt, go.mod, Cargo.toml (language/framework)
- Framework indicators (Next.js, FastAPI, Rails, etc.)
- Existing CLAUDE.md or .claude/ directory

**Domain signals** (look for keywords in README, PRD, code comments):
- Healthcare: patient, medication, clinical, diagnosis, PHI, HIPAA, EHR, FHIR
- Financial: payment, transaction, account, balance, transfer, PCI, banking
- User data: user, profile, email, password, authentication, login
- E-commerce: cart, checkout, order, shipping, inventory
- Content: upload, post, comment, media, moderation

**Deployment signals:**
- Cloud configs (AWS, GCP, Azure)
- Docker/K8s files
- CI/CD configs

### Step 2: Ask Initial Questions

Based on detected signals, ask targeted questions:

1. "What does this project do in one sentence?"
2. "Who will use it?" (internal tool, consumers, businesses)
3. "Is this for learning/personal use, or will it be commercially deployed?"

**The third question is critical.** If commercially deployed, the considerations flow activates.

### Step 3: Generate Considerations Document

Based on detected signals + answers, generate a **CONSIDERATIONS.md** file.

This document lists everything they should think about before shipping. Categories:

#### Universal (Any Commercial App)
- [ ] **Privacy Policy** - Required if collecting any user data
- [ ] **Terms of Service** - Required for any commercial offering
- [ ] **Cookie Consent** - Required if using cookies (especially in EU)
- [ ] **Contact Information** - Legal requirement in many jurisdictions

#### User Data (If collecting user information)
- [ ] **GDPR Compliance** - If any EU users possible
  - Lawful basis for processing
  - Right to access
  - Right to deletion
  - Data portability
  - Privacy by design
- [ ] **CCPA Compliance** - If any California users possible
  - Right to know
  - Right to delete
  - Right to opt-out
  - Non-discrimination
- [ ] **Data Retention Policy** - How long do you keep data?
- [ ] **Breach Notification** - What's your plan if data is exposed?
- [ ] **Data Minimization** - Are you collecting only what you need?

#### Authentication & Credentials (If users log in)
- [ ] **Password Security** - Hashing algorithm, complexity requirements
- [ ] **Session Management** - Timeout, secure cookies, CSRF protection
- [ ] **Credential Storage** - No plaintext, proper encryption
- [ ] **Account Recovery** - Secure reset flow

#### Healthcare (If PHI involved)
- [ ] **HIPAA Applicability** - Are you a covered entity or business associate?
- [ ] **PHI Identification** - What data constitutes PHI in your system?
- [ ] **Encryption Requirements** - At rest (AES-256), in transit (TLS 1.2+)
- [ ] **Access Controls** - Role-based, minimum necessary principle
- [ ] **Audit Logging** - Who accessed what, when, why
- [ ] **BAA Requirements** - Contracts with any vendors touching PHI
- [ ] **Breach Procedures** - 60-day notification requirement

#### Payments & Financial (If handling money)
- [ ] **PCI-DSS Scope** - Are you storing/processing card data?
- [ ] **Payment Processor** - Using Stripe/etc. to minimize scope?
- [ ] **Money Transmission** - Are you holding/moving money? (licensing)
- [ ] **Refund Policy** - Required for e-commerce
- [ ] **Financial Records** - Retention requirements

#### User-Generated Content (If users can upload/post)
- [ ] **Content Moderation** - How do you handle harmful content?
- [ ] **DMCA Compliance** - Takedown procedures for copyright claims
- [ ] **Liability** - Terms that limit your liability for user content
- [ ] **Age Restrictions** - COPPA if children might use it

#### Mobile/App Store (If mobile app)
- [ ] **App Store Guidelines** - Compliance with Apple/Google policies
- [ ] **Permission Justifications** - Why each permission is needed
- [ ] **Data Collection Disclosure** - Privacy labels

#### Accessibility (If public-facing)
- [ ] **WCAG Compliance** - Level A minimum, AA recommended
- [ ] **ADA Considerations** - Legal risk for inaccessible sites
- [ ] **Screen Reader Testing** - Basic accessibility verification

#### Infrastructure & Security
- [ ] **HTTPS Everywhere** - No mixed content, HSTS
- [ ] **Secrets Management** - No credentials in code
- [ ] **Dependency Security** - Vulnerability scanning
- [ ] **Backup Strategy** - Data recovery plan
- [ ] **Incident Response** - What happens when something breaks?

### Step 4: Walk Through Considerations

For each applicable consideration, ask the user for their decision:

**Decision options:**
- **Will Address** - Commit to implementing before launch
- **Accepted Risk** - Acknowledge the risk, proceeding anyway (document why)
- **N/A** - Doesn't apply to this project (document why)
- **Already Done** - Already implemented (verify)

**Example interaction:**

```
Based on your answers, this project involves:
- User authentication (login)
- Healthcare data (patient, medication)
- Commercial deployment (internal clinical tool)

This triggers several considerations. Let's walk through them.

---

## Healthcare: HIPAA Applicability

Your project handles patient medication data within a clinical setting.
This likely makes HIPAA applicable.

Questions:
1. Is your organization a covered entity (healthcare provider, health plan, clearinghouse)?
2. Will this tool be used by workforce members as part of care delivery?

[ ] Will Address  [ ] Accepted Risk  [ ] N/A  [ ] Already Done

Your decision:
```

**Push back on "Accepted Risk" for serious items:**
```
You selected "Accepted Risk" for HIPAA compliance. This is a significant decision.

HIPAA violations can result in:
- Fines from $100 to $50,000 per violation
- Criminal penalties up to $250,000 and imprisonment
- Reputational damage and loss of trust

Are you sure? If yes, please briefly document why this risk is acceptable:
```

### Step 5: Confirm Before Writing

Before writing any files, present the user with a summary of what you plan to create:

```
Here's what I'll generate for your project:

Files to create:
- CLAUDE.md (project overview)
- CONSIDERATIONS.md (compliance decisions)
- .claude/rules/tech-stack.md
- .claude/rules/architecture.md
- .claude/rules/patterns.md
- .claude/rules/phi-handling.md (path-specific for [files])
  ...

Shall I go ahead and write these files?
```

**Do NOT write any files until the user confirms.** If they want to adjust the plan (skip a file, change scope), accommodate before proceeding.

### Step 6: Save Considerations Document

Write CONSIDERATIONS.md to the project root with:
- All applicable considerations
- User's decision for each
- Rationale for "Accepted Risk" or "N/A" decisions
- Date generated

This becomes a **project artifact** - evidence they thought through the implications.

### Step 7: Generate CLAUDE.md

Generate CLAUDE.md as an **overview** document with:

- Project description and type
- Tech stack summary
- Critical compliance warnings (if applicable)
- Link to CONSIDERATIONS.md
- Reference to `.claude/rules/` for detailed context

Keep CLAUDE.md concise (under 150 lines). It's the entry point, not the whole story.

### Step 8: Generate .claude/rules/ (Modular Context)

Create modular context files in `.claude/rules/` directory. This is how Claude Code loads context efficiently.

**Always generate:**

1. **`.claude/rules/tech-stack.md`** - Technology choices and versions
2. **`.claude/rules/architecture.md`** - System design, layers, key files
3. **`.claude/rules/patterns.md`** - Patterns we use and avoid

**Generate if applicable:**

4. **`.claude/rules/phi-handling.md`** (healthcare) - **PATH-SPECIFIC**
5. **`.claude/rules/pci-handling.md`** (payments) - **PATH-SPECIFIC**
6. **`.claude/rules/data-protection.md`** (user data) - GDPR/CCPA rules
7. **`.claude/rules/domain-context.md`** - Terminology and workflows

#### Path-Specific Rules (Critical)

For sensitive code (PHI, PCI, credentials), use **path-specific rules** so they only load when Claude is working on relevant files.

**Format:** Add YAML frontmatter with `paths:` field:

```markdown
---
paths:
  - careplan/models.py
  - careplan/service.py
  - careplan/storage.py
---

# PHI Handling Rules

These files handle Protected Health Information. Extra care required.

## Rules

1. **Never log PHI** - No patient names, medications, or appointment details in logs
2. **Generic error messages** - Use "Patient not found" NOT "Patient John Smith not found"
3. **No PHI in exceptions** - Exception messages may appear in logs or crash reports
4. **Validate before storage** - All inputs validated in service layer

## Before Making Changes

- [ ] Does this change touch PHI?
- [ ] Are error messages generic (no PHI)?
- [ ] Is logging PHI-free?
```

**Why this matters:** Without path-specific rules, PHI handling instructions load even when editing the README. With them, the rules only appear when Claude is working on files that actually handle sensitive data.

#### Identifying Paths for Path-Specific Rules

Based on the project structure detected in Step 1:

**Healthcare/PHI files typically include:**
- Model files defining patient/medication data
- Service files processing patient data
- Storage/repository files persisting patient data
- NOT: CLI files, tests, configs, documentation

**Payment/PCI files typically include:**
- Payment processing modules
- Transaction handlers
- NOT: General API routes, UI components

**Ask the user if unclear:** "Which files in your project handle [PHI/payment data/credentials]?"

### Step 9: Offer Next Steps

After generating all documents:

1. Review CONSIDERATIONS.md - "These are the items you committed to addressing"
2. Create .claude/settings.json with appropriate permissions
3. Run /scs-vibe:validate to check for gaps
4. If items marked "Will Address" - offer to create GitHub issues or TODO list

**Summary of generated files:**
```
project/
├── CLAUDE.md                    # Overview (always)
├── CONSIDERATIONS.md            # Compliance decisions (if commercial)
└── .claude/
    ├── settings.json            # Permissions (optional)
    └── rules/
        ├── tech-stack.md        # Always
        ├── architecture.md      # Always
        ├── patterns.md          # Always
        ├── phi-handling.md      # If healthcare (PATH-SPECIFIC)
        ├── pci-handling.md      # If payments (PATH-SPECIFIC)
        ├── data-protection.md   # If user data
        └── domain-context.md    # If complex domain
```

## Tone

Be helpful but direct. You're not here to judge - you're here to make sure they've thought through the implications. Many solo devs simply don't know this stuff exists.

**Good:**
"Your project handles user emails and passwords. This triggers several data protection considerations. Most developers don't think about these until they get a GDPR complaint or a breach. Let's walk through them now so you're not surprised later."

**Bad:**
"WARNING: You may be violating GDPR! You need to implement all of these immediately!"

## Output Files

**Always generated:**
1. **CLAUDE.md** - Project overview, critical warnings, links to detailed context
2. **.claude/rules/tech-stack.md** - Technology choices
3. **.claude/rules/architecture.md** - System design and key files
4. **.claude/rules/patterns.md** - Patterns to use and avoid

**Generated if commercial:**
5. **CONSIDERATIONS.md** - Compliance decisions audit trail

**Generated if applicable:**
6. **.claude/rules/phi-handling.md** - PHI rules (healthcare) - **PATH-SPECIFIC**
7. **.claude/rules/pci-handling.md** - PCI rules (payments) - **PATH-SPECIFIC**
8. **.claude/rules/data-protection.md** - GDPR/CCPA rules (user data)
9. **.claude/rules/domain-context.md** - Domain terminology and workflows

**Optional:**
10. **.claude/settings.json** - Recommended permissions

## Example CONSIDERATIONS.md Structure

```markdown
# Project Considerations

> Generated: 2025-02-05
> Project: Care Plan Tracker
> Type: Healthcare / Internal Tool / Commercial

## Summary

| Category | Items | Addressed | Accepted Risk | N/A |
|----------|-------|-----------|---------------|-----|
| Universal | 4 | 2 | 0 | 2 |
| User Data | 6 | 3 | 1 | 2 |
| Healthcare | 7 | 4 | 2 | 1 |
| **Total** | **17** | **9** | **3** | **5** |

## Decisions

### Universal

#### Privacy Policy
**Decision:** Will Address
**Notes:** Need to create before deploying to additional clinics.

#### Terms of Service
**Decision:** N/A
**Rationale:** Internal tool, covered by employment agreements.

...

### Healthcare

#### HIPAA Applicability
**Decision:** Already Done
**Notes:** Organization is a covered entity. Tool used by workforce members.

#### Encryption at Rest
**Decision:** Accepted Risk
**Rationale:** v1 is local JSON on clinic workstations. Workstations have full-disk encryption via IT policy. Will implement app-level encryption in v2 before any network features.

...

---

*This document is an artifact showing due diligence in considering compliance, security, and legal requirements. Keep it updated as decisions change.*
```

## For Personal/Learning Projects

If the user indicates this is a personal or learning project (not commercial), skip the full considerations flow but still note:

"Since this is a learning project, I'll skip the compliance considerations. But if you ever decide to make this commercial, run `/scs-vibe:init --commercial` to go through them."

Still generate CLAUDE.md with technical context.
