"""Tests for Local Trainer.

Author: DriftAdapt Contributors
"""

import torch
import pytest
from app.core.metrics.metrics_bus import MetricsBus
from app.training.local_trainer import LocalLoRATrainer
from app.training.training_state import TrainingState
import os
import json


@pytest.fixture
def dummy_dataset_dir(tmp_path):
    dataset_dir = tmp_path / "datasets"
    clinic_dir = dataset_dir / "clinic_test"
    clinic_dir.mkdir(parents=True)
    file_path = clinic_dir / "month_01.jsonl"
    
    with open(file_path, "w") as f:
        for i in range(10):
            f.write(json.dumps({
                "instruction": f"Diagnose this {i}",
                "input": "Patient has fever",
                "output": "Prescribe paracetamol"
            }) + "\n")
            
    return str(dataset_dir)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires GPU and CUDA for NF4 quantization")
def test_real_local_lora_training(dummy_dataset_dir):
    bus = MetricsBus()
    config = {
        "model_name": "Qwen/Qwen2.5-0.5B-Instruct", # Using 0.5B for faster test, or 1.5B
        "dataset_dir": dummy_dataset_dir,
        "output_dir": "./test_results",
        "batch_size": 2,
        "learning_rate": 2e-4,
        "epochs": 1,
        "fp16": True,
        "bf16": False,
        "lora_rank": 8,
        "lora_alpha": 16
    }
    
    trainer = LocalLoRATrainer("trainer_test", "clinic_test", 1, config, bus)
    
    assert trainer.status() == TrainingState.CREATED.value
    
    trainer.initialize()
    assert trainer.model is not None
    assert trainer.tokenizer is not None
    
    trainer.prepare()
    assert trainer.train_dataset is not None
    
    trainer.train()
    assert trainer.status() == TrainingState.COMPLETED.value
    
    path = trainer.export_adapter()
    assert os.path.exists(path)
    
    trainer.cleanup()
    assert trainer.model is None
