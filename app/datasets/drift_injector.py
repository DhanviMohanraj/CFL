"""
Drift Injector Component.
Applies deterministic linguistic and protocol drift transformations to medical text.
Built as an independent, testable module with fixed random seed reproducibility.
"""

import re
import random
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Documented Linguistic Drift Dictionary
LINGUISTIC_REPLACEMENTS = [
    (r"\b(dengue fever|dengue)\b", "breakbone fever (hadditod bukhar)"),
    (r"\b(malaria)\b", "judie bukhar (periodic chills fever)"),
    (r"\b(tuberculosis|tb)\b", "tapedik (chronic chest cough)"),
    (r"\b(cholera)\b", "haiza (rice-water diarrhea)"),
    (r"\b(typhoid fever|typhoid)\b", "miadi bukhar (step-ladder fever)"),
    (r"\b(scabies)\b", "khaj (night-itch burrows)"),
    (r"\b(hypertension)\b", "high BP (raktchap)"),
    (r"\b(diabetes)\b", "sugar illness (madhumeh)"),
    (r"\bblood pressure\b", "BP"),
    (r"\bplatelet count\b", "PLT count"),
    (r"\boral rehydration solution\b", "ORS sachet"),
    (r"\bacid-fast bacilli\b", "AFB smear"),
    (r"\bhemoglobin\b", "Hb level"),
]

# Documented Protocol Drift Rules (Applied at defined change points, e.g. post month 6)
PROTOCOL_REPLACEMENTS = [
    (r"\bChloroquine alone\b", "Artemisinin-based Combination Therapy (ACT)"),
    (r"\bStandard intensive phase for active pulmonary tuberculosis\b", "Updated National DOTS Protocol with Bedaquiline guidance"),
    (r"\bPeripheral Blood Smear\b", "Rapid Diagnostic Test (RDT) strip + Blood Smear"),
]

class DriftInjector:
    def __init__(self, seed: int = 42):
        self.seed = seed

    def inject_linguistic_drift(
        self,
        text: str,
        drift_intensity: float = 1.0,
        rng: Optional[random.Random] = None
    ) -> Tuple[str, List[str]]:
        """
        Injects linguistic drift (slang, code-mixing, abbreviations) into text.
        Returns (transformed_text, list_of_applied_rule_descriptions).
        """
        if rng is None:
            rng = random.Random(self.seed)

        applied_rules = []
        transformed = text

        for pattern, replacement in LINGUISTIC_REPLACEMENTS:
            if re.search(pattern, transformed, re.IGNORECASE):
                if rng.random() < drift_intensity:
                    transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
                    applied_rules.append(f"Linguistic: '{pattern}' -> '{replacement}'")

        return transformed, applied_rules

    def inject_protocol_drift(
        self,
        text: str,
        month: int,
        change_point_month: int = 6,
        rng: Optional[random.Random] = None
    ) -> Tuple[str, List[str]]:
        """
        Injects protocol drift if month >= change_point_month.
        Returns (transformed_text, list_of_applied_rule_descriptions).
        """
        if month < change_point_month:
            return text, []

        if rng is None:
            rng = random.Random(self.seed + month)

        applied_rules = []
        transformed = text

        for pattern, replacement in PROTOCOL_REPLACEMENTS:
            if re.search(pattern, transformed, re.IGNORECASE):
                transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
                applied_rules.append(f"Protocol (Month {month} >= {change_point_month}): '{pattern}' -> '{replacement}'")

        return transformed, applied_rules

    def process_item(
        self,
        item: Dict[str, Any],
        month: int,
        drift_intensity: float = 1.0,
        change_point_month: int = 6,
        item_index: int = 0
    ) -> Dict[str, Any]:
        """
        Processes a single item, injecting linguistic and protocol drift.
        Returns item with updated text fields and a 'drift_metadata' record.
        """
        rng = random.Random(self.seed + month * 1000 + item_index)
        item_copy = dict(item)

        orig_q = item_copy.get("question", "")
        q_ling, rules_q = self.inject_linguistic_drift(orig_q, drift_intensity, rng)
        q_final, rules_prot = self.inject_protocol_drift(q_ling, month, change_point_month, rng)

        item_copy["question"] = q_final
        item_copy["drift_metadata"] = {
            "month": month,
            "drift_intensity": drift_intensity,
            "change_point_month": change_point_month,
            "applied_rules": rules_q + rules_prot,
            "has_drift": len(rules_q + rules_prot) > 0
        }

        return item_copy
