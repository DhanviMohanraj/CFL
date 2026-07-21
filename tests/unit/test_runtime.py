"""DriftAdapt Runtime and Device Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies environment details, CPU/GPU managers, seed determinism, and RuntimeInitializer.
Future Integration: Executed as part of the test suite in CI.
"""

import os
import random
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
import torch

from app.core.config import ConfigManager
from app.core.device import (
    DeviceManager,
    DeviceFactory,
    CPUManager,
    GPUManager,
    MemoryManager,
)
from app.core.metrics import MetricsBus
from app.core.runtime import (
    RuntimeManager,
    EnvironmentManager,
    DependencyChecker,
    RuntimeInitializer,
    InvalidDeviceError,
    DependencyMissingError,
)
from app.core.seed import SeedManager


def test_environment_manager() -> None:
    """Verifies that EnvironmentManager resolves core operating system and directories properties."""
    os_name = EnvironmentManager.get_os()
    py_version = EnvironmentManager.get_python_version()
    username = EnvironmentManager.get_username()
    root = EnvironmentManager.get_project_root_dir()
    disk = EnvironmentManager.get_available_disk_space()
    snap = EnvironmentManager.get_environment_snapshot()

    assert isinstance(os_name, str)
    assert isinstance(py_version, str)
    assert isinstance(username, str)
    assert isinstance(root, Path)
    assert root.exists()
    assert disk >= 0

    assert snap["os"] == os_name
    assert snap["python_version"] == py_version
    assert isinstance(snap["directory_verification"], dict)
    assert snap["directory_verification"]["configs"] is True


def test_dependency_checker() -> None:
    """Verifies that DependencyChecker checks present and missing modules without crashing."""
    success, missing, diagnostics = DependencyChecker.verify_dependencies()

    assert isinstance(success, bool)
    assert isinstance(missing, list)
    assert isinstance(diagnostics, dict)

    # Core dependencies like pydantic, loguru, pytest are guaranteed to be present as we just installed them
    assert "pydantic" in diagnostics
    assert diagnostics["pydantic"]["status"] == "OK"
    assert "version" in diagnostics["pydantic"]

    summary = DependencyChecker.get_summary_report()
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_cpu_and_memory_managers() -> None:
    """Verifies CPU and RAM specifications and load states."""
    cpu_info = CPUManager.get_cpu_info()
    cpu_util = CPUManager.get_current_utilization()

    assert isinstance(cpu_info.name, str)
    assert cpu_info.physical_cores >= 1
    assert cpu_info.logical_threads >= 1
    assert cpu_util >= 0.0

    mem_info = MemoryManager.get_memory_info()
    assert mem_info.total_ram_gb > 0.0
    assert mem_info.available_ram_gb >= 0.0
    assert mem_info.used_ram_gb >= 0.0
    assert mem_info.total_swap_gb >= 0.0


def test_gpu_manager() -> None:
    """Verifies GPU CUDA capacity checks."""
    cuda_avail = GPUManager.is_cuda_available()
    count = GPUManager.get_gpu_count()
    gpus = GPUManager.get_gpus_info()

    assert isinstance(cuda_avail, bool)
    assert count >= 0
    assert isinstance(gpus, list)

    if cuda_avail:
        assert count > 0
        assert len(gpus) == count
        assert gpus[0].total_memory_mb > 0.0
        assert gpus[0].vendor == "NVIDIA"
        assert GPUManager.get_current_gpu_index() >= 0
    else:
        assert count == 0
        assert len(gpus) == 0
        assert GPUManager.get_current_gpu_index() == -1


def test_seed_reproducibility() -> None:
    """Verifies that setting a global seed yields identical selections across executions."""
    # Run 1
    SeedManager.set_seed(42, deterministic=False)
    val1_py = random.random()
    val1_np = np.random.rand()
    val1_pt = torch.rand(1).item()

    # Run 2
    SeedManager.set_seed(42, deterministic=False)
    val2_py = random.random()
    val2_np = np.random.rand()
    val2_pt = torch.rand(1).item()

    assert val1_py == val2_py
    assert val1_np == val2_np
    assert val1_pt == val2_pt

    # Different seed should yield different values
    SeedManager.set_seed(100, deterministic=False)
    val3_py = random.random()
    assert val1_py != val3_py


def test_device_factory_and_manager() -> None:
    """Verifies device allocations, auto-selection, and fallback conditions."""
    cpu_device = DeviceFactory.create_device("cpu")
    assert str(cpu_device) == "cpu"

    # Requesting an invalid device name should raise InvalidDeviceError
    with pytest.raises(InvalidDeviceError):
        DeviceFactory.create_device("invalid_device_name_999")

    # Verify device manager auto fallback
    dev_mgr = DeviceManager()
    resolved = dev_mgr.resolve_device("invalid_device_name_999")
    assert isinstance(resolved, torch.device)

    summary = dev_mgr.get_hardware_summary()
    assert "cpu" in summary
    assert "memory" in summary


def test_runtime_manager_and_initializer() -> None:
    """Verifies complete bootstrap initialization and runtime reports."""
    # Ensure system configurations are clean
    config = ConfigManager().get_config()
    overrides = {"system": {"device": "cpu", "random_seed": 1337}}
    ConfigManager().apply_runtime_overrides(overrides)
    ConfigManager().refresh()

    # Execute initialization inside a mock patch for dependencies validation
    with patch("app.core.runtime.dependency_checker.DependencyChecker.verify_dependencies", return_value=(True, [], {})):
        manager = RuntimeManager()
        info = manager.initialize()

        assert info.project_name == config.system.project_name
        assert info.execution["device"] == "cpu"
        assert info.execution["random_seed"] == 1337

        # Check metrics bus integration (initialization time is published)
        bus = MetricsBus()
        init_time_metrics = bus.retrieve("runtime.initialization_time_ms")
        assert len(init_time_metrics) >= 1
        assert init_time_metrics[-1].value >= 0.0

        # Human-readable report
        text = info.get_summary_report()
        assert "DRIFTADAPT RUNTIME SUMMARY" in text
        assert "Hardware Overview" in text

    # Cleanup overrides
    ConfigManager().clear_overrides()
    ConfigManager().refresh()
