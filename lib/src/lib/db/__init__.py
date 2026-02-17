# Expose the connection pool getter
from .client import close_db_pool, get_db_pool

# Expose the CRUD operations via import from .operations
# Can now be imported with from "lib.db import get_user_id" for easier imports
from .operations import (
    create_dataset,
    create_evaluation_run,
    create_image,
    create_metric,
    create_prediction,
    create_schema,
    drop_schema,
    drop_table,
    get_all_inference_models,
    get_dataset,
    get_dataset_by_name,
    get_evaluation_run,
    get_image,
    get_metrics_by_prediction,
    get_predictions_by_run,
    get_run_metrics_summary,
    get_user_id,
    list_datasets,
    list_images_by_dataset,
    update_image_status,
    update_run_status,
)

__all__ = [
    "get_db_pool",
    "close_db_pool",
    "get_user_id",
    "drop_table",
    "create_schema",
    "drop_schema",
    "get_all_inference_models",
    "create_dataset",
    "get_dataset",
    "get_dataset_by_name",
    "list_datasets",
    "create_image",
    "get_image",
    "update_image_status",
    "list_images_by_dataset",
    "create_evaluation_run",
    "update_run_status",
    "get_evaluation_run",
    "create_prediction",
    "get_predictions_by_run",
    "create_metric",
    "get_metrics_by_prediction",
    "get_run_metrics_summary",
]
