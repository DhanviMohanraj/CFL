"""DriftAdapt Test Mock Models Fixture.

Author: DriftAdapt Contributors
Purpose: Provides PyTorch mock model and tokenizer objects for fast unit and integration testing without downloading remote weights.
Future Integration: Imported by unit and integration tests.
"""

from unittest.mock import MagicMock

import torch

from app.models.foundation.model_metadata import ModelMetadata


def create_mock_foundation_model() -> torch.nn.Module:
    """Creates a lightweight PyTorch Linear model test double."""
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 20),
        torch.nn.Linear(20, 5),
    )
    for p in model.parameters():
        p.requires_grad = False
    model.eval()
    return model


def create_mock_tokenizer() -> MagicMock:
    """Creates a mock tokenizer test double."""
    tokenizer = MagicMock()
    tokenizer.vocab_size = 1000
    tokenizer.pad_token = "[PAD]"
    tokenizer.eos_token = "[EOS]"
    tokenizer.is_fast = True
    return tokenizer


def create_mock_metadata() -> ModelMetadata:
    """Creates a sample ModelMetadata object."""
    return ModelMetadata(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        architecture="Qwen2ForCausalLM",
        parameter_count=3090000000,
        trainable_parameters=0,
        tokenizer_name="Qwen/Qwen2.5-3B-Instruct",
        vocab_size=151936,
        context_length=32768,
        hidden_size=2048,
        quantization_mode="4bit",
        precision="bfloat16",
        device="cpu",
        memory_footprint_mb=1800.5,
        load_time_seconds=0.1,
        disk_size_mb=1800.5,
        is_frozen=True,
    )
