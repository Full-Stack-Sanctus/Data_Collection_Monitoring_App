from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings


class JWTService:
    """
    Handles creation and verification of JWT access tokens.
    """

    def create_access_token(
        self,
        *,
        subject: str,
        role: str,
    ) -> str:
        """
        Create a signed JWT access token.
        """

        now = datetime.now(timezone.utc)

        expires_at = (
            now
            + timedelta(
                minutes=(
                    settings
                    .jwt_access_token_expire_minutes
                ),
            )
        )

        payload: dict[str, Any] = {
            "sub": subject,
            "role": role,
            "iat": now,
            "exp": expires_at,
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def decode_access_token(
        self,
        token: str,
    ) -> dict[str, Any]:
        """
        Decode and validate a JWT access token.

        PyJWT automatically validates the expiration claim.
        """

        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm,
            ],
        )