from pydantic import BaseModel
from typing import List


class EvalOutput(BaseModel):
    pass


class EvalDatasetItem(BaseModel):
    image_path: str
    image_type: str
    expected: str


class EvalDataset(BaseModel):
    name: str
    items: List[EvalDatasetItem]
