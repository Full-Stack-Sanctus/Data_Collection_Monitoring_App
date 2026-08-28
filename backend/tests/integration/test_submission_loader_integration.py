import pytest

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.data_quality_issue import (
    DataQualityIssue,
)
from app.models.field_officer import FieldOfficer
from app.models.location import Location
from app.models.program import Program
from app.models.raw_submission import RawSubmission

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


def create_unique_submission() -> dict:
    """
    Create a valid Kobo submission with unique identifiers.

    Unique values prevent integration tests from conflicting with
    existing development or test records in PostgreSQL.
    """

    submission = create_valid_submission()

    identifier = uuid4().hex

    submission["_uuid"] = (
        f"integration-test-{identifier}"
    )

    submission[
        "program_information/program"
    ] = (
        f"integration_program_{identifier}"
    )

    submission[
        "program_information/program_code"
    ] = (
        f"integration_program_{identifier}"
    )

    submission[
        "location_information/state"
    ] = (
        f"integration_state_{identifier}"
    )

    submission[
        "location_information/lga"
    ] = (
        f"integration_lga_{identifier}"
    )

    submission[
        "location_information/community"
    ] = (
        f"integration_community_{identifier}"
    )

    submission["username"] = (
        f"integration_user_{identifier}"
    )

    return submission


def test_valid_submission_is_persisted(
    db_session: Session,
) -> None:
    """
    Verify that a valid Kobo submission is successfully transformed
    and persisted into the normalized PostgreSQL structure.
    """

    raw_submission = create_unique_submission()

    external_submission_id = raw_submission["_uuid"]

    validator = SubmissionValidationService()

    loader = SubmissionLoader()

    pipeline_result = validator.process(
        [raw_submission]
    )

    assert pipeline_result.accepted_count == 1

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 1

    assert load_result.accepted_inserted == 1

    assert load_result.rejected_persisted == 0

    assert load_result.skipped_records == 0

    assert load_result.failed_records == 0

    persisted_raw_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == external_submission_id
        )
    )

    assert persisted_raw_submission is not None

    assert (
        persisted_raw_submission.source
        == "kobotoolbox"
    )

    assert (
        persisted_raw_submission.processing_status
        == "processed"
    )

    activity = db_session.scalar(
        select(Activity).where(
            Activity.raw_submission_id
            == persisted_raw_submission.id
        )
    )

    assert activity is not None

    assert activity.activity_title == (
        "Python Training"
    )

    assert activity.target_participants == 100

    assert activity.actual_participants == 90

    assert activity.male_participants == 50

    assert activity.female_participants == 40
        
        
def test_duplicate_submission_is_skipped(
    db_session: Session,
) -> None:
    """
    Verify that processing the same Kobo submission twice does not
    create duplicate database records.
    """

    raw_submission = create_unique_submission()

    external_submission_id = raw_submission["_uuid"]

    validator = SubmissionValidationService()

    loader = SubmissionLoader()

    pipeline_result = validator.process(
        [raw_submission]
    )

    first_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert first_result.accepted_inserted == 1

    second_pipeline_result = validator.process(
        [raw_submission]
    )

    second_result = loader.load(
        session=db_session,
        pipeline_result=second_pipeline_result,
    )

    assert second_result.accepted_inserted == 0

    assert second_result.skipped_records == 1

    assert second_result.failed_records == 0
    
    
    raw_submissions = db_session.scalars(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == external_submission_id
        )
    ).all()

    assert len(raw_submissions) == 1
    
        
def test_rejected_submission_is_preserved_with_issue(
    db_session: Session,
) -> None:
    """
    Verify that an invalid Kobo submission is preserved in the
    database and linked to a data quality issue.
    """

    raw_submission = (
        create_invalid_gender_total_submission()
    )

    identifier = uuid4().hex

    raw_submission["_uuid"] = (
        f"integration-rejected-{identifier}"
    )

    external_submission_id = raw_submission["_uuid"]

    validator = SubmissionValidationService()

    loader = SubmissionLoader()

    pipeline_result = validator.process(
        [raw_submission]
    )

    assert pipeline_result.accepted_count == 0

    assert pipeline_result.rejected_count == 1

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 1

    assert load_result.accepted_inserted == 0

    assert load_result.rejected_persisted == 1

    assert load_result.failed_records == 0

    persisted_raw_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == external_submission_id
        )
    )

    assert persisted_raw_submission is not None

    assert (
        persisted_raw_submission.processing_status
        == "failed"
    )

    issue = db_session.scalar(
        select(DataQualityIssue).where(
            DataQualityIssue.raw_submission_id
            == persisted_raw_submission.id
        )
    )

    assert issue is not None

    assert (
        issue.rule_name
        == "kobo_submission_validation"
    )

    assert issue.severity == "error"

    assert issue.status == "open"

    assert issue.issue_description
    
    

