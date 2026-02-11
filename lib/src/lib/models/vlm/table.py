from typing import List, Optional

from pydantic import BaseModel


class DataPoint(BaseModel):
    x: float
    y: float


class TableOutput(BaseModel):
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    legend: Optional[List[str]] = None
    data: List[DataPoint]
