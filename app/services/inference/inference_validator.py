"""Inference Validator Service.

Author: DriftAdapt Contributors
Purpose: Performs strict upfront validation of inference requests prior to tokenization or generation.
"""

from typing import Optional

from app.core.logging import LoggerFactory
from app.schemas.inference_request import InferenceRequest
from app.services.inference.adapter_registry import AdapterRegistry
from app.models.foundation.model_manager import ModelManager


class InferenceValidator:
    """Validates contexts, lengths, and adapter configurations for a request."""
    
    def __init__(self, model_manager: ModelManager, adapter_registry: AdapterRegistry) -> None:
        self._logger = LoggerFactory.get_logger("InferenceValidator")
        self._model_manager = model_manager
        self._registry = adapter_registry

    def validate_request(self, request: InferenceRequest) -> tuple[bool, Optional[str]]:
        """Strictly validates a request.
        
        Args:
            request: The client inference request.
            
        Returns:
            A tuple of (is_valid, error_reason).
        """
        # 1. Base Model Check
        if not self._model_manager.is_loaded():
            return False, "Foundation model is not loaded or available."
            
        # 2. Prompt Check
        if not request.prompt or not request.prompt.strip():
            return False, "Prompt cannot be empty or solely whitespace."
            
        # 3. Adapter Check
        if request.adapter_id is not None:
            if not self._registry.is_loaded(request.adapter_id):
                return False, f"Requested adapter '{request.adapter_id}' is not loaded."
                
        # 4. Generation Params Check
        if request.generation_parameters.max_new_tokens > 8192:
            return False, "max_new_tokens exceeds strict hard limit of 8192."
            
        if request.generation_parameters.num_beams > 1 and request.stream:
            return False, "Beam search is incompatible with streaming generation."
            
        return True, None
