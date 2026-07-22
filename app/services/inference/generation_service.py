"""Generation Service.

Author: DriftAdapt Contributors
Purpose: Core wrapper around HuggingFace generation routines.
"""

from typing import Dict, Any, Optional

try:
    import torch
except ImportError:
    pass

from app.core.logging import LoggerFactory
from app.models.foundation.model_manager import ModelManager
from app.schemas.generation_parameters import GenerationParameters
from app.services.inference.tokenizer_service import TokenizerService


class GenerationService:
    """Executes the forward pass text generation on the LLM."""
    
    def __init__(self, model_manager: ModelManager, tokenizer_service: TokenizerService) -> None:
        self._logger = LoggerFactory.get_logger("GenerationService")
        self._model_manager = model_manager
        self._tokenizer_service = tokenizer_service

    def generate(self, prompt: str, params: GenerationParameters) -> str:
        """Executes full standard generation.
        
        Args:
            prompt: The exact formatted prompt string.
            params: Parameters configuring generation behavior.
            
        Returns:
            The raw generated string.
        """
        model = self._model_manager.get_model()
        if model is None:
            raise RuntimeError("Foundation model is not loaded.")
            
        inputs = self._tokenizer_service.encode(prompt, return_tensors="pt")
        
        # Move to model device if necessary
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        if params.seed is not None:
            torch.manual_seed(params.seed)
            
        try:
            with torch.inference_mode():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=params.max_new_tokens,
                    temperature=params.temperature if params.do_sample else 1.0,
                    top_p=params.top_p,
                    top_k=params.top_k,
                    repetition_penalty=params.repetition_penalty,
                    do_sample=params.do_sample,
                    num_beams=params.num_beams,
                    early_stopping=params.early_stopping,
                    pad_token_id=self._tokenizer_service._get_tokenizer().pad_token_id or self._tokenizer_service._get_tokenizer().eos_token_id
                )
                
            # If return_full_text is false, slice off the prompt length
            prompt_len = inputs["input_ids"].shape[1]
            if not params.return_full_text:
                output_ids = outputs[0][prompt_len:]
            else:
                output_ids = outputs[0]
                
            generated_text = self._tokenizer_service.decode(output_ids, skip_special_tokens=True)
            return generated_text
            
        except Exception as e:
            self._logger.error("Generation forward pass failed", error=str(e))
            raise RuntimeError(f"Generation failed: {e}") from e
