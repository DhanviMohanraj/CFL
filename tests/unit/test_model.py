"""DriftAdapt Foundation Model Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies ModelRegistry, QuantizationManager, CacheManager, DownloadManager, ModelLoader, and ModelManager.
Future Integration: Executed in CI pipeline.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import torch

from app.core.config import ConfigManager
from app.core.metrics import MetricsBus
from app.models.foundation import (
    ModelManager,
    ModelFactory,
    ModelRegistry,
    ModelSpec,
    ModelMetadata,
    ModelInfo,
    QuantizationManager,
    CacheManager,
    DownloadManager,
    ModelValidator,
    count_parameters,
    freeze_all_parameters,
    verify_frozen_parameters,
    estimate_memory_footprint_mb,
    run_sanity_inference,
    UnsupportedModelError,
    QuantizationError,
    DownloadError,
)


def test_model_registry() -> None:
    """Verifies registry entries lookup, default model specs, and dynamic registration of novel HF repos."""
    # 1. Lookup default model
    default_spec = ModelRegistry.get_spec("Qwen/Qwen2.5-3B-Instruct")
    assert default_spec.model_name == "Qwen/Qwen2.5-3B-Instruct"
    assert default_spec.architecture == "Qwen2ForCausalLM"
    assert default_spec.context_length == 32768
    assert default_spec.recommended_quantization == "4bit"

    # 2. Check presence of other key architectures
    assert ModelRegistry.is_registered("microsoft/Phi-3-mini-4k-instruct")
    assert ModelRegistry.is_registered("meta-llama/Meta-Llama-3-8B-Instruct")
    assert ModelRegistry.is_registered("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    # 3. Dynamic registration of novel HF repo
    novel_spec = ModelRegistry.get_spec("custom-org/novel-health-llm-7b")
    assert novel_spec.model_name == "custom-org/novel-health-llm-7b"
    assert novel_spec.architecture == "AutoModelForCausalLM"

    # 4. Custom registration
    custom_spec = ModelSpec(
        model_name="custom/my-model",
        hf_repo="custom/my-model",
        architecture="CustomLM",
        context_length=16384,
    )
    ModelRegistry.register_model(custom_spec)
    assert ModelRegistry.is_registered("custom/my-model")
    assert ModelRegistry.get_spec("custom/my-model").context_length == 16384


def test_quantization_manager() -> None:
    """Verifies PyTorch precision dtypes and BitsAndBytes quantization configurations."""
    # 1. Dtype resolutions
    assert QuantizationManager.resolve_torch_dtype("float32") == torch.float32
    assert QuantizationManager.resolve_torch_dtype("float16") == torch.float16
    assert QuantizationManager.resolve_torch_dtype("bfloat16") in (torch.bfloat16, torch.float16)

    # 2. Disabled quantization mode
    bnb_cfg, dtype = QuantizationManager.get_quantization_config("none", "float32")
    assert bnb_cfg is None
    assert dtype == torch.float32

    # 3. Unsupported quantization string
    with pytest.raises(QuantizationError):
        QuantizationManager.get_quantization_config("invalid_quant_mode_123")


def test_cache_manager(tmp_path: Path) -> None:
    """Verifies CacheManager directory creation, cache hit/miss logic, size calculations, and cleaning."""
    cache_mgr = CacheManager(custom_cache_dir=str(tmp_path))

    assert cache_mgr.cache_dir == tmp_path.resolve()
    assert cache_mgr.is_cached("non_existent_model_999") is False

    # Create dummy cached model directory
    model_folder = cache_mgr.resolve_model_cache_path("org/test-model")
    model_folder.mkdir(parents=True, exist_ok=True)
    dummy_file = model_folder / "config.json"
    dummy_file.write_text("{}")

    assert cache_mgr.is_cached("org/test-model") is True
    assert cache_mgr.get_cache_size_bytes() > 0
    assert cache_mgr.get_cache_size_mb() >= 0.0

    listed = cache_mgr.list_cached_models()
    assert len(listed) == 1

    # Clear single entry
    assert cache_mgr.clear_cache("org/test-model") is True
    assert cache_mgr.is_cached("org/test-model") is False


def test_download_manager(tmp_path: Path) -> None:
    """Verifies DownloadManager offline mode checks and local path resolutions."""
    cache_mgr = CacheManager(custom_cache_dir=str(tmp_path))
    dl_mgr = DownloadManager(cache_manager=cache_mgr)

    # Test local filesystem path
    local_dir = tmp_path / "local_model"
    local_dir.mkdir(parents=True, exist_ok=True)

    res_path = dl_mgr.download_model(str(local_dir))
    assert res_path == local_dir

    # Offline mode error when missing from cache
    with patch.object(DownloadManager, "is_offline_mode", return_value=True):
        with pytest.raises(DownloadError):
            dl_mgr.download_model("unseen_remote_model_123")


def test_model_utils_and_freezing() -> None:
    """Verifies parameter counting, parameter freezing (requires_grad=False), and memory footprint estimation."""
    # Create dummy PyTorch Module
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 20),
        torch.nn.Linear(20, 5),
    )

    total_params, trainable_params = count_parameters(model)
    assert total_params == (10 * 20 + 20) + (20 * 5 + 5)
    assert trainable_params == total_params
    assert verify_frozen_parameters(model) is False

    # Freeze all parameters
    frozen_count = freeze_all_parameters(model)
    assert frozen_count == total_params

    total_params_after, trainable_params_after = count_parameters(model)
    assert trainable_params_after == 0
    assert verify_frozen_parameters(model) is True

    # Memory footprint
    mem_mb = estimate_memory_footprint_mb(model)
    assert mem_mb >= 0.0


def test_model_metadata_and_info() -> None:
    """Verifies ModelMetadata models and ModelInfo report export functions."""
    meta = ModelMetadata(
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
        load_time_seconds=2.4,
        disk_size_mb=1800.5,
        is_frozen=True,
    )

    info = ModelInfo(meta)
    info_dict = info.to_dict()
    metrics_dict = info.to_metrics_dict()
    report_text = info.get_summary_report()

    assert info_dict["model_name"] == "Qwen/Qwen2.5-3B-Instruct"
    assert metrics_dict["model.parameter_count"] == 3090000000
    assert metrics_dict["model.is_frozen"] == 1
    assert "DRIFTADAPT FOUNDATION MODEL SUMMARY" in report_text
    assert "3.09B" in report_text


def test_model_validator() -> None:
    """Verifies ModelValidator frozen state checks."""
    model = torch.nn.Linear(5, 5)
    freeze_all_parameters(model)

    assert ModelValidator.validate_frozen_state(model) is True

    # Make one param trainable to trigger validation error
    for p in model.parameters():
        p.requires_grad = True
        break

    with pytest.raises(Exception):
        ModelValidator.validate_frozen_state(model)


def test_model_manager_with_mocked_factory() -> None:
    """Verifies ModelManager loading, unloading, metrics publishing, and sanity inference with a mocked model."""
    # Construct dummy PyTorch model and tokenizer
    dummy_model = torch.nn.Linear(10, 10)
    freeze_all_parameters(dummy_model)

    dummy_tokenizer = MagicMock()
    dummy_tokenizer.vocab_size = 1000
    dummy_tokenizer.pad_token = "[PAD]"
    dummy_tokenizer.eos_token = "[EOS]"

    dummy_meta = ModelMetadata(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        architecture="Qwen2ForCausalLM",
        parameter_count=100,
        trainable_parameters=0,
        tokenizer_name="Qwen/Qwen2.5-3B-Instruct",
        vocab_size=1000,
        context_length=2048,
        hidden_size=10,
        quantization_mode="none",
        precision="float32",
        device="cpu",
        memory_footprint_mb=1.0,
        load_time_seconds=0.1,
        disk_size_mb=1.0,
        is_frozen=True,
    )

    # Patch ModelFactory inside ModelManager
    with patch("app.models.foundation.model_manager.ModelFactory") as MockFactoryCls:
        mock_factory_instance = MockFactoryCls.return_value
        mock_factory_instance.create_model_and_tokenizer.return_value = (
            dummy_model,
            dummy_tokenizer,
            dummy_meta,
        )

        config_mgr = ConfigManager()
        overrides = {
            "model": {
                "foundation_model": "Qwen/Qwen2.5-3B-Instruct",
                "tokenizer": "Qwen/Qwen2.5-3B-Instruct",
                "quantization": "none",
                "precision": "float32",
            }
        }
        config_mgr.apply_runtime_overrides(overrides)
        config_mgr.refresh()

        mgr = ModelManager(config_manager=config_mgr)
        info = mgr.load_model()

        assert info.metadata.model_name == "Qwen/Qwen2.5-3B-Instruct"
        assert mgr.get_model() is dummy_model
        assert mgr.get_tokenizer() is dummy_tokenizer
        assert mgr.get_memory_usage() >= 0.0

        # Check metrics published to MetricsBus
        bus = MetricsBus()
        load_metrics = bus.retrieve("model.load_time_ms")
        assert len(load_metrics) >= 1
        assert load_metrics[-1].value >= 0.0

        # Unload
        mgr.unload_model()
        assert mgr._model is None

        # Clean overrides
        config_mgr.clear_overrides()
        config_mgr.refresh()
