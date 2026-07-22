"""Metadata Builder Service.

Author: DriftAdapt Contributors
Purpose: Automatically gathers hardware, software, and framework context for metadata schemas.
"""

import time
import platform
import psutil
from typing import Dict, Any

TORCH_VERSION: str = "unknown"
try:
    import torch
    TORCH_VERSION = str(torch.__version__)
except ImportError:
    pass

try:
    import transformers
    TRANSFORMERS_VERSION = transformers.__version__
except ImportError:
    TRANSFORMERS_VERSION = "unknown"

try:
    import peft
    PEFT_VERSION = peft.__version__
except ImportError:
    PEFT_VERSION = "unknown"

from app.schemas.update_metadata import UpdateMetadata


class MetadataBuilder:
    """Builds comprehensive metadata describing the device and framework environment."""

    @staticmethod
    def build_metadata(
        project_name: str,
        foundation_model: str,
        adapter_name: str,
        dataset_version: str,
        training_duration: float,
        personalization_round: int,
        software_version: str = "1.0.0"
    ) -> UpdateMetadata:
        """Constructs the UpdateMetadata schema with dynamically gathered environment data.
        
        Args:
            project_name: Project name.
            foundation_model: Base model identifier.
            adapter_name: LoRA adapter name.
            dataset_version: Version of the local dataset.
            training_duration: Training time in seconds.
            personalization_round: Current federated round.
            software_version: Application software version.
            
        Returns:
            A fully populated UpdateMetadata instance.
        """
        device_information: Dict[str, Any] = {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "cpu_cores": psutil.cpu_count(logical=True),
            "total_ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2)
        }
        
        if torch.cuda.is_available():
            device_information["gpu_name"] = torch.cuda.get_device_name(0)
            device_information["gpu_count"] = torch.cuda.device_count()
        else:
            device_information["gpu_name"] = "None"
            device_information["gpu_count"] = 0
            
        framework_versions = {
            "pytorch": TORCH_VERSION,
            "transformers": TRANSFORMERS_VERSION,
            "peft": PEFT_VERSION,
            "python": platform.python_version()
        }
        
        return UpdateMetadata(
            project_name=project_name,
            foundation_model=foundation_model,
            adapter_name=adapter_name,
            dataset_version=dataset_version,
            training_duration=training_duration,
            personalization_round=personalization_round,
            software_version=software_version,
            device_information=device_information,
            framework_versions=framework_versions,
            timestamp=time.time()
        )
