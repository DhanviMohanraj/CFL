"""Inference Validator Service.

Author: DriftAdapt Contributors
Purpose: Pre-flight checks for the generation pipeline to ensure deterministic correctness.
"""

from typing import Tuple

from app.core.logging import LoggerFactory
from app.services.inference.inference_engine import InferenceEngine
from app.schemas.inference_request import InferenceRequest


class InferenceValidator:
    """Verifies that the inference pipeline can produce outputs without error."""
    
    def __init__(self, inference_engine: InferenceEngine) -> None:
        self._logger = LoggerFactory.get_logger("InferenceValidator_Module28")
        self._inference_engine = inference_engine

    def validate_inference_pipeline(self) -> Tuple[bool, str]:
        """Runs a tiny generation test to ensure end-to-end inference works."""
        self._logger.info("Running deterministic inference pre-flight check.")
        
        req = InferenceRequest(
            prompt="Hello",
            stream=False
        )
        # Force a small, deterministic generation
        req.generation_parameters.max_new_tokens = 5
        req.generation_parameters.do_sample = False
        req.generation_parameters.temperature = 0.0
        
        try:
            # We skip cache manually by assuming the engine runs it or we could bypass, 
            # but standard generate validates the whole stack
            response = self._inference_engine.run_generation(req)
            if response.success and len(response.generated_text) > 0:
                self._logger.info("Inference pipeline validation passed.")
                return True, "Pipeline generated successfully."
            else:
                return False, "Pipeline returned an empty or unsuccessful generation."
                
        except Exception as e:
            self._logger.error("Inference validation failed", error=str(e))
            return False, f"Exception during inference: {e}"
