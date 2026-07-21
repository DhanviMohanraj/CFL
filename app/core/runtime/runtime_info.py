"""DriftAdapt Runtime Information Schema Module.

Author: DriftAdapt Contributors
Purpose: Outlines structured reports detailing OS, hardware specs, packages, and execution seeds.
Future Integration: Queried by other modules or experiment logging systems.
"""

from typing import Dict, Any, List
from pydantic import BaseModel


class RuntimeInfo(BaseModel):
    """Aggregate model representing a full snapshot of the DriftAdapt platform runtime state."""

    project_name: str
    project_version: str
    timestamp: float

    # Subsystem details
    environment: Dict[str, Any]
    hardware: Dict[str, Any]
    dependencies: Dict[str, Any]
    execution: Dict[str, Any]

    def get_summary_report(self) -> str:
        """Produces a human-readable text summary of the runtime environment."""
        lines = [
            "=" * 60,
            f"DRIFTADAPT RUNTIME SUMMARY - {self.project_name} v{self.project_version}",
            "=" * 60,
            f"Execution Device:  {self.execution.get('device')}",
            f"Random Seed:       {self.execution.get('random_seed')}",
            f"Deterministic Mode: {self.execution.get('deterministic')}",
            f"OS Platform:       {self.environment.get('platform')}",
            f"Python Version:    {self.environment.get('python_version')}",
            f"In Virtual Env:    {self.environment.get('is_virtual_env')}",
            f"Hostname:          {self.environment.get('hostname')}",
            "-" * 60,
            "Hardware Overview:",
            f"  CPU Model:       {self.hardware.get('cpu', {}).get('name')}",
            f"  CPU Cores/Threads: {self.hardware.get('cpu', {}).get('physical_cores')} cores / {self.hardware.get('cpu', {}).get('logical_threads')} threads",
            f"  System Memory:   {self.hardware.get('memory', {}).get('total_ram_gb')} GB RAM",
            f"  GPU Count:       {self.hardware.get('gpu_count')} device(s)",
        ]

        # Detailed GPUs
        for g in self.hardware.get("gpus", []):
            lines.append(
                f"    - GPU {g.get('index')}: {g.get('name')} ({g.get('total_memory_mb')} MB VRAM, CC {g.get('compute_capability')})"
            )

        lines.extend(
            [
                "-" * 60,
                "Dependency Checklist:",
                f"  All Verified:    {self.dependencies.get('all_verified')}",
                f"  Missing Count:   {len(self.dependencies.get('missing', []))}",
            ]
        )

        for pkg in self.dependencies.get("missing", []):
            lines.append(f"    [MISSING] {pkg}")

        lines.append("=" * 60)
        return "\n".join(lines)
