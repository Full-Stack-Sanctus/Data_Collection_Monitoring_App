from datetime import date, datetime
from typing import Any

from app.schemas.kobo_submission import (
    KoboActivityData,
    KoboGPS,
    KoboLocationData,
    KoboParticipantData,
    KoboProgramData,
    KoboSubmission,
    KoboVerificationData,
)


class KoboTransformationError(Exception):
    """
    Raised when a raw Kobo submission cannot be transformed
    into the internal application model.
    """

    pass


def get_required(
    data: dict[str, Any],
    key: str,
) -> Any:
    """
    Retrieve a required value from a Kobo submission.
    """

    value = data.get(key)

    if value is None:
        raise KoboTransformationError(
            f"Required Kobo field is missing: {key}"
        )

    if isinstance(value, str) and not value.strip():
        raise KoboTransformationError(
            f"Required Kobo field is empty: {key}"
        )

    return value


def get_optional(
    data: dict[str, Any],
    key: str,
) -> Any:
    """
    Retrieve an optional Kobo field.
    """

    value = data.get(key)

    if value in ("", "NaN", "nan"):
        return None

    return value


def parse_datetime(
    value: str | None,
) -> datetime | None:
    """
    Convert Kobo ISO datetime strings into Python datetime objects.
    """

    if value is None:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def parse_date(
    value: str,
) -> date:
    """
    Convert a Kobo date into a Python date.
    """

    return date.fromisoformat(value)


def parse_int(
    value: Any,
) -> int:
    """
    Safely convert a Kobo numeric value to int.
    """

    try:
        return int(value)

    except (TypeError, ValueError) as error:
        raise KoboTransformationError(
            f"Expected integer-compatible value, got: {value!r}"
        ) from error


def parse_float(
    value: Any,
) -> float:
    """
    Safely convert a Kobo numeric value to float.
    """

    try:
        return float(value)

    except (TypeError, ValueError) as error:
        raise KoboTransformationError(
            f"Expected numeric value, got: {value!r}"
        ) from error


def parse_gps(
    value: str,
) -> KoboGPS:
    """
    Parse a Kobo geopoint.

    Expected format:

        latitude longitude altitude accuracy
    """

    parts = value.split()

    if len(parts) < 2:
        raise KoboTransformationError(
            f"Invalid Kobo geopoint: {value!r}"
        )

    latitude = parse_float(parts[0])
    longitude = parse_float(parts[1])

    altitude = (
        parse_float(parts[2])
        if len(parts) >= 3
        else None
    )

    accuracy = (
        parse_float(parts[3])
        if len(parts) >= 4
        else None
    )

    if not -90 <= latitude <= 90:
        raise KoboTransformationError(
            f"Invalid latitude: {latitude}"
        )

    if not -180 <= longitude <= 180:
        raise KoboTransformationError(
            f"Invalid longitude: {longitude}"
        )

    return KoboGPS(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        accuracy=accuracy,
    )


def transform_submission(
    raw: dict[str, Any],
) -> KoboSubmission:
    """
    Transform one raw Kobo API submission into our
    validated internal representation.
    """

    try:
        program_data = KoboProgramData(
            program=get_required(
                raw,
                "program_information/program",
            ),
            program_code=get_optional(
                raw,
                "program_information/program_code",
            ),
            reporting_period=get_required(
                raw,
                "program_information/reporting_period",
            ),
        )

        activity_data = KoboActivityData(
            activity_type=get_required(
                raw,
                "activity_information/activity_type",
            ),
            activity_type_other=get_optional(
                raw,
                "activity_information/activity_type_other",
            ),
            activity_title=get_required(
                raw,
                "activity_information/activity_title",
            ),
            activity_description=get_optional(
                raw,
                "activity_information/activity_description",
            ),
            activity_date=parse_date(
                get_required(
                    raw,
                    "activity_information/activity_date",
                )
            ),
            activity_status=get_required(
                raw,
                "activity_information/activity_status",
            ),
            target_participants=parse_int(
                get_required(
                    raw,
                    "activity_information/target_participants",
                )
            ),
        )

        location_data = KoboLocationData(
            state=get_required(
                raw,
                "location_information/state",
            ),
            lga=get_required(
                raw,
                "location_information/lga",
            ),
            community=get_required(
                raw,
                "location_information/community",
            ),
            gps_location=parse_gps(
                get_required(
                    raw,
                    "location_information/gps_location",
                )
            ),
        )

        activity_status = activity_data.activity_status

        if activity_status == "completed":
            participant_data = KoboParticipantData(
                actual_participants=parse_int(
                    get_required(
                        raw,
                        "participant_information/"
                        "actual_participants",
                    )
                ),
                male_participants=parse_int(
                    get_required(
                        raw,
                        "participant_information/"
                        "male_participants",
                    )
                ),
                female_participants=parse_int(
                    get_required(
                        raw,
                        "participant_information/"
                        "female_participants",
                    )
                ),
                youth_participants=parse_int(
                    get_required(
                        raw,
                        "participant_information/"
                        "youth_participants",
                    )
                ),
                adult_participants=parse_int(
                    get_required(
                        raw,
                        "participant_information/"
                        "adult_participants",
                    )
                ),
                participant_achievement_percentage=parse_float(
                    get_required(
                        raw,
                        "participant_information/"
                        "participant_achievement_percentage",
                    )
                ),
            )

        else:
            participant_data = KoboParticipantData(
                actual_participants=0,
                male_participants=0,
                female_participants=0,
                youth_participants=0,
                adult_participants=0,
                participant_achievement_percentage=0,
        )
            

        verification_data = KoboVerificationData(
            confirm_information=get_required(
                raw,
                "verification/confirm_information",
            )
        )

        submission = KoboSubmission(
            kobo_submission_id=parse_int(
                get_required(
                    raw,
                    "_id",
                )
            ),
            kobo_uuid=get_required(
                raw,
                "_uuid",
            ),
            instance_id=get_required(
                raw,
                "instance_id",
            ),
            formhub_uuid=get_required(
                raw,
                "formhub/uuid",
            ),
            xform_id=get_required(
                raw,
                "_xform_id_string",
            ),
            start_time=parse_datetime(
                get_required(
                    raw,
                    "start_time",
                )
            ),
            end_time=parse_datetime(
                get_required(
                    raw,
                    "end_time",
                )
            ),
            submission_date=parse_date(
                get_required(
                    raw,
                    "submission_date",
                )
            ),
            device_id=get_optional(
                raw,
                "device_id",
            ),
            username=get_optional(
                raw,
                "username",
            ),
            submission_time=parse_datetime(
                get_optional(
                    raw,
                    "_submission_time",
                )
            ),
            validation_status=raw.get(
                "_validation_status",
                {},
            ),
            submitted_by=get_optional(
                raw,
                "_submitted_by",
            ),
            submission_status=get_optional(
                raw,
                "_status",
            ),
            program_data=program_data,
            activity_data=activity_data,
            location_data=location_data,
            participant_data=participant_data,
            verification_data=verification_data,
        )

        submission.validate_business_rules()

        return submission

    except KoboTransformationError:
        raise

    except Exception as error:
        raise KoboTransformationError(
            "Failed to transform Kobo submission: "
            f"{error}"
        ) from error