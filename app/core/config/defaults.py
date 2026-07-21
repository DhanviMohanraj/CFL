"""DriftAdapt Config Defaults.

Author: DriftAdapt Contributors
Purpose: Exposes standard default dictionary structures for configurations fallback.
Future Integration: Merged by configuration loader if YAML files are partially or fully missing.
"""

from typing import Dict, Any

DEFAULT_SYSTEM_CONFIG: Dict[str, Any] = {
    "project_name": "DriftAdapt",
    "project_version": "0.1.0",
    "random_seed": 42,
    "device": "cuda",
    "logs_dir": "./logs",
    "experiments_dir": "./experiments",
    "checkpoints_dir": "./checkpoints",
    "datasets_dir": "./datasets",
    "num_workers": 4,
    "debug": False,
}

DEFAULT_MODEL_CONFIG: Dict[str, Any] = {
    "foundation_model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "tokenizer": "meta-llama/Meta-Llama-3-8B-Instruct",
    "max_seq_length": 512,
    "context_window": 2048,
    "quantization": "4bit",
    "precision": "bfloat16",
    "cache_dir": "./checkpoints/hf_cache",
    "use_cache": True,
}

DEFAULT_LORA_CONFIG: Dict[str, Any] = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "bias": "none",
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    "adapters_dir": "./checkpoints/adapters",
    "version": "v1.0",
}

DEFAULT_TRAINING_CONFIG: Dict[str, Any] = {
    "batch_size": 8,
    "epochs": 3,
    "optimizer": "adamw_torch",
    "learning_rate": 0.0002,
    "scheduler": "cosine",
    "gradient_accumulation_steps": 4,
    "mixed_precision": "bf16",
    "weight_decay": 0.01,
    "max_grad_norm": 1.0,
}

DEFAULT_FEDERATED_CONFIG: Dict[str, Any] = {
    "num_clients": 10,
    "participation_rate": 0.8,
    "algorithm": "fedavg",
    "num_rounds": 50,
    "local_epochs": 3,
    "client_timeout": 30.0,
    "communication_frequency": 1,
}

DEFAULT_DATASET_CONFIG: Dict[str, Any] = {
    "dataset_name": "MIMIC-IV-Advisory",
    "split_ratios": {
        "train": 0.7,
        "val": 0.1,
        "test": 0.2,
    },
    "clinic_partitions": 10,
    "season_partitions": ["summer", "rainy", "winter"],
    "shuffle": True,
    "stream_batch_size": 32,
}

DEFAULT_DRIFT_CONFIG: Dict[str, Any] = {
    "drift_detector": "adwin",
    "window_size": 200,
    "threshold": 0.01,
    "adaptation_threshold": 0.05,
    "sampling_interval": 10,
}

DEFAULT_EVALUATION_CONFIG: Dict[str, Any] = {
    "metrics": ["accuracy", "f1_score", "rouge_l", "bleu", "latency_ms"],
    "plots": ["loss_curves", "drift_alerts", "confusion_matrix"],
    "output_dir": "./experiments/results",
    "evaluation_frequency": 5,
}

DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    "log_level": "INFO",
    "console_logging": True,
    "file_logging": True,
    "rotation": "10 MB",
    "retention": "1 month",
}

DEFAULT_EXPERIMENT_CONFIG: Dict[str, Any] = {
    "experiment_name": "baseline_personalization",
    "tracker": "local",
    "tags": ["llama3", "fedavg", "adwin"],
    "description": "Baseline federated LoRA personalization run.",
}

DEFAULT_APP_CONFIG: Dict[str, Any] = {
    "system": DEFAULT_SYSTEM_CONFIG,
    "model": DEFAULT_MODEL_CONFIG,
    "lora": DEFAULT_LORA_CONFIG,
    "training": DEFAULT_TRAINING_CONFIG,
    "federated": DEFAULT_FEDERATED_CONFIG,
    "dataset": DEFAULT_DATASET_CONFIG,
    "drift": DEFAULT_DRIFT_CONFIG,
    "evaluation": DEFAULT_EVALUATION_CONFIG,
    "logging": DEFAULT_LOGGING_CONFIG,
    "experiment": DEFAULT_EXPERIMENT_CONFIG,
}
