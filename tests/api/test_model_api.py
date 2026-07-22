"""DriftAdapt Model API Test Suite.

Author: DriftAdapt Contributors
Purpose: Verifies GET /model endpoint foundation model metadata payload.
Future Integration: Executed by pytest.
"""

def test_get_model_endpoint(api_test_client) -> None:
    """Verifies GET /model returns foundation model metadata specifications."""
    response = api_test_client.get("/model")
    assert response.status_code == 200

    data = response.json()
    assert "model_name" in data
    assert "architecture" in data
    assert "parameter_count" in data
    assert "trainable_parameters" in data
    assert "quantization_mode" in data
    assert "precision" in data
    assert "memory_footprint_mb" in data
    assert data["is_frozen"] is True
