from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    Represents an issued access token.
    """

    access_token: str

    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Represents the validated claims contained in an access token.
    """

    sub: str

    role: str

    exp: int