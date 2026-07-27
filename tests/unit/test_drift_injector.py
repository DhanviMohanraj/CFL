import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.datasets.drift_injector import DriftInjector

class TestDriftInjector(unittest.TestCase):
    def setUp(self):
        self.injector = DriftInjector(seed=42)

    def test_linguistic_drift_injection(self):
        sample_text = "A patient with dengue fever and high blood pressure presents with chills."
        transformed, rules = self.injector.inject_linguistic_drift(sample_text, drift_intensity=1.0)
        
        self.assertIn("breakbone fever", transformed.lower())
        self.assertIn("bp", transformed.lower())
        self.assertGreaterEqual(len(rules), 2)

    def test_protocol_drift_before_change_point(self):
        sample_text = "Treatment includes Chloroquine alone for malaria."
        transformed, rules = self.injector.inject_protocol_drift(sample_text, month=3, change_point_month=6)
        
        self.assertEqual(sample_text, transformed)
        self.assertEqual(len(rules), 0)

    def test_protocol_drift_at_change_point(self):
        sample_text = "Treatment includes Chloroquine alone for malaria."
        transformed, rules = self.injector.inject_protocol_drift(sample_text, month=6, change_point_month=6)
        
        self.assertIn("Artemisinin-based Combination Therapy", transformed)
        self.assertGreaterEqual(len(rules), 1)

    def test_deterministic_seed_reproducibility(self):
        injector1 = DriftInjector(seed=123)
        injector2 = DriftInjector(seed=123)

        item = {
            "question": "A patient with tuberculosis presents with cough and acid-fast bacilli in sputum.",
            "options": ["A: Isoniazid", "B: Penicillin"],
            "answer": "A",
            "explanation": "Standard treatment."
        }

        res1 = injector1.process_item(item, month=7, drift_intensity=0.8, item_index=5)
        res2 = injector2.process_item(item, month=7, drift_intensity=0.8, item_index=5)

        self.assertEqual(res1["question"], res2["question"])
        self.assertEqual(res1["drift_metadata"], res2["drift_metadata"])

if __name__ == "__main__":
    unittest.main()
