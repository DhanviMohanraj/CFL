"""DriftAdapt Training Monitor Service.

Author: DriftAdapt Contributors
Purpose: Exposes real-time throughput, ETA, and state tracking during an active training loop.
"""

import time
from typing import Dict, Any

from app.core.logging import LoggerFactory


class TrainingMonitor:
    """Service to track live training execution progress."""

    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("TrainingMonitor")
        self._start_time = 0.0
        self._total_steps = 0
        self._current_step = 0
        self._current_epoch = 0.0
        self._is_running = False

    def start(self, total_steps: int) -> None:
        """Initializes the monitor for a new training run."""
        self._start_time = time.perf_counter()
        self._total_steps = total_steps
        self._current_step = 0
        self._current_epoch = 0.0
        self._is_running = True
        self._logger.info(f"Training monitor started for {total_steps} total steps.")

    def update(self, current_step: int, current_epoch: float) -> None:
        """Updates current progress."""
        self._current_step = current_step
        self._current_epoch = current_epoch

    def stop(self) -> None:
        """Stops the monitor."""
        self._is_running = False
        duration = time.perf_counter() - self._start_time
        self._logger.info(f"Training monitor stopped. Total duration: {duration:.2f}s")

    def get_status(self) -> Dict[str, Any]:
        """Calculates current ETA and throughput.

        Returns:
            Dictionary containing progress stats.
        """
        if not self._is_running or self._current_step == 0:
            return {
                "running": self._is_running,
                "progress_percent": 0.0,
                "eta_seconds": 0.0,
                "throughput_steps_per_sec": 0.0,
                "current_epoch": self._current_epoch
            }

        elapsed = time.perf_counter() - self._start_time
        throughput = self._current_step / elapsed
        remaining_steps = self._total_steps - self._current_step
        eta = remaining_steps / throughput if throughput > 0 else 0.0

        return {
            "running": self._is_running,
            "progress_percent": (self._current_step / self._total_steps) * 100.0,
            "eta_seconds": eta,
            "throughput_steps_per_sec": throughput,
            "current_epoch": self._current_epoch
        }
