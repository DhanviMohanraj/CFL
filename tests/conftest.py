"""DriftAdapt Root Pytest Configuration and Global Fixtures.

Author: DriftAdapt Contributors
Purpose: Provides global pytest setup, mock patches, and test environment isolation.
Future Integration: Loaded automatically by pytest for all tests in tests/.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.container import ServiceContainer
from app.core.config import ConfigManager
from app.main import app
from tests.fixtures.mock_models import (
    create_mock_foundation_model,
    create_mock_metadata,
    create_mock_tokenizer,
)


@pytest.fixture
def mock_dependencies():
    """Patches DependencyChecker to report all core software dependencies as verified."""
    with patch("app.core.runtime.dependency_checker.DependencyChecker.verify_dependencies", return_value=(True, [], {})):
        yield


@pytest.fixture
def mock_foundation_factory():
    """Patches ModelFactory to return mock models and tokenizers for fast test execution."""
    dummy_model = create_mock_foundation_model()
    dummy_tokenizer = create_mock_tokenizer()
    dummy_meta = create_mock_metadata()

    with patch("app.models.foundation.model_manager.ModelFactory") as MockFactoryCls:
        mock_factory_instance = MockFactoryCls.return_value
        mock_factory_instance.create_model_and_tokenizer.return_value = (
            dummy_model,
            dummy_tokenizer,
            dummy_meta,
        )
        yield mock_factory_instance


@pytest.fixture
def clean_config():
    """Provides a fresh ConfigManager instance and ensures overrides are cleared after test completion."""
    mgr = ConfigManager()
    mgr.clear_overrides()
    mgr.refresh()
    yield mgr
    mgr.clear_overrides()
    mgr.refresh()


@pytest.fixture
def api_test_client(mock_dependencies, mock_foundation_factory):
    """Provides FastAPI TestClient instance with mocked runtime dependencies and foundation model factory."""
    container = ServiceContainer()
    container.mark_ready(True)
    with TestClient(app) as client:
        yield client
