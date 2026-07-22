"""DriftAdapt Health API Test Suite.

Author: DriftAdapt Contributors
Purpose: Verifies GET /health endpoint payload, uptime tracking, and service container statuses.
Future Integration: Executed by pytest.
"""

def test_get_health_endpoint_success(api_test_client) -> None:
    """Verifies GET /health returns HTTP 200 OK and expected status fields."""
    response = api_test_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "project_name" in data
    assert "project_version" in data
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0.0
    assert "is_ready" in data
    assert "services" in data
    assert data["services"]["config_manager"] == "HEALTHY"
    assert data["services"]["model_manager"] == "HEALTHY"
