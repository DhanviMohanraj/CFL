"""
Clinic Instantiation Sampler.
Simulates N (default 4) distinct Community Health Worker (CHW) clinics across 12 months.
Assigns region profiles, manages seasonal sampling, and applies drift profiles.
"""

import logging
from typing import List, Dict, Any

from app.datasets.seasonal import SeasonalSampler
from app.datasets.drift_injector import DriftInjector

logger = logging.getLogger(__name__)

DEFAULT_CLINIC_PROFILES = [
    {
        "clinic_id": "clinic_00",
        "name": "Clinic 1 - Tropical Lowlands",
        "region_id": "region_tropical_lowlands",
        "drift_start_month": 7,
        "max_drift_intensity": 0.8
    },
    {
        "clinic_id": "clinic_01",
        "name": "Clinic 2 - Northern High Altitude",
        "region_id": "region_high_altitude",
        "drift_start_month": 11,
        "max_drift_intensity": 0.8
    },
    {
        "clinic_id": "clinic_02",
        "name": "Clinic 3 - Urban Slum / Flood-Prone",
        "region_id": "region_urban_slum",
        "drift_start_month": 5,
        "max_drift_intensity": 0.8
    },
    {
        "clinic_id": "clinic_03",
        "name": "Clinic 4 - Primary Health Center (Control Baseline)",
        "region_id": "region_phc_baseline",
        "drift_start_month": 6,
        "max_drift_intensity": 0.3
    },
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
