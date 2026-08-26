from typing import Any

from pydantic import BaseModel, Field


class KoboAsset(BaseModel):
    """
    Represents the minimum Kobo project/asset information
    required by this application.
    """

    uid: str

    name: str

    data: str | None = None


class KoboSubmissionPage(BaseModel):
    """
    Represents one paginated response from the Kobo data endpoint.

    Kobo v2 returns submissions inside the `results` field and provides
    a `next` URL when additional pages are available.
    """

    count: int

    next: str | None = None

    previous: str | None = None

    results: list[dict[str, Any]] = Field(default_factory=list)