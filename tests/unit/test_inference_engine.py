"""Unit Tests for Module 2.7 Inference Engine.

Author: DriftAdapt Contributors
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.schemas.inference_request import InferenceRequest
from app.schemas.generation_parameters import GenerationParameters
from app.services.inference.inference_engine import InferenceEngine
from app.services.inference.adapter_registry import AdapterRegistry
from app.services.inference.cache_manager import CacheManager
from app.services.inference.inference_metrics import InferenceMetrics


@pytest.fixture
def mock_validator():
    val = MagicMock()
    val.validate_request.return_value = (True, None)
    return val

@pytest.fixture
def mock_prompt_processor():
    proc = MagicMock()
    proc.process_prompt.return_value = ("User: Test", MagicMock())
    return proc

@pytest.fixture
def mock_tokenizer_service():
    tok = MagicMock()
    tok.count_tokens.return_value = 10
    tok.encode.return_value = {"input_ids": [1, 2, 3]}
    tok.decode.return_value = "Mock response text"
    return tok

@pytest.fixture
def mock_adapter_switcher():
    sw = MagicMock()
    sw.switch_adapter.return_value = True
    return sw

@pytest.fixture
def mock_generation_service():
    gen = MagicMock()
    gen.generate.return_value = "Mock response text"
    return gen

@pytest.fixture
def cache_manager():
    return CacheManager(ttl_seconds=3600)

@pytest.fixture
def inference_metrics():
    return InferenceMetrics()

@pytest.fixture
def mock_history_manager():
    return MagicMock()

@pytest.fixture
def mock_response_formatter():
    fmt = MagicMock()
    mock_resp = MagicMock()
    mock_resp.generated_text = "Mock response text"
    fmt.format_response.return_value = mock_resp
    return fmt

@pytest.fixture
def inference_engine(
    mock_validator,
    mock_prompt_processor,
    mock_tokenizer_service,
    mock_adapter_switcher,
    mock_generation_service,
    cache_manager,
    inference_metrics,
    mock_history_manager,
    mock_response_formatter
):
    return InferenceEngine(
        adapter_loader=MagicMock(),
        adapter_switcher=mock_adapter_switcher,
        adapter_registry=AdapterRegistry(),
        cache_manager=cache_manager,
        prompt_processor=mock_prompt_processor,
        tokenizer_service=mock_tokenizer_service,
        generation_service=mock_generation_service,
        streaming_service=MagicMock(),
        response_formatter=mock_response_formatter,
        history_manager=mock_history_manager,
        metrics=inference_metrics,
        validator=mock_validator
    )


def test_standard_generation(inference_engine, mock_generation_service, inference_metrics):
    req = InferenceRequest(prompt="Test", adapter_id="test_adapter")
    
    resp = inference_engine.run_generation(req)
    
    # Assert generation was called
    mock_generation_service.generate.assert_called_once()
    
    # Assert metrics were updated
    stats = inference_metrics.get_statistics()
    assert stats.successful_requests == 1
    assert stats.cache_misses == 1


def test_caching_behavior(inference_engine, mock_generation_service, inference_metrics):
    req1 = InferenceRequest(prompt="Cache Me", adapter_id="test_adapter")
    req2 = InferenceRequest(prompt="Cache Me", adapter_id="test_adapter")
    
    # First request should miss cache and generate
    inference_engine.run_generation(req1)
    assert mock_generation_service.generate.call_count == 1
    
    # Second request should hit cache
    inference_engine.run_generation(req2)
    assert mock_generation_service.generate.call_count == 1 # Still 1, didn't call generate again
    
    stats = inference_metrics.get_statistics()
    assert stats.cache_hits == 1
    assert stats.cache_misses == 1


def test_cache_adapter_isolation(inference_engine, mock_generation_service, inference_metrics):
    req1 = InferenceRequest(prompt="Cache Me", adapter_id="adapter_a")
    req2 = InferenceRequest(prompt="Cache Me", adapter_id="adapter_b")
    
    # First request
    inference_engine.run_generation(req1)
    
    # Second request with same prompt but DIFFERENT adapter should MISS
    inference_engine.run_generation(req2)
    
    assert mock_generation_service.generate.call_count == 2
    
    stats = inference_metrics.get_statistics()
    assert stats.cache_hits == 0
    assert stats.cache_misses == 2


def test_validation_failure_raises_error(inference_engine):
    inference_engine._validator.validate_request.return_value = (False, "Bad request")
    
    req = InferenceRequest(prompt="Test")
    with pytest.raises(RuntimeError):
        inference_engine.run_generation(req)
