from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.field_officer import FieldOfficer
from app.models.location import Location
from app.models.program import Program
from app.models.raw_submission import RawSubmission
from app.repositories.monitoring_repository import MonitoringRepository


def create_activity(
    session: Session,
    *,
    status: str,
    target_participants: int,
    actual_participants: int,
    male_participants: int,
    female_participants: int,
    youth_participants: int,
    adult_participants: int,
) -> Activity:
    """
    Create a complete Activity record with the required related
    database entities.

    A unique identifier is used so records created by separate tests
    cannot conflict with each other.
    """

    identifier = uuid4().hex

    program = Program(
        name=f"monitoring-program-{identifier}",
        is_active=True,
    )

    location = Location(
        state=f"monitoring-state-{identifier}",
        lga=f"monitoring-lga-{identifier}",
        community=f"monitoring-community-{identifier}",
        latitude=None,
        longitude=None,
    )

    field_officer = FieldOfficer(
        external_id=f"monitoring-officer-{identifier}",
        full_name="Monitoring Test Officer",
        is_active=True,
    )

    raw_submission = RawSubmission(
        source="integration-test",
        external_submission_id=(
            f"monitoring-submission-{identifier}"
        ),
        payload={},
        retrieved_at=datetime.now(timezone.utc),
        processing_status="processed",
    )

    session.add_all(
        [
            program,
            location,
            field_officer,
            raw_submission,
        ]
    )

    session.flush()

    activity = Activity(
        raw_submission_id=raw_submission.id,
        program_id=program.id,
        location_id=location.id,
        field_officer_id=field_officer.id,
        activity_type="training",
        activity_title="Monitoring Repository Test",
        activity_description=None,
        activity_date=date(2026, 8, 26),
        status=status,
        target_participants=target_participants,
        actual_participants=actual_participants,
        male_participants=male_participants,
        female_participants=female_participants,
        youth_participants=youth_participants,
        adult_participants=adult_participants,
        submitted_at=datetime.now(timezone.utc),
    )

    session.add(activity)
    session.commit()

    return activity


def test_returns_zero_totals_when_no_activities_exist(
    db_session: Session,
) -> None:
    """
    Verify that the monitoring repository returns zero-valued totals
    when the database contains no Activity records.
    """

    repository = MonitoringRepository()

    totals = repository.get_summary_totals(db_session)

    assert totals == {
        "total_activities": 0,
        "completed_activities": 0,
        "cancelled_activities": 0,
        "total_target_participants": 0,
        "total_actual_participants": 0,
        "total_male_participants": 0,
        "total_female_participants": 0,
        "total_youth_participants": 0,
        "total_adult_participants": 0,
    }


def test_aggregates_single_completed_activity(
    db_session: Session,
) -> None:
    """
    Verify that a completed activity contributes correctly to all
    monitoring totals.
    """

    create_activity(
        db_session,
        status="completed",
        target_participants=100,
        actual_participants=90,
        male_participants=50,
        female_participants=40,
        youth_participants=70,
        adult_participants=20,
    )

    repository = MonitoringRepository()

    totals = repository.get_summary_totals(db_session)

    assert totals["total_activities"] == 1
    assert totals["completed_activities"] == 1
    assert totals["cancelled_activities"] == 0

    assert totals["total_target_participants"] == 100
    assert totals["total_actual_participants"] == 90
    assert totals["total_male_participants"] == 50
    assert totals["total_female_participants"] == 40
    assert totals["total_youth_participants"] == 70
    assert totals["total_adult_participants"] == 20


def test_aggregates_multiple_activity_statuses(
    db_session: Session,
) -> None:
    """
    Verify that activity counts and participant totals are correctly
    aggregated across multiple activity records.
    """

    create_activity(
        db_session,
        status="completed",
        target_participants=100,
        actual_participants=90,
        male_participants=50,
        female_participants=40,
        youth_participants=60,
        adult_participants=30,
    )

    create_activity(
        db_session,
        status="completed",
        target_participants=200,
        actual_participants=180,
        male_participants=100,
        female_participants=80,
        youth_participants=120,
        adult_participants=60,
    )

    create_activity(
        db_session,
        status="cancelled",
        target_participants=50,
        actual_participants=0,
        male_participants=0,
        female_participants=0,
        youth_participants=0,
        adult_participants=0,
    )

    repository = MonitoringRepository()

    totals = repository.get_summary_totals(db_session)

    assert totals["total_activities"] == 3
    assert totals["completed_activities"] == 2
    assert totals["cancelled_activities"] == 1

    assert totals["total_target_participants"] == 350
    assert totals["total_actual_participants"] == 270
    assert totals["total_male_participants"] == 150
    assert totals["total_female_participants"] == 120
    assert totals["total_youth_participants"] == 180
    assert totals["total_adult_participants"] == 90


def test_cancelled_activity_is_included_in_total_count(
    db_session: Session,
) -> None:
    """
    Verify that a cancelled activity is included in the total activity
    count while participant values remain correctly aggregated.
    """

    create_activity(
        db_session,
        status="cancelled",
        target_participants=0,
        actual_participants=0,
        male_participants=0,
        female_participants=0,
        youth_participants=0,
        adult_participants=0,
    )

    repository = MonitoringRepository()

    totals = repository.get_summary_totals(db_session)

    assert totals["total_activities"] == 1
    assert totals["completed_activities"] == 0
    assert totals["cancelled_activities"] == 1
    assert totals["total_target_participants"] == 0
    assert totals["total_actual_participants"] == 0