"""Unit Tests for Module 2.8 Validation Engine.

Author: DriftAdapt Contributors
"""

import pytest
from unittest.mock import MagicMock

from app.schemas.validation_request import ValidationRequest
from app.schemas.benchmark_request import BenchmarkRequest
from app.services.validation.validation_engine import ValidationEngine
from app.services.validation.benchmark_engine import BenchmarkEngine
from app.schemas.integrity_report import IntegrityReport


@pytest.fixture
def mock_integrity():
    val = MagicMock()
    val.check_integrity.return_value = (True, IntegrityReport())
    return val

@pytest.fixture
def mock_adapter_validator():
    val = MagicMock()
    val.validate_loaded_adapter.return_value = (True, "OK")
    return val

@pytest.fixture
def mock_inference_validator():
    val = MagicMock()
    val.validate_inference_pipeline.return_value = (True, "OK")
    return val

@pytest.fixture
def mock_metrics():
    val = MagicMock()
    return val

@pytest.fixture
def mock_history():
    val = MagicMock()
    return val

@pytest.fixture
def mock_registry():
    val = MagicMock()
    val.is_validation_running.return_value = False
    val.is_benchmark_running.return_value = False
    return val

@pytest.fixture
def validation_engine(
    mock_integrity,
    mock_adapter_validator,
    mock_inference_validator,
    mock_metrics,
    mock_history,
    mock_registry
):
    return ValidationEngine(
        integrity_checker=mock_integrity,
        adapter_validator=mock_adapter_validator,
        inference_validator=mock_inference_validator,
        metrics_collector=mock_metrics,
        history=mock_history,
        registry=mock_registry
    )

def test_successful_validation_sweep(validation_engine, mock_integrity, mock_adapter_validator, mock_inference_validator):
    req = ValidationRequest(adapter_id="test_adapter", validation_scope=["model", "adapter", "inference"])
    
    result = validation_engine.run_validation(req)
    
    assert result.success is True
    assert result.validation_status == "COMPLETED"
    assert result.model_status == "PASSED"
    assert result.adapter_status == "PASSED"
    assert result.inference_status == "PASSED"
    
    mock_integrity.check_integrity.assert_called_once()
    mock_adapter_validator.validate_loaded_adapter.assert_called_with("test_adapter")
    mock_inference_validator.validate_inference_pipeline.assert_called_once()

def test_validation_cascading_failure(validation_engine, mock_integrity, mock_inference_validator):
    # If model integrity fails, inference should be SKIPPED
    mock_integrity.check_integrity.return_value = (False, IntegrityReport())
    
    req = ValidationRequest(validation_scope=["model", "inference"])
    result = validation_engine.run_validation(req)
    
    assert result.success is False
    assert result.model_status == "FAILED"
    assert result.inference_status == "SKIPPED"
    assert len(result.errors) == 1
    
    mock_inference_validator.validate_inference_pipeline.assert_not_called()

def test_concurrent_validation_rejected(validation_engine, mock_registry):
    mock_registry.is_validation_running.return_value = True
    
    req = ValidationRequest()
    with pytest.raises(RuntimeError):
        validation_engine.run_validation(req)
