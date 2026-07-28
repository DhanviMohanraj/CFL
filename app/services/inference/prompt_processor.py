"""Prompt Processor Service.

Author: DriftAdapt Contributors
Purpose: Sanitizes, normalizes, and wraps input prompts for inference.
"""

from typing import Optional, Dict, Any
import time

from app.core.logging import LoggerFactory
from app.schemas.prompt_metadata import PromptMetadata


class PromptProcessor:
    """Prepares and structures raw prompts for the LLM."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("PromptProcessor")

    def process_prompt(
        self,
        raw_prompt: str,
        system_prompt: Optional[str] = None
    ) -> tuple[str, PromptMetadata]:
        """Normalizes the prompt and applies chat templates if needed.
        
        Args:
            raw_prompt: The user input text.
            system_prompt: Optional system-level instructions.
            
        Returns:
            A tuple of (formatted_prompt_string, metadata_object).
        """
        start_time = time.perf_counter()
        
        # Trim whitespace
        clean_prompt = raw_prompt.strip()
        
        # Apply standard ChatML-like structure (or just simple prefixes for now, customizable later)
        if system_prompt:
            clean_sys = system_prompt.strip()
            # Simple fallback format
            formatted = f"System: {clean_sys}\nUser: {clean_prompt}\nAssistant:"
        else:
            formatted = f"User: {clean_prompt}\nAssistant:"
            
        # Analyze prompt
        length = len(formatted)
        
        metadata = PromptMetadata(
            language="en", # Stub for real langdetect integration
            prompt_length=length,
            detected_domain="general",
            estimated_complexity=min(1.0, length / 1000.0),
            preprocessing_time=time.perf_counter() - start_time
        )
        
        self._logger.debug(f"Processed prompt (Len: {length})")
        return formatted, metadata
