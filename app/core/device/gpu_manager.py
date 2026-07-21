"""DriftAdapt GPU Manager Module.

Author: DriftAdapt Contributors
Purpose: Detects CUDA status, names, vendors, compute capability, and memory states.
Future Integration: Invoked by DeviceManager and GPUMonitor.
"""

from typing import List, Tuple
from app.core.device.device_info import GPUInfo

try:
    import torch
except ImportError:
    torch = None


class GPUManager:
    """Manages graphics processor detection, memory parameters, and CUDA capabilities."""

    @staticmethod
    def is_cuda_available() -> bool:
        """Returns True if PyTorch detects active CUDA support."""
        if torch is not None:
            return bool(torch.cuda.is_available())
        return False

    @staticmethod
    def get_cuda_version() -> str:
        """Returns the active CUDA compiler version version tag."""
        if torch is not None and torch.cuda.is_available():
            return str(torch.version.cuda or "unknown")
        return "N/A"

    @staticmethod
    def get_gpu_count() -> int:
        """Returns total discrete graphics processors detected by PyTorch."""
        if torch is not None and torch.cuda.is_available():
            return int(torch.cuda.device_count())
        return 0

    @classmethod
    def get_gpus_info(cls) -> List[GPUInfo]:
        """Gathers and returns lists of active GPU specifications."""
        gpus: List[GPUInfo] = []
        if torch is None or not torch.cuda.is_available():
            return gpus

        count = torch.cuda.device_count()
        for idx in range(count):
            try:
                name = torch.cuda.get_device_name(idx)
                cap = torch.cuda.get_device_capability(idx)
                capability = f"{cap[0]}.{cap[1]}"

                # Retrieve memory (in bytes)
                free_bytes, total_bytes = torch.cuda.mem_get_info(idx)
                total_mb = total_bytes / (1024 * 1024)
                free_mb = free_bytes / (1024 * 1024)

                gpus.append(
                    GPUInfo(
                        index=idx,
                        name=name,
                        vendor="NVIDIA",
                        total_memory_mb=round(total_mb, 2),
                        available_memory_mb=round(free_mb, 2),
                        compute_capability=capability,
                    )
                )
            except Exception:
                # Fallback properties
                try:
                    props = torch.cuda.get_device_properties(idx)
                    total_mb = props.total_memory / (1024 * 1024)
                    gpus.append(
                        GPUInfo(
                            index=idx,
                            name=props.name,
                            vendor="NVIDIA",
                            total_memory_mb=round(total_mb, 2),
                            available_memory_mb=0.0,
                            compute_capability="unknown",
                        )
                    )
                except Exception:
                    pass
        return gpus

    @staticmethod
    def get_current_gpu_index() -> int:
        """Returns the index of the current active GPU device."""
        if torch is not None and torch.cuda.is_available():
            return int(torch.cuda.current_device())
        return -1
