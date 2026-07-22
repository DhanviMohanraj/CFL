"""DriftAdapt Model Factory Module.

Author: DriftAdapt Contributors
Purpose: Instantiates and couples foundation model and tokenizer objects using registry specifications.
Future Integration: Invoked by ModelManager during initialization and model switching.
"""

import time
from typing import Any, Dict, Optional, Tuple

from app.core.device import DeviceManager
from app.core.logging import LoggerFactory
from app.models.foundation.model_loader import ModelLoader
from app.models.foundation.model_metadata import ModelMetadata
from app.models.foundation.model_registry import ModelRegistry, ModelSpec
from app.models.foundation.model_utils import (
    count_parameters,
    estimate_memory_footprint_mb,
    verify_frozen_parameters,
)
from app.models.foundation.tokenizer_loader import TokenizerLoader

logger = LoggerFactory.get_logger("ModelFactory")


class ModelFactory:
    """Factory responsible for instantiating model and tokenizer pairs."""

    def __init__(
        self,
        model_loader: Optional[ModelLoader] = None,
        tokenizer_loader: Optional[TokenizerLoader] = None,
    ) -> None:
        """Initializes ModelFactory."""
        self._model_loader = model_loader or ModelLoader()
        self._tokenizer_loader = tokenizer_loader or TokenizerLoader()

    def create_model_and_tokenizer(
        self,
        model_name: str,
        tokenizer_name: Optional[str] = None,
        quantization: Optional[str] = None,
        precision: Optional[str] = None,
        device: Any = None,
        cache_dir: Optional[str] = None,
    ) -> Tuple[Any, Any, ModelMetadata]:
        """Creates, loads, and metadata-wraps a foundation model and tokenizer pair.

        Args:
            model_name: Repository ID or registered model identifier.
            tokenizer_name: Optional custom tokenizer ID. Defaults to model_name.
            quantization: Quantization mode override.
            precision: Precision dtype override.
            device: Target execution device.
            cache_dir: Custom cache path directory.

        Returns:
            Tuple containing:
            - PyTorch model instance
            - Tokenizer instance
            - ModelMetadata metadata object
        """
        start_time = time.time()
        spec: ModelSpec = ModelRegistry.get_spec(model_name)
        target_tokenizer_name = tokenizer_name or model_name

        # Resolve quantization and precision defaults from spec if not explicitly provided
        active_quant = quantization if quantization is not None else spec.recommended_quantization
        active_prec = precision if precision is not None else spec.default_precision

        # Resolve device via Module 1.4 DeviceManager
        dev_mgr = DeviceManager()
        active_device = device if device is not None else dev_mgr.get_device()

        logger.info(
            f"ModelFactory creating model '{model_name}' (spec='{spec.architecture}', "
            f"quantization='{active_quant}', precision='{active_prec}', device='{active_device}')."
        )

        # 1. Load Tokenizer
        tokenizer = self._tokenizer_loader.load_tokenizer(
            tokenizer_name_or_path=target_tokenizer_name,
            cache_dir=cache_dir,
        )

        # 2. Load Model & Freeze
        model = self._model_loader.load_model(
            model_name_or_path=model_name,
            device=active_device,
            quantization=active_quant,
            precision=active_prec,
            cache_dir=cache_dir,
        )

        elapsed = time.time() - start_time
        total_params, trainable_params = count_parameters(model)
        mem_mb = estimate_memory_footprint_mb(model)
        is_frozen = verify_frozen_parameters(model)
        vocab_size = getattr(tokenizer, "vocab_size", spec.vocab_size)

        # 3. Construct Metadata object
        metadata = ModelMetadata(
            model_name=model_name,
            architecture=spec.architecture,
            parameter_count=total_params or spec.parameter_count,
            trainable_parameters=trainable_params,
            tokenizer_name=target_tokenizer_name,
            vocab_size=vocab_size,
            context_length=spec.context_length,
            hidden_size=spec.hidden_size,
            quantization_mode=active_quant or "none",
            precision=active_prec or "float32",
            device=str(active_device),
            memory_footprint_mb=mem_mb,
            load_time_seconds=round(elapsed, 2),
            disk_size_mb=mem_mb,
            checkpoint_location=cache_dir or "./models/cache",
            is_frozen=is_frozen,
        )

        logger.info(f"ModelFactory created model & tokenizer pair for '{model_name}' successfully.")
        return model, tokenizer, metadata
