# DriftAdapt Developer & Contributor Guide

## Quick Start Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Virtualenv package manager

### 2. Environment Initialization
```bash
# Clone the repository
git clone https://github.com/DhanviMohanraj/CFL.git
cd CFL

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install base and development dependencies
pip install -r requirements/dev.txt

# Run bootstrap folder initialization
python scripts/bootstrap.py
```

---

## Dependency Injection & Service Container

All application services are registered as singletons inside `ServiceContainer` ([app/container.py](file:///c:/Users/dhanv/OneDrive/Desktop/CFL/CFL/app/container.py#L19)). Endpoint handlers request dependencies via FastAPI `Depends()`:

```python
from fastapi import APIRouter, Depends
from app.dependencies import get_model_manager
from app.models.foundation import ModelManager

router = APIRouter()

@router.get("/my-endpoint")
def my_endpoint(model_mgr: ModelManager = Depends(get_model_manager)):
    model = model_mgr.get_model()
    return {"status": "ok"}
```

---

## Adding New API Routes

1. Create a new router file in `app/routes/feature_name.py`:
   ```python
   from fastapi import APIRouter
   router = APIRouter(tags=["Feature"])

   @router.get("/feature")
   def get_feature():
       return {"data": "value"}
   ```
2. Register router in `app/main.py`:
   ```python
   from app.routes.feature_name import router as feature_router
   application.include_router(feature_router)
   ```

---

## Extension Guidelines for Module 2 (LoRA Engine)

Module 2 (PEFT / LoRA Personalization Engine) will build directly on top of this backend:
1. **Query Frozen Foundation Model**: Call `ModelManager().get_model()` and `ModelManager().get_tokenizer()`.
2. **Attach LoRA Adapters**: Wrap base model using `get_peft_model(model, lora_config)`.
3. **Register LoRA Service**: Register `LoRAService` singleton in `ServiceContainer`.
