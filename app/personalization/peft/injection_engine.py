"""DriftAdapt PEFT Injection Engine.

Author: DriftAdapt Contributors
Purpose: Engine responsible for wrapping the base foundation model with the LoRA adapter.
"""

from typing import Any
import time
from torch.nn import Module

from app.core.logging import LoggerFactory
from app.personalization.peft.peft_exceptions import AdapterInjectionError

try:
    from peft import get_peft_model, LoraConfig, PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False


class InjectionEngine:
    """Wraps the frozen base model with trainable adapter layers."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("InjectionEngine")

    def inject_lora_adapters(self, base_model: Module, lora_config: "LoraConfig") -> "PeftModel":
        """Injects LoRA adapters into the base model.
        
        Args:
            base_model: The completely frozen PyTorch foundation model.
            lora_config: The peft configuration object.
            
        Returns:
            The wrapped peft model.
            
        Raises:
            ImportError: If peft is not installed.
            AdapterInjectionError: If injection fails.
        """
        if not PEFT_AVAILABLE:
            raise ImportError("The 'peft' library is required for adapter injection.")

        self._logger.info("Starting PEFT adapter injection...")
        start_time = time.perf_counter()

        try:
            # The heart of the injection process via Hugging Face PEFT
            wrapped_model = get_peft_model(base_model, lora_config)
            
            # get_peft_model automatically sets requires_grad=False on all non-LoRA parameters, 
            # reinforcing our frozen model invariants.
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._logger.info(f"Adapter injection completed successfully in {duration_ms:.2f}ms.")
            
            return wrapped_model
            
        except Exception as e:
            self._logger.error("Failed to inject PEFT adapters into the base model.", error=str(e))
            raise AdapterInjectionError(f"Adapter injection failed: {e}") from e
