"""
Seasonal Sampling Engine.
Parses per-month, per-region sampling distributions p(condition | month, region)
from configs/seasonal_curves.yaml to model regional epidemiological seasonality.
"""

import os
import yaml
import random
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SeasonalSampler:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "configs", "seasonal_curves.yaml"
            )
        config_path = os.path.abspath(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.regions = {r["id"]: r for r in data.get("regions", [])}

    def get_condition_distribution(self, region_id: str, month: int) -> Dict[str, float]:
        """
        Returns normalized probability vector p(condition | month, region) for month (1..12).
        """
        if region_id not in self.regions:
            raise ValueError(f"Unknown region_id '{region_id}'. Available: {list(self.regions.keys())}")
        if not (1 <= month <= 12):
            raise ValueError(f"Month must be 1..12, got {month}")

        base_weights = self.regions[region_id]["base_weights"]
        month_idx = month - 1

        probs = {}
        total = 0.0
        for cond_id, weights_12 in base_weights.items():
            w = weights_12[month_idx]
            probs[cond_id] = w
            total += w

        if total > 0:
            for cid in probs:
                probs[cid] /= total

        return probs

    def sample_items(
        self,
        mapped_pool: List[Dict[str, Any]],
        region_id: str,
        month: int,
        n_samples: int = 200,
        rng_seed: int = 42
    ) -> List[Dict[str, Any]]:
        """
        Samples n_samples from mapped_pool according to p(condition | month, region).
        """
        rng = random.Random(rng_seed + month * 100)
        cond_dist = self.get_condition_distribution(region_id, month)

        condition_buckets: Dict[str, List[Dict[str, Any]]] = {}
        for item in mapped_pool:
            for cid in item.get("condition_ids", []):
                condition_buckets.setdefault(cid, []).append(item)

        sampled_items = []
        cond_ids = list(cond_dist.keys())
        weights = [cond_dist[cid] for cid in cond_ids]

        for _ in range(n_samples):
            target_cid = rng.choices(cond_ids, weights=weights, k=1)[0]
            candidates = condition_buckets.get(target_cid, [])
            if candidates:
                item = rng.choice(candidates)
            else:
                item = rng.choice(mapped_pool)
            sampled_items.append(dict(item))

        return sampled_items
