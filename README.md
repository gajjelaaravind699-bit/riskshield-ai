# RiskShield AI — Abuse-Ring Sentinel

> **Explainable payment-abuse detection and decision-support platform built with FastAPI, PostgreSQL, and Next.js.**

---

## 🛡️ Overview

**RiskShield AI** is an intelligence and decision-support system designed to identify, analyze, and mitigate coordinated payment abuse where organized fraud rings rotate accounts, cards, devices, and IP addresses to evade per-account velocity thresholds.

Operating strictly as a **decision-support platform**, RiskShield AI produces bounded explainable risk assessments, transparent evidence signals, and recommendations without executing autonomous financial debits or payment settlements.

## Problem & Solution

**Problem:** Payment-abuse rings can distribute activity across multiple accounts, devices, IP addresses, and payment instruments, making account-level controls less effective.

**Solution:** RiskShield AI correlates these relationships, detects explainable behavioral patterns, produces deterministic risk recommendations, and provides an auditable analyst case-review workflow.

### Core Capabilities
1. **Zero-Trust Ingestion & Graph Resolution (Phase 2)**: Validates and stores safe payment-instrument references while rejecting raw PANs and CVVs.
2. **Graph & Pattern Analysis Engine (Phase 3)**: 5 deterministic detectors identifying shared cards, shared devices, IP clusters, velocity spikes, and rapid failure bursts.
3. **Deterministic Bounded Risk Scoring (Phase 4)**: Evaluates 0–100 risk scores with rule contribution breakdowns and versioned decision policy recommendations (`ALLOW`, `REVIEW`, `BLOCK`).
4. **Human Analyst Case Management & Audit Trails (Phase 5)**: State machine case lifecycle (`NEW` &rarr; `ASSIGNED` &rarr; `IN_REVIEW` &rarr; `CLOSED`), append-only notes, and review dispositions (`CONFIRMED_SUSPICIOUS`, `FALSE_POSITIVE`, `NO_ACTION`, `ESCALATED`).
5. **Production Hardening & Deployment Readiness (Phase 6)**: RBAC API key authentication, correlation ID propagation, request timing observability, security headers, rate limiting, centralized safe error handling, structured JSON logging with sensitive data redaction, multi-stage Docker containers, and zero-downtime deployment runbooks.

---

## 📁 Repository Structure

```
riskshield-ai/
├── backend/                      # FastAPI Application (Python 3.12 Slim)
│   ├── alembic/                  # Database schema migrations (5 revisions)
│   ├── app/
│   │   ├── api/v1/               # Versioned API routes & RBAC endpoints
│   │   ├── core/                 # Config, DB pool, security, logging, middlewares
│   │   │   ├── config.py         # Pydantic Settings with production validation
│   │   │   ├── database.py       # SQLAlchemy async connection pooling
│   │   │   ├── security.py       # RBAC & API key authentication
│   │   │   ├── logging.py        # Structured JSON logging & sensitive data scrubber
│   │   │   ├── middleware.py     # Correlation ID, timing, rate limiter, security headers
│   │   │   └── errors.py         # Centralized error envelopes & stack trace masking
│   │   ├── models/               # SQLAlchemy ORM declarative models
│   │   ├── schemas/              # Pydantic data validation schemas
│   │   ├── services/             # Ingestion, detectors, scoring, and case logic
│   │   └── main.py               # FastAPI application entrypoint
│   ├── tests/                    # Automated pytest suite (44 tests)
│   ├── Dockerfile                # Multi-stage production container
│   ├── .env.example              # Backend environment template
│   └── requirements.txt          # Python dependencies
├── frontend/                     # Next.js 15+ (TypeScript) Console
│   ├── src/
│   │   ├── app/                  # Next.js App Router (Layout & Pages)
│   │   ├── components/           # UI components (Queue, Detail Modal, Explorer)
│   │   └── lib/api.ts            # Type-safe authenticated API client
│   ├── Dockerfile                # Multi-stage Next.js standalone container
│   ├── .env.example              # Frontend environment template
│   └── package.json              # Node dependencies & scripts
├── docs/                         # System Documentation
│   ├── architecture.md           # End-to-end 5-layer system architecture
│   └── deployment.md             # Production operations, migrations & rollback runbook
├── docker-compose.yml            # Local development PostgreSQL
├── docker-compose.prod.yml       # Production stack (Postgres + Backend + Frontend)
├── PROJECT_SPEC.md               # Product & system specification
└── README.md                     # Project overview & quickstart
```

---

## 🚀 Quickstart

### Prerequisites
- **Python**: 3.11+ (Python 3.12+ recommended)
- **Node.js**: 20+ LTS
- **PostgreSQL**: 15+ (or Docker)

---

### 1. Local Development Setup

#### Start PostgreSQL (Docker)
```bash
docker compose up -d
```

#### Run Database Migrations (Alembic)
```bash
cd backend
alembic upgrade head
```

#### Start Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Liveness Probe: [http://localhost:8000/api/v1/health/liveness](http://localhost:8000/api/v1/health/liveness)
- Readiness Probe: [http://localhost:8000/api/v1/health/readiness](http://localhost:8000/api/v1/health/readiness)

#### Start Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
- Sentinel Console: [http://localhost:3000](http://localhost:3000)

---

### 2. Production Docker Deployment

```bash
# 1. Copy and configure environment variables
cp .env.example .env

# 2. Build and start production stack
docker compose -f docker-compose.prod.yml up -d --build

# 3. Check health status
docker compose -f docker-compose.prod.yml ps
```

---

## 🧪 Testing & Verification

Run the complete backend automated test suite:
```bash
cd backend
pytest -v
# Automated backend test suite covering ingestion, graph analysis, risk assessment, analyst case management, and security/reliability.
```

Run frontend build & lint:
```bash
cd frontend
npm run build
npm run lint
```

---

## 🔒 Security & Architectural Guardrails

- **Zero-Action Guarantee**: The platform is strictly an advisory intelligence system. It **never** executes unilateral fund transfers, payment settlements, or automated charge cancellations.
- **Data Protection**: Sensitive credentials, PANs, CVVs, tokens, and authorization headers are scrubbed before logging and never exposed in error responses.
- **Fail-Safe Configuration**: Production mode strictly validates cryptographic secrets, database credentials, and production API keys at startup.
- For complete operational procedures, consult [`docs/deployment.md`](docs/deployment.md) and [`docs/architecture.md`](docs/architecture.md).
