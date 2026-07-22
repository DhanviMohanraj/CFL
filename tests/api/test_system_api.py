"""DriftAdapt System API Test Suite.

Author: DriftAdapt Contributors
Purpose: Verifies GET /system endpoint hardware, OS, CPU, GPU, RAM, VRAM, and execution device specs.
Future Integration: Executed by pytest.
"""

def test_get_system_endpoint(api_test_client) -> None:
    """Verifies GET /system returns runtime environment report."""
    response = api_test_client.get("/system")
    assert response.status_code == 200

    data = response.json()
    assert "environment" in data
    assert "hardware" in data
    assert "execution" in data
    assert "platform" in data["environment"]
    assert "python_version" in data["environment"]
    assert "cpu" in data["hardware"]
    assert "memory" in data["hardware"]
    assert "device" in data["execution"]
