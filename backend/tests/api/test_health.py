from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.config import settings


def test_liveness_check_endpoint(client: TestClient) -> None:
    """
    Verify that the liveness check endpoint returns a 200 OK status code
    and confirms the API instance is up and running.
    """
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.api.routes.health.check_database_connection")
def test_readiness_check_healthy(
    mock_check_db: patch, client: TestClient
) -> None:
    """
    Verify that the readiness check endpoint reports a healthy status
    when the database connection is functional.
    """
    # Force the database check to return True
    mock_check_db.return_value = True

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "environment": settings.app_env,
        "database": "connected",
    }


@patch("app.api.routes.health.check_database_connection")
def test_readiness_check_degraded(
    mock_check_db: patch, client: TestClient
) -> None:
    """
    Verify that the readiness check endpoint reports a degraded status
    when the database connection fails.
    """
    # Force the database check to return False
    mock_check_db.return_value = False

    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "environment": settings.app_env,
        "database": "disconnected",
    }
