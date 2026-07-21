"""DriftAdapt Process Monitor Module.

Author: DriftAdapt Contributors
Purpose: Exposes active Python process RAM footprints and uptime durations.
Future Integration: Invoked by SystemMonitor.
"""

import os
import time
from typing import Dict, Any

try:
    import psutil
except ImportError:
    psutil = None


class ProcessMonitor:
    """Monitors resource parameters of the current running process."""

    _start_time: float = time.time()

    @classmethod
    def get_snapshot(cls) -> Dict[str, Any]:
        """Collects memory footprint and uptime of the current Python process."""
        pid = os.getpid()
        rss_mb = 0.0
        cpu_percent = 0.0

        if psutil is not None:
            try:
                proc = psutil.Process(pid)
                # RSS memory in MB
                rss_mb = proc.memory_info().rss / (1024 * 1024)
                # CPU load of this process
                cpu_percent = proc.cpu_percent(interval=None)
            except Exception:
                pass

        uptime = time.time() - cls._start_time

        return {
            "pid": pid,
            "memory_rss_mb": round(rss_mb, 2),
            "cpu_utilization_percent": round(cpu_percent, 2),
            "runtime_seconds": round(uptime, 2),
        }