def test_mixed_batch_persists_valid_and_rejected_records(
    db_session: Session,
) -> None:
    """
    Verify that valid and invalid submissions can be processed in the
    same pipeline batch.

    A rejected submission must not prevent a valid submission from
    being successfully persisted.
    """

    valid_submission = create_unique_submission()

    valid_submission_id = valid_submission["_uuid"]

    invalid_submission = (
        create_invalid_gender_total_submission()
    )

    invalid_identifier = uuid4().hex

    invalid_submission["_uuid"] = (
        f"integration-invalid-{invalid_identifier}"
    )

    invalid_submission_id = (
        invalid_submission["_uuid"]
    )

    validator = SubmissionValidationService()

    loader = SubmissionLoader()

    pipeline_result = validator.process(
        [
            valid_submission,
            invalid_submission,
        ]
    )

    assert pipeline_result.total_records == 2

    assert pipeline_result.accepted_count == 1

    assert pipeline_result.rejected_count == 1

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 2

    assert load_result.accepted_inserted == 1

    assert load_result.rejected_persisted == 1

    assert load_result.skipped_records == 0

    assert load_result.failed_records == 0

    valid_raw_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == valid_submission_id
        )
    )

    invalid_raw_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == invalid_submission_id
        )
    )

    assert valid_raw_submission is not None

    assert invalid_raw_submission is not None

    assert (
        valid_raw_submission.processing_status
        == "processed"
    )

    assert (
        invalid_raw_submission.processing_status
        == "failed"
    )
    
    
def test_database_failure_is_recorded(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that an unexpected database failure is handled safely.

    The failed submission should:

    - be rolled back;
    - increment failed_records;
    - record failure information;
    - not be reported as successfully inserted.
    """

    raw_submission = create_unique_submission()

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [raw_submission]
    )

    assert pipeline_result.accepted_count == 1

    loader = SubmissionLoader()

    def raise_database_error(*args, **kwargs):
        """
        Simulate an unexpected failure during raw submission
        persistence.
        """

        raise RuntimeError(
            "Simulated database failure."
        )

    monkeypatch.setattr(
        loader.raw_submission_repository,
        "create",
        raise_database_error,
    )

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 1

    assert load_result.accepted_inserted == 0

    assert load_result.rejected_persisted == 0

    assert load_result.skipped_records == 0

    assert load_result.failed_records == 1

    assert len(load_result.failures) == 1

    failure = load_result.failures[0]

    assert (
        failure.submission_reference
        == raw_submission["_uuid"]
    )

    assert (
        failure.error
        == "Simulated database failure."
    )    
    

def test_database_failure_does_not_stop_remaining_records(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that a database failure for one submission does not
    prevent later submissions in the same batch from being
    processed successfully.
    """

    first_submission = create_unique_submission()

    failing_submission = create_unique_submission()

    successful_submission = create_unique_submission()

    failing_submission_id = (
        failing_submission["_uuid"]
    )

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [
            first_submission,
            failing_submission,
            successful_submission,
        ]
    )

    assert pipeline_result.accepted_count == 3

    loader = SubmissionLoader()

    original_create = (
        loader.raw_submission_repository.create
    )

    def create_with_simulated_failure(
        session: Session,
        *,
        source: str,
        external_submission_id: str,
        payload: dict,
        retrieved_at,
        processing_status: str = "pending",
    ):
        """
        Fail only for one specific submission.

        All other submissions continue through the real repository
        implementation.
        """

        if (
            external_submission_id
            == failing_submission_id
        ):
            raise RuntimeError(
                "Simulated database failure."
            )

        return original_create(
            session,
            source=source,
            external_submission_id=(
                external_submission_id
            ),
            payload=payload,
            retrieved_at=retrieved_at,
            processing_status=processing_status,
        )

    monkeypatch.setattr(
        loader.raw_submission_repository,
        "create",
        create_with_simulated_failure,
    )

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 3

    assert load_result.accepted_inserted == 2

    assert load_result.rejected_persisted == 0

    assert load_result.skipped_records == 0

    assert load_result.failed_records == 1

    assert len(load_result.failures) == 1

    assert (
        load_result.failures[0]
        .submission_reference
        == failing_submission_id
    )
    
    
