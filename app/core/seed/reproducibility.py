"""DriftAdapt Reproducibility Module.

Author: DriftAdapt Contributors
Purpose: Checks PYTHONHASHSEED environment variables to verify start-time hash seed alignments.
Future Integration: Invoked at startup to warn researchers of potential hash non-determinism.
"""

import os
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger("Reproducibility")


def check_hash_seed_compliance(target_seed: int) -> bool:
    """Checks if the host interpreter has been booted with matching PYTHONHASHSEED.

    Logs a warning if unset or mismatching, explaining how to configure it.
    """
    hash_seed_str = os.environ.get("PYTHONHASHSEED")
    if hash_seed_str is None:
        logger.warning(
            "PYTHONHASHSEED is not set in the environment! "
            "Dict iterations and sets order will be non-deterministic. "
            f"To ensure total reproducibility, set environment variable 'PYTHONHASHSEED={target_seed}' "
            "before launching the Python interpreter process."
        )
        return False

    try:
        hash_seed_val = int(hash_seed_str)
        if hash_seed_val != target_seed:
            logger.warning(
                f"PYTHONHASHSEED environment variable is set to '{hash_seed_val}' but the requested seed is '{target_seed}'! "
                f"Please update 'PYTHONHASHSEED={target_seed}' before running for strict alignment."
            )
            return False
    except ValueError:
        logger.warning(
            f"PYTHONHASHSEED is set to an invalid non-integer string: '{hash_seed_str}'. "
            f"Please set 'PYTHONHASHSEED={target_seed}' to restore determinism."
        )
        return False

    return True
