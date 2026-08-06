from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["status"])

@router.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}
