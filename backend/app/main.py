from fastapi import FastAPI

from app.core.config import settings
from app.database.health import check_database_connection


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """
    Return the application health status.
    """

    database_connected = check_database_connection()

    return {
        "status": "healthy" if database_connected else "degraded",
        "environment": settings.app_env,
        "database": "connected" if database_connected else "disconnected",
    }