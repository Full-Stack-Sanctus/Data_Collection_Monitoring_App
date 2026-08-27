from copy import deepcopy
from typing import Any


def create_valid_submission(submission_uuid: str = "submission-uuid-123",
) -> dict[str, Any]:
    """
    Return a valid Kobo submission matching the structure of the
    deployed digital activity monitoring form.

    Each call returns a new dictionary so tests can safely modify
    the submission without affecting other tests.
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
        "_uuid": submission_uuid,
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


def create_invalid_gender_total_submission() -> dict[str, Any]:
    """
    Return a submission where male and female participant totals
    do not equal actual participants.
    """

    submission = create_valid_submission()

    submission[
        "participant_information/male_participants"
    ] = 80

    return submission


def create_invalid_age_total_submission() -> dict[str, Any]:
    """
    Return a submission where youth and adult participant totals
    do not equal actual participants.
    """

    submission = create_valid_submission()

    submission[
        "participant_information/youth_participants"
    ] = 80

    return submission


def create_invalid_achievement_submission() -> dict[str, Any]:
    """
    Return a submission with an incorrect participant
    achievement percentage.
    """

    submission = create_valid_submission()

    submission[
        "participant_information/"
        "participant_achievement_percentage"
    ] = 75

    return submission


def create_unconfirmed_submission() -> dict[str, Any]:
    """
    Return a submission that was not confirmed by the
    field officer.
    """

    submission = create_valid_submission()

    submission[
        "verification/confirm_information"
    ] = "no"

    return submission


def create_cancelled_submission() -> dict[str, Any]:
    """
    Return a cancelled activity without participant information.

    The transformation layer is expected to normalize participant
    values to zero for activities that were not completed.
    """

    submission = create_valid_submission()

    submission["_uuid"] = (
        "cancelled-submission-uuid"
    )

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

    return submission