"""DriftAdapt Quantization Manager Module.

Author: DriftAdapt Contributors
Purpose: Configures PyTorch floating point dtypes and BitsAndBytes 8-bit / 4-bit quantization settings.
Future Integration: Invoked by ModelLoader during model loading.
"""

from typing import Dict, Any, Optional, Tuple
import torch

from app.core.logging import LoggerFactory
from app.models.foundation.exceptions import QuantizationError

logger = LoggerFactory.get_logger("QuantizationManager")

try:
    import bitsandbytes
    HAS_BITSANDBYTES = True
except ImportError:
    HAS_BITSANDBYTES = False

try:
    from transformers import BitsAndBytesConfig
    HAS_BNB_CONFIG = True
except ImportError:
    HAS_BNB_CONFIG = False


class QuantizationManager:
    """Manages PyTorch precision dtypes and BitsAndBytes quantization configurations."""

    @staticmethod
    def resolve_torch_dtype(precision_str: str) -> torch.dtype:
        """Parses precision string and returns matching PyTorch dtype.

        Supported: 'float32', 'fp32', 'float16', 'fp16', 'bfloat16', 'bf16'.
        """
        prec_clean = str(precision_str).lower().strip()

        if prec_clean in ("float32", "fp32"):
            return torch.float32
        elif prec_clean in ("float16", "fp16"):
            return torch.float16
        elif prec_clean in ("bfloat16", "bf16"):
            # Fall back to float16 if bfloat16 is unsupported on current hardware
            if hasattr(torch, "bfloat16"):
                return torch.bfloat16
            return torch.float16
        else:
            logger.warning(f"Unrecognized precision '{precision_str}'. Defaulting to torch.float32.")
            return torch.float32

    @classmethod
    def get_quantization_config(
        cls,
        quantization_mode: str,
        precision: str = "bfloat16",
    ) -> Tuple[Optional[Any], torch.dtype]:
        """Resolves quantization parameters.

        Args:
            quantization_mode: Mode ('none', 'fp32', 'fp16', 'bf16', '8bit', '4bit').
            precision: Default fallback precision dtype string.

        Returns:
            Tuple containing:
            - Optional[BitsAndBytesConfig] instance (if 4bit/8bit selected and available, else None)
            - torch.dtype for tensor representations

        Raises:
            QuantizationError: If 4bit/8bit is requested but bitsandbytes is missing on host.
        """
        mode = str(quantization_mode).lower().strip()
        torch_dtype = cls.resolve_torch_dtype(precision)

        if mode in ("none", "fp32", "fp16", "bf16", ""):
            logger.info(f"Quantization disabled ({mode or 'none'}). Using precision dtype: {torch_dtype}")
            return None, torch_dtype

        if mode in ("4bit", "8bit"):
            if not HAS_BNB_CONFIG or not HAS_BITSANDBYTES:
                logger.warning(
                    f"Quantization '{mode}' was requested, but 'bitsandbytes' package is not installed. "
                    "Falling back to standard precision dtype to prevent load crash. "
                    "To enable 4-bit/8-bit quantization, run 'pip install bitsandbytes'."
                )
                return None, torch_dtype

            compute_dtype = cls.resolve_torch_dtype(precision)

            if mode == "4bit":
                logger.info(f"Configuring 4-bit NF4 quantization with compute_dtype={compute_dtype}.")
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=compute_dtype,
                )
                return bnb_config, compute_dtype

            elif mode == "8bit":
                logger.info("Configuring 8-bit quantization.")
                bnb_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                )
                return bnb_config, compute_dtype

        raise QuantizationError(
            f"Unsupported quantization mode '{quantization_mode}'. "
            "DriftAdapt supports: 'none', 'fp32', 'fp16', 'bf16', '8bit', '4bit'."
        )
