"""Tests for Adapter Exporter.

Author: DriftAdapt Contributors
"""

import os
import pytest
from app.training.adapter_exporter import AdapterExporter


def test_adapter_exporter(tmp_path):
    exporter = AdapterExporter(export_dir=str(tmp_path))
    
    metadata = {"clinic_id": "clinic_01"}
    path = exporter.export_adapter("trainer_1", {}, metadata)
    
    assert path.endswith("trainer_1_adapter.pt")
    assert "checksum" in metadata
