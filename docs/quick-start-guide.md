
# Structured Context (SCS) — Quick Start Guide (Version 0.3)
*Get from zero to your first working SCS bundle in 30 minutes.*

---

## **What You'll Build**

By the end of this guide, you will have:

1. Created your first **SCD (Structured Context Document)**
2. Built a minimal **Domain Bundle**
3. Created a **Project Bundle** that imports it
4. Validated your bundle structure
5. Seen how AI behaves differently with structured context loaded

**Time Required:** 30 minutes
**Prerequisites:** Basic YAML knowledge, familiarity with software development concepts

---

## **Step 1: Understand the Core Concepts (5 minutes)**

Before diving in, understand these three building blocks:

### **SCD (Structured Context Document)**
A single, atomic definition of one essential thing:
- A rule
- A boundary
- A constraint
- A domain concept

### **Bundle**
A versioned manifest that assembles SCDs into an operating environment.

**The 4 Bundle Types:**
1. **Project Bundle** — top-level orchestrator (imports all other bundles)
2. **Meta Bundle** — SCS foundation vocabulary (from specification)
3. **Standards Bundle** — compliance/regulatory requirements
4. **Domain Bundle** — organized by concern area (you'll create one of these)

### **The 11 Prescribed Domains**
Every production project needs all 11 domain bundles:
- Architecture
- Business Context
- Compliance & Governance
- Data & Provenance
- Deployment & Operations
- Ethics & AI Accountability
- Performance & Reliability
- Safety & Risk
- Security
- Testing & Validation
- Usability & Accessibility

**For this quick start, we'll create just the Business Context domain to keep it simple.**

---

## **Step 2: Create Your First SCD (5 minutes)**

Let's build a simple task management system and create our first SCD.

**Create:** `scd/project/business-context/actor-user.yaml`

```yaml
id: scd:business-context:actor-user
version: "0.1.0"
domain: business-context
type: actor
provenance:
  author: "Your Name"
  date: "2025-12-09"
  rationale: "Define the primary user of the task management system"

title: "User Actor Definition"

definition:
  name: "User"
  description: "Individual who creates, manages, and completes tasks"

responsibilities:
  - "Create new tasks with title and description"
  - "Mark tasks as complete or incomplete"
  - "View their task list"
  - "Delete tasks they own"

constraints:
  - "Users can only view and modify their own tasks"
  - "Users must be authenticated to access any functionality"

relationships:
  owns: ["Task"]
```

**What makes this a good SCD?**
- ✓ Atomic (defines exactly one concept: the User actor)
- ✓ Machine-readable (YAML structure)
- ✓ Minimal (only essential information)
- ✓ Versioned (0.1.0)
- ✓ Traceable (includes provenance)

---

## **Step 3: Create a Second SCD (5 minutes)**

Let's add a boundary constraint to define what the system is and isn't.

**Create:** `scd/project/architecture/boundary-system-scope.yaml`

```yaml
id: scd:architecture:boundary-system-scope
version: "0.1.0"
domain: architecture
type: boundary
provenance:
  author: "Your Name"
  date: "2025-12-09"
  rationale: "Define clear system boundaries to prevent scope creep"

title: "System Scope Boundary"

boundary:
  inside:
    - "Task creation and management"
    - "User authentication"
    - "Task completion tracking"

  outside:
    - "Team collaboration features"
    - "Task assignment to others"
    - "Calendar integration"
    - "Notifications or reminders"
    - "File attachments"

architectural_implications:
  - "System operates as single-user application"
  - "No real-time sync required"
  - "No complex permission model needed"
  - "Local-first data storage acceptable"
```

---

## **Step 4: Create Domain Bundles (5 minutes)**

Now organize your SCDs into domain bundles.

**Create:** `bundles/business-context.yaml`

```yaml
id: bundle:business-context
type: domain
version: "0.1.0"
description: "Business context for task management system"

provenance:
  author: "Your Name"
  date: "2025-12-09"

scds:
  - id: scd:business-context:actor-user
    version: "0.1.0"
```

**Create:** `bundles/architecture.yaml`

```yaml
id: bundle:architecture
type: domain
version: "0.1.0"
description: "Architectural boundaries and constraints"

provenance:
  author: "Your Name"
  date: "2025-12-09"

scds:
  - id: scd:architecture:boundary-system-scope
    version: "0.1.0"
```

**Note:** In a real project, you'd create all 11 domain bundles. For this quick start, we're keeping it minimal.

---

## **Step 5: Create the Project Bundle (5 minutes)**

The Project Bundle is the top-level orchestrator that imports all other bundles.

**Create:** `project-bundle.yaml`

```yaml
id: bundle:task-manager
type: project
version: "0.1.0"
description: "Task management system - minimal quick start example"

provenance:
  author: "Your Name"
  date: "2025-12-09"
  purpose: "Quick start demonstration of SCS structure"

# In a real project, you'd import meta and standards bundles
# For this quick start, we're focusing on domain bundles only

imports:
  # Domain bundles
  - id: bundle:business-context
    version: "0.1.0"
  - id: bundle:architecture
    version: "0.1.0"

# Project bundles contain imports only, no SCDs directly
scds: []

metadata:
  system_name: "Personal Task Manager"
  system_identity: "Single-user task tracking application"
  target_users: ["Individual users managing personal tasks"]
```

---

## **Step 6: Validate Your Bundle (3 minutes)**

**Manual validation checklist:**

✓ Every SCD has a unique `id`
✓ Every SCD has a `version`
✓ Every SCD declares one of the 11 canonical `domain` values
✓ Every Bundle references SCDs with matching `id` and `version`
✓ Project Bundle uses `type: project`
✓ Domain Bundles use `type: domain`
✓ Project Bundle contains imports only (empty `scds` array)
✓ Domain Bundles contain SCDs only (no `imports`)

**Using SCS-CLI (when available):**
```bash
scs-cli validate project-bundle.yaml
scs-cli explain bundle:task-manager:0.1.0
```

---

## **Step 7: Use Your Bundle with AI (5 minutes)**

Now comes the payoff. Load your bundle into an AI coding assistant and see the difference.

### **Without the bundle:**

**Prompt:** "Create a Task model for our task management system"

**AI might generate:**
```python
class Task:
    def __init__(self, title, description, assignee, team_id, priority, tags):
        self.title = title
        self.description = description
        self.assignee = assignee  # ❌ Not in scope!
        self.team_id = team_id    # ❌ Not in scope!
        self.priority = priority
        self.tags = tags
        self.attachments = []     # ❌ Not in scope!
```

The AI invented features outside your boundaries.

---

### **With the bundle loaded:**

**Instructions for your AI assistant:**
```
Load the following structured context as the authoritative
environment for this project:

[Paste your project-bundle.yaml and all imported bundles]

Now, create a Task model for our task management system.
```

**AI will generate:**
```python
class Task:
    """
    Task owned by a User. Per system scope boundary, this is
    single-user only with no team features or attachments.
    """
    def __init__(self, title, description, owner_id):
        self.title = title
        self.description = description
        self.owner_id = owner_id  # References User actor
        self.completed = False

    def mark_complete(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False
```

**Notice the difference:**
- ✓ Respects the system boundary (no teams, assignments, attachments)
- ✓ References the User actor from your SCD
- ✓ Includes only in-scope functionality
- ✓ Adds relevant comment showing it understands the constraints

---

## **What You've Learned**

You now understand:

1. **SCDs** are atomic, versioned definitions of essential concepts
2. **Domain Bundles** organize SCDs by concern area
3. **Project Bundles** orchestrate the complete environment by importing domain bundles
4. **Bundles create alignment** between human intent and AI behavior
5. **Structured context prevents drift** and keeps AI working within boundaries

---

## **Next Steps**

### **Expand Your Quick Start Project:**

1. Add more SCDs to your existing domain bundles:
   - `scd:business-context:entity-task` (define what a Task is)
   - `scd:security:auth-requirement` (how users authenticate)
   - `scd:data-provenance:task-schema` (task data structure)

2. Create the remaining 9 domain bundles:
   - Compliance & Governance
   - Data & Provenance
   - Deployment & Operations
   - Ethics & AI Accountability
   - Performance & Reliability
   - Safety & Risk
   - Security
   - Testing & Validation
   - Usability & Accessibility

3. Add Meta and Standards bundles (imported from SCS specification)

4. Version your bundle to 1.0.0 when ready for use

### **Explore the Reference Implementation:**

See a complete, production-ready example:
- `reference-implementation-guide-v0.3.md` in the boilerplate docs
- Full medication adherence system with all 11 domain bundles
- A/B comparisons of AI behavior with and without bundles

### **Learn the Full Lifecycle:**

Read `cedm-overview-v0.2.md` to understand:
- **Intent Phase** — capturing essential system truth
- **Validation Phase** — ensuring correctness and coherence
- **Versioning Phase** — freezing the contract
- **Build Phase** — developing with AI in the governed environment

### **Deepen Your Understanding:**

- **For the big picture:** Read `scs-cedm-story-v0.3.md` (7 chapters, comprehensive)
- **For messaging:** Review `messaging-guide-v0.3.md` (canonical terminology)
- **For specific questions:** Check `FAQ-v0.3.md` (20+ common questions)
- **For executives:** Share `scs-exec-overview-v0.3.md` with leadership

---

## **Common Mistakes to Avoid**

### **❌ Making SCDs too large**
Each SCD should define exactly one concept. If you're describing multiple things, split into multiple SCDs.

### **❌ Skipping domain assignment**
Every SCD must declare one of the 11 canonical domains.

### **❌ Mixing content in bundles**
- Project Bundles: imports only, no SCDs
- Domain Bundles: SCDs only, no imports
- Standards Bundle: either imports OR SCDs (not both)

### **❌ Adding implementation details**
SCDs define the environment, not the implementation. "Users must authenticate" ✓ vs. "Use JWT tokens with RS256 encryption" ❌

### **❌ Versioning too early**
Use 0.x versions while developing. Only move to 1.0.0+ when you're ready to freeze the contract.

---

## **Getting Help**

- **Specification:** Read the full SCS specification for detailed rules
- **Examples:** Explore the reference implementation repository
- **Community:** [Add community links when available]
- **Issues:** [Add GitHub issues link when available]

---

## **What Makes This Different?**

Traditional approaches:
- **Long prompts** → Ephemeral, inconsistent, not versioned
- **Documentation** → Verbose, scattered, not machine-readable
- **RAG retrieval** → Surfaces information but doesn't constrain behavior
- **Requirements docs** → Written for humans, AI can't apply consistently

**SCS provides:**
- Compact, structured, versioned contracts
- Machine-readable constraints
- Atomic, governable definitions
- Shared baseline for humans and AI
- Foundation for autonomic governance

---

## **You're Ready!**

You've just created your first structured context environment. You've seen how:
- Small, atomic SCDs compose into powerful contracts
- Domain organization keeps context manageable
- AI behavior stabilizes when operating in a structured environment
- Boundaries prevent drift before it happens

This is the foundation of **AI-native, context-driven software development**.

Welcome to the future of building software with AI.

---

Version **0.3**
Created: 2025-12-09
Updated: 2025-12-09

**Next:** Try the [Reference Implementation Guide](./reference-implementation-guide-v0.3.md) for a complete, production-ready example.
