"""DriftAdapt FastAPI API Integration Tests.

Author: DriftAdapt Contributors
Purpose: Verifies health, readiness, system, and model API endpoints, middlewares, lifespan, and dependency injection.
Future Integration: Executed in CI pipeline.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.container import ServiceContainer
from app.core.config import ConfigManager
from app.main import app
from app.models.foundation.model_metadata import ModelMetadata


@pytest.fixture
def setup_api_test_environment():
    """Autouse fixture mocking dependency checker and foundation model factory for fast API tests."""
    dummy_model = MagicMock()
    dummy_tokenizer = MagicMock()
    dummy_tokenizer.vocab_size = 1000

    dummy_meta = ModelMetadata(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        architecture="Qwen2ForCausalLM",
        parameter_count=3090000000,
        trainable_parameters=0,
        tokenizer_name="Qwen/Qwen2.5-3B-Instruct",
        vocab_size=151936,
        context_length=32768,
        hidden_size=2048,
        quantization_mode="4bit",
        precision="bfloat16",
        device="cpu",
        memory_footprint_mb=1800.5,
        load_time_seconds=0.1,
        disk_size_mb=1800.5,
        is_frozen=True,
    )

    with patch("app.core.runtime.dependency_checker.DependencyChecker.verify_dependencies", return_value=(True, [], {})), \
         patch("app.models.foundation.model_manager.ModelFactory") as MockFactoryCls:
        mock_factory_instance = MockFactoryCls.return_value
        mock_factory_instance.create_model_and_tokenizer.return_value = (
            dummy_model,
            dummy_tokenizer,
            dummy_meta,
        )
        yield mock_factory_instance


def test_health_endpoint(setup_api_test_environment) -> None:
    """Verifies GET /health endpoint returns HTTP 200 OK and system status details."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "HEALTHY"
        assert "project_name" in data
        assert "project_version" in data
        assert "uptime_seconds" in data
        assert "services" in data
        assert data["services"]["config_manager"] == "HEALTHY"


def test_readiness_endpoint(setup_api_test_environment) -> None:
    """Verifies GET /ready endpoint returns 503 when unready and 200 OK when startup finishes."""
    container = ServiceContainer()

    with TestClient(app) as client:
        # 1. Simulate unready state
        container.mark_ready(False)
        res_unready = client.get("/ready")
        assert res_unready.status_code == 503
        assert res_unready.json()["status"] == "NOT_READY"

        # 2. Simulate ready state
        container.mark_ready(True)
        res_ready = client.get("/ready")
        assert res_ready.status_code == 200
        assert res_ready.json()["status"] == "READY"


def test_system_endpoint(setup_api_test_environment) -> None:
    """Verifies GET /system endpoint returns HTTP 200 OK and environment/hardware details."""
    with TestClient(app) as client:
        response = client.get("/system")
        assert response.status_code == 200
        data = response.json()

        assert "environment" in data
        assert "hardware" in data
        assert "execution" in data
        assert "os" in data["environment"]
        assert "python_version" in data["environment"]


def test_model_endpoint(setup_api_test_environment) -> None:
    """Verifies GET /model endpoint returns HTTP 200 OK and foundation model metadata."""
    with TestClient(app) as client:
        response = client.get("/model")
        assert response.status_code == 200
        data = response.json()

        assert data["model_name"] == "Qwen/Qwen2.5-3B-Instruct"
        assert data["architecture"] == "Qwen2ForCausalLM"
        assert data["quantization_mode"] == "4bit"
        assert data["is_frozen"] is True


def test_middlewares_headers(setup_api_test_environment) -> None:
    """Verifies CorrelationID (X-Request-ID) and RequestTiming (X-Response-Time-MS) middleware headers."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

        assert "X-Response-Time-MS" in response.headers
        assert float(response.headers["X-Response-Time-MS"]) >= 0.0


def test_custom_correlation_id_propagation(setup_api_test_environment) -> None:
    """Verifies that an incoming X-Request-ID header is preserved and echoed back."""
    custom_req_id = "test-correlation-uuid-999"
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": custom_req_id})
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == custom_req_id


def test_service_container_singletons() -> None:
    """Verifies that ServiceContainer returns consistent singletons."""
    container = ServiceContainer()

    cfg1 = container.config_manager()
    cfg2 = container.config_manager()
    assert cfg1 is cfg2

    bus1 = container.metrics_bus()
    bus2 = container.metrics_bus()
    assert bus1 is bus2

    dev1 = container.device_manager()
    dev2 = container.device_manager()
    assert dev1 is dev2
