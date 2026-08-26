import pytest


@pytest.fixture
def sample_submission_id() -> str:
    """
    Provide a reusable sample external submission identifier.
    """

    return "submission-uuid-123"