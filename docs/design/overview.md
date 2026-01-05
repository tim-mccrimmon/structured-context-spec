# SCS Multi-Domain Platform - Concept Overview

**Version:** 1.0
**Date:** 2025-12-12
**Status:** Concept Definition

---

## Executive Summary

**The Problem:** People use AI (ChatGPT, Claude, etc.) without proper context, leading to poor results and wasted time.

**The Solution:** SCS provides structured context bundles that give AI the information it needs to help effectively.

**The Opportunity:** Expand beyond software development to serve ANY domain where people need AI assistance with structured context.

**The Business Model:** SaaS platform where users create custom context bundles for their specific needs using our pre-built domain templates.

---

## Background: From App-Dev to Universal Context

### Where We Started (scs-spec)

**Original SCS:** A specification for software development teams building applications with AI assistance.

**Problem it solved:** Development teams (especially distributed teams) struggled to build coherent software with AI because the AI lacked context about:
- Architecture decisions
- Business requirements
- Security policies
- Compliance needs
- Team conventions

**Solution:** Structured Context Documents (SCDs) organized into bundles that provide complete project context.

**Limitation:** Only serves the software development market.

### The Realization

**Key Insight:** If you are using AI without structured context, you are doing it wrong.

This applies to:
- Sales directors analyzing opportunities
- Healthcare administrators managing workflows
- Finance teams building budgets
- Legal teams drafting contracts
- Marketing teams planning campaigns
- **Anyone using AI in their work**

**The Market:** Not just developers, but END USERS across every industry.

---

## The New Vision: Multi-Domain Platform

### Core Concept

**Structured context is needed for ANY domain where people use AI.**

Instead of building one specification for software development, we build a **platform that supports multiple domains** through pluggable domain templates.

### What is a Domain?

**Domain (n.):** An explicit description of business context for a specific area of work.

**Examples:**
- **Software Development Domain:** Context for building applications (architecture, security, testing, etc.)
- **Sales Domain:** Context for sales processes (opportunities, customers, products, territories, etc.)
- **Healthcare Domain:** Context for healthcare operations (patients, workflows, protocols, compliance, etc.)
- **Finance Domain:** Context for financial planning (budgets, forecasts, accounts, controls, etc.)
- **Legal Domain:** Context for legal work (contracts, cases, precedents, regulations, etc.)

**Key Principle:** Each domain defines the STRUCTURE of context needed for that type of work.

---

## The Three-Layer Architecture

### Layer 1: Domain Template (We Create)

**What:** The standardized structure/schema for a domain.

**Created by:** Us (requires domain expertise)

