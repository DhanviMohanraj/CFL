# DriftAdapt Testing & Quality Assurance Guide

## Testing Philosophy
DriftAdapt uses pytest for unit, integration, and API testing. Fast test doubles and mock fixtures bypass multi-gigabyte model downloads and external hardware dependencies, allowing the full test suite to execute in under 10 seconds.

---

## Test Organization
- `tests/conftest.py`: Root pytest fixtures (`mock_dependencies`, `mock_foundation_factory`, `clean_config`, `api_test_client`).
- `tests/fixtures/`: Shared test data and PyTorch mock models (`mock_models.py`, `sample_configs.py`).
- `tests/unit/`: Component-level unit test modules ([test_config.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/unit/test_config.py), [test_logger.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/unit/test_logger.py), [test_metrics.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/unit/test_metrics.py), [test_runtime.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/unit/test_runtime.py), [test_model.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/unit/test_model.py)).
- `tests/integration/`: End-to-end lifespan startup/shutdown tests ([test_api.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/integration/test_api.py)).
- `tests/api/`: Dedicated API route tests ([test_health_api.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/api/test_health_api.py), [test_ready_api.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests/api/test_ready_api.py), etc.).

---

## Running Tests & Coverage Commands

```bash
# Run full pytest test suite
pytest

# Run tests with detailed coverage report
pytest --cov=app --cov-report=term-missing

# Run code style and syntax checks
flake8 . --exclude=.venv --count --select=E9,F63,F7,F82 --show-source --statistics

# Run static type validation
mypy app
```
