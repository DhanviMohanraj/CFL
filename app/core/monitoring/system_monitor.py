"""DriftAdapt System Monitor Module.

Author: DriftAdapt Contributors
Purpose: Orchestrates hardware utilization polling, manages local history, and calculates average/peak loads.
Future Integration: Invoked by training loop metrics publishers and platform dashboard engines.
"""

from collections import deque
import shutil
import threading
import time
from typing import Dict, Any, List, Optional

from app.core.config.loader import get_project_root
from app.core.monitoring.cpu_monitor import CPUMonitor
from app.core.monitoring.gpu_monitor import GPUMonitor
from app.core.monitoring.memory_monitor import MemoryMonitor
from app.core.monitoring.process_monitor import ProcessMonitor


class SystemMonitor:
    """Singleton coordinator capturing CPU, GPU, RAM, Process, and Disk telemetry."""

    _instance: Optional["SystemMonitor"] = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "SystemMonitor":
        """Thread-safe instantiation for singleton caching."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, history_limit: int = 1000) -> None:
        """Initializes internal locks, snapshots deques, and time counters."""
        if getattr(self, "_initialized", False):
            return

        self._history_limit = history_limit
        self._history: deque = deque(maxlen=history_limit)
        self._lock = threading.Lock()
        self._initialized = True

    def get_snapshot(self) -> Dict[str, Any]:
        """Queries CPU, GPU, RAM, Disk, Process, and Network states to form a telemetry snapshot."""
        # 1. Disk usage of project root partition
        root_path = get_project_root()
        disk_total_gb = 0.0
        disk_free_gb = 0.0
        disk_used_gb = 0.0
        disk_percent = 0.0
        try:
            total, used, free = shutil.disk_usage(root_path)
            disk_total_gb = total / (1024**3)
            disk_free_gb = free / (1024**3)
            disk_used_gb = used / (1024**3)
            disk_percent = (used / total) * 100
        except Exception:
            pass

        # 2. Network Usage placeholder
        network_snap = {
            "bytes_sent": 0,
            "bytes_received": 0,
            "latency_ms": 0.0,
        }

        # 3. Pull from individual monitors
        cpu_snap = CPUMonitor.get_snapshot()
        gpu_snap = GPUMonitor.get_snapshot()
        mem_snap = MemoryMonitor.get_snapshot()
        proc_snap = ProcessMonitor.get_snapshot()

        return {
            "timestamp": time.time(),
            "cpu": cpu_snap,
            "gpu": gpu_snap,
            "memory": mem_snap,
            "process": proc_snap,
            "disk": {
                "total_gb": round(disk_total_gb, 2),
                "used_gb": round(disk_used_gb, 2),
                "free_gb": round(disk_free_gb, 2),
                "utilization_percent": round(disk_percent, 2),
            },
            "network": network_snap,
        }

    def record_snapshot(self) -> Dict[str, Any]:
        """Captures a snapshot and appends it to the historical deque in a thread-safe manner."""
        snap = self.get_snapshot()
        with self._lock:
            self._history.append(snap)
        return snap

    def get_historical_snapshots(self) -> List[Dict[str, Any]]:
        """Returns a list of all recorded history snapshots."""
        with self._lock:
            return list(self._history)

    def clear_history(self) -> None:
        """Clears all historical snapshots."""
        with self._lock:
            self._history.clear()

    def get_average_usage(self) -> Dict[str, float]:
        """Calculates arithmetic averages of key resource loads over the historical timeline."""
        with self._lock:
            snapshots = list(self._history)

        if not snapshots:
            return {
                "cpu_utilization_percent": 0.0,
                "gpu_allocated_memory_mb": 0.0,
                "ram_utilization_percent": 0.0,
                "process_memory_rss_mb": 0.0,
                "disk_utilization_percent": 0.0,
            }

        count = len(snapshots)
        cpu_sum = sum(s["cpu"]["utilization_percent"] for s in snapshots)
        gpu_sum = sum(s["gpu"]["allocated_memory_mb"] for s in snapshots)
        ram_sum = sum(s["memory"]["ram_utilization_percent"] for s in snapshots)
        proc_sum = sum(s["process"]["memory_rss_mb"] for s in snapshots)
        disk_sum = sum(s["disk"]["utilization_percent"] for s in snapshots)

        return {
            "cpu_utilization_percent": round(cpu_sum / count, 2),
            "gpu_allocated_memory_mb": round(gpu_sum / count, 2),
            "ram_utilization_percent": round(ram_sum / count, 2),
            "process_memory_rss_mb": round(proc_sum / count, 2),
            "disk_utilization_percent": round(disk_sum / count, 2),
        }

    def get_peak_usage(self) -> Dict[str, float]:
        """Retrieves peak (maximum) usage parameters across all cached snapshots."""
        with self._lock:
            snapshots = list(self._history)

        if not snapshots:
            return {
                "cpu_utilization_percent": 0.0,
                "gpu_allocated_memory_mb": 0.0,
                "ram_utilization_percent": 0.0,
                "process_memory_rss_mb": 0.0,
                "disk_utilization_percent": 0.0,
            }

        return {
            "cpu_utilization_percent": max(s["cpu"]["utilization_percent"] for s in snapshots),
            "gpu_allocated_memory_mb": max(s["gpu"]["allocated_memory_mb"] for s in snapshots),
            "ram_utilization_percent": max(s["memory"]["ram_utilization_percent"] for s in snapshots),
            "process_memory_rss_mb": max(s["process"]["memory_rss_mb"] for s in snapshots),
            "disk_utilization_percent": max(s["disk"]["utilization_percent"] for s in snapshots),
        }