**Contains:**
- Content schemas (what fields exist)
- Bundle templates (common use cases)
- Validation rules (what's required)
- Documentation and examples

**Example - Sales Domain Template:**
```yaml
domain:
  id: "domain:sales"
  name: "Sales & Marketing"

  # Defines what context is needed for sales
  schemas:
    project:
      content_schema:
        properties:
          products:
            type: array
            description: "Products being sold"
            required: true

          customers:
            type: array
            description: "Customer profiles and segments"
            required: true

          territories:
            type: array
            description: "Sales territories"

          pricing:
            type: object
            description: "Pricing models and discount structures"
            required: true

          competitors:
            type: array
            description: "Competitive landscape"

  # Pre-built bundle templates
  templates:
    bundle_templates:
      - name: "opportunity-analysis"
        description: "Analyze and qualify sales opportunities"

      - name: "customer-segmentation"
        description: "Customer profiling and segmentation"

      - name: "product-positioning"
        description: "Product catalog and competitive positioning"
```

**Think of it as:** The blueprint that defines what information is needed.

**Customer interaction:** Customers SELECT a domain template, but don't modify the structure.

**Monetization:** Commercial domains require paid subscription.

---

### Layer 2: Domain Instance (Customer Creates)

**What:** A customer's specific data/context filling out a domain template.

**Created by:** End user (Bob the sales director)

**Contains:**
- Their products
- Their customers
- Their pricing
- Their territories
- Their competitive landscape

**Example - Bob's Sales Instance:**
```yaml
# Bob's customized sales bundle (instance of sales domain)
id: bundle:acme-sales-context
domain: "domain:sales"
version: "1.0.0"
title: "Acme Corp Sales Context"

scds:
  - scd:project:acme-products
    content:
      products:
        - name: "Widget Pro"
          description: "Professional-grade widget"
          price: 499
          target_market: "SMB"

        - name: "Widget Enterprise"
          description: "Enterprise widget with advanced features"
          price: 2499
          target_market: "Enterprise"

      customers:
        - segment: "Manufacturing SMBs"
          size: "50-500 employees"
          pain_points:
            - "Manual processes"
            - "Lack of integration"
          buying_cycle: "3-6 months"

        - segment: "Enterprise Healthcare"
          size: "1000+ employees"
          pain_points:
            - "Regulatory compliance"
            - "Legacy systems"
          buying_cycle: "9-12 months"

      territories:
        - name: "Northeast US"
          rep: "John Smith"
          quota: 1000000

        - name: "Canada"
          rep: "Jane Doe"
          quota: 500000

      pricing:
        discount_structure:
          volume:
            "1-10 units": "0%"
            "11-50 units": "10%"
            "51+ units": "20%"

          contract_length:
            "annual": "5%"
            "multi-year": "15%"

      competitors:
        - name: "WidgetCo"
          strengths: ["Market leader", "Brand recognition"]
          weaknesses: ["High price", "Poor support"]

        - name: "CheapWidgets Inc"
          strengths: ["Low price"]
          weaknesses: ["Poor quality", "Limited features"]
```

**Think of it as:** Bob's completed workbook using the sales template.

**Customer interaction:**
- Customer uploads their docs (brochures, spreadsheets, price lists)
- Platform extracts information
- Platform populates their bundle instance
- Customer reviews and refines
- Customer downloads their bundle

**Validation:** Ensures Bob filled out required fields correctly according to the sales domain schema.

**Monetization:** Included in domain subscription - create unlimited instances.

---

### Layer 3: Custom Domains (Advanced)

**What:** Entirely new domain structures we don't provide.

**Created by:** Advanced customers or via professional services

**Use case:** Customer needs a domain we don't offer (e.g., "Event Planning", "Real Estate", "Supply Chain")

**Contains:**
- Custom schema definitions
- Custom templates
- Custom validation rules

**Customer interaction:**
- Enterprise tier feature
- DIY tools for domain creation
- Or professional services engagement

**Monetization:** Premium tier or professional services fees.

---

## Key Use Case: Bob the Sales Director

### The Scenario

**Who:** Bob is a sales director with a team of sales reps.

**Problem:** Bob sends his team to trade shows, but suspects they're not qualifying opportunities effectively. The trade show provides attendee lists, but Bob doesn't know how to turn that into qualified leads.

**Current approach:** Bob spends hours in ChatGPT trying to get help, but the AI doesn't understand:
- What products Acme sells
- Who Acme's ideal customers are
- Acme's pricing and discount structure
- How Acme competes against competitors
- Bob's sales territories and quotas

**Result:** Generic, unhelpful advice that wastes Bob's time.

### The Solution: SCS Platform

**Step 1: Bob Signs Up**

Bob signs up for the SCS platform and selects the **Sales Domain** (paid subscription).

**Step 2: Platform Guides Bob**

Platform asks Bob about his sales operation:
- "Tell me about your products"
- "Upload your pricing sheets"
- "Upload your sales materials"
- "Who are your competitors?"
- "Describe your ideal customers"

**Step 3: Bob Uploads Documents**

Bob uploads:
- Product brochures (PDFs)
- Price lists (Excel)
- Sales playbooks (Word docs)
- Competitive analysis (PowerPoint)
- Customer profiles (CRM export)

**Step 4: Platform Processes**

Platform uses AI to:
- Extract product information from brochures
- Parse pricing from spreadsheets
- Identify customer segments from profiles
- Extract competitor intel from documents
- Structure everything into Bob's sales bundle

**Step 5: Bob Reviews & Refines**

Bob reviews the generated bundle:
- Corrects any misinterpretations
- Adds missing information
- Validates the context is accurate

**Step 6: Platform Validates**

Platform validates Bob's bundle:
- All required fields filled in?
- Data types correct?
- Relationships valid?
- Structure follows sales domain schema?

**Step 7: Bob Downloads Bundle**

Bob gets his completed bundle:
```
acme-sales-context-v1.0.0.zip
├── bundle.yaml
├── scds/
│   ├── products.yaml
│   ├── customers.yaml
│   ├── territories.yaml
│   ├── pricing.yaml
│   └── competitors.yaml
└── README.md
```

**Step 8: Bob Uses Bundle**

Bob now uses his bundle with AI:

**In ChatGPT:**
```
[Pastes bundle content]

Here's my sales context. I have a trade show attendee list
with 500 companies. Help me identify the top 20 qualified
opportunities that match my ideal customer profile.

[Uploads attendee list]
```

**ChatGPT response:**
```
Based on your context, here are the top 20 qualified opportunities:

1. MedTech Manufacturing (Booth 245)
   - Segment: Manufacturing SMB (matches your target)
   - Size: 250 employees (in your sweet spot)
   - Pain points: Manual processes, lack of integration (perfect fit)
   - Recommended approach: Widget Pro with SMB discount
   - Assigned territory: Northeast US (John Smith should visit)

2. HealthCare Systems Inc (Booth 112)
   - Segment: Enterprise Healthcare (matches your target)
   - Size: 2000 employees (enterprise opportunity)
   - Pain points: Regulatory compliance, legacy systems (you solve this)
   - Recommended approach: Widget Enterprise, emphasize compliance features
   - Assigned territory: Canada (Jane Doe should visit)
   - Note: Longer sales cycle (9-12 months), plan accordingly

[... 18 more opportunities ...]

Recommended Action Plan:
- John Smith: Visit booths 245, 167, 389 (Manufacturing SMBs)
- Jane Doe: Visit booths 112, 456 (Healthcare Enterprise)
- Avoid booths with competitors: 78 (WidgetCo), 234 (CheapWidgets)
```

**Result:** Bob gets actionable, context-aware advice that actually helps his business.

---

## The Business Model

### Revenue Streams

**Tier 1: Free**
- Software Development domain (open source)
- Create unlimited instances
- Community support

**Tier 2: Professional ($99/user/month)**
- Access to 1 commercial domain (Sales, Healthcare, Finance, Legal, etc.)
- Create unlimited instances
- Upload documents for extraction
- Validation and testing
- Email support

**Tier 3: Business ($299/user/month)**
- Access to 5 commercial domains
- Everything in Professional
- Priority support
- Advanced validation

**Tier 4: Enterprise (Custom pricing)**
- All commercial domains
- Custom domain creation tools
- Professional services for custom domains
- Dedicated support
- White-label options
- On-premise deployment

### Value Proposition

**What customers pay for:**
1. **Domain expertise** - We've done the hard work of defining what context is needed
2. **Validation** - Ensures their context is complete and correct
3. **Platform** - Easy document upload and extraction
4. **Updates** - Domains evolve with best practices
5. **Support** - Help creating effective context

**What customers get:**
- Better AI results (10x improvement)
- Time savings (hours → minutes)
- Reusable context (one-time setup, ongoing benefit)
- Competitive advantage (better insights than competitors)

---

## Platform Architecture (High Level)

### Components

**1. Domain Registry (Separate Repo)**
- Stores domain templates
- Version management
- Distribution/download
- License verification

**2. SCS Core (This Repo)**
- Domain-agnostic infrastructure
- SCD and bundle specifications
- Validation engine
- CLI tools (for domain creators)

**3. Platform (Future - Web Application)**
- User authentication
- Domain selection
- Document upload and processing
- Bundle generation
- Download and export
- AI integration (optional)

**4. Document Processor (Future)**
- PDF extraction
- Excel parsing
- Word document processing
- AI-powered information extraction
- Mapping to domain schemas

### User Flows

**Flow 1: Domain Creator (Us)**
```
1. Design domain (identify what context is needed)
2. Create domain manifest (schemas, templates, rules)
3. Create bundle templates
4. Test and validate
5. Publish to registry
6. Set pricing (free/commercial)
```

**Flow 2: End User (Bob)**
```
1. Sign up for platform
2. Select domain (Sales)
3. Choose template (opportunity-analysis)
4. Upload documents (brochures, spreadsheets, etc.)
5. Platform processes and populates bundle
6. Review and refine
7. Validate bundle
8. Download bundle
9. Use with AI (ChatGPT, Claude, etc.)
```

**Flow 3: Advanced User (Custom Domain)**
```
1. Request custom domain creation
2. Work with professional services OR
3. Use domain creation tools (enterprise tier)
4. Define schema
5. Create templates
6. Test and validate
7. Use privately or publish to registry
```

---

## Answers to Key Questions

### 1. What are the other domains?

**We define major domains based on:**
- Market demand
- Our domain expertise
- Revenue potential
- Feasibility

**Initial commercial domains:**
- Sales & Marketing
- Healthcare & Clinical
- Finance & Accounting
- Legal & Compliance
- Human Resources
- Supply Chain & Operations
- Marketing & Content
- Customer Success

**Future domains:** Based on customer demand and market research.

### 2. Are we defining them or is the customer?

**Both:**
- **We define** the domain STRUCTURE (template/schema)
- **Customer fills in** their SPECIFIC DATA (instance)
- **Advanced customers** can create entirely new domains (custom)

**Analogy:**
- We build the form (domain template)
- Customer fills it out (domain instance)
- Advanced users can create new forms (custom domains)

### 3. If the customer is allowed to alter them, what is the purpose?

**Clarification:** Customers don't ALTER the domain structure.

**They:**
- SELECT a domain template
- CREATE an instance with their data
- CUSTOMIZE their instance (not the template)

**Validation ensures:**
- They filled it out correctly
- Required fields are present
- Data types match
- Relationships are valid
- Structure follows template

**Think:** Tax software
- IRS defines tax form structure (domain template)
- You fill in your numbers (domain instance)
- Software validates you did it right (validation)
- You can't change the form structure (can't alter domain)

