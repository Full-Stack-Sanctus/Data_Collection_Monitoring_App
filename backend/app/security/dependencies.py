from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from app.core.exceptions import AuthenticationError
from app.schemas.auth import TokenPayload
from app.security.jwt import JWTService


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_principal(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> TokenPayload:
    """
    Validate the bearer token and return the authenticated
    principal.
    """

    if credentials is None:
        raise AuthenticationError(
            "Authentication credentials are required."
        )

    token = credentials.credentials

    try:
        payload = JWTService().decode_access_token(
            token
        )

    except jwt.ExpiredSignatureError as error:
        raise AuthenticationError(
            "Access token has expired."
        ) from error

    except jwt.InvalidTokenError as error:
        raise AuthenticationError(
            "Invalid access token."
        ) from error

    subject = payload.get("sub")

    role = payload.get("role")

    if not subject or not role:
        raise AuthenticationError(
            "Access token is missing required claims."
        )

    return TokenPayload(
        sub=str(subject),
        role=str(role),
        exp=int(payload["exp"]),
    )