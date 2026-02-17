from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ModelInfo(BaseModel):
    model_name: str
    inference_type: str
    inference_class: str
    requires_gpu: Optional[bool] = True
    default_config: Optional[Dict[str, Any]] = {}


class InferenceConfig(BaseModel):
    model_name: str
    prompt: str
    output_schema_name: Optional[str] = None
    system_prompt: Optional[str] = None

    use_gpu: Optional[bool] = None
    dtype: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None

    api_key: Optional[str] = None

    model_class: Optional[str] = None
    device_map: Optional[str] = None
    return_tensors: Optional[str] = None
    padding: Optional[str] = None
    attn_implementation: Optional[str] = None


class Infer(ModelInfo):
    version: int
    multimodal: bool
    avg_latency: float
    top_percentile_accuracy: float
    latest_eval_accuracy: float
    latest_eval_datetime: datetime
