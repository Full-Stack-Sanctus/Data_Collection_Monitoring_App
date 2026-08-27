import pytest
from sqlalchemy.orm import Session

from app.database.session import (
    SessionLocal,
    engine,
)


@pytest.fixture
def sample_submission_id() -> str:
    """
    Provide a reusable sample external submission identifier.
    """

    return "submission-uuid-123"


@pytest.fixture
def db_session() -> Session:
    """
    Provide an isolated PostgreSQL session for integration tests.

    Each test runs inside an outer database transaction.

    The application code can call session.commit() normally, while
    the outer transaction is rolled back after the test completes.

    This prevents integration tests from permanently modifying the
    development database.
    """

    connection = engine.connect()

    transaction = connection.begin()

    session = SessionLocal(
        bind=connection,
    )

    try:
        yield session

    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()