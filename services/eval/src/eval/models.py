from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


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


class Dataset(BaseModel):
    dataset_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None


class Image(BaseModel):
    image_id: Optional[UUID] = None
    dataset_id: Optional[UUID] = None
    file_path: str  # S3 key
    s3_etag: Optional[str] = None
    status: ImageStatus = ImageStatus.PENDING_UPLOAD
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    image_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ground_truth: Optional[Any] = (
        None  # Can be List[List[str]] for 2D tables or Dict for structured data
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ImageCreate(BaseModel):
    dataset_id: Optional[UUID] = None
    file_path: str
    s3_etag: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    image_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ground_truth: Optional[Any] = (
        None  # Can be List[List[str]] for 2D tables or Dict for structured data
    )


class EvaluationRun(BaseModel):
    run_id: Optional[UUID] = None
    model_name: str
    model_version: Optional[str] = None
    dataset_id: Optional[UUID] = None
    dataset_version: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    status: RunStatus = RunStatus.PENDING
    error_message: Optional[str] = None
    total_images: int = 0
    processed_images: int = 0
    failed_images: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    initiated_by: Optional[str] = None


class EvaluationRunCreate(BaseModel):
    model_name: str
    model_version: Optional[str] = None
    dataset_id: Optional[UUID] = None
    dataset_version: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    initiated_by: Optional[str] = None


class Prediction(BaseModel):
    prediction_id: Optional[UUID] = None
    image_id: UUID
    run_id: UUID
    output: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
    latency_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class PredictionCreate(BaseModel):
    image_id: UUID
    run_id: UUID
    output: Optional[Dict[str, Any]] = None
    raw_response: Optional[str] = None
    latency_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None


class Metric(BaseModel):
    metric_id: Optional[UUID] = None
    prediction_id: UUID
    metric_name: str
    metric_value: float
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class MetricCreate(BaseModel):
    prediction_id: UUID
    metric_name: str
    metric_value: float
    meta_data: Dict[str, Any] = Field(default_factory=dict)


class EvalOutput(BaseModel):
    model_name: str
    dataset_name: str
    output_schema_name: str
    avg_rnss: float
    avg_rms: float
