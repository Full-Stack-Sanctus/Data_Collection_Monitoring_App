from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KoboGPS(BaseModel):
    """
    Normalized representation of a Kobo geopoint.

    Kobo returns geopoints as:

        latitude longitude altitude accuracy
    """

    latitude: float
    longitude: float
    altitude: float | None = None
    accuracy: float | None = None


class KoboProgramData(BaseModel):
    """
    Program-related fields from the Kobo submission.
    """

    program: str
    program_code: str | None = None
    reporting_period: str


class KoboActivityData(BaseModel):
    """
    Activity-related fields from the Kobo submission.
    """

    activity_type: str
    activity_type_other: str | None = None
    activity_title: str
    activity_description: str | None = None
    activity_date: date
    activity_status: str
    target_participants: int = Field(ge=0)


class KoboLocationData(BaseModel):
    """
    Location information collected by the field officer.
    """

    state: str
    lga: str
    community: str
    gps_location: KoboGPS


class KoboParticipantData(BaseModel):
    """
    Participant statistics collected for completed activities.
    """

    actual_participants: int = Field(ge=0)
    male_participants: int = Field(ge=0)
    female_participants: int = Field(ge=0)
    youth_participants: int = Field(ge=0)
    adult_participants: int = Field(ge=0)
    participant_achievement_percentage: float = Field(ge=0)

    def validate_totals(self) -> None:
        """
        Validate demographic totals against actual participants.
        """

        if (
            self.male_participants
            + self.female_participants
            != self.actual_participants
        ):
            raise ValueError(
                "Male and female participants must equal "
                "actual participants."
            )

        if (
            self.youth_participants
            + self.adult_participants
            != self.actual_participants
        ):
            raise ValueError(
                "Youth and adult participants must equal "
                "actual participants."
            )


class KoboVerificationData(BaseModel):
    """
    Final form verification response.
    """

    confirm_information: str

    @field_validator("confirm_information")
    @classmethod
    def confirmation_must_be_yes(cls, value: str) -> str:
        if value != "yes":
            raise ValueError(
                "Kobo submission was not confirmed by the respondent."
            )

        return value


class KoboSubmission(BaseModel):
    """
    Internal representation of one KoboToolbox submission.

    This model deliberately separates:
    - Kobo metadata
    - program information
    - activity information
    - location
    - participants
    - verification

    The raw Kobo submission remains available separately and is
    never discarded.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # Kobo identifiers

    kobo_submission_id: int

    kobo_uuid: str

    instance_id: str

    formhub_uuid: str

    xform_id: str

    # Submission metadata

    start_time: datetime
    end_time: datetime
    submission_date: date

    device_id: str | None = None
    username: str | None = None

    submission_time: datetime | None = None
    validation_status: dict[str, Any] = Field(
        default_factory=dict
    )

    submitted_by: str | None = None

    submission_status: str | None = None

    # Business data

    program_data: KoboProgramData
    activity_data: KoboActivityData
    location_data: KoboLocationData
    participant_data: KoboParticipantData
    verification_data: KoboVerificationData

    def validate_business_rules(self) -> None:
        """
        Validate cross-field business rules that involve
        multiple sections of the submission.
        """

        self.participant_data.validate_totals()

        target = self.activity_data.target_participants
        actual = self.participant_data.actual_participants

        if target > 0:
            expected_percentage = (
                actual / target
            ) * 100
        else:
            expected_percentage = 0

        actual_percentage = (
            self.participant_data
            .participant_achievement_percentage
        )

        if abs(
            actual_percentage - expected_percentage
        ) > 0.01:
            raise ValueError(
                "Participant achievement percentage does not "
                "match target and actual participants."
            )