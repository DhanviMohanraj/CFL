"""Cache Manager Service.

Author: DriftAdapt Contributors
Purpose: Resolves exact prompt matches using an adapter-aware caching mechanism.
"""

import hashlib
import time
from typing import Optional, Dict

from app.core.logging import LoggerFactory


class CacheEntry:
    """Internal cache structure."""
    def __init__(self, response_text: str, timestamp: float):
        self.response_text = response_text
        self.timestamp = timestamp


class CacheManager:
    """Adapter-aware exact-match cache for generated responses."""
    
    def __init__(self, ttl_seconds: float = 3600.0) -> None:
        self._logger = LoggerFactory.get_logger("CacheManager")
        self._ttl = ttl_seconds
        # Structure: { "adapter_id|None": { "prompt_hash": CacheEntry } }
        self._cache: Dict[str, Dict[str, CacheEntry]] = {}
        
    def _get_namespace(self, adapter_id: Optional[str]) -> str:
        return adapter_id if adapter_id else "BASE_MODEL"

    def _hash_prompt(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def check_cache(self, prompt: str, adapter_id: Optional[str]) -> Optional[str]:
        """Retrieves a cached response if valid.
        
        Args:
            prompt: The exact prompt text.
            adapter_id: The context adapter.
            
        Returns:
            The cached response text, or None if miss/expired.
        """
        namespace = self._get_namespace(adapter_id)
        if namespace not in self._cache:
            return None
            
        prompt_hash = self._hash_prompt(prompt)
        entry = self._cache[namespace].get(prompt_hash)
        
        if entry:
            if time.time() - entry.timestamp > self._ttl:
                # Expired
                del self._cache[namespace][prompt_hash]
                return None
            self._logger.debug(f"Cache hit for adapter {namespace}.")
            return entry.response_text
            
        return None

    def store_cache(self, prompt: str, response: str, adapter_id: Optional[str]) -> None:
        """Stores a generated response in the cache."""
        namespace = self._get_namespace(adapter_id)
        if namespace not in self._cache:
            self._cache[namespace] = {}
            
        prompt_hash = self._hash_prompt(prompt)
        self._cache[namespace][prompt_hash] = CacheEntry(response, time.time())
        self._logger.debug(f"Stored prompt in cache for adapter {namespace}.")

    def invalidate(self, adapter_id: Optional[str] = None) -> None:
        """Clears cache for a specific adapter, or entirely if None."""
        if adapter_id is None:
            self._cache.clear()
            self._logger.info("Cleared entire inference cache.")
        else:
            if adapter_id in self._cache:
                del self._cache[adapter_id]
                self._logger.info(f"Cleared cache for adapter {adapter_id}.")
