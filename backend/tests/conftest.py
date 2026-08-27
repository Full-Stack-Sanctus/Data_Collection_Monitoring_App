import pytest
from sqlalchemy.orm import Session

from app.database.session import SessionLocal


@pytest.fixture
def sample_submission_id() -> str:
    """
    Provide a reusable sample external submission identifier.
    """

    return "submission-uuid-123"


@pytest.fixture
def db_session() -> Session:
    """
    Provide a real PostgreSQL database session for integration tests.

    Each test receives a fresh session. The session is closed after
    the test completes.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()