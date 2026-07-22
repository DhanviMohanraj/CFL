"""
Clinic Instantiation Sampler.
Simulates N (default 8) distinct Community Health Worker (CHW) clinics across 12 months.
Assigns region profiles, manages seasonal sampling, and applies drift profiles.
"""

import logging
from typing import List, Dict, Any

from app.datasets.seasonal import SeasonalSampler
from app.datasets.drift_injector import DriftInjector

logger = logging.getLogger(__name__)

DEFAULT_CLINIC_PROFILES = [
    {"clinic_id": "clinic_00", "name": "CHW Subcenter - Rural North (Delta)", "region_id": "region_north_monsoon", "drift_start_month": 4, "max_drift_intensity": 0.8},
    {"clinic_id": "clinic_01", "name": "CHW Subcenter - Coastal South", "region_id": "region_south_coastal", "drift_start_month": 6, "max_drift_intensity": 0.7},
    {"clinic_id": "clinic_02", "name": "CHW Subcenter - Western Desert", "region_id": "region_western_arid", "drift_start_month": 3, "max_drift_intensity": 0.9},
    {"clinic_id": "clinic_03", "name": "CHW Subcenter - Eastern Forest", "region_id": "region_eastern_hilly", "drift_start_month": 5, "max_drift_intensity": 0.85},
    {"clinic_id": "clinic_04", "name": "CHW Subcenter - North Peri-Urban", "region_id": "region_north_monsoon", "drift_start_month": 7, "max_drift_intensity": 0.6},
    {"clinic_id": "clinic_05", "name": "CHW Subcenter - South Inland", "region_id": "region_south_coastal", "drift_start_month": 5, "max_drift_intensity": 0.75},
    {"clinic_id": "clinic_06", "name": "CHW Subcenter - Western Rural", "region_id": "region_western_arid", "drift_start_month": 8, "max_drift_intensity": 0.5},
    {"clinic_id": "clinic_07", "name": "CHW Subcenter - Eastern Hill Tribe", "region_id": "region_eastern_hilly", "drift_start_month": 4, "max_drift_intensity": 0.95},
]

class ClinicSampler:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.seasonal_sampler = SeasonalSampler()
        self.drift_injector = DriftInjector(seed=seed)

    def generate_clinic_timeline(
        self,
        mapped_pool: List[Dict[str, Any]],
        clinic_profiles: List[Dict[str, Any]] = DEFAULT_CLINIC_PROFILES,
        num_months: int = 12,
        items_per_month: int = 200
    ) -> Dict[str, Dict[int, List[Dict[str, Any]]]]:
        """
        Generates month-by-month dataset shards for each clinic.
        Returns: { clinic_id: { month_1: [items], month_2: [items], ... } }
        """
        results = {}

        for profile in clinic_profiles:
            cid = profile["clinic_id"]
            region_id = profile["region_id"]
            drift_start = profile["drift_start_month"]
            max_drift = profile["max_drift_intensity"]

            results[cid] = {}
            logger.info(f"Generating timeline for Clinic [{cid}] ({profile['name']})")

            for month in range(1, num_months + 1):
                if month < drift_start:
                    drift_intensity = 0.0
                else:
                    ramp_steps = max(1, num_months - drift_start + 1)
                    step_idx = month - drift_start + 1
                    drift_intensity = min(max_drift, (step_idx / ramp_steps) * max_drift)

                raw_sampled = self.seasonal_sampler.sample_items(
                    mapped_pool=mapped_pool,
                    region_id=region_id,
                    month=month,
                    n_samples=items_per_month,
                    rng_seed=self.seed + hash(cid) % 10000 + month
                )

                drifted_items = []
                for idx, item in enumerate(raw_sampled):
                    d_item = self.drift_injector.process_item(
                        item=item,
                        month=month,
                        drift_intensity=drift_intensity,
                        change_point_month=drift_start,
                        item_index=idx
                    )
                    d_item["clinic_id"] = cid
                    d_item["month"] = month
                    drifted_items.append(d_item)

                results[cid][month] = drifted_items

        return results
