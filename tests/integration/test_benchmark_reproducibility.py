import os
import sys
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.datasets.benchmark_generator import generate_drift_health_benchmark, compute_sha256

class TestBenchmarkReproducibility(unittest.TestCase):
    def setUp(self):
        self.tmp_dir_1 = tempfile.mkdtemp(prefix="drift_test_run1_")
        self.tmp_dir_2 = tempfile.mkdtemp(prefix="drift_test_run2_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir_1, ignore_errors=True)
        shutil.rmtree(self.tmp_dir_2, ignore_errors=True)

    def test_byte_identical_reproduction(self):
        summary1 = generate_drift_health_benchmark(
            output_dir=self.tmp_dir_1,
            force_offline=True,
            items_per_month=20,
            seed=42
        )

        summary2 = generate_drift_health_benchmark(
            output_dir=self.tmp_dir_2,
            force_offline=True,
            items_per_month=20,
            seed=42
        )

        manifest1_path = os.path.join(self.tmp_dir_1, "manifest.json")
        manifest2_path = os.path.join(self.tmp_dir_2, "manifest.json")

        with open(manifest1_path, "r", encoding="utf-8") as f:
            m1 = json.load(f)
        with open(manifest2_path, "r", encoding="utf-8") as f:
            m2 = json.load(f)

        checksums1 = m1["checksums"]
        checksums2 = m2["checksums"]

        self.assertEqual(set(checksums1.keys()), set(checksums2.keys()))

        for rel_path in checksums1:
            sha1 = checksums1[rel_path]
            sha2 = checksums2[rel_path]
            self.assertEqual(
                sha1, sha2,
                f"File '{rel_path}' failed byte-identical reproducibility! Run1: {sha1}, Run2: {sha2}"
            )

        print("\nPASSED: Benchmark generation is 100% byte-identical across independent runs!")

if __name__ == "__main__":
    unittest.main()
