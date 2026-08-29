import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.session import (
    SessionLocal,
    engine,
)
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Provide a FastAPI test client.

    The client exercises the application through the same HTTP
    interface used by real API consumers.
    """

    return TestClient(app)


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

    Application code may call session.commit() normally, but the
    outer transaction is rolled back after the test completes.
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

        transaction.rollback()

        connection.close()