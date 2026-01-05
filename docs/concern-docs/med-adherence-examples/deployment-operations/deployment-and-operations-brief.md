# Deployment & Operations Context Brief
Project: Medication Adherence Platform
Domain: Deployment & Operations
Version: 1.0
Status: Draft
Phase: Intent

This brief describes how the Medication Adherence Platform will be deployed and
operated in production, including infrastructure, observability, and incident
response processes.

---

## 1. Purpose and Scope
The platform runs in AWS, hosting PHI and clinical escalation data. Operations
must ensure:

- High availability for patient notifications
- Reliable ingestion of adherence events
- Strong observability and rapid incident detection
- Clear operational ownership and on-call processes

Scope includes cloud infrastructure, CI/CD, backups, DR, monitoring, and
incident response.

---

## 2. Hosting & Deployment Environments

**Cloud Provider:** AWS (HIPAA-aligned)

**Regions:**
- Primary: us-east-1  
- Failover: us-west-2

**Environments:**
- Dev: isolated VPC, reduced data, no PHI  
- Staging: full-stack environment with synthetic PHI  
- Production: full HIPAA-compliant environment  
- DR: warm standby in us-west-2

**Network Model:**
- Public subnets: ALB, API Gateway  
- Private subnets: ECS services, databases  
- VPC endpoints for S3, Secrets Manager, ECR  

---

## 3. Infrastructure Components

### Compute
- AWS ECS on Fargate for stateless backend services  
- Lambda for async processing (e.g., notification fanout)

### Storage
- Primary PHI datastore: Aurora PostgreSQL (encrypted at rest)  
- Audit logs: S3 with object lock  
- Caching: Redis (Elasticache)  
- Object storage: S3 (plans, artifacts, logs)

### Networking
- API Gateway in front of ECS services  
- Application Load Balancer  
- VPC with private subnets and security groups restricting access

### Messaging
- SNS for notification dispatch  
- SQS for task queues and retries

### Secrets & Config
- AWS Secrets Manager  
- AWS Systems Manager Parameter Store  

---

## 4. Deployment Architecture & Processes

- **IaC:** Terraform for VPC, ECS, databases, S3, IAM  
- **CI/CD:** GitHub Actions → ECR → ECS blue/green deployment via CodeDeploy  
- **Artifact Packaging:** Docker images with semantic versioning  
- **Rollout Strategy:**  
  - Staging: rolling  
  - Production: blue/green with automated health checks  
- **Config Management:** Environment variables + Parameter Store  

---

## 5. Operational Responsibilities & On-Call Model

- **Primary Operations Owner:** DevOps Team  
- **Secondary (L2):** Backend Engineering  
- **Escalation:** Security team (for PHI issues)  
- **On-call:** Rotating weekly schedule, 24/7 PagerDuty coverage  
- **Service SLOs:**
  - API availability: 99.9%  
  - Notification latency < 3 minutes  
  - Adherence event ingestion: 99.95% durability  

---

## 6. Observability Strategy

### Logging
- Centralized logs via CloudWatch Logs
- Log aggregation to OpenSearch for querying
- Masking for PHI fields

### Metrics
- ECS service-level metrics  
- Custom app metrics:
  - notification delivery success rate  
  - adherence event ingestion latency  
  - scheduler failures  

### Tracing
- Distributed tracing with AWS X-Ray  
- Trace IDs propagated across all services  

### Dashboards
- CloudWatch dashboards for backend health  
- Grafana dashboards for custom metrics  

---

## 7. Health Checks & Monitoring

### Health Checks
- ECS tasks publish:
  - **Liveness**: container running  
  - **Readiness**: all downstream dependencies reachable (DB, Redis)  

### Monitoring
- CPU, memory, DB connections  
- Lag in SQS queues  
- Notification failure rate  
- Escalation engine stall detection  

### Synthetic Monitoring
- Ping-based external health checks from multiple regions  

---

## 8. Alerts & Escalation Policies

**Alert Types:**
- High API error rate  
- Notification failure > 5%  
- DB latency spikes  
- SQS queue length > threshold  
- ECS task restart loops  
- PHI access anomalies (via security monitoring)

**Escalation:**
L1 DevOps → L2 Engineering → Security (if PHI-related) → Leadership (if prolonged)

---

## 9. Backup & Disaster Recovery Expectations

### Backups
- Aurora PostgreSQL: automated daily backups + 7-day PITR  
- S3: versioning + object lock  
- Redis: snapshot every 6 hours  

### DR Strategy
- Warm standby replica in us-west-2  
- Automated failover via RDS multi-region configuration  
- Application failover manual at first (future: automated)

### RPO/RTO
- RPO: 5 minutes  
- RTO: 1 hour  

---

## 10. Capacity Planning & Performance Management

- Expected scale:  
  - 50k–250k patients  
  - 100k+ daily notifications  
  - 200k+ daily adherence events  

- Auto-scaling rules:
  - ECS scales based on CPU > 70% or queue depth > threshold  
  - DB read replicas for reporting workloads  

- Load Testing:
  - Performed quarterly  
  - Target: 2× expected peak load  

---

## 11. Operational Risks & Mitigations

- **Risk:** Regional outage in us-east-1  
  - **Mitigation:** warm standby in us-west-2  

- **Risk:** SMS vendor outage impacts notifications  
  - **Mitigation:** multi-provider fallback  

- **Risk:** ECS misconfiguration could impact availability  
  - **Mitigation:** IaC + automated CI/CD checks  

- **Risk:** Log ingestion failure hides operational issues  
  - **Mitigation:** log buffer alerts + dual logging to S3  

---

## 12. Provenance
created_by: "DevOps Lead – Medication Adherence"
created_at: "2025-11-27T20:00:00Z"
source: "Intent Phase – Deployment & Operations Domain"
notes: "Initial deployment and operations context; updated after architecture review."