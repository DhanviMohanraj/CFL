"""Inference Engine Service.

Author: DriftAdapt Contributors
Purpose: Central orchestrator connecting all inference sub-services to process a request end-to-end.
"""

import time
from typing import Dict, Any, Union, AsyncGenerator

from app.core.logging import LoggerFactory
from app.schemas.inference_request import InferenceRequest
from app.schemas.inference_response import InferenceResponse

from app.services.inference.adapter_loader import AdapterLoader
from app.services.inference.adapter_switcher import AdapterSwitcher
from app.services.inference.adapter_registry import AdapterRegistry
from app.services.inference.cache_manager import CacheManager
from app.services.inference.prompt_processor import PromptProcessor
from app.services.inference.tokenizer_service import TokenizerService
from app.services.inference.generation_service import GenerationService
from app.services.inference.streaming_service import StreamingService
from app.services.inference.response_formatter import ResponseFormatter
from app.services.inference.inference_history_manager import InferenceHistoryManager
from app.services.inference.inference_metrics import InferenceMetrics
from app.services.inference.inference_validator import InferenceValidator


class InferenceEngine:
    """Orchestrates end-to-end personalized LLM generation."""
    
    def __init__(
        self,
        adapter_loader: AdapterLoader,
        adapter_switcher: AdapterSwitcher,
        adapter_registry: AdapterRegistry,
        cache_manager: CacheManager,
        prompt_processor: PromptProcessor,
        tokenizer_service: TokenizerService,
        generation_service: GenerationService,
        streaming_service: StreamingService,
        response_formatter: ResponseFormatter,
        history_manager: InferenceHistoryManager,
        metrics: InferenceMetrics,
        validator: InferenceValidator
    ) -> None:
        self._logger = LoggerFactory.get_logger("InferenceEngine")
        self._adapter_loader = adapter_loader
        self._adapter_switcher = adapter_switcher
        self._registry = adapter_registry
        self._cache_manager = cache_manager
        self._prompt_processor = prompt_processor
        self._tokenizer_service = tokenizer_service
        self._generation_service = generation_service
        self._streaming_service = streaming_service
        self._response_formatter = response_formatter
        self._history_manager = history_manager
        self._metrics = metrics
        self._validator = validator

    def run_generation(self, request: InferenceRequest) -> InferenceResponse:
        """Executes a complete standard (non-streaming) generation request."""
        start_time = time.perf_counter()
        
        try:
            # 1. Validation
            is_valid, err = self._validator.validate_request(request)
            if not is_valid:
                raise ValueError(err)
                
            # 2. Process Prompt
            formatted_prompt, metadata = self._prompt_processor.process_prompt(request.prompt, request.system_prompt)
            prompt_tokens = self._tokenizer_service.count_tokens(formatted_prompt)
            
            # 3. Check Cache
            cached_text = self._cache_manager.check_cache(formatted_prompt, request.adapter_id)
            if cached_text:
                self._metrics.record_cache_hit()
                comp_tokens = self._tokenizer_service.count_tokens(cached_text)
                latency = time.perf_counter() - start_time
                response = self._response_formatter.format_response(
                    request, cached_text, latency, prompt_tokens, comp_tokens, request.adapter_id
                )
                self._metrics.record_success(latency, prompt_tokens + comp_tokens, streaming=False)
                self._history_manager.record_history(request.request_id, formatted_prompt, response)
                return response
                
            self._metrics.record_cache_miss()
            
            # 4. Switch Adapter
            if not self._adapter_switcher.switch_adapter(request.adapter_id):
                raise RuntimeError(f"Failed to switch to adapter {request.adapter_id}")
                
            # 5. Execute Generation
            generated_text = self._generation_service.generate(formatted_prompt, request.generation_parameters)
            comp_tokens = self._tokenizer_service.count_tokens(generated_text)
            
            # 6. Store in Cache
            self._cache_manager.store_cache(formatted_prompt, generated_text, request.adapter_id)
            
            # 7. Format Response and Record
            latency = time.perf_counter() - start_time
            response = self._response_formatter.format_response(
                request, generated_text, latency, prompt_tokens, comp_tokens, request.adapter_id
            )
            
            self._metrics.record_success(latency, prompt_tokens + comp_tokens, streaming=False)
            self._history_manager.record_history(request.request_id, formatted_prompt, response)
            return response
            
        except Exception as e:
            self._logger.error(f"Inference engine failed for request {request.request_id}: {str(e)}")
            self._metrics.record_failure()
            latency = time.perf_counter() - start_time
            
            fail_response = InferenceResponse(
                success=False,
                inference_time=latency,
                finish_reason="error",
                adapter_used=request.adapter_id
            )
            self._history_manager.record_history(request.request_id, request.prompt, fail_response)
            raise RuntimeError(str(e)) from e

    async def run_streaming(self, request: InferenceRequest) -> AsyncGenerator[str, None]:
        """Executes a streaming generation request."""
        # 1. Validation
        is_valid, err = self._validator.validate_request(request)
        if not is_valid:
            raise ValueError(err)
            
        # 2. Process Prompt
        formatted_prompt, metadata = self._prompt_processor.process_prompt(request.prompt, request.system_prompt)
        
        # Cache check omitted for streaming, though we could return entire chunk immediately
        
        # 3. Switch Adapter
        if not self._adapter_switcher.switch_adapter(request.adapter_id):
            raise RuntimeError(f"Failed to switch to adapter {request.adapter_id}")
            
        # 4. Execute Streaming Generation
        stream = self._streaming_service.generate_stream(formatted_prompt, request.generation_parameters, request.request_id)
        
        # Note: True token counting and latency requires tracking inside the streamer,
        # For this implementation, we just record a basic success metric when stream ends
        async for chunk in stream:
            yield chunk
            
        self._metrics.record_success(0.0, 0, streaming=True) # Approximate telemetry for streaming