def test_integrity_error_is_recorded(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that a SQLAlchemy IntegrityError is handled safely and
    recorded as a database failure.
    """

    raw_submission = create_unique_submission()

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [raw_submission]
    )

    loader = SubmissionLoader()

    integrity_error = IntegrityError(
        statement="INSERT INTO raw_submissions",
        params={},
        orig=Exception(
            "Simulated integrity constraint violation."
        ),
    )

    def raise_integrity_error(*args, **kwargs):
        """
        Simulate a database integrity constraint failure.
        """

        raise integrity_error

    monkeypatch.setattr(
        loader.raw_submission_repository,
        "create",
        raise_integrity_error,
    )

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 1

    assert load_result.accepted_inserted == 0

    assert load_result.failed_records == 1

    assert len(load_result.failures) == 1

    failure = load_result.failures[0]

    assert (
        failure.submission_reference
        == raw_submission["_uuid"]
    )

    assert (
        failure.error
        == "Simulated integrity constraint violation."
    )
    

def test_savepoint_rolls_back_only_failed_submission(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that a failure occurring after database persistence has
    started rolls back only the failing submission.

    This test proves that the nested transaction used for each
    submission isolates the failed record from other successfully
    processed records.

    Expected outcome:

        First submission
            -> persisted successfully

        Second submission
            -> RawSubmission creation begins
            -> simulated failure occurs
            -> nested transaction rolls back

        Third submission
            -> persisted successfully

    The final database state must contain the first and third
    submissions, but not the failed second submission.
    """

    first_submission = create_unique_submission()
    failing_submission = create_unique_submission()
    successful_submission = create_unique_submission()

    first_submission_id = first_submission["_uuid"]
    failing_submission_id = failing_submission["_uuid"]
    successful_submission_id = successful_submission["_uuid"]

    validator = SubmissionValidationService()

    pipeline_result = validator.process(
        [
            first_submission,
            failing_submission,
            successful_submission,
        ]
    )

    assert pipeline_result.total_records == 3
    assert pipeline_result.accepted_count == 3

    loader = SubmissionLoader()

    original_create = loader.raw_submission_repository.create

    def create_then_fail_for_one_submission(
        session: Session,
        *,
        source: str,
        external_submission_id: str,
        payload: dict,
        retrieved_at,
        processing_status: str = "pending",
    ):
        """
        Allow RawSubmission persistence to begin normally.

        For the designated failing submission, raise an exception
        after the repository has already added the record to the
        SQLAlchemy session.

        The nested transaction must roll back this partial database
        work without affecting the surrounding submissions.
        """

        raw_submission = original_create(
            session,
            source=source,
            external_submission_id=external_submission_id,
            payload=payload,
            retrieved_at=retrieved_at,
            processing_status=processing_status,
        )

        if external_submission_id == failing_submission_id:
            raise RuntimeError(
                "Simulated failure after persistence began."
            )

        return raw_submission

    monkeypatch.setattr(
        loader.raw_submission_repository,
        "create",
        create_then_fail_for_one_submission,
    )

    load_result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert load_result.total_records == 3
    assert load_result.accepted_inserted == 2
    assert load_result.rejected_persisted == 0
    assert load_result.skipped_records == 0
    assert load_result.failed_records == 1

    assert len(load_result.failures) == 1

    failure = load_result.failures[0]

    assert failure.submission_reference == failing_submission_id

    assert (
        failure.error
        == "Simulated failure after persistence began."
    )

    persisted_first_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == first_submission_id
        )
    )

    persisted_failing_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == failing_submission_id
        )
    )

    persisted_successful_submission = db_session.scalar(
        select(RawSubmission).where(
            RawSubmission.external_submission_id
            == successful_submission_id
        )
    )

    assert persisted_first_submission is not None
    assert persisted_failing_submission is None
    assert persisted_successful_submission is not None

    first_activity = db_session.scalar(
        select(Activity).where(
            Activity.raw_submission_id
            == persisted_first_submission.id
        )
    )

    successful_activity = db_session.scalar(
        select(Activity).where(
            Activity.raw_submission_id
            == persisted_successful_submission.id
        )
    )

    assert first_activity is not None
    assert successful_activity is not None