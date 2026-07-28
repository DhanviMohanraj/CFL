"""DriftAdapt PEFT Adapter Loader.

Author: DriftAdapt Contributors
Purpose: Exposes utilities to load pre-trained adapters from disk into a base model.
"""

from pathlib import Path
from typing import Union
from torch.nn import Module

from app.core.logging import LoggerFactory
from app.personalization.peft.peft_exceptions import AdapterInjectionError

try:
    from peft import PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False


class PEFTLoader:
    """Utility class to load existing PEFT adapters from disk."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("PEFTLoader")

    def load_adapter(self, base_model: Module, model_id_or_path: Union[str, Path]) -> "PeftModel":
        """Loads a pre-trained PEFT adapter onto the frozen base model.
        
        Args:
            base_model: The PyTorch foundation model.
            model_id_or_path: Path to the saved adapter or a Hugging Face Hub ID.
            
        Returns:
            The wrapped peft model.
            
        Raises:
            ImportError: If peft is not installed.
            AdapterInjectionError: If loading fails.
        """
        if not PEFT_AVAILABLE:
            raise ImportError("The 'peft' library is required to load adapters.")

        self._logger.info(f"Loading PEFT adapter from: {model_id_or_path}")

        try:
            wrapped_model = PeftModel.from_pretrained(base_model, str(model_id_or_path))
            self._logger.info("Adapter loaded successfully.")
            return wrapped_model
            
        except Exception as e:
            self._logger.error(f"Failed to load PEFT adapter from {model_id_or_path}.", error=str(e))
            raise AdapterInjectionError(f"Adapter loading failed: {e}") from e
