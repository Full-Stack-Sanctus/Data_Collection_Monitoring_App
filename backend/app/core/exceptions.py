class ApplicationError(Exception):
    """
    Base exception for expected application-level errors.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "application_error",
        status_code: int = 400,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code
        self.status_code = status_code


class ResourceNotFoundError(ApplicationError):
    """
    Raised when a requested resource does not exist.
    """

    def __init__(
        self,
        message: str = "Resource not found.",
    ) -> None:
        super().__init__(
            message,
            code="resource_not_found",
            status_code=404,
        )


class ConflictError(ApplicationError):
    """
    Raised when an operation conflicts with the current state
    of a resource.
    """

    def __init__(
        self,
        message: str = "Resource conflict.",
    ) -> None:
        super().__init__(
            message,
            code="resource_conflict",
            status_code=409,
        )


class AuthenticationError(ApplicationError):
    """
    Raised when authentication fails.
    """

    def __init__(
        self,
        message: str = "Authentication failed.",
    ) -> None:
        super().__init__(
            message,
            code="authentication_failed",
            status_code=401,
        )


class AuthorizationError(ApplicationError):
    """
    Raised when an authenticated caller is not authorized.
    """

    def __init__(
        self,
        message: str = (
            "You are not authorized to perform this operation."
        ),
    ) -> None:
        super().__init__(
            message,
            code="authorization_failed",
            status_code=403,
        )