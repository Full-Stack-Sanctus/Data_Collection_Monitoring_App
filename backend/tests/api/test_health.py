# Fixed version of tests/api/test_health.py
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.config import settings


def test_liveness_check_endpoint(client: TestClient) -> None:
    """
    Verify that the liveness check endpoint returns a 200 OK status code.
    """
    # Changed from "/api/v1/health/live" to "/health/live"
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.api.routes.health.check_database_connection")
def test_readiness_check_healthy(
    mock_check_db: patch, client: TestClient
) -> None:
    """
    Verify that the readiness check endpoint reports a healthy status.
    """
    mock_check_db.return_value = True

    # Changed from "/api/v1/health/ready" to "/health/ready"
    response = client.get("/health/ready")

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
    Verify that the readiness check endpoint reports a degraded status.
    """
    mock_check_db.return_value = False

    # Changed from "/api/v1/health/ready" to "/health/ready"
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "environment": settings.app_env,
        "database": "disconnected",
    }
