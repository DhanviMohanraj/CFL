"""DriftAdapt Personalization LoRA Default Configurations.

Author: DriftAdapt Contributors
Purpose: Provides production-ready dictionary representations of default configurations for the Personalization module.
"""

from typing import Dict, Any

DEFAULT_LORA_CONFIGURATION: Dict[str, Any] = {
    "adapter": {
        "name": "default_adapter",
        "version": "1.0",
        "description": "Default personalization adapter",
        "author": "DriftAdapt",
        "organization": "Research",
        "tags": ["healthcare", "personalization"]
    },
    "lora": {
        "rank": 16,
        "alpha": 32.0,
        "dropout": 0.05,
        "bias": "none",
        "task_type": "CAUSAL_LM",
        "inference_mode": False,
        "fan_in_fan_out": False,
        "modules_to_save": [],
        "init_lora_weights": True
    },
    "target_modules": {
        "modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    },
    "precision": {
        "dtype": "bfloat16",
        "mixed_precision": True,
        "gradient_checkpointing": True,
        "autocast": True
    },
    "storage": {
        "adapter_directory": "./models/adapters",
        "checkpoint_directory": "./models/checkpoints",
        "export_directory": "./models/exports",
        "temporary_directory": "/tmp/driftadapt",
        "cache_directory": "./models/cache"
    },
    "training": {
        "learning_rate": 2e-4,
        "batch_size": 4,
        "epochs": 3,
        "gradient_accumulation_steps": 4,
        "optimizer": "adamw_torch",
        "scheduler": "cosine",
        "warmup_ratio": 0.03,
        "weight_decay": 0.001,
        "gradient_clipping": True,
        "max_grad_norm": 1.0,
        "logging_steps": 10,
        "evaluation_steps": 50
    },
    "checkpoint": {
        "save_every": 100,
        "keep_last": 3,
        "save_optimizer": True,
        "save_scheduler": True,
        "resume_training": False,
        "export_format": "safetensors"
    },
    "logging": {
        "verbose": True,
        "log_parameter_count": True,
        "log_adapter_creation": True,
        "log_serialization": True,
        "log_validation": True
    },
    "validation": {
        "verify_target_modules": True,
        "verify_parameter_count": True,
        "verify_adapter_metadata": True,
        "verify_storage_paths": True,
        "verify_precision": True,
        "verify_task_type": True
    }
}