### 4. If the customer alters them, what is the purpose of Validation?

**Re-framed:** Validation ensures the customer's INSTANCE follows our domain TEMPLATE.

**Validation checks:**
- "Did Bob fill in all required product information?"
- "Are Bob's prices in the correct format?"
- "Did Bob define at least one customer segment?"
- "Are Bob's territory assignments valid?"

**Without validation:**
- Incomplete context (AI gets confused)
- Incorrect data types (breaks integrations)
- Missing critical information (poor AI results)

**With validation:**
- Complete, correct context
- AI can reliably use the information
- Consistent structure across all instances

---

## Competitive Advantages

### 1. First Mover
- No one else is doing "structured context as a service"
- Create new category: "AI Context Management"

### 2. Domain Expertise
- 12+ years in healthcare (can build authoritative healthcare domain)
- Software development expertise (proven with scs-spec)
- Can partner with experts for other domains

### 3. Platform Architecture
- Designed for multi-domain from day one
- Pluggable, extensible
- Not bolting on domains as an afterthought

### 4. Network Effects
- More users → More validated instances → Better domain templates
- Domain templates improve over time with real usage
- Community contributions (enterprise custom domains become commercial domains)

### 5. Monetization Clarity
- Clear subscription model
- Value scales with domains
- Enterprise upsell path

