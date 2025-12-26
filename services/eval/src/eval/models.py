from pydantic import BaseModel
from typing import List, Literal


class EvalOutput(BaseModel):
    eval_type: Literal["table", "generic"]
    avg_rnss: float
    avg_rms: float


class EvalDatasetItem(BaseModel):
    image_path: str
    eval_type: Literal["table", "generic"] # becomes very annoying if put into a separate BaseModel
    expected: str


class EvalDataset(BaseModel):
    name: str
    items: List[EvalDatasetItem]
