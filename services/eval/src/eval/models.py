from pydantic import BaseModel
from typing import List


class EvalOutput(BaseModel):
    model_name: str
    dataset_name: str
    output_schema_name: str
    avg_rnss: float
    avg_rms: float


class EvalDatasetItem(BaseModel):
    image_path: str
    output_schema_name: str
    expected: str


class EvalDataset(BaseModel):
    name: str
    items: List[EvalDatasetItem]
