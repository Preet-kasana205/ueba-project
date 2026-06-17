# UEBA Platform
### User and Entity Behaviour Analytics for Insider Threat Detection

A FastAPI-based security platform that continuously monitors user activity,
builds per-user behavioural baselines, detects statistical anomalies, and
generates explainable risk-scored alerts with automatic step-up verification
triggers. Built for the Identity Trust framework in banking environments.

---

## The Problem It Solves

Traditional security tools block known threats. Insider threats are different —
the attacker already has legitimate access. Detecting them requires knowing what
**normal** looks like for each individual user, then identifying when behaviour
deviates from that baseline.

This platform answers: *"Is this the same person who normally uses this account?"*

---

## Threats Detected

| Threat | Detection Method | Severity |
|--------|-----------------|----------|
| Unusual login time | Z-score vs 30-day login hour baseline | High |
| New device login | Registry of known devices per user | High |
| Data volume spike | Z-score vs daily transfer baseline | Critical |
| Privilege escalation | Event type classification | Critical |
| Impossible travel | Geographic distance vs time delta | High |

Risk scores above **70 / 100** automatically trigger step-up verification.

---

## How It Works

```
Log Sources (Auth · File Access · Network)
        ↓
Ingestion Layer
SHA-256 checksum · deduplication · batch processing
        ↓
Raw Events Store (immutable · forensic integrity)
        ↓
Normalisation Pipeline
Dispatch table · source-specific parsers · user resolution
        ↓
Baseline Engine
30-day rolling window per user · login hours · devices · data volume
        ↓
Detection Engine
Rule-based · z-score analysis · confidence scoring
        ↓
Risk Scoring Engine
Weighted signals · worst-per-type · 0–100 scale
        ↓
Alert Engine
Explainable alerts · step-up verification trigger
        ↓
Streamlit Dashboard
Fleet overview · risk charts · analyst actions
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI, Python 3.11 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Scheduling | APScheduler |
| Dashboard | Streamlit, Plotly |
| Package manager | uv |

---

## Project Structure

```
ueba-platform/
├── app/
│   ├── api/v1/          # Route handlers
│   │   ├── ingest.py    # Log ingestion endpoints
│   │   ├── users.py     # User management
│   │   ├── baseline.py  # Baseline computation
│   │   ├── detection.py # Anomaly detection trigger
│   │   └── alerts.py    # Alert management
│   ├── detection/
│   │   └── rules/       # Rule-based detectors
│   │       ├── login_time.py
│   │       ├── new_device.py
│   │       └── data_volume.py
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic
│   │   ├── ingestion.py
│   │   ├── normalization.py
│   │   ├── baseline.py
│   │   ├── detection.py
│   │   └── alert_engine.py
│   └── scoring/
│       └── risk_scorer.py
├── dashboard/
│   └── app.py           # Streamlit dashboard
├── data/
│   ├── generate_sample_data.py
│   └── load_sample_data.py
└── alembic/             # Database migrations
```

---

## Setup and Running

### Prerequisites

- Python 3.11 or higher
- PostgreSQL running locally
- uv installed → https://docs.astral.sh/uv/

### Install uv (Windows)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.sh | iex"
```

### 1. Clone and install dependencies

```bash
git clone https://github.com/Preet-kasana205/ueba-project
cd ueba-project
uv sync
```

### 2. Configure environment

```bash
cp .envexample .env
```

Edit `.env` with your PostgreSQL password:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ueba
SECRET_KEY=changethislater
ENVIRONMENT=development
```

### 3. Create the database

```bash
psql -U postgres -c "CREATE DATABASE ueba;"
```

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Start the backend (Terminal 1)

```bash
uv run uvicorn app.main:app --reload
```

API is now running at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 6. Load demo data (Terminal 2)

```bash
uv run python data/generate_sample_data.py
uv run python data/load_sample_data.py
```

This generates 30 days of normal activity and injects anomalous events.

### 7. Start the dashboard (Terminal 3)

```bash
uv run streamlit run dashboard/app.py
```

Open `http://localhost:8501` and click **Run Full Demo**.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/ingest/events/batch` | Ingest batch of raw log events |
| POST | `/api/v1/ingest/normalize` | Normalize pending raw events |
| POST | `/api/v1/baseline/compute` | Compute behavioural baselines |
| POST | `/api/v1/detection/run` | Run anomaly detection |
| POST | `/api/v1/alerts/generate` | Generate alerts from anomalies |
| GET | `/api/v1/alerts` | List all alerts |
| PATCH | `/api/v1/alerts/{id}/status` | Update alert status |
| GET | `/api/v1/users` | List monitored users |
| POST | `/api/v1/users` | Register a monitored user |

Full interactive documentation available at `/docs` when server is running.

---

## Demo Scenario

The sample data simulates 3 users across 30 days of normal working hours,
then injects the following suspicious events:

**john.smith (Finance Analyst)**
- Login at 2:13am from a device never seen before
- Downloads 50MB of payroll data (normal: 3.7MB/day)

**sara.jones (HR Manager)**
- Login at 12:05am from an unknown device
- Downloads 40MB of employee records

**preet.kasana (Developer)**
- Single login at 3:05am from an unknown device

**Expected results after running the pipeline:**

```
john.smith   → Risk score: 73.3 → Step-up verification: TRIGGERED
sara.jones   → Risk score: 73.3 → Step-up verification: TRIGGERED
preet.kasana → Risk score: 33.4 → Monitoring only
```

---

## Key Engineering Decisions

**Immutable raw events**
Raw logs are never modified after ingestion. SHA-256 checksums enable
forensic proof that logs were not tampered with after collection.

**Idempotent ingestion**
Duplicate events are detected via checksum before insertion. Safe to
retry failed batches without creating duplicate records.

**Dispatch table normalisation**
Each log source has its own normaliser function registered in a dictionary.
Adding a new log source requires adding one function — no existing code changes.
This enforces the Open/Closed Principle.

**Worst-per-type risk scoring**
Risk scores take the highest confidence anomaly of each type rather than
summing all instances. Prevents score inflation from repeated events.

**Subquery-based state tracking**
Processing state is derived from actual data relationships, not boolean flags.
Avoids inconsistency when jobs fail mid-batch.

---

## Areas for Extension

- Impossible travel detection (geolocation + time delta)
- Isolation Forest ML-based anomaly detection
- Kafka integration for real-time streaming ingestion
- Active Directory sync for automatic user registration
- Email/Slack alerts for critical severity events
- REST webhook for triggering step-up authentication systems

---

## Author

Preet Kasana   
Built as a resume project demonstrating backend engineering and cybersecurity concepts.


