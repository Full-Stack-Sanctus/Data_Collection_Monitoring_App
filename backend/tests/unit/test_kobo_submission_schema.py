import pytest

from app.kobo.transformer import transform_submission
from tests.fixtures.kobo_submissions import (
    create_invalid_age_total_submission,
    create_invalid_achievement_submission,
    create_invalid_gender_total_submission,
    create_unconfirmed_submission,
    create_valid_submission,
)


def test_valid_submission_passes_business_rules() -> None:
    """
    A valid submission should successfully pass all business rules.
    """

    submission = transform_submission(
        create_valid_submission()
    )

    submission.validate_business_rules()


def test_rejects_invalid_gender_totals() -> None:
    """
    Male and female participant totals must equal the total number
    of actual participants.
    """

    submission = transform_submission(
        create_invalid_gender_total_submission()
    )

    with pytest.raises(
        ValueError,
        match=(
            "Male and female participants must equal "
            "actual participants"
        ),
    ):
        submission.validate_business_rules()


def test_rejects_invalid_age_totals() -> None:
    """
    Youth and adult participant totals must equal actual participants.
    """

    submission = transform_submission(
        create_invalid_age_total_submission()
    )

    with pytest.raises(
        ValueError,
        match=(
            "Youth and adult participants must equal "
            "actual participants"
        ),
    ):
        submission.validate_business_rules()


def test_rejects_invalid_achievement_percentage() -> None:
    """
    The reported achievement percentage must match the calculated
    value from actual and target participants.
    """

    submission = transform_submission(
        create_invalid_achievement_submission()
    )

    with pytest.raises(
        ValueError,
        match=(
            "Participant achievement percentage does not "
            "match target and actual participants"
        ),
    ):
        submission.validate_business_rules()


def test_rejects_unconfirmed_submission() -> None:
    """
    A Kobo submission must be explicitly confirmed before it is
    accepted into the monitoring system.
    """

    with pytest.raises(ValueError):
        transform_submission(
            create_unconfirmed_submission()
        )