"""DriftAdapt CPU Manager Module.

Author: DriftAdapt Contributors
Purpose: Resolves CPU name, architecture, core counts, and frequencies.
Future Integration: Invoked by DeviceManager and CPUMonitor.
"""

import os
import platform
import subprocess

from app.core.device.device_info import CPUInfo

try:
    import psutil
except ImportError:
    psutil = None


class CPUManager:
    """Manages CPU hardware detection, core counts, threads, and current load."""

    @staticmethod
    def get_cpu_name() -> str:
        """Gathers the CPU processor name (e.g. Intel Core i7, AMD Ryzen 5)."""
        system = platform.system()
        if system == "Windows":
            try:
                # Use registry query for Windows
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                )
                name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                return str(name).strip()
            except Exception:
                return platform.processor() or "Unknown CPU"
        elif system == "Darwin":
            try:
                # Use sysctl on macOS
                return subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"]
                ).decode().strip()
            except Exception:
                return platform.processor() or "Apple Silicon"
        elif system == "Linux":
            try:
                # Read /proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            except Exception:
                return platform.processor() or "Linux CPU"
        return platform.processor() or "Unknown CPU"

    @classmethod
    def get_cpu_info(cls) -> CPUInfo:
        """Gathers and returns complete CPUInfo details."""
        arch = platform.machine()
        physical_cores = 1
        logical_threads = 1
        max_freq = 0.0
        curr_freq = 0.0

        if psutil is not None:
            physical_cores = psutil.cpu_count(logical=False) or 1
            logical_threads = psutil.cpu_count(logical=True) or 1
            try:
                freq = psutil.cpu_freq()
                if freq:
                    max_freq = freq.max
                    curr_freq = freq.current
            except Exception:
                pass
        else:
            logical_threads = os.cpu_count() or 1
            physical_cores = logical_threads  # fallback matching

        return CPUInfo(
            name=cls.get_cpu_name(),
            architecture=arch,
            physical_cores=physical_cores,
            logical_threads=logical_threads,
            max_frequency_mhz=max_freq,
            current_frequency_mhz=curr_freq,
        )

    @staticmethod
    def get_current_utilization() -> float:
        """Returns current CPU utilization percentage."""
        if psutil is not None:
            return float(psutil.cpu_percent(interval=None))
        return 0.0
