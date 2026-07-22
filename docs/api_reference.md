# DriftAdapt OpenAPI & REST API Reference

The DriftAdapt backend exposes interactive OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running.

---

## Headers & Tracing

All responses include performance and correlation headers:
- `X-Request-ID`: Unique UUID correlation trace string.
- `X-Response-Time-MS`: Request execution time in milliseconds.

---

## Core Endpoints

### 1. Application Health Probe
- **URL**: `GET /health`
- **Status Code**: `200 OK`
- **Description**: Returns application health status, version, uptime, and service container statuses.
- **Example Payload**:
```json
{
  "status": "HEALTHY",
  "project_name": "DriftAdapt",
  "project_version": "0.1.0",
  "timestamp": 1784712000.0,
  "uptime_seconds": 120.45,
  "is_ready": true,
  "services": {
    "config_manager": "HEALTHY",
    "metrics_bus": "HEALTHY",
    "device_manager": "HEALTHY",
    "runtime_manager": "HEALTHY",
    "model_manager": "HEALTHY",
    "logger_factory": "HEALTHY",
    "environment_manager": "HEALTHY",
    "seed_manager": "HEALTHY"
  }
}
```

---

### 2. Readiness Probe
- **URL**: `GET /ready`
- **Status Codes**:
  - `200 OK`: When application startup sequence is complete (`{"status": "READY"}`).
  - `503 Service Unavailable`: When startup is in progress or unready (`{"status": "NOT_READY"}`).
- **Description**: Used by Kubernetes / Docker load balancers to gate traffic.

---

### 3. System Runtime Diagnostics
- **URL**: `GET /system`
- **Status Code**: `200 OK`
- **Description**: Returns environment, hardware specifications, CPU cores, GPU specs, and target execution device.
- **Example Payload**:
```json
{
  "project_name": "DriftAdapt",
  "environment": {
    "os": "Windows-11-10.0.26200-SP0",
    "python_version": "3.12.5",
    "in_virtual_env": true,
    "hostname": "DriftAdapt-Node"
  },
  "hardware": {
    "cpu_model": "12th Gen Intel(R) Core(TM) i7-1255U",
    "cpu_cores_threads": "12 cores / 12 threads",
    "system_memory_gb": "8.0 GB RAM",
    "gpu_count": 0
  },
  "execution": {
    "device": "cpu",
    "random_seed": 42,
    "deterministic_mode": false
  }
}
```

---

### 4. Foundation Model Specifications
- **URL**: `GET /model`
- **Status Code**: `200 OK`
- **Description**: Returns model metadata, architecture, tokenizer, quantization, precision, and memory footprint in MB.
- **Example Payload**:
```json
{
  "model_name": "Qwen/Qwen2.5-3B-Instruct",
  "architecture": "Qwen2ForCausalLM",
  "parameter_count": 3090000000,
  "trainable_parameters": 0,
  "tokenizer_name": "Qwen/Qwen2.5-3B-Instruct",
  "vocab_size": 151936,
  "context_length": 32768,
  "hidden_size": 2048,
  "quantization_mode": "4bit",
  "precision": "bfloat16",
  "device": "cpu",
  "memory_footprint_mb": 1800.5,
  "load_time_seconds": 2.4,
  "is_frozen": true
}
```
