"""Streaming Service.

Author: DriftAdapt Contributors
Purpose: Yields Server-Sent Events (SSE) representing token-by-token generation for low-latency streaming.
"""

import json
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import threading

try:
    import torch
    from transformers import TextIteratorStreamer
except ImportError:
    pass

from app.core.logging import LoggerFactory
from app.models.foundation.model_manager import ModelManager
from app.schemas.generation_parameters import GenerationParameters
from app.services.inference.tokenizer_service import TokenizerService


class StreamingService:
    """Manages continuous token stream delivery via Server-Sent Events."""
    
    def __init__(self, model_manager: ModelManager, tokenizer_service: TokenizerService) -> None:
        self._logger = LoggerFactory.get_logger("StreamingService")
        self._model_manager = model_manager
        self._tokenizer_service = tokenizer_service

    async def generate_stream(
        self,
        prompt: str,
        params: GenerationParameters,
        request_id: str
    ) -> AsyncGenerator[str, None]:
        """Executes generation while yielding tokens iteratively as SSE strings.
        
        Args:
            prompt: Formatted prompt.
            params: Generation parameters.
            request_id: ID to attach to streaming payload metadata.
            
        Yields:
            Formatted Server-Sent Events (SSE) string chunks.
        """
        model = self._model_manager.get_model()
        if model is None:
            raise RuntimeError("Foundation model is not loaded.")
            
        tokenizer = self._tokenizer_service._get_tokenizer()
        inputs = self._tokenizer_service.encode(prompt, return_tensors="pt")
        
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=params.max_new_tokens,
            temperature=params.temperature if params.do_sample else 1.0,
            top_p=params.top_p,
            top_k=params.top_k,
            repetition_penalty=params.repetition_penalty,
            do_sample=params.do_sample,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
        )
        
        # We must run generation in a background thread since HF generate() is blocking
        thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        self._logger.debug(f"Started token streaming for request {request_id}")
        
        for new_text in streamer:
            # Format as SSE
            payload = json.dumps({"text": new_text, "request_id": request_id})
            yield f"data: {payload}\n\n"
            
            # Brief yield to the event loop
            await asyncio.sleep(0)
            
        thread.join()
        
        # Conclude stream
        yield f"data: [DONE]\n\n"
        
        self._logger.debug(f"Concluded token streaming for request {request_id}")
