from fastapi import APIRouter, Depends

from app.api.v1 import alerts, baseline, detection, ingest, users
from app.api.v1.auth import router as auth_router
from app.core.deps import get_current_user

router = APIRouter()

# Public — no auth needed
router.include_router(auth_router)

# Protected — requires valid JWT
router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"], dependencies=[Depends(get_current_user)])
router.include_router(users.router, prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])
router.include_router(baseline.router, prefix="/baseline", tags=["Baseline"], dependencies=[Depends(get_current_user)])
router.include_router(detection.router, prefix="/detection", tags=["Detection"], dependencies=[Depends(get_current_user)])
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"], dependencies=[Depends(get_current_user)])



