"""DriftAdapt Readiness API Test Suite.

Author: DriftAdapt Contributors
Purpose: Verifies GET /ready endpoint HTTP 200 OK (READY) and HTTP 503 (NOT_READY) responses.
Future Integration: Executed by pytest.
"""

from app.container import ServiceContainer


def test_get_ready_endpoint_states(api_test_client) -> None:
    """Verifies GET /ready responds with 200 when ready and 503 when unready."""
    container = ServiceContainer()

    # 1. Test ready state (HTTP 200)
    container.mark_ready(True)
    res_ready = api_test_client.get("/ready")
    assert res_ready.status_code == 200
    data_ready = res_ready.json()
    assert data_ready["status"] == "READY"
    assert "uptime_seconds" in data_ready

    # 2. Test unready state (HTTP 503)
    container.mark_ready(False)
    res_unready = api_test_client.get("/ready")
    assert res_unready.status_code == 503
    data_unready = res_unready.json()
    assert data_unready["status"] == "NOT_READY"

    # Reset container state
    container.mark_ready(True)
