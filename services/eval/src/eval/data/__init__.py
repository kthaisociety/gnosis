from lib.db.operations.eval import (
    create_dataset,
    create_evaluation_run,
    create_image,
    create_metric,
    create_prediction,
    get_dataset_by_name,
    get_evaluation_run,
    get_image,
    get_metrics_by_prediction,
    get_predictions_by_run,
    get_run_metrics_summary,
    list_datasets,
    list_images_by_dataset,
    update_image_status,
    update_run_status,
)
from lib.db.operations.eval import (
    get_dataset as get_dataset_by_id,
)

# S3 operations
from lib.storage.s3 import (
    check_image_exists,
    delete_dataset_images,
    delete_image_from_s3,
    ensure_s3_bucket_exists,
    generate_s3_key,
    get_image_metadata,
    get_s3_url,
    upload_image_to_s3,
)

# Pipeline operations
from .pipeline import (
    bulk_upload_images,
    upload_benchmark_image,
    verify_image_upload,
)

__all__ = [
    # Benchmark datasets
    "create_dataset",
    "get_dataset_by_id",
    "get_dataset_by_name",
    "list_datasets",
    # Benchmark images
    "create_image",
    "get_image",
    "update_image_status",
    "list_images_by_dataset",
    # Benchmark evaluation runs
    "create_evaluation_run",
    "update_run_status",
    "get_evaluation_run",
    # Benchmark predictions
    "create_prediction",
    "get_predictions_by_run",
    # Benchmark metrics
    "create_metric",
    "get_metrics_by_prediction",
    "get_run_metrics_summary",
    # S3 operations
    "ensure_s3_bucket_exists",
    "generate_s3_key",
    "upload_image_to_s3",
    "get_image_metadata",
    "delete_image_from_s3",
    "delete_dataset_images",
    "get_s3_url",
    "check_image_exists",
    # Pipeline
    "upload_benchmark_image",
    "bulk_upload_images",
    "verify_image_upload",
]
