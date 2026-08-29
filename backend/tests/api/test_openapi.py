from fastapi.testclient import TestClient


def test_monitoring_routes_are_documented(
    client: TestClient,
) -> None:
    """
    Verify that the monitoring API routes are registered in the
    generated OpenAPI specification.
    """

    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    paths = schema["paths"]

    assert (
        "/api/v1/monitoring/summary"
        in paths
    )

    assert (
        "/api/v1/monitoring/programs"
        in paths
    )

    assert (
        "/api/v1/monitoring/geography"
        in paths
    )

    assert (
        "/api/v1/monitoring/data-quality"
        in paths
    )

    assert (
        "/api/v1/monitoring/data-quality/issues"
        in paths
    )