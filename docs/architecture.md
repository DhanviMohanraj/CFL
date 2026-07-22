# DriftAdapt System Architecture & Module Decomposition

## Executive Summary
**DriftAdapt** is a production-grade AI research platform designed for Continual Federated LoRA Personalization of Foundation Models for Privacy-Preserving Health Advisory Systems in Low-Resource Settings.

The Foundation Phase (Modules 1.1–1.7) establishes the core infrastructure, configuration framework, logging and telemetry bus, hardware device management, foundation model loader, and FastAPI application lifecycle.

---

## High-Level System Architecture

```
                                  ┌────────────────────────────────────────┐
                                  │          FastAPI Web Service           │
                                  │              (Module 1.6)              │
                                  └───────────────────┬────────────────────┘
                                                      │
                                                      ▼
                                  ┌────────────────────────────────────────┐
                                  │            ServiceContainer            │
                                  │       (Dependency Injection)           │
                                  └───────────────────┬────────────────────┘
                                                      │
            ┌─────────────────┬───────────────────────┼───────────────────────┬─────────────────┐
            ▼                 ▼                       ▼                       ▼                 ▼
   ┌─────────────────┐┌─────────────────┐   ┌───────────────────┐   ┌───────────────────┐┌───────────────┐
   │  ConfigManager  ││  LoggerFactory  │   │    MetricsBus     │   │   RuntimeManager  ││ ModelManager  │
   │  (Module 1.2)   ││  (Module 1.3)   │   │   (Module 1.3)    │   │   (Module 1.4)    ││ (Module 1.5)  │
   └─────────────────┘└─────────────────┘   └───────────────────┘   └───────────────────┘└───────────────┘
                                                                              │                 │
                                                                              ▼                 ▼
                                                                     ┌─────────────────┐┌───────────────┐
                                                                     │  DeviceManager  ││  ModelLoader  │
                                                                     │  SeedManager    ││ (Frozen Base) │
                                                                     │EnvironmentManager│└───────────────┘
                                                                     └─────────────────┘
```

---

## Module Breakdown (Foundation Phase)

### Module 1.1: Project Architecture & Repository Foundation
- Standardized directory tree structure ([app/](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app), [configs/](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/configs), [scripts/](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/scripts), [tests/](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/tests), [docs/](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/docs)).
- Environment bootstrapping script ([scripts/bootstrap.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/scripts/bootstrap.py)).
- Dependencies manifest setup (`requirements/base.txt`, `requirements/dev.txt`).

### Module 1.2: Configuration Management Framework
- YAML configuration loaders ([configs/system.yaml](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/configs/system.yaml), [configs/model.yaml](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/configs/model.yaml), etc.).
- Environment variable overrides (`DRIFTADAPT__*`) and `.env` loader.
- Pydantic schema validation (`AppConfig`, `SystemConfig`, `ModelConfig`, `TrainingConfig`, etc.).
- Thread-safe singleton [ConfigManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/config/config_manager.py#L22).

### Module 1.3: Logging Framework & Metrics Bus
- Multi-sink structured logging ([LoggerFactory](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/logging/logger_factory.py#L24)) via Loguru with console, file rotation, and split metrics logs.
- Centralized telemetry coordinator ([MetricsBus](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/metrics/metrics_bus.py#L46)) supporting in-memory caching, category validation, observer pub/sub events, async publishing queues, and background telemetry threads.

### Module 1.4: Device Manager, Environment Detection & Seed Manager
- [EnvironmentManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/runtime/environment.py#L18): OS platform, Python version, memory, and virtual environment detection.
- [DeviceManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/device/device_manager.py#L18): Hardware query and automatic CPU fallback resolution.
- [SeedManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/seed/seed_manager.py#L18): Seeding across Python `random`, `numpy`, `torch`, `torch.cuda`, and hash seeds.
- [RuntimeInitializer](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/core/runtime/startup.py#L20): Dependency verification and system boot report generator.

### Module 1.5: Foundation Model Management Framework
- Extensible model loader ([ModelLoader](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/model_loader.py#L26)) supporting Hugging Face causal models, tokenizer setup ([TokenizerLoader](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/tokenizer_loader.py#L21)), and model specifications ([ModelRegistry](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/model_registry.py#L86)).
- Quantization management ([QuantizationManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/quantization.py#L30)) for FP32, FP16, BF16, 4-bit NF4, and 8-bit.
- Cache management ([CacheManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/cache_manager.py#L18)) and download manager ([DownloadManager](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/models/foundation/download_manager.py#L22)).
- Zero parameter mutation: base weights strictly frozen (`requires_grad = False`, `.eval()`).

### Module 1.6: FastAPI Backend Backend Infrastructure
- Application lifespan pipeline ([app/lifecycle.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/lifecycle.py#L22)).
- Service Container DI ([app/container.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/container.py#L19) and [app/dependencies.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/dependencies.py#L14)).
- Middleware chain (`CorrelationIDMiddleware`, `RequestTimingMiddleware`, `RequestLoggingMiddleware`, `GlobalExceptionHandlerMiddleware`).
- REST Endpoints: `GET /health`, `GET /ready`, `GET /system`, `GET /model`.

---

## Core System Data Flows

```
[HTTP Client Request]
       │
       ▼
[CorrelationIDMiddleware] ──► Injects X-Request-ID
       │
       ▼
[RequestTimingMiddleware] ──► Injects X-Response-Time-MS
       │
       ▼
[RequestLoggingMiddleware] ──► Logs via LoggerFactory & publishes http.request_latency_ms
       │
       ▼
[FastAPI Route Handler] ──► Resolves service via Depends(get_*_manager)
       │
       ▼
[ServiceContainer Singleton] ──► Interacts with ConfigManager / ModelManager / DeviceManager
       │
       ▼
[HTTP Response Payload]
```
