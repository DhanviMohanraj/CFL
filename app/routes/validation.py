"""Validation API Router.

Author: DriftAdapt Contributors
Purpose: Exposes endpoints for executing system validations and performance benchmarks.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    get_validation_engine,
    get_benchmark_engine,
    get_system_health_monitor,
    get_validation_history,
    get_validation_report_gen,
    get_benchmark_report_gen,
    get_model_integrity_checker
)
from app.schemas.validation_request import ValidationRequest
from app.schemas.validation_result import ValidationResult
from app.schemas.benchmark_request import BenchmarkRequest
from app.schemas.benchmark_result import BenchmarkResult
from app.schemas.system_health import SystemHealth
from app.schemas.integrity_report import IntegrityReport

from app.services.validation.validation_engine import ValidationEngine
from app.services.validation.benchmark_engine import BenchmarkEngine
from app.services.validation.system_health_monitor import SystemHealthMonitor
from app.services.validation.validation_history import ValidationHistory
from app.services.validation.validation_report_generator import ValidationReportGenerator
from app.services.validation.benchmark_report_generator import BenchmarkReportGenerator
from app.services.validation.model_integrity_checker import ModelIntegrityChecker


router = APIRouter(prefix="/validation", tags=["Validation & Benchmarking"])


@router.post("/run", response_model=ValidationResult, summary="Run a validation sweep")
async def run_validation(
    request: ValidationRequest,
    engine: ValidationEngine = Depends(get_validation_engine)
) -> ValidationResult:
    """Executes a full QA check on the model, adapters, and inference pipeline."""
    try:
        return engine.run_validation(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmark", response_model=BenchmarkResult, summary="Run performance benchmarks")
async def run_benchmark(
    request: BenchmarkRequest,
    engine: BenchmarkEngine = Depends(get_benchmark_engine)
) -> BenchmarkResult:
    """Measures latency, throughput, and memory consumption."""
    try:
        return engine.run_benchmark(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=SystemHealth, summary="Get system health snapshot")
async def get_health(
    monitor: SystemHealthMonitor = Depends(get_system_health_monitor)
) -> SystemHealth:
    """Returns real-time RAM, VRAM, and model status."""
    return monitor.get_health_snapshot()


@router.get("/integrity", response_model=IntegrityReport, summary="Get model integrity status")
async def get_integrity(
    checker: ModelIntegrityChecker = Depends(get_model_integrity_checker)
) -> IntegrityReport:
    """Scans the neural network for weight corruption or unauthorized gradients."""
    ok, report = checker.check_integrity()
    return report


@router.get("/history", summary="Get recent validation and benchmark history")
async def get_history(
    history: ValidationHistory = Depends(get_validation_history)
) -> Dict[str, Any]:
    """Returns the ledger of recent runs."""
    return {
        "validations": [v.model_dump() for v in history.get_recent_validations()],
        "benchmarks": [b.model_dump() for b in history.get_recent_benchmarks()]
    }


@router.get("/reports/latest-validation", summary="Get markdown report of last validation")
async def get_latest_validation_report(
    history: ValidationHistory = Depends(get_validation_history),
    report_gen: ValidationReportGenerator = Depends(get_validation_report_gen)
) -> Dict[str, str]:
    """Retrieves a human-readable summary of the last validation sweep."""
    runs = history.get_recent_validations(1)
    if not runs:
        raise HTTPException(status_code=404, detail="No validations found.")
    return {"report": report_gen.generate_markdown(runs[0])}


@router.get("/reports/latest-benchmark", summary="Get markdown report of last benchmark")
async def get_latest_benchmark_report(
    history: ValidationHistory = Depends(get_validation_history),
    report_gen: BenchmarkReportGenerator = Depends(get_benchmark_report_gen)
) -> Dict[str, str]:
    """Retrieves a human-readable summary of the last benchmark sweep."""
    runs = history.get_recent_benchmarks(1)
    if not runs:
        raise HTTPException(status_code=404, detail="No benchmarks found.")
    return {"report": report_gen.generate_markdown(runs[0])}
