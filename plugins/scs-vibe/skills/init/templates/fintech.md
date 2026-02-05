# [Project Name]

> [One-line description of what this financial system does]

## System Overview

[2-3 paragraphs describing:
- What the system does and who uses it (customers, internal ops, partners)
- The financial workflows it supports (payments, lending, trading, etc.)
- Key integrations (banks, payment processors, regulatory systems)]

## Architecture

### High-Level Design

[Describe the overall architecture]
- **Type**: [Monolith / Microservices / Serverless / Hybrid]
- **Deployment**: [Cloud provider, region requirements, data residency]
- **Key external dependencies**: [Banks, payment processors, market data providers]

### Core Components

| Component | Purpose | Location | Handles Financial Data? |
|-----------|---------|----------|------------------------|
| [Component 1] | [What it does] | `/src/...` | Yes/No |
| [Component 2] | [What it does] | `/src/...` | Yes/No |
| [Component 3] | [What it does] | `/src/...` | Yes/No |

### Data Flow

[Describe how data moves through the system, noting trust boundaries]

```
Request → [Auth] → [Validation] → [Processing] → [Settlement] → Response
              ↓           ↓             ↓              ↓
          Audit Log   Audit Log    Audit Log      Audit Log
```

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Language | | |
| Framework | | |
| Database | | ACID compliance, encryption at rest |
| Cache | | Encryption requirements |
| Queue | | Exactly-once semantics |
| Infrastructure | | SOC2 compliant |

## Compliance Context

### Regulatory Requirements

**This system handles financial data. All development must comply with applicable regulations.**

#### Compliance Frameworks
- [ ] **SOC2 Type II**: [In progress / Certified]
- [ ] **PCI-DSS**: [Level, if handling card data]
- [ ] **State/Federal regulations**: [Money transmitter licenses, etc.]
- [ ] **[Other]**: [SEC, FINRA, CFPB as applicable]

#### Sensitive Data Locations
- **Database tables with financial data**: [List tables]
- **API endpoints handling transactions**: [List endpoints]
- **PII locations**: [Customer data, account numbers]

#### Required Controls
- [ ] All sensitive data encrypted at rest (AES-256)
- [ ] All data encrypted in transit (TLS 1.2+)
- [ ] Access logging for all financial operations
- [ ] Segregation of duties enforced
- [ ] Change management procedures followed

### Audit Logging Requirements

**Every financial operation must be logged with:**
- Who (user ID, role, IP)
- What (operation type, amounts, accounts)
- When (timestamp, timezone)
- Result (success/failure, error codes)
- Correlation ID (for tracing)

**Audit log location**: [Path/table]
**Retention requirement**: [X years per regulation]
**Immutability**: [How audit logs are protected from modification]

### Access Control

| Role | Financial Operations | Scope |
|------|---------------------|-------|
| [Role 1] | [View/Execute/Approve] | [What they can access] |
| [Role 2] | [View/Execute/Approve] | [What they can access] |

## Patterns We Use

### Idempotency Pattern
- **Where**: All transaction endpoints
- **Why**: Prevents duplicate transactions from network retries
- **Implementation**: [Idempotency key approach, storage]
- **Example**: [File or code reference]

### Double-Entry Bookkeeping
- **Where**: All balance-affecting operations
- **Why**: Ensures money never appears or disappears
- **Implementation**: [How ledger entries are created]
- **Example**: [File or code reference]

### Optimistic Locking
- **Where**: Balance updates, account modifications
- **Why**: Prevents race conditions in concurrent operations
- **Implementation**: [Version columns, etc.]
- **Example**: [File or code reference]

### Audit Trail Pattern
- **Where**: All financial operations
- **Implementation**: [How audit logging is implemented]
- **Example**: [File or code reference]

## Patterns We MUST Avoid

### Floating Point for Money
- **Why**: Precision errors lead to accounting discrepancies
- **What to do instead**: Use decimal types, store cents/smallest unit as integers

### Non-Idempotent Transaction Endpoints
- **Why**: Network retries can cause duplicate transactions
- **What to do instead**: Always accept idempotency key, check before processing

### Direct Balance Modifications
- **Why**: Breaks audit trail, allows money to appear/disappear
- **What to do instead**: All balance changes via ledger entries

### Async-Only for Critical Operations
- **Why**: Hard to guarantee completion, complex failure handling
- **What to do instead**: Synchronous confirmation, then async side effects

### Logging Sensitive Financial Data
- **Why**: PCI/compliance violation, security risk
- **What to do instead**: Log transaction IDs only, mask account numbers

## Constraints

### Regulatory Constraints
- **SOC2**: All changes must follow change management
- **PCI-DSS**: [If applicable - card data isolation requirements]
- **Data residency**: [Geographic restrictions on data storage]
- **Retention**: [Data retention requirements by type]

### Technical Constraints
- **Consistency**: Financial operations require strong consistency (not eventual)
- **Availability**: [SLA requirements, failover requirements]
- **Latency**: [Transaction processing time requirements]

### Business Constraints
- **Settlement windows**: [When transactions settle]
- **Rate limits**: [API/transaction limits]
- **Amount limits**: [Transaction size constraints]

## Domain Context

### Financial Terminology
- **[Term 1]**: [Definition in this system's context]
- **[Term 2]**: [Definition in this system's context]
- **Ledger**: Immutable record of all balance-affecting transactions
- **Settlement**: Final transfer of funds between parties
- **Reconciliation**: Process of verifying internal records match external systems

### Key Financial Workflows
1. **[Workflow 1]**: [Description, approval requirements]
2. **[Workflow 2]**: [Description, settlement timing]

### Integration Points
- **Banking partner**: [Name, integration type (API, SFTP, etc.)]
- **Payment processor**: [Name, integration approach]
- **Compliance/KYC**: [Vendor, integration]

## Development Guidelines

### Before Making Changes
- [ ] Identify if change affects financial calculations
- [ ] Verify audit logging covers the change
- [ ] Check idempotency is maintained
- [ ] Review for race conditions in concurrent scenarios
- [ ] Confirm decimal precision is preserved
- [ ] Consult compliance team if uncertain

### Testing Requirements
- All transaction paths must have audit log tests
- Idempotency must be tested (duplicate requests)
- Concurrent access must be tested (race conditions)
- Decimal precision must be verified
- Failure scenarios must be tested (what happens on error mid-transaction?)

### Areas Requiring Extra Care

**ANY change involving money movement requires senior review.**

- **[Ledger/Transaction Component]**: Core financial logic - requires [Person/Team] review
- **[Payment Integration]**: External money movement - requires compliance review
- **[Settlement Process]**: Reconciliation impact - requires ops review
- **Authentication/Authorization**: Changes require security review

## Reconciliation

### Daily Reconciliation
- **Process**: [How internal records are reconciled with external systems]
- **Timing**: [When reconciliation runs]
- **Alerts**: [What triggers investigation]

### Discrepancy Handling
- **Process**: [How discrepancies are investigated and resolved]
- **Escalation**: [When and how to escalate]

## Emergency Contacts

- **Compliance Officer**: [Name, contact]
- **Security Team**: [Contact]
- **Treasury/Ops Lead**: [Name, contact for money movement issues]
- **Banking Partner Support**: [Contact for integration issues]

---

*Last updated: [Date]*
*Generated with [SCS](https://structuredcontext.io)*

**REMINDER**: This codebase handles financial data. Money must never appear or disappear. When in doubt, ask before implementing.
