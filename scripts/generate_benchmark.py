"""
CLI Script to Generate or Verify the DriftHealth Benchmark Dataset.

Usage:
  python scripts/generate_benchmark.py --output_dir datasets --force_offline
  python scripts/generate_benchmark.py --output_dir datasets --verify_only
"""

import os
import sys
import json
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.datasets.benchmark_generator import generate_drift_health_benchmark, compute_sha256

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_benchmark")

def verify_benchmark(output_dir: str) -> bool:
    """Verifies existing benchmark against manifest.json SHA-256 checksums."""
    manifest_path = os.path.join(output_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error(f"Manifest file not found at '{manifest_path}'")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    checksums = manifest.get("checksums", {})
    all_valid = True
    logger.info(f"Verifying {len(checksums)} shards against SHA-256 checksums...")

    for rel_path, expected_sha in checksums.items():
        abs_path = os.path.join(output_dir, rel_path)
        if not os.path.exists(abs_path):
            logger.error(f"Missing file: {abs_path}")
            all_valid = False
            continue
        
        actual_sha = compute_sha256(abs_path)
        if actual_sha != expected_sha:
            logger.error(f"Checksum MISMATCH for {rel_path}! Expected: {expected_sha}, Got: {actual_sha}")
            all_valid = False

    if all_valid:
        logger.info("PASSED: All benchmark dataset shards are byte-identical and checksum verified!")
    else:
        logger.error("FAILED: Benchmark checksum verification failed.")
    return all_valid

def main():
    parser = argparse.ArgumentParser(description="DriftHealth Benchmark Generator & Verifier")
    parser.add_argument("--output_dir", type=str, default="datasets", help="Target output directory")
    parser.add_argument("--force_offline", action="store_true", help="Force offline synthetic data generator")
    parser.add_argument("--items_per_month", type=int, default=200, help="Number of items per clinic per month")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation")
    parser.add_argument("--verify_only", action="store_true", help="Verify existing dataset against manifest.json")

    args = parser.parse_args()

    if args.verify_only:
        success = verify_benchmark(args.output_dir)
        sys.exit(0 if success else 1)

    summary = generate_drift_health_benchmark(
        output_dir=args.output_dir,
        force_offline=args.force_offline,
        items_per_month=args.items_per_month,
        seed=args.seed
    )
    print("\n" + "=" * 60)
    print("DRIFTHEALTH BENCHMARK GENERATION COMPLETE")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print("=" * 60)

if __name__ == "__main__":
    main()
