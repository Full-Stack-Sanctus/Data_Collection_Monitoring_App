from app.pipeline.validation import (
    SubmissionValidationService,
)


def create_valid_submission() -> dict:
    """
    Return a valid Kobo submission using the real field structure
    of the deployed form.
    """

    return {
        "_id": 1,
        "formhub/uuid": "form-uuid",
        "start_time": (
            "2026-08-25T14:19:47+01:00"
        ),
        "end_time": (
            "2026-08-25T14:23:15+01:00"
        ),
        "submission_date": "2026-08-25",
        "device_id": "device-123",
        "username": "test-user",
        "instance_id": "uuid:instance-123",
        "_uuid": "submission-uuid-123",
        "_xform_id_string": "form-id-123",
        "_submission_time": (
            "2026-08-25T13:23:16"
        ),
        "_validation_status": {},
        "_submitted_by": None,
        "_status": "submitted_via_web",

        "program_information/program": (
            "digital_skills"
        ),
        "program_information/program_code": (
            "digital_skills"
        ),
        "program_information/reporting_period": (
            "q3"
        ),

        "activity_information/activity_type": (
            "training"
        ),
        "activity_information/activity_title": (
            "Python Training"
        ),
        "activity_information/activity_date": (
            "2026-08-25"
        ),
        "activity_information/activity_status": (
            "completed"
        ),
        "activity_information/target_participants": 100,

        "location_information/state": "rivers",
        "location_information/lga": (
            "Port Harcourt"
        ),
        "location_information/community": (
            "Orogbum"
        ),
        "location_information/gps_location": (
            "7.70737 8.525931 0 50"
        ),

        "participant_information/actual_participants": 90,
        "participant_information/male_participants": 50,
        "participant_information/female_participants": 40,
        "participant_information/youth_participants": 70,
        "participant_information/adult_participants": 20,
        "participant_information/"
        "participant_achievement_percentage": 90,

        "verification/confirm_information": "yes",
    }


def test_accepts_valid_submission() -> None:
    """
    A valid submission should be accepted.
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

    submission = create_valid_submission()

    submission[
        "participant_information/male_participants"
    ] = 80

    service = SubmissionValidationService()

    result = service.process(
        [submission]
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

    invalid_submission = create_valid_submission()

    invalid_submission["_uuid"] = (
        "invalid-submission"
    )

    invalid_submission[
        "participant_information/"
        "actual_participants"
    ] = 100

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
    Cancelled activities should not require participant fields.

    The transformation layer normalizes participant statistics
    to zero for activities that were not completed.
    """

    submission = create_valid_submission()

    submission["_uuid"] = "cancelled-activity"

    submission[
        "activity_information/activity_status"
    ] = "cancelled"

    participant_fields = [
        "participant_information/actual_participants",
        "participant_information/male_participants",
        "participant_information/female_participants",
        "participant_information/youth_participants",
        "participant_information/adult_participants",
        "participant_information/"
        "participant_achievement_percentage",
    ]

    for field in participant_fields:
        submission.pop(field)

    service = SubmissionValidationService()

    result = service.process(
        [submission]
    )

    assert result.accepted_count == 1

    accepted = result.accepted_records[0]

    assert (
        accepted.submission.actual_participants == 0
    )

    assert (
        accepted.submission.male_participants
        == 0
    )

    assert (
        accepted.submission.female_participants
        == 0
    )