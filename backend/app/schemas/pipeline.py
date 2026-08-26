from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.kobo_submission import KoboSubmission


class AcceptedSubmission(BaseModel):
    """
    Represents a Kobo submission that successfully passed
    transformation and validation.

    Both the normalized submission and the original raw payload
    are preserved so the normalized database records can maintain
    a traceable relationship to their source data.
    """

    submission: KoboSubmission

    raw_submission: dict[str, Any]


class RejectedSubmission(BaseModel):
    """
    Represents a Kobo submission that could not pass the
    transformation or validation process.

    The raw submission is preserved so the record can be
    investigated or reprocessed later.
    """

    submission_reference: str | int | None = None

    error: str

    raw_submission: dict[str, Any]


class PipelineResult(BaseModel):
    """
    Represents the result of processing a batch of Kobo submissions.
    """

    started_at: datetime

    completed_at: datetime | None = None

    total_records: int = Field(ge=0)

    accepted_records: list[AcceptedSubmission] = Field(
        default_factory=list
    )

    rejected_records: list[RejectedSubmission] = Field(
        default_factory=list
    )

    @property
    def accepted_count(self) -> int:
        """
        Number of successfully validated submissions.
        """

        return len(self.accepted_records)

    @property
    def rejected_count(self) -> int:
        """
        Number of rejected submissions.
        """

        return len(self.rejected_records)