import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_api_key(
    x_api_key: str | None = Header(
        default=None,
        alias="X-API-Key",
    ),
) -> None:
    """
    Authenticate an API request using the configured API key.

    Authentication can be disabled explicitly through configuration,
    which is useful for local development or controlled internal
    environments.

    When authentication is enabled:

        Missing API key
            → 401 Unauthorized

        Invalid API key
            → 401 Unauthorized

        Valid API key
            → request proceeds

    secrets.compare_digest() is used to avoid ordinary string
    comparison for credential verification.
    """

    if not settings.api_auth_enabled:
        return

    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication is not configured.",
        )

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "ApiKey",
            },
        )

    if not secrets.compare_digest(
        x_api_key,
        settings.api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={
                "WWW-Authenticate": "ApiKey",
            },
        )