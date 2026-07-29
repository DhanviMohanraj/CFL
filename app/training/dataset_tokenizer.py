"""DriftAdapt Dataset Tokenizer.

Author: DriftAdapt Contributors
"""

from typing import Dict, Any
from datasets import Dataset

class DatasetTokenizer:
    """Tokenizes healthcare datasets."""
    
    def __init__(self, tokenizer: Any, config: Dict[str, Any]):
        self.tokenizer = tokenizer
        self.max_length = config.get("max_seq_length", 512)
        
    def tokenize(self, dataset: Dataset) -> Dataset:
        """Applies tokenization."""
        
        def tokenize_function(examples):
            # Assuming the dataset has a 'text' field or we format 'instruction', 'input', 'output'
            if 'text' in examples:
                texts = examples['text']
            elif 'instruction' in examples and 'output' in examples:
                texts = [
                    f"Instruction: {inst}\nInput: {inp}\nOutput: {out}"
                    for inst, inp, out in zip(examples.get('instruction', ['']*len(examples['output'])), examples.get('input', ['']*len(examples['output'])), examples['output'])
                ]
            else:
                texts = [""] * len(examples[list(examples.keys())[0]])
                
            return self.tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=self.max_length
            )
            
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        tokenized_dataset.set_format("torch")
        return tokenized_dataset
