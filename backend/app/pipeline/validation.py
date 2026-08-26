from datetime import datetime
from typing import Any

from app.kobo.transformer import (
    KoboTransformationError,
    transform_submission,
)
from app.schemas.pipeline import (
    PipelineResult,
    RejectedSubmission,
)


class SubmissionValidationService:
    """
    Validates and transforms batches of raw Kobo submissions.

    A failure in one submission does not stop processing of
    the remaining submissions.
    """

    def process(
        self,
        raw_submissions: list[dict[str, Any]],
    ) -> PipelineResult:
        """
        Process a batch of raw Kobo submissions.

        Each record is independently transformed and validated.
        """

        result = PipelineResult(
            started_at=datetime.now(),
            total_records=len(raw_submissions),
        )

        for raw_submission in raw_submissions:
            self._process_submission(
                raw_submission=raw_submission,
                result=result,
            )

        result.completed_at = datetime.now()

        return result

    def _process_submission(
        self,
        raw_submission: dict[str, Any],
        result: PipelineResult,
    ) -> None:
        """
        Process one raw Kobo submission.

        Successful records are added to accepted_records.

        Failed records are added to rejected_records along
        with their raw payload and error information.
        """

        submission_reference = (
            raw_submission.get("_uuid")
            or raw_submission.get("_id")
        )

        try:
            submission = transform_submission(
                raw_submission
            )

            result.accepted_records.append(
                submission
            )

        except KoboTransformationError as error:
            result.rejected_records.append(
                RejectedSubmission(
                    submission_reference=(
                        submission_reference
                    ),
                    error=str(error),
                    raw_submission=raw_submission,
                )
            )

        except Exception as error:
            result.rejected_records.append(
                RejectedSubmission(
                    submission_reference=(
                        submission_reference
                    ),
                    error=(
                        "Unexpected validation error: "
                        f"{error}"
                    ),
                    raw_submission=raw_submission,
                )
            )