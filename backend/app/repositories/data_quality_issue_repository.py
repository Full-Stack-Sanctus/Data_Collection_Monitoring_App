from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.data_quality_issue import (
    DataQualityIssue,
)


class DataQualityIssueRepository:
    """
    Handles persistence of data quality issues detected during
    transformation and validation.
    """

    def create(
        self,
        session: Session,
        *,
        raw_submission_id: UUID,
        rule_name: str,
        severity: str,
        issue_description: str,
        detected_at: datetime,
        status: str = "open",
    ) -> DataQualityIssue:
        """
        Create a data quality issue linked to a raw submission.
        """

        issue = DataQualityIssue(
            raw_submission_id=raw_submission_id,
            rule_name=rule_name,
            severity=severity,
            issue_description=issue_description,
            status=status,
            detected_at=detected_at,
        )

        session.add(issue)

        session.flush()

        return issue