from typing import Optional
from pydantic import BaseModel

class VLMResponseFormat(BaseModel):
    html: Optional[str] = None
    json: Optional[str] = None
    csv: Optional[str] = None
    text: Optional[str] = None
    markdown: Optional[str] = None
    model_name: Optional[str] = None
    inference_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None

