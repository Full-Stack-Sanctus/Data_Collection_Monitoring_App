from fastapi import APIRouter

from app.api.routes.monitoring import router as monitoring_router


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(
    monitoring_router,
)