---

## Technical Implementation Focus

### Repository Scope (This Repo: scs-commercial)

**What we're building here:**
- Domain-agnostic SCS core specification
- Pluggable domain architecture
- Domain manifest schema
- Bundle and SCD formats (with domain support)
- Validation engine (domain-aware)
- CLI tools (for domain creators)

**What we're NOT building here (yet):**
- Web platform UI
- Document processing
- User authentication
- Payment processing
- AI integrations

**Focus:** Get the spec and architecture right first.

### Next Steps (Repository)

**Phase 1: Complete Design (DONE ✅)**
- Multi-domain architecture
- Domain manifest schema
- Bundle format updates
- Configuration management
- CLI architecture

**Phase 2: Core Implementation**
- Domain loader
- Validation engine
- Configuration system
- CLI commands

**Phase 3: Domain Creation**
- Extract software-dev as domain
- Create sales domain template
- Create healthcare domain template
- Validate with examples

**Phase 4: Registry Integration**
- Connect to registry repo
- Domain distribution
- License verification

**Phase 5: Platform Planning**
- Design web application
- Document processing architecture
- Integration points

---

## Success Metrics

### Technical Metrics
- Domain templates created: 5-10 in year 1
- Validation accuracy: >95%
- Bundle generation time: <5 minutes
- Template coverage: 80% of common use cases

### Business Metrics
- Users: 1000 in year 1
- Paid subscribers: 100 in year 1 (10% conversion)
- MRR: $10k in year 1
- Domains per user: 1.5 average
- NPS: >50

### Product Metrics
- Bundle creation time: <30 minutes
- AI result improvement: 10x (qualitative)
- User return rate: >70%
- Support tickets: <5% of users

---

## Open Questions & Future Decisions

### Architecture
- [ ] How do domains handle versioning and breaking changes?
- [ ] Can domains depend on other domains?
- [ ] How do we handle domain conflicts in multi-domain bundles?

### Business
- [ ] Freemium vs trial for commercial domains?
- [ ] Per-seat vs per-domain pricing?
- [ ] Marketplace for third-party domains?

### Platform
- [ ] Host bundles on platform vs download only?
- [ ] Integrate directly with ChatGPT/Claude APIs?
- [ ] Mobile app for bundle management?

### Privacy
- [ ] On-premise deployment model?
- [ ] Data residency options?
- [ ] HIPAA/SOC2 compliance for platform?

---

## Conclusion

**The Vision:**
SCS evolves from a software development specification into a universal platform for structured AI context across any domain.

**The Strategy:**
- Build domain-agnostic infrastructure (this repo)
- Create commercial domain templates (our expertise)
- Enable customers to create instances with their data
- Deliver through SaaS platform (future)

**The Value:**
Anyone using AI gets 10x better results by using structured context bundles tailored to their domain.

**The Revenue:**
Subscription-based access to commercial domain templates with platform tools for easy bundle creation.

**Status:**
Design phase complete. Ready to begin implementation of core infrastructure.

---

*This overview defines the product vision and architecture for SCS multi-domain platform. All design work flows from this concept.*
