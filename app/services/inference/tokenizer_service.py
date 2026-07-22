"""Tokenizer Service.

Author: DriftAdapt Contributors
Purpose: Exposes tokenization, decoding, and truncation functionality for inference.
"""

from typing import List, Dict, Any, Union

from app.core.logging import LoggerFactory
from app.models.foundation.model_manager import ModelManager


class TokenizerService:
    """Wraps HuggingFace tokenization for standardized prompt ingestion and output decoding."""
    
    def __init__(self, model_manager: ModelManager) -> None:
        self._logger = LoggerFactory.get_logger("TokenizerService")
        self._model_manager = model_manager

    def _get_tokenizer(self) -> Any:
        tokenizer = self._model_manager.get_tokenizer()
        if tokenizer is None:
            raise ValueError("Tokenizer not loaded via ModelManager.")
        return tokenizer

    def encode(self, prompt: str, return_tensors: str = "pt") -> Any:
        """Tokenizes a string prompt."""
        tokenizer = self._get_tokenizer()
        try:
            return tokenizer(prompt, return_tensors=return_tensors)
        except Exception as e:
            self._logger.error("Failed to encode prompt.", error=str(e))
            raise ValueError(f"Encoding failed: {e}") from e

    def decode(self, token_ids: Union[List[int], Any], skip_special_tokens: bool = True) -> str:
        """Decodes token IDs back to a string."""
        tokenizer = self._get_tokenizer()
        try:
            return tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
        except Exception as e:
            self._logger.error("Failed to decode tokens.", error=str(e))
            raise ValueError(f"Decoding failed: {e}") from e

    def count_tokens(self, prompt: str) -> int:
        """Calculates the exact token footprint of a prompt."""
        tokenizer = self._get_tokenizer()
        try:
            # Using encode directly gives token IDs
            tokens = tokenizer.encode(prompt, add_special_tokens=False)
            return len(tokens)
        except Exception as e:
            self._logger.error("Failed to count tokens.", error=str(e))
            return 0
