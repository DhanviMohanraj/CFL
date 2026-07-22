# DriftAdapt Production Deployment Guide

## Running with Uvicorn ASGI Server

### 1. Direct Python Launch
```bash
# Start Uvicorn production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Launch via Main Script
```bash
python -m app.main
```

---

## Health & Readiness Probe Configuration

For Kubernetes or Docker Compose setups:
- **Liveness Probe**: `GET http://localhost:8000/health` (Interval: 30s)
- **Readiness Probe**: `GET http://localhost:8000/ready` (Interval: 5s, initialDelay: 10s)

---

## Environment Variable Configuration

```bash
# Production environment overrides
export DRIFTADAPT__SYSTEM__ENVIRONMENT=production
export DRIFTADAPT__SYSTEM__DEVICE=cuda
export DRIFTADAPT__MODEL__QUANTIZATION=4bit
export HF_HUB_OFFLINE=0
```
