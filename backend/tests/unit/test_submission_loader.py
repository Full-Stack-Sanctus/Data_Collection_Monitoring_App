from app.pipeline.validation import (
    SubmissionValidationService,
)
from app.services.submission_loader import (
    SubmissionLoader,
)
from tests.fixtures.kobo_submissions import (
    create_invalid_gender_total_submission,
    create_valid_submission,
)


def test_load_result_counts_valid_submission(
    mocker,
) -> None:
    """
    Verify that the loader counts a successfully inserted
    accepted submission.
    """

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [create_valid_submission()]
    )

    loader = SubmissionLoader()

    mock_session = mocker.MagicMock()

    mocker.patch.object(
        loader,
        "_load_accepted",
        return_value="inserted",
    )

    result = loader.load(
        session=mock_session,
        pipeline_result=pipeline_result,
    )

    assert result.total_records == 1

    assert result.accepted_inserted == 1

    assert result.rejected_persisted == 0

    assert result.skipped_records == 0

    assert result.failed_records == 0

    mock_session.begin_nested.assert_called_once()

    mock_session.commit.assert_called_once()

    mock_session.rollback.assert_not_called()
    

def test_load_skips_duplicate_submission(
    mocker,
) -> None:
    """
    Verify that the loader counts a record as skipped when the
    underlying loading operation reports that the submission
    already exists.

    A skipped record does not represent a database failure, so the
    transaction must not be committed or rolled back.
    """

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [create_valid_submission()]
    )

    loader = SubmissionLoader()

    mock_session = mocker.MagicMock()

    mocker.patch.object(
        loader,
        "_load_accepted",
        return_value="skipped",
    )

    result = loader.load(
        session=mock_session,
        pipeline_result=pipeline_result,
    )

    assert result.total_records == 1

    assert result.accepted_inserted == 0

    assert result.skipped_records == 1

    assert result.failed_records == 0

    mock_session.begin_nested.assert_called_once()

    mock_session.commit.assert_not_called()

    mock_session.rollback.assert_not_called()
    


def test_load_result_counts_rejected_submission(
    mocker,
) -> None:
    """
    Verify that rejected submissions are passed to the rejected
    loading path and counted as successfully persisted.
    """

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [
            create_invalid_gender_total_submission()
        ]
    )

    loader = SubmissionLoader()

    mock_session = mocker.MagicMock()

    mocker.patch.object(
        loader,
        "_load_rejected",
        return_value="persisted",
    )

    result = loader.load(
        session=mock_session,
        pipeline_result=pipeline_result,
    )

    assert result.total_records == 1

    assert result.rejected_persisted == 1

    assert result.accepted_inserted == 0

    assert result.failed_records == 0

    mock_session.begin_nested.assert_called_once()

    mock_session.commit.assert_called_once()

    mock_session.rollback.assert_not_called()


def test_database_failure_does_not_stop_processing(
    mocker,
) -> None:
    """
    Verify that one unexpected database failure does not prevent
    the remaining submissions from being processed.

    Each submission is isolated using its own nested transaction.
    """

    validator = SubmissionValidationService()

    first_submission = create_valid_submission()

    second_submission = create_valid_submission()

    second_submission["_uuid"] = (
        "second-submission-uuid"
    )

    pipeline_result = validator.process(
        [
            first_submission,
            second_submission,
        ]
    )

    loader = SubmissionLoader()

    mock_session = mocker.MagicMock()

    mocker.patch.object(
        loader,
        "_load_accepted",
        side_effect=[
            Exception("Database unavailable"),
            "inserted",
        ],
    )

    result = loader.load(
        session=mock_session,
        pipeline_result=pipeline_result,
    )

    assert result.total_records == 2

    assert result.failed_records == 1

    assert result.accepted_inserted == 1

    assert result.rejected_persisted == 0

    assert result.skipped_records == 0

    assert len(result.failures) == 1

    assert (
        result.failures[0].submission_reference
        == "submission-uuid-123"
    )

    assert (
        result.failures[0].error
        == "Database unavailable"
    )

    assert mock_session.begin_nested.call_count == 2

    mock_session.commit.assert_called_once()

    mock_session.rollback.assert_not_called()