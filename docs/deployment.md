# RiskShield AI — Production Deployment & Operations Guide

This document defines the operational deployment standards, security controls, migration workflows, monitoring strategies, and emergency rollback procedures for **RiskShield AI (Abuse-Ring Sentinel)**.

---

## 1. Production Architecture Overview

```
                        ┌───────────────────────────────┐
                        │   Edge Ingress / API Gateway  │
                        │    (TLS Termination & WAF)    │
                        └───────────────┬───────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │  Next.js Console      │               │   FastAPI Gateway     │
        │  (Standalone Node 20) │               │   (Python 3.12 Slim)  │
        │  Port: 3000           │               │   Port: 8000          │
        │  Non-root: nextjs     │               │   Non-root: riskshield│
        └───────────────────────┘               └───────────┬───────────┘
                                                            │
                                                            │ Connection Pool (asyncpg)
                                                            ▼
                                                ┌───────────────────────┐
                                                │     PostgreSQL 16     │
                                                │ (Alembic Schema v005) │
                                                └───────────────────────┘
```

---

## 2. Environment Variables & Secrets Configuration

All sensitive production values must be provided via environment variables or a secure secret manager (e.g. AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets).

| Variable | Description | Production Requirement |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Runtime environment mode (`production`) | Must be set to `production`. |
| `DEBUG` | FastAPI debug flag | Must be `false`. |
| `SECRET_KEY` | Cryptographic signing secret | Minimum 32 characters, cryptographically random. |
| `API_KEYS` | JSON string mapping keys to identities and roles | Custom random keys with `analyst`, `ingest`, `admin` roles. |
| `POSTGRES_SERVER` | PostgreSQL server hostname or IP | Dedicated RDS or managed cluster. |
| `POSTGRES_DB` | Database name | E.g. `riskshield_prod`. |
| `POSTGRES_USER` | Database username | Dedicated non-superuser. |
| `POSTGRES_PASSWORD`| Database password | Strong randomized password (min 16 chars). |
| `CORS_ORIGINS` | Permitted browser origins | Explicit frontend domain(s), no wildcards. |
| `ALLOWED_HOSTS` | Allowed HTTP Host headers | Specific hostnames. |
| `RATE_LIMIT_ENABLED`| In-memory rate limiting | `true` (default: 120 req/min). |
| `LOG_FORMAT` | Structured logging format | `json` for centralized log ingestion (Datadog/Elastic). |

---

## 3. Database Migration Runbook (Alembic)

Database schema updates are strictly managed through **Alembic**. Schema creation at application startup is strictly prohibited.

### 3.1 Pre-Deployment Migration Check
Verify current revision status:
```bash
cd backend
alembic current
alembic check
```

### 3.2 Executing Database Migrations
Run schema upgrades before starting new application containers:
```bash
cd backend
alembic upgrade head
```

### 3.3 Validating Migration History
RiskShield AI includes 5 discrete schema migrations:
1. `001_phase2_schema`: `transactions`, `entities`, `transaction_entities`
2. `002_phase3_schema`: `analysis_runs`, `findings`, `finding_entities`, `finding_transactions`
3. `003_unique_finding_fingerprint`: Deduplication constraints
4. `004_phase4_assessments`: `assessments`, `rule_contributions`
5. `005_phase5_case_management`: `cases`, `case_notes`, `case_audit_events`

---

## 4. Container Deployment (Docker Compose & Kubernetes)

### 4.1 Production Docker Compose Deployment
```bash
# 1. Populate production environment
cp .env.example .env
# Edit .env with production credentials

# 2. Build and start containers in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# 3. Verify health status
docker compose -f docker-compose.prod.yml ps
```

### 4.2 Health & Readiness Probe Configuration
Configure orchestrator probes (Kubernetes, AWS ECS, GCP Cloud Run):
- **Liveness Probe**: `GET /api/v1/health/liveness` (Initial delay: 10s, Period: 15s, Timeout: 5s)
- **Readiness Probe**: `GET /api/v1/health/readiness` (Initial delay: 5s, Period: 10s, Timeout: 5s)

---

## 5. Zero-Downtime Rolling Update Strategy

1. **Pre-flight**:
   - Run unit and security regression test suite.
   - Perform automated Alembic migration (`alembic upgrade head`).
2. **Deploy Backend**:
   - Spin up new backend container instances.
   - Verify `/api/v1/health/readiness` returns HTTP 200 on all new instances.
   - Switch traffic to new backend instances.
   - Terminate old backend containers.
3. **Deploy Frontend**:
   - Build standalone Next.js image.
   - Deploy new frontend containers and switch ingress routing.

---

## 6. Observability, Structured Logging & Request Correlation

- **Structured JSON Logging**: All logs are emitted as single-line JSON objects with UTC timestamp, severity level, message, correlation ID, and sanitized attributes.
- **Sensitive Data Redaction**: Automatic filter scrubs raw PANs, passwords, API keys, CVVs, and tokens before writing to log streams.
- **Correlation ID Tracing**: Pass `X-Correlation-ID` header with all upstream calls. The backend propagates this ID through all logs, database error envelopes, and response headers (`X-Correlation-ID`, `X-Process-Time`).

---

## 7. Emergency Rollback Runbook

If a critical deployment failure or regression is detected:

### Step 1: Ingress Traffic Switch
Immediately redirect ingress routing to the previous known-good deployment revision.

### Step 2: Database Schema Rollback (If Required)
If a database rollback is strictly necessary:
```bash
cd backend
# Downgrade to target revision
alembic downgrade -1
# Or to specific revision ID:
alembic downgrade 004_phase4_assessments
```

### Step 3: Container Rollback
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build <previous_image_tag>
```

### Step 4: Verification
Confirm `/api/v1/health/readiness` returns HTTP 200 and audit logs confirm operational status.
