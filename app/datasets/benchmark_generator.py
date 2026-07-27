"""
DriftHealth Benchmark Generator & Checksum Harness.
Generates frozen benchmark shards, SHA-256 checksum manifests,
drift ground-truth timeline, and dataset datasheet.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List

from app.datasets.loaders import load_all_corpora, CORPUS_LICENSES
from app.datasets.ontology import ConditionOntology
from app.datasets.sampler import ClinicSampler, DEFAULT_CLINIC_PROFILES

logger = logging.getLogger(__name__)

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_drift_health_benchmark(
    output_dir: str,
    force_offline: bool = False,
    items_per_month: int = 200,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Main orchestration function to build and freeze the DriftHealth benchmark dataset.
    """
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Clean up stale clinic directories from previous runs if present
    import shutil
    for entry in os.listdir(output_dir):
        if entry.startswith("clinic_"):
            item_path = os.path.join(output_dir, entry)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, ignore_errors=True)

    logger.info("Step 1/6: Loading raw medical corpora...")
    corpora = load_all_corpora(force_offline=force_offline)
    all_raw_items = []
    for c_name, items in corpora.items():
        all_raw_items.extend(items)

    logger.info("Step 2/6: Mapping items to CHW Condition Ontology...")
    ontology = ConditionOntology()
    mapped_pool, ontology_metrics = ontology.map_corpus(all_raw_items)

    logger.info("Step 3/6: Sampling clinic timelines across 12 months...")
    sampler = ClinicSampler(seed=seed)
    clinic_timelines = sampler.generate_clinic_timeline(
        mapped_pool=mapped_pool,
        clinic_profiles=DEFAULT_CLINIC_PROFILES,
        num_months=12,
        items_per_month=items_per_month
    )

    logger.info("Step 4/6: Writing frozen JSONL dataset shards...")
    manifest_checksums = {}
    drift_ground_truth = {"clinics": {}}

    for cid, months_dict in clinic_timelines.items():
        clinic_dir = os.path.join(output_dir, cid)
        os.makedirs(clinic_dir, exist_ok=True)
        
        profile_info = next((p for p in DEFAULT_CLINIC_PROFILES if p["clinic_id"] == cid), {})
        drift_ground_truth["clinics"][cid] = {
            "name": profile_info.get("name", ""),
            "region_id": profile_info.get("region_id", ""),
            "drift_start_month": profile_info.get("drift_start_month", 0),
            "max_drift_intensity": profile_info.get("max_drift_intensity", 0.0),
            "monthly_drift_records": {}
        }

        for month, items in months_dict.items():
            filename = f"month_{month:02d}.jsonl"
            rel_path = os.path.join(cid, filename)
            abs_path = os.path.join(clinic_dir, filename)

            with open(abs_path, "w", encoding="utf-8") as f:
                for item in items:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

            sha = compute_sha256(abs_path)
            manifest_checksums[rel_path] = sha

            drifted_item_count = sum(1 for item in items if item["drift_metadata"]["has_drift"])
            drift_ground_truth["clinics"][cid]["monthly_drift_records"][str(month)] = {
                "item_count": len(items),
                "drifted_item_count": drifted_item_count,
                "drift_fraction": round(drifted_item_count / len(items), 4),
                "drift_intensity": items[0]["drift_metadata"]["drift_intensity"]
            }

    logger.info("Step 5/6: Exporting manifests and ground-truth timeline...")
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark_name": "DriftHealth",
            "version": "1.0",
            "seed": seed,
            "items_per_month": items_per_month,
            "ontology_metrics": ontology_metrics,
            "checksums": manifest_checksums
        }, f, indent=2)

    gt_path = os.path.join(output_dir, "drift_ground_truth.json")
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(drift_ground_truth, f, indent=2)

    logger.info("Step 6/6: Generating DATASHEET.md...")
    datasheet_path = os.path.join(output_dir, "DATASHEET.md")
    write_datasheet(datasheet_path, ontology_metrics)

    summary = {
        "output_dir": output_dir,
        "total_shards": len(manifest_checksums),
        "total_items": len(manifest_checksums) * items_per_month,
        "ontology_coverage_percent": ontology_metrics["coverage_rate_percent"],
        "manifest_path": manifest_path,
        "ground_truth_path": gt_path,
        "datasheet_path": datasheet_path
    }
    logger.info(f"DriftHealth Benchmark successfully generated: {summary}")
    return summary

def write_datasheet(path: str, ontology_metrics: Dict[str, Any]):
    """Writes the standardized Datasheet for the dataset."""
    content = f"""# Datasheet for DriftHealth Benchmark

## 1. Motivation
- **Purpose**: DriftHealth is constructed to evaluate federated continual learning algorithms (DriftAdapt) under realistic spatial, seasonal, linguistic, and protocol concept drift across Community Health Worker (CHW) clinics.
- **Creators**: DriftAdapt Research Team.

## 2. Composition & Provenance
- **Raw Corpora**:
  - MedMCQA (License: {CORPUS_LICENSES['MedMCQA']})
  - MedQA (License: {CORPUS_LICENSES['MedQA']})
  - HealthCareMagic (License: {CORPUS_LICENSES['HealthCareMagic']})
  - MedDialog (License: {CORPUS_LICENSES['MedDialog']})
  - PubMedQA (License: {CORPUS_LICENSES['PubMedQA']})
- **Ontology Coverage**: {ontology_metrics.get('coverage_rate_percent', 0)}% mapped across 16 CHW condition categories.
- **Discard Rate**: {ontology_metrics.get('discard_rate_percent', 0)}% unmapped items discarded.

## 3. Structure & Simulation
- **Clinics**: 4 simulated CHW clinics assigned to 4 regional epidemiological profiles.
- **Time Horizon**: 12 monthly steps.
- **Items per Shard**: \u2265200 items per (clinic, month) pair.
- **Drift Injections**: Deterministic linguistic drift (local disease terms, code-mixing, clinical abbreviations) and step-change protocol drift.

## 4. Intended Use & Limitations
- **Intended Use**: Benchmarking federated continual learning, drift estimation, and concept drift mitigation models.
- **Limitations**: Synthetic sampling distributions modeled on epidemiological data; does not replace real clinical field trials.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
