"""DriftAdapt Model Utilities Module.

Author: DriftAdapt Contributors
Purpose: Utility functions for parameter count, parameter freezing, memory estimation, and sanity inference checks.
Future Integration: Invoked by ModelLoader and ModelValidator.
"""

from typing import Any, Tuple

import torch

from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger("ModelUtils")


def count_parameters(model: Any) -> Tuple[int, int]:
    """Counts total and trainable parameters of a PyTorch model.

    Returns:
        Tuple containing (total_parameters, trainable_parameters).
    """
    if not isinstance(model, torch.nn.Module):
        return (0, 0)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return (total_params, trainable_params)


def freeze_all_parameters(model: Any) -> int:
    """Freezes all model parameters by setting requires_grad = False.

    Returns:
        int: Total number of parameters frozen.
    """
    if not isinstance(model, torch.nn.Module):
        return 0

    count = 0
    for param in model.parameters():
        param.requires_grad = False
        count += param.numel()

    # Also set model to eval mode
    model.eval()
    logger.info(f"Successfully froze all {count:,} model parameters for zero-gradient base state.")
    return count


def verify_frozen_parameters(model: Any) -> bool:
    """Verifies that all parameters in the model have requires_grad set to False."""
    if not isinstance(model, torch.nn.Module):
        return True

    for param in model.parameters():
        if param.requires_grad:
            return False
    return True


def estimate_memory_footprint_mb(model: Any) -> float:
    """Estimates the in-memory footprint of a model's parameters and buffers in Megabytes (MB)."""
    if not isinstance(model, torch.nn.Module):
        return 0.0

    total_bytes = 0
    for param in model.parameters():
        total_bytes += param.numel() * param.element_size()

    for buffer in model.buffers():
        total_bytes += buffer.numel() * buffer.element_size()

    return round(total_bytes / (1024 * 1024), 2)


def run_sanity_inference(
    model: Any,
    tokenizer: Any,
    prompt: str = "Hello",
    max_new_tokens: int = 10,
    device: Any = None,
) -> str:
    """Performs a simple forward inference test to verify that the model and tokenizer function correctly.

    This check runs strictly under torch.no_grad() and DOES NOT perform training or weight modification.
    """
    if model is None or tokenizer is None:
        return "Model or Tokenizer unavailable for sanity inference."

    try:
        model.eval()
        inputs = tokenizer(prompt, return_tensors="pt")

        if device is not None:
            inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        res_str = str(decoded).strip()
        logger.info(f"Sanity inference check succeeded. Input: '{prompt}' -> Generated output: '{res_str[:60]}...'")
        return res_str
    except Exception as e:
        logger.warning(f"Sanity inference execution warning: {e}")
        return f"Sanity check warning: {e}"
