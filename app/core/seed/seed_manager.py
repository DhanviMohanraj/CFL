"""DriftAdapt Seed Manager Module.

Author: DriftAdapt Contributors
Purpose: Centralizes and sets seed allocations for Python, NumPy, and PyTorch (CPU and CUDA).
Future Integration: Invoked at startup to ensure reproducible experiment starts.
"""

import random
from typing import Optional
import numpy as np
import torch

from app.core.logging import LoggerFactory
from app.core.runtime.exceptions import SeedInitializationError
from app.core.seed.deterministic import configure_deterministic_execution
from app.core.seed.reproducibility import check_hash_seed_compliance

logger = LoggerFactory.get_logger("SeedManager")


class SeedManager:
    """Manages system seeds across all core libraries to maintain research reproducibility."""

    @classmethod
    def set_seed(cls, seed: int, deterministic: bool = False) -> None:
        """Sets random seeds for Python, NumPy, PyTorch CPU, and PyTorch CUDA.

        Args:
            seed: The integer seed value.
            deterministic: If True, configures CUDA/PyTorch deterministic flags.

        Raises:
            SeedInitializationError: If validation or assignment fails.
        """
        logger.info(f"Setting global random seeds to: {seed} (deterministic={deterministic})")

        try:
            # 1. Validate seed type and range
            if not isinstance(seed, int) or seed < 0:
                raise ValueError("Seed value must be a non-negative integer.")

            # 2. Python standard random library
            random.seed(seed)

            # 3. NumPy random library
            np.random.seed(seed)

            # 4. PyTorch CPU manual seed
            torch.manual_seed(seed)

            # 5. PyTorch CUDA manual seed (all GPUs)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)

            # 6. Check PYTHONHASHSEED compliance warning
            check_hash_seed_compliance(seed)

            # 7. Configure backend deterministic path
            if deterministic:
                configure_deterministic_execution(True)
            else:
                configure_deterministic_execution(False)

            logger.info("Global seeds set successfully across all random generators.")

        except Exception as e:
            raise SeedInitializationError(f"Failed to initialize random seeds: {e}") from e
