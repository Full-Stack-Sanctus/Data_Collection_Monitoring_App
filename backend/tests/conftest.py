import pytest

import time

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, engine
from app.main import app

# Import your actual schemas and dependencies
from app.api.dependencies.auth import require_api_key
from app.security.dependencies import get_current_principal
from app.schemas.auth import TokenPayload  # Imported to serve as mock contract



@pytest.fixture(autouse=True)
def bypass_security_dependencies():
    """
    Globally mock out all authentication and authorization blocks.
    
    Returns a valid TokenPayload instance to satisfy inner role-checking 
    closures that expect dot-notation property attributes.
    """
    # 1. Bypass explicit, static API Key dependencies
    app.dependency_overrides[require_api_key] = lambda: None
    
    # 2. Return a valid Pydantic TokenPayload instance with 'admin' role privileges
    # This guarantees principal.role returns "admin" and satisfies your allowed_roles check!
    mock_payload = TokenPayload(
        sub="ci-test-user-id",
        email="test@example.com",
        role="admin",
        exp=int(time.time()) + 3600  # Sets token expiration to 1 hour in the future
    )
    app.dependency_overrides[get_current_principal] = lambda: mock_payload

    yield

    # Clean up and reset overrides cleanly after each test finishes to prevent test bleeding
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """
    Provide a FastAPI test client.
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
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
