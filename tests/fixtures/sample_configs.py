"""DriftAdapt Test Sample Configurations Fixture.

Author: DriftAdapt Contributors
Purpose: Provides standard configuration dictionaries for testing ConfigManager and system modules.
Future Integration: Imported by unit and integration tests.
"""

from typing import Any, Dict

SAMPLE_SYSTEM_CONFIG: Dict[str, Any] = {
    "project_name": "DriftAdapt-Test",
    "project_version": "0.1.0-test",
    "environment": "testing",
    "device": "cpu",
    "random_seed": 42,
    "deterministic": False,
    "debug": True,
}

SAMPLE_MODEL_CONFIG: Dict[str, Any] = {
    "foundation_model": "Qwen/Qwen2.5-3B-Instruct",
    "tokenizer": "Qwen/Qwen2.5-3B-Instruct",
    "max_seq_length": 512,
    "context_window": 2048,
    "quantization": "none",
    "precision": "float32",
    "cache_dir": "./models/cache",
    "use_cache": True,
}
