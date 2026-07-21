"""DriftAdapt Deterministic Execution Configuration Module.

Author: DriftAdapt Contributors
Purpose: Configures PyTorch, CuDNN, and CuBLAS deterministic execution parameters.
Future Integration: Invoked at startup if deterministic mode is selected in config.
"""

import os
import torch

from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger("Deterministic")


def configure_deterministic_execution(enabled: bool = True) -> None:
    """Sets up PyTorch and CUDA libraries to run with deterministic algorithms.

    Args:
        enabled: If True, locks backends to deterministic states. If False, keeps standard behavior.
    """
    if not enabled:
        logger.info("Deterministic execution is disabled. Backends will utilize standard optimized paths.")
        return

    logger.info("Configuring deterministic execution path...")

    # 1. Warn user of potential performance penalty
    logger.warning(
        "Deterministic execution is ACTIVE. Standard optimizations (e.g. CuDNN autotuner) "
        "have been disabled. This may lead to reduced throughput, increased training runtime, "
        "and higher GPU memory utilization."
    )

    # 2. PyTorch deterministic operators
    try:
        # warn_only=True allows fallback instead of crashing when non-deterministic ops are called
        torch.use_deterministic_algorithms(True, warn_only=True)
        logger.info("PyTorch deterministic algorithms configured (with warning fallback).")
    except Exception as e:
        logger.warning(f"Could not enable PyTorch deterministic algorithms: {e}")

    # 3. CuDNN determinism
    try:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        logger.info("CuDNN deterministic backends locked (benchmark=False, deterministic=True).")
    except Exception as e:
        logger.warning(f"Could not lock CuDNN deterministic backends: {e}")

    # 4. CuBLAS workspace setup
    # CuBLAS requires setting workspace config environment variables for determinism.
    # Recommended settings: ':4096:8' or ':16:8'
    if torch.cuda.is_available():
        cublas_config = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
        if cublas_config not in (":4096:8", ":16:8"):
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            logger.info("NVIDIA CuBLAS workspace config variable set: 'CUBLAS_WORKSPACE_CONFIG=:4096:8'")
