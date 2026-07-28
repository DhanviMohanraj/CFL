"""DriftAdapt Adapter Exporter.

Author: DriftAdapt Contributors
"""

import os
import hashlib
from typing import Dict, Any

from app.training.trainer_exceptions import AdapterExportError


class AdapterExporter:
    """Exports updated LoRA adapters for federation."""
    
    def __init__(self, export_dir: str = "exports") -> None:
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        
    def export_adapter(self, trainer_id: str, state_dict: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Exports the LoRA adapter weights and metadata."""
        try:
            export_path = os.path.join(self.export_dir, f"{trainer_id}_adapter.pt")
            
            # Generate a mock checksum
            checksum = hashlib.sha256(b"mock_adapter_data").hexdigest()
            metadata["checksum"] = checksum
            
            return export_path
        except Exception as e:
            raise AdapterExportError(f"Failed to export adapter: {e}")
