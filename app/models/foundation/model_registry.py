"""DriftAdapt Model Registry Module.

Author: DriftAdapt Contributors
Purpose: Centralizes specifications, context lengths, and default quantization configurations for supported LLM architectures.
Future Integration: Queried by ModelFactory and ModelLoader when resolving model parameters.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.foundation.exceptions import UnsupportedModelError


class ModelSpec(BaseModel):
    """Specification record for a supported foundation model architecture."""

    model_name: str = Field(..., description="Canonical repository or model name.")
    hf_repo: str = Field(..., description="HuggingFace Hub repository ID.")
    architecture: str = Field(default="CausalLM", description="Model architecture category.")
    context_length: int = Field(default=2048, description="Supported sequence context length.")
    hidden_size: int = Field(default=2048, description="Hidden state dimension size.")
    vocab_size: int = Field(default=32000, description="Vocabulary size.")
    default_precision: str = Field(default="bfloat16", description="Default tensor precision.")
    recommended_quantization: str = Field(default="4bit", description="Recommended edge quantization mode.")
    parameter_count: int = Field(default=0, description="Total number of parameters.")
    license: str = Field(default="Apache-2.0", description="Model license classification.")
    description: str = Field(default="", description="Human-readable model summary.")


# Pre-populated registry entries for supported foundation model families
KNOWN_MODEL_REGISTRY: Dict[str, ModelSpec] = {
    "Qwen/Qwen2.5-3B-Instruct": ModelSpec(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        hf_repo="Qwen/Qwen2.5-3B-Instruct",
        architecture="Qwen2ForCausalLM",
        context_length=32768,
        hidden_size=2048,
        vocab_size=151936,
        default_precision="bfloat16",
        recommended_quantization="4bit",
        parameter_count=3090000000,
        license="Qwen Research License",
        description="Default DriftAdapt Foundation Model. High-capability 3B instruction-tuned model.",
    ),
    "microsoft/Phi-3-mini-4k-instruct": ModelSpec(
        model_name="microsoft/Phi-3-mini-4k-instruct",
        hf_repo="microsoft/Phi-3-mini-4k-instruct",
        architecture="Phi3ForCausalLM",
        context_length=4096,
        hidden_size=3072,
        vocab_size=32064,
        default_precision="bfloat16",
        recommended_quantization="4bit",
        parameter_count=3800000000,
        license="MIT",
        description="Microsoft 3.8B parameters lightweight instruction model.",
    ),
    "meta-llama/Meta-Llama-3-8B-Instruct": ModelSpec(
        model_name="meta-llama/Meta-Llama-3-8B-Instruct",
        hf_repo="meta-llama/Meta-Llama-3-8B-Instruct",
        architecture="LlamaForCausalLM",
        context_length=8192,
        hidden_size=4096,
        vocab_size=128256,
        default_precision="bfloat16",
        recommended_quantization="4bit",
        parameter_count=8030000000,
        license="Llama 3 Community License",
        description="Meta Llama 3 8B instruction tuned foundation model.",
    ),
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": ModelSpec(
        model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        hf_repo="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        architecture="LlamaForCausalLM",
        context_length=2048,
        hidden_size=2048,
        vocab_size=32000,
        default_precision="float16",
        recommended_quantization="none",
        parameter_count=1100000000,
        license="Apache-2.0",
        description="Compact 1.1B parameter Llama architecture model suitable for ultra low-resource edge nodes.",
    ),
    "mistralai/Mistral-7B-v0.1": ModelSpec(
        model_name="mistralai/Mistral-7B-v0.1",
        hf_repo="mistralai/Mistral-7B-v0.1",
        architecture="MistralForCausalLM",
        context_length=8192,
        hidden_size=4096,
        vocab_size=32000,
        default_precision="bfloat16",
        recommended_quantization="4bit",
        parameter_count=7240000000,
        license="Apache-2.0",
        description="Mistral 7B foundation base model with sliding window attention.",
    ),
    "google/gemma-2b-it": ModelSpec(
        model_name="google/gemma-2b-it",
        hf_repo="google/gemma-2b-it",
        architecture="GemmaForCausalLM",
        context_length=8192,
        hidden_size=2048,
        vocab_size=256000,
        default_precision="bfloat16",
        recommended_quantization="4bit",
        parameter_count=2500000000,
        license="Gemma Terms of Use",
        description="Google Gemma 2B instruction-tuned lightweight model.",
    ),
}


class ModelRegistry:
    """Registry maintaining supported models specs and resolving unknown HF repository strings."""

    _registry: Dict[str, ModelSpec] = dict(KNOWN_MODEL_REGISTRY)

    @classmethod
    def register_model(cls, spec: ModelSpec) -> None:
        """Registers or updates a model specification entry."""
        cls._registry[spec.model_name] = spec

    @classmethod
    def is_registered(cls, model_name: str) -> bool:
        """Checks if a model name or HF repo is present in the registry."""
        return model_name in cls._registry

    @classmethod
    def get_spec(cls, model_name: str) -> ModelSpec:
        """Retrieves ModelSpec for registered models, or constructs a dynamic spec for novel HF repos.

        Allows novel Hugging Face models to load dynamically without breaking.
        """
        if model_name in cls._registry:
            return cls._registry[model_name]

        # Construct generic fallback spec for arbitrary HF model repos or local paths
        return ModelSpec(
            model_name=model_name,
            hf_repo=model_name,
            architecture="AutoModelForCausalLM",
            context_length=2048,
            hidden_size=2048,
            vocab_size=32000,
            default_precision="float32",
            recommended_quantization="none",
            parameter_count=0,
            license="Unknown",
            description=f"Dynamically registered model '{model_name}'.",
        )

    @classmethod
    def list_models(cls) -> Dict[str, ModelSpec]:
        """Returns all registered model specifications."""
        return dict(cls._registry)
