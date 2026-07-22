"""DriftAdapt Model Loader Module.

Author: DriftAdapt Contributors
Purpose: Loads foundation model weights, routes device targeting via DeviceManager, applies quantization, and freezes parameters.
Future Integration: Invoked by ModelFactory and ModelManager.
"""

import time
from typing import Any, Dict, Optional

import torch

from app.core.device import DeviceManager
from app.core.logging import LoggerFactory
from app.models.foundation.download_manager import DownloadManager
from app.models.foundation.exceptions import ModelLoadError
from app.models.foundation.interfaces import ModelLoaderInterface
from app.models.foundation.model_utils import count_parameters, freeze_all_parameters
from app.models.foundation.quantization import QuantizationManager

logger = LoggerFactory.get_logger("ModelLoader")

try:
    from transformers import AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class ModelLoader(ModelLoaderInterface):
    """Loads, quantizes, and prepares foundation language models with frozen zero-gradient base states."""

    def __init__(self, download_manager: Optional[DownloadManager] = None) -> None:
        """Initializes ModelLoader."""
        self._download_manager = download_manager or DownloadManager()

    def load_model(
        self,
        model_name_or_path: str,
        device: Any = None,
        quantization: Optional[str] = None,
        precision: Optional[str] = "bfloat16",
        cache_dir: Optional[str] = None,
    ) -> Any:
        """Loads foundation language model weights and freezes all parameters.

        Args:
            model_name_or_path: HuggingFace repository identifier or local directory path.
            device: Optional target device. If None, retrieves device from Module 1.4 DeviceManager.
            quantization: Quantization mode ('none', '4bit', '8bit', etc.).
            precision: PyTorch precision string ('bfloat16', 'float16', 'float32').
            cache_dir: Optional cache directory path.

        Returns:
            Any: PyTorch foundation model in eval state with all parameters frozen.

        Raises:
            ModelLoadError: If transformers is missing or weight loading fails.
        """
        start_time = time.time()

        # 1. Obtain execution device via Module 1.4 DeviceManager if not supplied
        if device is None:
            dev_mgr = DeviceManager()
            target_device = dev_mgr.get_device()
        else:
            target_device = torch.device(device) if isinstance(device, str) else device

        logger.info(
            f"Loading foundation model '{model_name_or_path}' on device '{target_device}' "
            f"(quantization='{quantization or 'none'}', precision='{precision or 'float32'}')."
        )

        if not HAS_TRANSFORMERS:
            raise ModelLoadError(
                "Package 'transformers' is not installed. Unable to load AutoModelForCausalLM. "
                "Install via 'pip install transformers'."
            )

        try:
            # 2. Download or verify local availability
            local_path = self._download_manager.download_model(model_name_or_path)

            # 3. Resolve quantization and precision dtypes
            quant_config, torch_dtype = QuantizationManager.get_quantization_config(
                quantization_mode=quantization or "none",
                precision=precision or "bfloat16",
            )

            # 4. Construct loading kwargs
            kwargs: Dict[str, Any] = {
                "cache_dir": cache_dir,
                "trust_remote_code": True,
                "torch_dtype": torch_dtype,
            }

            if quant_config is not None:
                kwargs["quantization_config"] = quant_config
                # When using bitsandbytes 4bit/8bit quantization, device_map='auto' or device allocation is handled by transformers
                kwargs["device_map"] = "auto"
            else:
                # Standard precision loading
                if str(target_device).startswith("cuda"):
                    kwargs["device_map"] = str(target_device)

            # 5. Load model weights
            model = AutoModelForCausalLM.from_pretrained(
                str(local_path),
                **kwargs,
            )

            # Move to device if device_map was not auto-set
            if quant_config is None and not str(target_device).startswith("cuda"):
                model = model.to(target_device)

            # 6. Strictly freeze all parameters (requires_grad = False, model.eval())
            freeze_all_parameters(model)

            elapsed = time.time() - start_time
            total_params, trainable_params = count_parameters(model)
            logger.info(
                f"Foundation model '{model_name_or_path}' loaded and frozen successfully in {elapsed:.2f}s "
                f"(total_params={total_params:,}, trainable_params={trainable_params:,})."
            )

            return model

        except Exception as e:
            logger.error(f"Failed to load foundation model '{model_name_or_path}': {e}")
            raise ModelLoadError(f"Error loading foundation model '{model_name_or_path}': {e}") from e
