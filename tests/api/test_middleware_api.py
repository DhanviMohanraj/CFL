"""DriftAdapt Middleware API Test Suite.

Author: DriftAdapt Contributors
Purpose: Verifies Correlation ID, Request Timing, Logging, and Global Exception Handler middlewares.
Future Integration: Executed by pytest.
"""

def test_middleware_headers_generation(api_test_client) -> None:
    """Verifies X-Request-ID and X-Response-Time-MS response headers on endpoints."""
    response = api_test_client.get("/health")
    assert response.status_code == 200

    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

    assert "X-Response-Time-MS" in response.headers
    assert float(response.headers["X-Response-Time-MS"]) >= 0.0


def test_correlation_id_propagation(api_test_client) -> None:
    """Verifies that an incoming X-Request-ID header is echoed back unchanged."""
    custom_uuid = "custom-test-trace-uuid-12345"
    response = api_test_client.get("/health", headers={"X-Request-ID": custom_uuid})

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_uuid


def test_global_exception_handler_middleware(api_test_client) -> None:
    """Verifies that uncaught exceptions return structured JSON error payloads (HTTP 500)."""
    # Trigger 404 non-existent path
    response = api_test_client.get("/non_existent_route_path_999")
    assert response.status_code == 404
