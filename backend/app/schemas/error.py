from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Standard API error response.

    Every expected application error exposed through the API should
    follow this structure.
    """

    error: str

    message: str

    path: str