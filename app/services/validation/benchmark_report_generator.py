"""Benchmark Report Generator Service.

Author: DriftAdapt Contributors
Purpose: Compiles raw latency and throughput metrics into readable summaries.
"""

from typing import Dict, Any

from app.core.logging import LoggerFactory
from app.schemas.benchmark_result import BenchmarkResult


class BenchmarkReportGenerator:
    """Produces performance summary reports from benchmark runs."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("BenchmarkReportGen")

    def generate_markdown(self, result: BenchmarkResult) -> str:
        """Formats the benchmark result as Markdown."""
        md = f"# DriftAdapt Performance Benchmark Report\n\n"
        md += f"**ID:** `{result.benchmark_id}`\n"
        md += f"**Type:** `{result.benchmark_type}`\n"
        md += f"**Total Runtime:** {result.execution_time:.2f}s\n\n"
        
        md += f"## Latency Metrics\n"
        md += f"- **Average:** {result.average_latency:.4f}s\n"
        md += f"- **Minimum:** {result.minimum_latency:.4f}s\n"
        md += f"- **Maximum:** {result.maximum_latency:.4f}s\n\n"
        
        md += f"## Throughput\n"
        md += f"- **Tokens/Second:** {result.throughput:.2f}\n\n"
        
        md += f"## Hardware Profiling\n"
        md += f"- **Peak RAM:** {result.memory_usage:.2f} MB\n"
        md += f"- **Peak VRAM:** {result.gpu_usage:.2f} MB\n"
        md += f"- **CPU Avg:** {result.cpu_usage:.1f}%\n"
        
        self._logger.info(f"Generated Markdown benchmark report for {result.benchmark_id}")
        return md

    def generate_json(self, result: BenchmarkResult) -> Dict[str, Any]:
        """Formats the benchmark result as JSON."""
        return result.model_dump()
