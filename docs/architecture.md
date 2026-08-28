# RiskShield AI — System Architecture

This document describes the architectural design and component structure for **RiskShield AI (Abuse-Ring Sentinel)** across all 5 production phases.

---

## 1. System Vision & Purpose

RiskShield AI is a specialized intelligence and decision-support platform designed to identify, analyze, and mitigate coordinated payment abuse. Organized fraud groups distribute transactions across multiple synthetic accounts, rotating cards, IP addresses, and device fingerprints to evade per-account velocity limits.

RiskShield AI correlates dispersed signals across transactions to isolate suspicious abuse rings, evaluate deterministic bounded risk scores, produce actionable recommendations (`ALLOW`, `REVIEW`, `BLOCK`), and enable human compliance analysts to investigate cases with append-only notes and immutable audit event trails.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client Layer (Frontend)
        WebConsole["RiskShield Web Console\n(Next.js 15+ + TypeScript)"]
        CaseQueue["Analyst Case Review Queue\n(Phase 5)"]
        AssessmentExp["Risk Assessment Explorer\n(Phase 4)"]
        FindingsExp["Graph Findings Explorer\n(Phase 3)"]
        IngestionUI["Transaction Ingest UI\n(Phase 2)"]
    end

    subgraph API & Gateway Layer (FastAPI)
        FastAPI["RiskShield Backend Gateway\n(/api/v1)"]
        HealthRouter["Health & Readiness API\n(/api/v1/health)"]
        TxRouter["Transactions API\n(/api/v1/transactions)"]
        AnalysisRouter["Analysis API\n(/api/v1/analysis)"]
        AssessmentRouter["Assessments API\n(/api/v1/assessments)"]
        CasesRouter["Analyst Cases API\n(/api/v1/cases)"]
    end

    subgraph Engine & Service Layer
        TxService["Transaction Ingestion Service\n(Entity Normalization & Hashing)"]
        AnalysisService["Graph & Ring Analysis Engine\n(5 Deterministic Detectors)"]
        AssessmentService["Risk Scoring & Decision Engine\n(Additive Point Model & Advisory Recs)"]
        CaseService["Analyst Case Management Service\n(State Machine, Notes & Audit Trails)"]
    end

    subgraph Persistence & Audit Layer (PostgreSQL)
        PostgreSQL[("PostgreSQL 16\n(Async SQLAlchemy 2.0 + Alembic)")]
        TblTransactions[("transactions & entities")]
        TblFindings[("analysis_runs, findings, finding_entities")]
        TblAssessments[("assessments & rule_contributions")]
        TblCases[("cases, case_notes, case_audit_events")]
    end

    WebConsole --> CaseQueue & AssessmentExp & FindingsExp & IngestionUI
    CaseQueue & AssessmentExp & FindingsExp & IngestionUI -->|HTTP / JSON| FastAPI
    FastAPI --> HealthRouter & TxRouter & AnalysisRouter & AssessmentRouter & CasesRouter

    TxRouter --> TxService
    AnalysisRouter --> AnalysisService
    AssessmentRouter --> AssessmentService
    CasesRouter --> CaseService

    TxService --> TblTransactions
    AnalysisService --> TblFindings
    AssessmentService --> TblAssessments
    CaseService --> TblCases

    TblTransactions & TblFindings & TblAssessments & TblCases --- PostgreSQL
