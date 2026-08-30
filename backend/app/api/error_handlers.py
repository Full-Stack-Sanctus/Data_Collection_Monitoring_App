import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ApplicationError


logger = logging.getLogger(__name__)


def application_error_handler(
    request: Request,
    exception: ApplicationError,
) -> JSONResponse:
    """
    Convert an expected application exception into a consistent
    JSON API response.
    """

    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.code,
            "message": exception.message,
            "path": request.url.path,
        },
    )


async def unexpected_error_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """
    Handle unexpected application failures.

    Internal exception details are logged but never exposed to
    API consumers.
    """

    logger.exception(
        "Unhandled exception while processing %s",
        request.url.path,
        exc_info=exception,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred.",
            "path": request.url.path,
        },
    )