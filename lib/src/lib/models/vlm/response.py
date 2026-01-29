from typing import Optional

from pydantic import BaseModel


class VLMResponseFormat(BaseModel):
    text: Optional[str] = None
    format: Optional[str] = None  # "json" | "html" | "text" from detect_format
    model_name: Optional[str] = None
    inference_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
