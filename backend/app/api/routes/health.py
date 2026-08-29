from fastapi import APIRouter
from app.core.config import settings
from app.database.health import check_database_connection

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("/live")
def liveness_check() -> dict[str, str]:
    """
    Lightweight check to confirm the API instance is running.
    """
    return {"status": "ok"}

@router.get("/ready")
async def readiness_check():
    """
    Deeper check to ensure the database connection is healthy.
    """
    database_connected = check_database_connection()
    
    return {
        "status": "healthy" if database_connected else "degraded",
        "environment": settings.app_env,
        "database": "connected" if database_connected else "disconnected",
    }
