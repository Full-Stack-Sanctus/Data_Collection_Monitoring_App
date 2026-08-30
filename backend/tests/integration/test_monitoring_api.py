from fastapi.testclient import TestClient

from app.api.dependencies.database import get_db
from app.main import app


def test_monitoring_summary_api_uses_database(
    client: TestClient,
    db_session,
) -> None:
    """
    Verify the complete monitoring request path against PostgreSQL.

    The API uses the real MonitoringService and repository while
    the test database transaction is rolled back after completion.
    """

    app.dependency_overrides[
        get_db
    ] = lambda: db_session

    try:
        response = client.get(
            "/api/v1/monitoring/summary"
        )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    payload = response.json()

    assert "total_activities" in payload

    assert "completed_activities" in payload

    assert "total_target_participants" in payload

    assert "total_actual_participants" in payload

    assert (
        "participant_achievement_percentage"
        in payload
    )