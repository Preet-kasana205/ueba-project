# UEBA Platform

A FastAPI prototype for detecting insider-threat behavior from authentication
and file-access events.

## Current Pipeline

1. Ingest raw events with checksum-based duplicate checks.
2. Normalize source-specific payloads into a common event model.
3. Build per-user baselines for login hours, devices, and data volume.
4. Evaluate recent events with behavioral detection rules.
5. Combine findings into persistent, idempotent risk alerts.

Implemented rules:

- Unusual login time
- New device
- Data-volume spike

## Run Locally

```powershell
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Generate and load the demo story in a second terminal:

```powershell
uv run python data/generate_sample_data.py
uv run python data/load_sample_data.py
```

The loader intentionally computes baselines from normal history before loading
the anomalous John Smith events.

## API Flow

```text
POST /api/v1/ingest/events/batch
POST /api/v1/ingest/normalize
POST /api/v1/baseline/compute
POST /api/v1/detection/run?lookback_hours=24
POST /api/v1/alerts/generate?lookback_hours=24
GET  /api/v1/alerts/
```

Interactive API documentation is available at `http://localhost:8000/docs`.

## Tests

```powershell
uv run python -m unittest discover -s codex/tests -v
```
