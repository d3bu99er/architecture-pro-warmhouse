from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

# ✅ "/" вместо "/health" (prefix="/health" добавит сам!)
@router.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "device-service",
        "timestamp": datetime.utcnow().isoformat()
    }
@router.get("/ready")
async def readiness_check():
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    return {"status": "live"}
