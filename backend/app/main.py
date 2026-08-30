from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import (
    application_error_handler,
    unexpected_error_handler,
)
from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.exceptions import ApplicationError


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    application = FastAPI(
        title=(
            "Digital Data Collection and "
            "Program Monitoring App"
        ),
        version="1.0.0",
        summary=(
            "REST API for digital data collection, "
            "data quality management, and program monitoring."
        ),
        description=(
            "A backend service for ingesting digital field data, "
            "performing validation and data quality checks, "
            "persisting normalized records, and exposing "
            "program monitoring indicators."
        ),
        debug=settings.debug,
    )

    application.add_exception_handler(
        ApplicationError,
        application_error_handler,
    )

    application.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET"],
            allow_headers=["*"],
        )

    application.include_router(
        health_router,
    )

    application.include_router(
        api_router,
    )

    return application


app = create_application()