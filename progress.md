# UEBA Platform - Progress Log

## Stack
FastAPI, PostgreSQL, SQLAlchemy, Alembic, APScheduler, uv
Path: C:\Users\Lenovo\ueba-project
GitHub: Preet-kasana205/ueba-project

## Completed
- Project structure and folder layout
- Database models: User, RawEvent, NormalizedEvent, UserDevice, Baseline
- Alembic migrations running
- Log ingestion with SHA-256 checksum + idempotency
- Normalisation pipeline with dispatch table pattern
- Auto-normalisation via APScheduler every 60 seconds
- User management endpoints
- User-to-event linking during normalisation
- Baseline computation: login_hours, known_devices, data_volume
- Sample data generator (30 days normal + anomaly scenario)
- Sample data loader script
- Detection rules (new device, unusual login time, data volume spike)

## Hackathon Context
- 10 day deadline
- Need: prototype demo link + workflow diagram
- Story scenario: john.smith 2am login, unknown device, 50MB download

## Next To Build

1. Risk scoring engine
2. Alert generation
3. Streamlit dashboard
4. Workflow diagram
5. Docker Compose

## Key Decisions Made
- Raw events immutable, checksum verified
- Subquery for idempotent normalisation
- Dispatch table pattern for normalizers (Open/Closed)
- Baselines stored as JSONB parameters, old ones kept 
  with is_current=False
- Corrupted timestamps rejected, not silently substituted
