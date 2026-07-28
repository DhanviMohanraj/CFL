"""DriftAdapt LoRA Metadata Service.

Author: DriftAdapt Contributors
Purpose: Exposes adapter statistics formatting and query capabilities based on the registry.
"""

from typing import Dict, Any, List

from app.services.lora.adapter_registry import AdapterRegistry


class MetadataService:
    """Service generating detailed statistics and insights for registered adapters."""

    def __init__(self, registry: AdapterRegistry) -> None:
        """Initializes MetadataService.
        
        Args:
            registry: Injected AdapterRegistry instance.
        """
        self._registry = registry

    def get_adapter_statistics(self, adapter_id: str) -> Dict[str, Any]:
        """Calculates memory footprints, ratios, and summary metrics for an adapter.
        
        Args:
            adapter_id: The ID of the adapter to query.
            
        Returns:
            Dictionary containing statistics.
            
        Raises:
            KeyError: If adapter is not found.
        """
        adapter = self._registry.get_adapter(adapter_id)
        if not adapter:
            raise KeyError(f"Adapter ID '{adapter_id}' not found.")

        ratio = 0.0
        if adapter.parameter_count > 0:
            ratio = adapter.trainable_parameters / adapter.parameter_count

        return {
            "adapter_id": adapter.adapter_id,
            "adapter_name": adapter.adapter_name,
            "trainable_parameters": adapter.trainable_parameters,
            "total_parameters": adapter.parameter_count,
            "percentage_trainable": ratio * 100.0,
            "lora_efficiency_score": 1.0 / (ratio + 1e-9) if ratio > 0 else 0.0,
            "target_layers": len(adapter.target_modules),
            "initialization_timestamp": adapter.creation_timestamp
        }
        
    def list_all_statistics(self) -> List[Dict[str, Any]]:
        """Lists statistics for all registered adapters."""
        stats = []
        for adapter in self._registry.list_adapters():
            stats.append(self.get_adapter_statistics(adapter.adapter_id))
        return stats
