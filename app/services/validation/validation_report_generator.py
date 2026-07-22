"""Validation Report Generator Service.

Author: DriftAdapt Contributors
Purpose: Transforms raw validation results into formatted Markdown/JSON summaries.
"""

from typing import Dict, Any

from app.core.logging import LoggerFactory
from app.schemas.validation_result import ValidationResult


class ValidationReportGenerator:
    """Creates human-readable QA reports from systematic validation sweeps."""
    
    def __init__(self) -> None:
        self._logger = LoggerFactory.get_logger("ValidationReportGen")

    def generate_markdown(self, result: ValidationResult) -> str:
        """Formats the result as a Markdown report."""
        status_icon = "✅" if result.success else "❌"
        
        md = f"# DriftAdapt System Validation Report\n\n"
        md += f"**ID:** `{result.validation_id}`\n"
        md += f"**Overall Status:** {status_icon} `{result.validation_status}`\n"
        md += f"**Execution Time:** {result.execution_time:.2f}s\n\n"
        
        md += f"## Subsystem Health\n"
        md += f"- **Base Model:** `{result.model_status}`\n"
        md += f"- **PEFT Adapter:** `{result.adapter_status}`\n"
        md += f"- **Inference Pipeline:** `{result.inference_status}`\n"
        md += f"- **Structural Integrity:** `{result.integrity_status}`\n\n"
        
        if result.warnings:
            md += f"## Warnings\n"
            for w in result.warnings:
                md += f"- {w}\n"
                
        if result.errors:
            md += f"## Errors\n"
            for e in result.errors:
                md += f"- **{e}**\n"
                
        self._logger.info(f"Generated Markdown report for {result.validation_id}")
        return md

    def generate_json(self, result: ValidationResult) -> Dict[str, Any]:
        """Formats the result as a raw JSON dict."""
        return result.model_dump()
