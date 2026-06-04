# UEBA Platform - Progress Log

## Stack
- FastAPI, PostgreSQL, SQLAlchemy, Alembic, uv

## Completed
- Project structure created
- Database models: User, RawEvent, NormalizedEvent
- Alembic migrations running
- .env setup with credentials fixed
- Git initialised with .gitignore

## In Progress
- Log ingestion endpoint

## Next
- Normalisation pipeline
- Baseline computation

## Key Decisions Made
- Raw events are immutable, checksum verified
- Alembic for all schema changes, never create_all
- Pydantic schemas separate from SQLAlchemy models
- Config centralised in app/core/config.py