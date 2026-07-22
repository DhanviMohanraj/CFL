"""DriftAdapt Device Info Data Models.

Author: DriftAdapt Contributors
Purpose: Strictly structures hardware properties (CPU, GPU, RAM) using Pydantic.
Future Integration: Exported by DeviceManager and SystemMonitor report functions.
"""

from pydantic import BaseModel


class CPUInfo(BaseModel):
    """Metadata detailing CPU architecture and specifications."""

    name: str
    architecture: str
    physical_cores: int
    logical_threads: int
    max_frequency_mhz: float
    current_frequency_mhz: float


class GPUInfo(BaseModel):
    """Metadata detailing graphics processor capabilities and memory states."""

    index: int
    name: str
    vendor: str
    total_memory_mb: float
    available_memory_mb: float
    compute_capability: str


class MemoryInfo(BaseModel):
    """Metadata detailing global RAM memory and swap availability."""

    total_ram_gb: float
    available_ram_gb: float
    used_ram_gb: float
    total_swap_gb: float
    available_swap_gb: float
