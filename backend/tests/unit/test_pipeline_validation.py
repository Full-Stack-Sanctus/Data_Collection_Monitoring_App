from app.pipeline.validation import (
    SubmissionValidationService,
)
from tests.fixtures.kobo_submissions import (
    create_cancelled_submission,
    create_invalid_gender_total_submission,
    create_valid_submission,
)


def test_accepts_valid_submission() -> None:
    """
    A valid Kobo submission should successfully pass transformation
    and validation.
    """

    service = SubmissionValidationService()

    result = service.process(
        [create_valid_submission()]
    )

    assert result.total_records == 1
    assert result.accepted_count == 1
    assert result.rejected_count == 0


def test_rejects_invalid_participant_totals() -> None:
    """
    A submission with inconsistent gender totals should be rejected.
    """

    service = SubmissionValidationService()

    result = service.process(
        [create_invalid_gender_total_submission()]
    )

    assert result.total_records == 1
    assert result.accepted_count == 0
    assert result.rejected_count == 1

    assert (
        result.rejected_records[0]
        .submission_reference
        == "submission-uuid-123"
    )


def test_continues_when_one_submission_fails() -> None:
    """
    One invalid record must not prevent valid records in the same
    batch from being processed.
    """

    valid_submission = create_valid_submission()

    invalid_submission = (
        create_invalid_gender_total_submission()
    )

    invalid_submission["_uuid"] = (
        "invalid-submission-uuid"
    )

    service = SubmissionValidationService()

    result = service.process(
        [
            valid_submission,
            invalid_submission,
        ]
    )

    assert result.total_records == 2
    assert result.accepted_count == 1
    assert result.rejected_count == 1


def test_cancelled_activity_uses_zero_participants() -> None:
    """
    Cancelled activities should have participant statistics
    normalized to zero.
    """

    service = SubmissionValidationService()

    result = service.process(
        [create_cancelled_submission()]
    )

    assert result.accepted_count == 1
    assert result.rejected_count == 0

    accepted = result.accepted_records[0]

    assert (
        accepted.submission.participant_data.actual_participants
        == 0
    )

    assert (
        accepted.submission.participant_data.male_participants
        == 0
    )

    assert (
        accepted.submission.participant_data.female_participants
        == 0
    )

    assert (
        accepted.submission.participant_data.youth_participants
        == 0
    )

    assert (
        accepted.submission.participant_data.adult_participants
        == 0
    )