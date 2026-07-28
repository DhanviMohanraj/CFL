"""DriftAdapt Benchmarks Module.

Author: DriftAdapt Contributors
"""

from app.evaluation.benchmarks.base_benchmark import BaseBenchmark
from app.evaluation.benchmarks.medmcqa import MedMCQABenchmark
from app.evaluation.benchmarks.medqa import MedQABenchmark
from app.evaluation.benchmarks.pubmedqa import PubMedQABenchmark
from app.evaluation.benchmarks.chatdoctor import ChatDoctorBenchmark
from app.evaluation.benchmarks.synthetic_benchmark import SyntheticBenchmark

__all__ = [
    "BaseBenchmark",
    "MedMCQABenchmark",
    "MedQABenchmark",
    "PubMedQABenchmark",
    "ChatDoctorBenchmark",
    "SyntheticBenchmark"
]
