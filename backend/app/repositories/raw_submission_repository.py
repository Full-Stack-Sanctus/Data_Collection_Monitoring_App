from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_submission import RawSubmission


class RawSubmissionRepository:
    """
    Handles persistence and lookup of raw submissions received
    from external data collection platforms.
    """

    def get_by_source_and_external_id(
        self,
        session: Session,
        *,
        source: str,
        external_submission_id: str,
    ) -> RawSubmission | None:
        """
        Retrieve an existing raw submission using its source and
        external submission identifier.
        """

        statement = select(RawSubmission).where(
            RawSubmission.source == source,
            RawSubmission.external_submission_id
            == external_submission_id,
        )

        return session.scalar(statement)

    def create(
        self,
        session: Session,
        *,
        source: str,
        external_submission_id: str,
        payload: dict[str, Any],
        retrieved_at: datetime,
        processing_status: str = "pending",
    ) -> RawSubmission:
        """
        Store the original source payload.

        The processing status represents the current state of the
        application's handling of the submission.
        """

        raw_submission = RawSubmission(
            source=source,
            external_submission_id=external_submission_id,
            payload=payload,
            retrieved_at=retrieved_at,
            processing_status=processing_status,
        )

        session.add(raw_submission)

        # Flush so the generated UUID is available for related
        # Activity or DataQualityIssue records.
        session.flush()

        return raw_submission