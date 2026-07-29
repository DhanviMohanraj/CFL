"""DriftAdapt Personalization Engine.

Author: DriftAdapt Contributors
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
from app.core.logging.logger_factory import LoggerFactory

class PersonalizationEngine:
    """Prepares the foundation model with the specific LoRA adapter for local training."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._logger = LoggerFactory.get_logger("PersonalizationEngine")
        
    def prepare_model(self) -> Tuple[nn.Module, Any]:
        """Loads foundation model, quantizes it, and attaches trainable LoRA."""
        
        model_name = self.config.get("model_name", "Qwen/Qwen2.5-1.5B-Instruct")
        self._logger.info(f"Loading tokenizer for {model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
            
        self._logger.info(f"Configuring NF4 Quantization for {model_name}")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        
        self._logger.info(f"Loading foundation model {model_name}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto"
        )
        
        model = prepare_model_for_kbit_training(model)
        
        lora_rank = self.config.get("lora_rank", 8)
        lora_alpha = self.config.get("lora_alpha", 16)
        lora_dropout = self.config.get("lora_dropout", 0.05)
        
        self._logger.info(f"Injecting LoRA with rank {lora_rank}, alpha {lora_alpha}")
        peft_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, peft_config)
        self._logger.info("Model preparation completed.")
        
        return model, tokenizer
