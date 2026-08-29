from fastapi.testclient import TestClient


def test_health_endpoint_returns_ok(
    client: TestClient,
) -> None:
    """
    Verify that the health endpoint is reachable and returns the
    expected response.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
    }