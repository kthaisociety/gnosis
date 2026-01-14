from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class VLMResponseFormat(BaseModel):
    html: Optional[str] = None
    json_data: Optional[str] = None
    csv: Optional[str] = None
    text: Optional[str] = None
    markdown: Optional[str] = None
    model_name: Optional[str] = None
    inference_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None


class DataPoint(BaseModel):
    x: float
    y: float


class VLMTableOutput(BaseModel):
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    legend: Optional[List[str]] = None
    data: List[DataPoint]


class ModelInfo(BaseModel):
    model_name: str
    inference_type: str
    inference_class: str
    requires_gpu: Optional[bool] = True
    default_prompt_name: Optional[str] = None
    default_config: Optional[Dict[str, Any]] = {}


class InferenceConfig(BaseModel):
    model_name: str
    output_schema_name: Optional[str] = None  # structured output

    # Common parameters
    use_gpu: Optional[bool] = None
    dtype: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None

    # API models
    api_key: Optional[str] = None

    # vLLM models
    max_model_len: Optional[int] = None

    # Transformers models
    model_class: Optional[str] = None
    device_map: Optional[str] = None
    return_tensors: Optional[str] = None
    padding: Optional[str] = None
    attn_implementation: Optional[str] = None  # "eager", "sdpa", "flash_attention_2"


class Infer(ModelInfo):
    version: int
    multimodal: bool
    max_len_tokens: int
    avg_latency: float
    top_percentile_accuracy: float
    latest_eval_accuracy: float
    latest_eval_datetime: datetime
