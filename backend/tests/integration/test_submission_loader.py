from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
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
from app.tests.fixtures.kobo_submissions import (
    create_valid_submission,
)


def test_loads_valid_submission_into_database(
    db_session: Session,
) -> None:
    """
    Verify that a valid Kobo submission is persisted as a complete
    normalized database record.
    """

    submission_id = (
        f"test-submission-{uuid4()}"
    )

    raw_submission = create_valid_submission(
        submission_uuid=submission_id,
    )

    validation_service = SubmissionValidationService()

    pipeline_result = validation_service.process(
        [raw_submission]
    )

    loader = SubmissionLoader()

    result = loader.load(
        session=db_session,
        pipeline_result=pipeline_result,
    )

    assert result.total_records == 1

    assert result.accepted_inserted == 1

    assert result.rejected_persisted == 0

    assert result.skipped_records == 0

    assert result.failed_records == 0

    statement = select(RawSubmission).where(
        RawSubmission.external_submission_id
        == submission_id
    )

    raw_record = db_session.scalar(statement)

    assert raw_record is not None

    assert raw_record.source == "kobotoolbox"

    assert raw_record.processing_status == "processed"

    assert raw_record.processed_at is not None

    statement = select(Activity).where(
        Activity.raw_submission_id
        == raw_record.id
    )

    activity = db_session.scalar(statement)

    assert activity is not None

    assert activity.activity_title == "Python Training"

    assert activity.target_participants == 100

    assert activity.actual_participants == 90

    assert activity.male_participants == 50

    assert activity.female_participants == 40

    assert activity.youth_participants == 70

    assert activity.adult_participants == 20

    program = db_session.get(
        Program,
        activity.program_id,
    )

    assert program is not None

    assert program.name == "digital_skills"

    location = db_session.get(
        Location,
        activity.location_id,
    )

    assert location is not None

    assert location.state == "rivers"

    assert location.lga == "Port Harcourt"

    assert location.community == "Orogbum"

    assert location.latitude == 7.70737

    assert location.longitude == 8.525931

    field_officer = db_session.get(
        FieldOfficer,
        activity.field_officer_id,
    )

    assert field_officer is not None

    assert field_officer.external_id == "test-user"