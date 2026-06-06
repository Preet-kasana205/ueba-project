# UEBA Platform - Progress Log

## Stack
FastAPI, PostgreSQL, SQLAlchemy, Alembic, uv, Scikit-learn, Pandas, 
Plotly, Streamlit, Docker

## Completed
- Project scaffolding and folder structure
- PostgreSQL database and Alembic migrations
- Models: User, RawEvent, NormalizedEvent
- Central config with pydantic-settings
- Batch ingestion endpoint with checksum and idempotency
- Database index on checksum
- Normalisation pipeline for auth and file_access logs
- .gitignore, .env.example, Git initialised

## In Progress
- normalisation concept complete inderstanding 
## Next
- Sample log generator
- User management endpoints
- Baseline computation engine
- Rule-based detection

## Key Files
- app/core/config.py — central settings
- app/db/session.py — database session and Base
- app/models/ — SQLAlchemy models
- app/schemas/ — Pydantic schemas
- app/services/ingestion.py — batch ingestion logic
- app/services/normalization.py — normalisation pipeline
- app/api/v1/ingest.py — ingestion routes