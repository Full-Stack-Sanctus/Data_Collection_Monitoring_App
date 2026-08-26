from app.kobo.transformer import transform_submission


def test_transform_real_kobo_submission() -> None:
    """
    Test the transformer against the actual structure returned
    by the deployed Kobo form.
    """

    raw_submission = {
        "_id": 849271796,
        "formhub/uuid": "3ceab6c885154efcabd8df36d9fa3de2",
        "start_time": "2026-08-25T14:19:47.231+01:00",
        "end_time": "2026-08-25T14:23:15.272+01:00",
        "submission_date": "2026-08-25",
        "device_id": (
            "ee.kobotoolbox.org:tj2OrVQAq2og5ALz"
        ),
        "username": "username not found",
        "instance_id": (
            "uuid:f4f8a2df-af7b-4ff2-971c-efb0de8aa652"
        ),
        "program_information/program": "digital_skills",
        "program_information/program_code": "digital_skills",
        "program_information/reporting_period": "q3",
        "activity_information/activity_type": "training",
        "activity_information/activity_title": (
            "Introduction to Digital Skills"
        ),
        "activity_information/activity_description": (
            "A practical introductory training session "
            "on digital literacy skills."
        ),
        "activity_information/activity_date": "2026-08-25",
        "activity_information/activity_status": "completed",
        "activity_information/target_participants": 90,
        "location_information/state": "rivers",
        "location_information/lga": "Port Harcourt",
        "location_information/community": "Orogbum",
        "location_information/gps_location": (
            "7.70737 8.525931 0 500"
        ),
        "participant_information/actual_participants": 90,
        "participant_information/male_participants": 50,
        "participant_information/female_participants": 40,
        "participant_information/youth_participants": 80,
        "participant_information/adult_participants": 10,
        "participant_information/"
        "participant_achievement_percentage": 100,
        "verification/confirm_information": "yes",
        "_xform_id_string": "aiuBWRQmYHE2UGdEvu645y",
        "_submission_time": "2026-08-25T13:23:16",
        "_validation_status": {},
        "_submitted_by": None,
        "_status": "submitted_via_web",
        "_uuid": (
            "508a246f-8d43-4d66-a7ed-815d50f9a61d"
        ),
    }

    submission = transform_submission(
        raw_submission
    )

    assert submission.kobo_submission_id == 849271796

    assert (
        submission.kobo_uuid
        == "508a246f-8d43-4d66-a7ed-815d50f9a61d"
    )

    assert (
        submission.program_data.program
        == "digital_skills"
    )

    assert (
        submission.activity_data.activity_type
        == "training"
    )

    assert (
        submission.activity_data.target_participants
        == 90
    )

    assert (
        submission.participant_data.actual_participants
        == 90
    )

    assert (
        submission.participant_data.male_participants
        == 50
    )

    assert (
        submission.participant_data.female_participants
        == 40
    )

    assert (
        submission.participant_data.youth_participants
        == 80
    )

    assert (
        submission.participant_data.adult_participants
        == 10
    )

    assert (
        submission.participant_data
        .participant_achievement_percentage
        == 100
    )

    assert (
        submission.location_data
        .gps_location
        .latitude
        == 7.70737
    )

    assert (
        submission.location_data
        .gps_location
        .longitude
        == 8.525931
    )