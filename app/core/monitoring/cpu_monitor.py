"""DriftAdapt CPU Monitor Module.

Author: DriftAdapt Contributors
Purpose: Exposes CPU load and frequencies polling.
Future Integration: Invoked by SystemMonitor.
"""

from typing import Any, Dict

from app.core.device.cpu_manager import CPUManager

try:
    import psutil
except ImportError:
    psutil = None


class CPUMonitor:
    """Monitors CPU usage statistics, load percentages, and frequencies."""

    @staticmethod
    def get_snapshot() -> Dict[str, Any]:
        """Collects current CPU utilization and performance stats."""
        cpu_info = CPUManager.get_cpu_info()

        util = CPUManager.get_current_utilization()

        return {
            "utilization_percent": util,
            "current_frequency_mhz": cpu_info.current_frequency_mhz,
            "max_frequency_mhz": cpu_info.max_frequency_mhz,
            "physical_cores": cpu_info.physical_cores,
            "logical_threads": cpu_info.logical_threads,
        }
