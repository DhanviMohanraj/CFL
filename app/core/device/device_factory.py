"""DriftAdapt Device Factory Module.

Author: DriftAdapt Contributors
Purpose: Parses configuration strings and returns torch.device objects.
Future Integration: Invoked by DeviceManager to create execution devices.
"""

import torch

from app.core.runtime.exceptions import InvalidDeviceError


class DeviceFactory:
    """Factory creating and configuring PyTorch execution devices (CPU, CUDA, MPS, TPU)."""

    @staticmethod
    def create_device(device_str: str) -> torch.device:
        """Parses device name string and returns matching torch.device instance.

        Supported types: 'cpu', 'cuda', 'cuda:X', 'mps', 'tpu'.

        Raises:
            InvalidDeviceError: If target backend is requested but unavailable or incorrect.
        """
        device_lower = device_str.lower().strip()

        # 1. CPU device
        if device_lower == "cpu":
            return torch.device("cpu")

        # 2. CUDA device
        elif device_lower.startswith("cuda"):
            if not torch.cuda.is_available():
                raise InvalidDeviceError(
                    "CUDA device requested but NVIDIA CUDA drivers or hardware is unavailable. "
                    "Please verify CUDA Toolkit installations or run on 'cpu'."
                )
            try:
                return torch.device(device_lower)
            except Exception as e:
                raise InvalidDeviceError(
                    f"Invalid CUDA device format '{device_str}': {e}. Use format 'cuda' or 'cuda:0'."
                ) from e

        # 3. Apple Silicon MPS device
        elif device_lower == "mps":
            # Check PyTorch backend availability
            if not hasattr(torch.backends, "mps") or not torch.backends.mps.is_available():
                raise InvalidDeviceError(
                    "MPS device requested but Apple Silicon Metal Performance Shaders (MPS) "
                    "backend is not supported or active on this platform. Fallback to 'cpu'."
                )
            return torch.device("mps")

        # 4. TPU device (interface only)
        elif device_lower == "tpu":
            # torch_xla is required for TPU in PyTorch. For now, raise interface error.
            raise InvalidDeviceError(
                "TPU device requested but torch_xla package is not installed. "
                "TPU execution is currently supported as an interface only. Install 'torch_xla'."
            )

        else:
            raise InvalidDeviceError(
                f"Requested device '{device_str}' is unrecognized. "
                " DriftAdapt supports: 'cpu', 'cuda', 'cuda:<index>', 'mps', 'tpu'."
            )