```

---

## 3. Layered Design

### 3.1 Presentation Layer (Frontend)
- **Framework**: Next.js 15+ (App Router), React 19, TypeScript, Tailwind CSS, Lucide React.
- **Role**: Operations console for risk analysts and compliance officers.
- **Key Modules**:
  - **Transaction Ingest & Live Explorer (Phase 2)**: Real-time transaction submission and normalized entity relationships.
  - **Graph & Pattern Analysis Explorer (Phase 3)**: Interactive view of abuse-ring findings, shared instrument/device clusters, and velocity bursts.
  - **Risk Assessment Explorer (Phase 4)**: Audit trace modal with point contribution breakdowns and advisory recommendations (`ALLOW`, `REVIEW`, `BLOCK`).
  - **Analyst Case Review Queue (Phase 5)**: Comprehensive case management interface supporting status transitions, priority updates, analyst assignment, append-only notes, review dispositions, and immutable audit event timelines.

### 3.2 Ingestion & API Layer (Backend)
- **Framework**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn.
- **Role**: Secure API gateway, request validation, and orchestrator.
- **Endpoints**:
  - `GET /api/v1/health`: System health and optional database probe.
  - `POST /api/v1/transactions`: Single & batch transaction ingestion with card PAN masking/hashing and entity normalization.
  - `GET /api/v1/transactions`: Filtered and paginated transaction queries.
  - `POST /api/v1/analysis/run`: Deterministic graph and pattern analysis execution.
  - `GET /api/v1/analysis/findings`: Filtered detection findings.
  - `POST /api/v1/assessments/evaluate/{transaction_id}`: Deterministic risk scoring and advisory decision generation.
  - `GET /api/v1/assessments`: Paginated assessment queries.
  - `POST /api/v1/cases`: Case creation (manually or escalated from assessment).
  - `GET /api/v1/cases`: Case queue with status, priority, and disposition filtering.
  - `PATCH /api/v1/cases/{case_id}/status`: Controlled state machine transition.
  - `PATCH /api/v1/cases/{case_id}/assignment`: Reassign case to analyst.
  - `PATCH /api/v1/cases/{case_id}/priority`: Update case priority.
  - `POST /api/v1/cases/{case_id}/notes`: Add append-only note.
  - `POST /api/v1/cases/{case_id}/disposition`: Record final analyst review disposition.

### 3.3 Engine & Service Layer
- **Transaction Ingestion**: Normalizes entities (Cards, VPAs, IPs, Devices) and prevents raw PAN exposure.
- **Analysis Engine**: 5 deterministic detectors:
  1. `SHARED_PAYMENT_INSTRUMENT`: Cross-customer card/VPA sharing.
  2. `SHARED_DEVICE`: Cross-account device collisions.
  3. `SHARED_IP_CLUSTER`: Dispersed account subnet clustering.
  4. `VELOCITY_BURST`: High-frequency transaction spikes.
  5. `RAPID_FAILURE_BURST`: Authorization testing attack patterns.
- **Risk Scoring & Decision Engine**:
  - Deterministic additive point model bounded between 0 and 100.
  - Policy evaluation mapping scores to advisory recommendations:
    - Score < 30 &rarr; `ALLOW` (Low Risk)
    - 30 &le; Score < 60 &rarr; `REVIEW` (Medium Risk)
    - Score &ge; 60 &rarr; `BLOCK` (High/Critical Risk)
- **Case Management Engine**:
  - State machine lifecycle: `NEW` &rarr; `ASSIGNED` &rarr; `IN_REVIEW` &rarr; `PENDING_INFO` &rarr; `CLOSED` &rarr; `ARCHIVED`.
  - Dispositions: `NO_ACTION`, `FALSE_POSITIVE`, `CONFIRMED_SUSPICIOUS`, `ESCALATED`.
  - Append-only notes and immutable audit event ledger.

### 3.4 Persistence & Migration Layer
- **PostgreSQL 16**: Relational storage managed with async SQLAlchemy 2.0 and `asyncpg`.
- **Alembic Revisions**:
  - `001_phase2_schema`: Transactions and entities.
  - `002_phase3_schema`: Analysis runs and findings.
  - `003_unique_finding_fingerprint`: Finding deduplication.
  - `004_phase4_assessments`: Risk assessments and rule contributions.
  - `005_phase5_case_management`: Cases, case notes, and case audit events.

---

## 4. Architectural Guardrails & Non-Action Guarantee

1. **Strict Non-Action Constraint**:
   - The platform is strictly an advisory, intelligence, and compliance review tool.
   - It **never** triggers automated financial debiting, payment cancellation, or autonomous transaction blocking.
2. **Immutability of Source Data**:
   - Ingested transactions and evaluated assessment scores are immutable; case workflows and dispositions do not alter transaction execution states.
3. **Auditability & Explainability**:
   - Every risk recommendation is mathematically decomposable into its triggering detector findings.
   - Every analyst case action is permanently recorded in the `case_audit_events` ledger.
