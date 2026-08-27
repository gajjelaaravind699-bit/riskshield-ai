# RiskShield AI — Abuse-Ring Sentinel

> **Coordinated payment abuse detection & decision-support platform**

---

## 🛡️ Overview

**RiskShield AI** is designed to identify coordinated payment abuse where multiple accounts, cards, devices, or transaction patterns indicate coordinated fraud rings. Operating strictly as a **decision-support system**, RiskShield AI produces risk assessments, transparent evidence signals, and recommendations without executing unrestricted financial actions.

### Core Objectives
1. **Cluster & Ring Identification**: Detect shared entities across customer accounts, devices, IPs, and payment instruments.
2. **Explainable AI Decision Support**: Generate auditable scores and actionable recommendations:
   - `ALLOW`: Normal transaction behavior.
   - `REVIEW`: Anomalous or clustered signals requiring manual analyst intervention.
   - `BLOCK`: High-confidence coordinated abuse ring indicators.
3. **Transparent Evidence & Auditing**: Provide full signal traces and immutable audit records for regulatory compliance and forensic review.

---

## 📁 Repository Structure

```
riskshield-ai/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/v1/           # Versioned API routes & endpoints
│   │   │   ├── endpoints/    # Individual route handlers (e.g., health)
│   │   │   └── router.py     # Aggregated v1 router
│   │   ├── core/             # Configuration & Database connection
│   │   │   ├── config.py     # Pydantic Settings & environment parsing
│   │   │   └── database.py   # SQLAlchemy async session management
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic data validation schemas
│   │   ├── services/         # Business logic layer
│   │   └── main.py           # FastAPI application entrypoint
│   ├── tests/                # Automated pytest suite
│   ├── .env.example          # Backend environment template
│   ├── pyproject.toml        # Pytest & tool configurations
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js (TypeScript) Web Console
│   ├── src/
│   │   ├── app/              # Next.js App Router (Layout & Pages)
│   │   ├── components/       # Reusable UI components
│   │   └── lib/              # API clients & utilities
│   ├── .env.example          # Frontend environment template
│   ├── package.json          # Node dependencies & scripts
│   └── tsconfig.json         # TypeScript configuration
├── docs/                     # Architectural documentation
│   └── architecture.md       # Detailed system architecture
├── docker-compose.yml        # Local PostgreSQL container service
├── PROJECT_SPEC.md           # Product & system specification
└── README.md                 # Project guide
```

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ (Node 20+ LTS recommended)
- **PostgreSQL**: 15+ (or Docker)

---

### 1. Database Setup (Optional via Docker)
To start a local PostgreSQL instance using Docker:
```bash
docker compose up -d
```

---

### 2. Backend Setup (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment file:
   ```bash
   copy .env.example .env     # Windows
   # or
   cp .env.example .env       # Linux/macOS
   ```
5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Verify the backend health check:
   - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Endpoint: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### 3. Frontend Setup (Next.js + TypeScript)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Copy the environment template:
   ```bash
   copy .env.example .env.local    # Windows
   # or
   cp .env.example .env.local      # Linux/macOS
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```
5. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Tests

Run backend automated tests with `pytest`:
```bash
cd backend
pytest -v
```

---

## 📜 Architectural Notes & Constraints

- **Decision-Support Guardrail**: The AI is strictly an advisory engine; automated irreversible financial operations are prohibited.
- **Audit Logging**: Every evaluation yields a transparent trace explaining why a recommendation was made, accompanied by confidence signals.
- For in-depth architectural details, refer to [`docs/architecture.md`](docs/architecture.md).
