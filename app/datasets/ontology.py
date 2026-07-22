"""
Condition Ontology Mapper.
Maps raw medical QA items onto 16 CHW condition categories based on keywords and MeSH terms.
Logs mapping coverage and unmapped item discard rates.
"""

import os
import re
import yaml
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class ConditionOntology:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "configs", "ontology.yaml"
            )
        config_path = os.path.abspath(config_path)
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        self.version = data.get("version", "1.0")
        self.conditions = data.get("conditions", [])
        self.condition_map = {c["id"]: c for c in self.conditions}
        
    def classify_item(self, item: Dict[str, Any]) -> List[str]:
        """
        Classifies a single QA item into 1 or more condition IDs.
        Matches against question text, options, and explanation.
        """
        text = (
            item.get("question", "") + " " +
            " ".join(item.get("options", [])) + " " +
            item.get("explanation", "")
        ).lower()
        
        matched_ids = []
        for cond in self.conditions:
            cond_id = cond["id"]
            keywords = cond.get("keywords", [])
            for kw in keywords:
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, text):
                    matched_ids.append(cond_id)
                    break
        
        return matched_ids

    def map_corpus(self, items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Maps a list of items to the ontology.
        Attaches 'condition_ids' to mapped items.
        Returns (mapped_items, metrics_summary).
        """
        mapped_items = []
        unmapped_count = 0
        total_count = len(items)
        condition_counts = {c["id"]: 0 for c in self.conditions}

        for item in items:
            c_ids = self.classify_item(item)
            if c_ids:
                item_copy = dict(item)
                item_copy["condition_ids"] = c_ids
                mapped_items.append(item_copy)
                for cid in c_ids:
                    condition_counts[cid] += 1
            else:
                unmapped_count += 1

        coverage_rate = (len(mapped_items) / total_count * 100.0) if total_count > 0 else 0.0
        discard_rate = (unmapped_count / total_count * 100.0) if total_count > 0 else 0.0

        metrics = {
            "total_items": total_count,
            "mapped_items": len(mapped_items),
            "unmapped_discarded": unmapped_count,
            "coverage_rate_percent": round(coverage_rate, 2),
            "discard_rate_percent": round(discard_rate, 2),
            "condition_distribution": condition_counts
        }

        logger.info(
            f"Ontology Mapping complete. Coverage: {metrics['coverage_rate_percent']}%, "
            f"Discard Rate: {metrics['discard_rate_percent']}%"
        )
        return mapped_items, metrics
