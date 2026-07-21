"""DriftAdapt Environment Manager Module.

Author: DriftAdapt Contributors
Purpose: Automatically gathers platform details, timezone, disk space, and directory states.
Future Integration: Invoked during system startup initialization.
"""

import getpass
import os
import platform
import shutil
import socket
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config.loader import get_project_root


class EnvironmentManager:
    """Detects and reports operating system, shell, timezone, and project directories states."""

    @staticmethod
    def get_os() -> str:
        """Returns the operating system name (e.g. Windows, Linux, Darwin)."""
        return platform.system()

    @staticmethod
    def get_python_version() -> str:
        """Returns the Python version string."""
        return platform.python_version()

    @staticmethod
    def is_virtual_env() -> bool:
        """Returns True if the process runs inside a virtual environment (venv/conda)."""
        # standard virtual env checks
        in_venv = sys.prefix != sys.base_prefix
        in_conda = "CONDA_PREFIX" in os.environ
        return in_venv or in_conda

    @staticmethod
    def get_virtual_env_path() -> Optional[str]:
        """Returns path to the virtual env directory if present, else None."""
        if sys.prefix != sys.base_prefix:
            return sys.prefix
        return os.environ.get("CONDA_PREFIX")

    @staticmethod
    def get_project_root_dir() -> Path:
        """Returns the resolved project root directory."""
        return get_project_root()

    @staticmethod
    def get_hostname() -> str:
        """Returns the system hostname."""
        return socket.gethostname()

    @staticmethod
    def get_username() -> str:
        """Returns the user name under which this process is running."""
        try:
            return getpass.getuser()
        except Exception:
            return os.getenv("USER", os.getenv("USERNAME", "unknown"))

    @staticmethod
    def get_timezone() -> str:
        """Returns the current timezone name."""
        try:
            return time.tzname[0] if time.daylight == 0 else time.tzname[1]
        except Exception:
            return "UTC"

    @staticmethod
    def get_architecture() -> str:
        """Returns the hardware architecture (e.g. AMD64, arm64)."""
        return platform.machine()

    @staticmethod
    def get_platform() -> str:
        """Returns the detailed platform info description."""
        return platform.platform()

    @staticmethod
    def get_available_disk_space(path: Optional[Path] = None) -> int:
        """Returns the available disk space in bytes for the specified path (or project root)."""
        if path is None:
            path = get_project_root()
        try:
            total, used, free = shutil.disk_usage(path)
            return free
        except Exception:
            return 0

    @staticmethod
    def get_temp_dir() -> Path:
        """Returns the system temporary directory."""
        return Path(tempfile.gettempdir())

    @classmethod
    def verify_project_directories(cls) -> Dict[str, bool]:
        """Verifies that all required workspace folders exist.

        Expected: logs, checkpoints, datasets, experiments, configs
        """
        root = get_project_root()
        dirs = {
            "logs": root / "logs",
            "checkpoints": root / "checkpoints",
            "datasets": root / "datasets",
            "experiments": root / "experiments",
            "configs": root / "configs",
            "metrics": root / "metrics",
        }
        return {name: path.exists() and path.is_dir() for name, path in dirs.items()}

    @classmethod
    def get_environment_snapshot(cls) -> Dict[str, Any]:
        """Compiles a complete metadata report of the current environment state."""
        root = get_project_root()
        disk_free_gb = cls.get_available_disk_space(root) / (1024**3)

        return {
            "os": cls.get_os(),
            "python_version": cls.get_python_version(),
            "is_virtual_env": cls.is_virtual_env(),
            "virtual_env_path": cls.get_virtual_env_path(),
            "current_working_directory": str(Path.cwd()),
            "project_root": str(root),
            "hostname": cls.get_hostname(),
            "username": cls.get_username(),
            "timezone": cls.get_timezone(),
            "architecture": cls.get_architecture(),
            "platform": cls.get_platform(),
            "available_disk_space_gb": round(disk_free_gb, 2),
            "temp_directory": str(cls.get_temp_dir()),
            "directory_verification": cls.verify_project_directories(),
        }
