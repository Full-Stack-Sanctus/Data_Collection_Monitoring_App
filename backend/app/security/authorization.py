from typing import Annotated

from fastapi import Depends

from app.core.exceptions import AuthorizationError
from app.schemas.auth import TokenPayload
from app.security.dependencies import (
    get_current_principal,
)


def require_role(
    *allowed_roles: str,
):
    """
    Require the authenticated user to have one of the
    specified roles.
    """

    def dependency(
        principal: Annotated[
            TokenPayload,
            Depends(get_current_principal),
        ],
    ) -> TokenPayload:

        if principal.role not in allowed_roles:
            raise AuthorizationError()

        return principal

    return dependency