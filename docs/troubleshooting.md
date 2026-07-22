# DriftAdapt Troubleshooting & Operational Guide

## Common Operational Issues & Resolutions

### 1. CUDA Fallback Warning
**Symptom**: `WARNING [DeviceManager] Preferred device 'cuda' failed validation... Falling back to best available hardware.`
**Cause**: NVIDIA CUDA drivers or GPU hardware are not available on host.
**Resolution**: System automatically defaults to `cpu`. If GPU is intended, verify CUDA Toolkit installation (`nvidia-smi`) and PyTorch CUDA build (`python -c "import torch; print(torch.cuda.is_available())"`).

---

### 2. Missing Core Dependencies Error
**Symptom**: `app.core.runtime.exceptions.DependencyMissingError` on startup.
**Cause**: One or more required packages are missing from the virtual environment.
**Resolution**: Run `pip install -r requirements/dev.txt` to install missing packages.

---

### 3. Model Cache Space Constraints
**Symptom**: `CacheError` or disk full errors during model loading.
**Resolution**: Use `CacheManager().clear_cache()` or clear local `models/cache/` directory.

---

### 4. Log Inspection Locations
- **Console Output**: Real-time loguru structured stdout streams.
- **Application File Logs**: Written to `logs/driftadapt.log` with size rotation.
- **Metrics File Logs**: Written to `metrics/metrics.log`.
