from pydantic import BaseModel
from typing import List, Literal


class EvalType(BaseModel):
    type: Literal["table", "generic"]


class EvalOutput(BaseModel):
    eval_type: EvalType
    avg_rnss: float
    avg_rms: float


class EvalDatasetItem(BaseModel):
    image_path: str
    eval_type: EvalType
    expected: str


class EvalDataset(BaseModel):
    name: str
    items: List[EvalDatasetItem]
