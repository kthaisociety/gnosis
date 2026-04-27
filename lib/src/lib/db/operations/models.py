from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from enum import Enum


class ImageStatus(str, Enum):
    PENDING_UPLOAD = "pending_upload"
    ACTIVE = "active"
    UPLOAD_FAILED = "upload_failed"
    DELETED = "deleted"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None


class Dataset(BaseModel):
    dataset_id: UUID
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    created_at: str
    updated_at: str


class ImageCreate(BaseModel):
    dataset_id: Optional[UUID] = None
    file_path: str
    s3_etag: Optional[str] = None
    status: ImageStatus = ImageStatus.PENDING_UPLOAD
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    image_type: Optional[str] = None
    metadata: Optional[dict] = None
    ground_truth: Optional[dict] = None


class Image(BaseModel):
    image_id: UUID
    dataset_id: Optional[UUID] = None
    file_path: str
    s3_etag: Optional[str] = None
    status: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    image_type: Optional[str] = None
    metadata: dict
    ground_truth: Optional[dict] = None
    created_at: str
    updated_at: str


class EvaluationRunCreate(BaseModel):
    model_name: str
    model_version: Optional[str] = None
    dataset_id: Optional[UUID] = None
    dataset_version: Optional[str] = None
    config: dict
    initiated_by: Optional[str] = None


class EvaluationRun(BaseModel):
    run_id: UUID
    model_name: str
    model_version: Optional[str] = None
    dataset_id: Optional[UUID] = None
    dataset_version: Optional[str] = None
    config: dict
    status: str
    error_message: Optional[str] = None
    total_images: int = 0
    processed_images: int = 0
    failed_images: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    initiated_by: Optional[str] = None


class PredictionCreate(BaseModel):
    image_id: UUID
    run_id: UUID
    output: Optional[dict] = None
    raw_response: Optional[str] = None
    latency_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None


class Prediction(BaseModel):
    prediction_id: UUID
    image_id: UUID
    run_id: UUID
    output: Optional[dict] = None
    raw_response: Optional[str] = None
    latency_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    created_at: str


class MetricCreate(BaseModel):
    prediction_id: UUID
    metric_name: str
    metric_value: float
    meta_data: Optional[dict] = None


class Metric(BaseModel):
    metric_id: UUID
    prediction_id: UUID
    metric_name: str
    metric_value: float
    meta_data: dict
    created_at: str
