from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes.health import router as health_router


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    application = FastAPI(
        title="Digital Data Collection and Program Monitoring System",
        version="1.0.0",
        description=(
            "REST API for digital data collection, "
            "data quality management, and program monitoring."
        ),
    )

    application.include_router(
        health_router,
    )

    application.include_router(
        api_router,
    )

    return application


app = create_application()