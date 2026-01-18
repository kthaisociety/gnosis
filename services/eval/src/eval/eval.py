import json
import time
from typing import List, Union, Optional

from lib.models.vlm_models import InferenceConfig, VLMTableOutput
from lib.utils.log import get_logger
from .metrics import compute_rms, compute_rnss
from .models import (
    EvalOutput,
    EvaluationRunCreate,
    RunStatus,
    PredictionCreate,
    MetricCreate,
)
from .data import (
    get_dataset_by_name,
    list_images_by_dataset,
    create_evaluation_run,
    update_run_status,
    create_prediction,
    create_metric,
)
from .data.s3_bucket import get_s3_url
from .api import infer

logger = get_logger(__name__)


def eval_cloud(
    runner: str,
    config: InferenceConfig,
    dataset_name: str,
    prompt: Optional[str] = None,
    initiated_by: Optional[str] = None,
) -> EvalOutput:
    """
    Evaluate VLM on a cloud-based benchmark dataset.

    Workflow:
    1. Fetch dataset and images from Neon DB
    2. Create evaluation run to track progress
    3. For each image:
       - Fetch from S3
       - Run inference
       - Parse output to table format
       - Compute RMS and RNSS metrics
       - Store prediction and metrics in DB
    4. Aggregate metrics and return results

    Args:
        runner: Inference runner type ("grpc" or "modal")
        config: VLM inference configuration
        dataset_name: Name of the dataset to evaluate on
        prompt: Optional custom prompt for inference
        initiated_by: Optional identifier for who started this evaluation

    Returns:
        EvalOutput with aggregated metrics
    """
    dataset = get_dataset_by_name(dataset_name)
    if not dataset:
        raise ValueError(f"Dataset '{dataset_name}' not found in database")

    logger.info(f"Evaluating on dataset: {dataset.name} (version: {dataset.version})")

    images = list_images_by_dataset(dataset.dataset_id)
    if not images:
        raise ValueError(f"No images found for dataset '{dataset_name}'")

    logger.info(f"Found {len(images)} images in dataset")

    # Eval run for database
    eval_run = EvaluationRunCreate(
        model_name=config.model_name,
        model_version=getattr(config, "model_version", None),
        dataset_id=dataset.dataset_id,
        dataset_version=dataset.version,
        config=config.model_dump(),
        initiated_by=initiated_by or "manual",
    )

    run_id = create_evaluation_run(eval_run)
    if not run_id:
        raise RuntimeError("Failed to create evaluation run")

    logger.info(f"Created evaluation run: {run_id}")

    update_run_status(
        run_id,
        RunStatus.RUNNING,
        total_images=len(images),
        processed_images=0,
        failed_images=0,
    )

    total_rnss = 0.0
    total_rms = 0.0
    processed_count = 0
    failed_count = 0

    try:
        for idx, image in enumerate(images, 1):
            logger.info(f"[{idx}/{len(images)}] Processing image: {image.file_path}")

            try:
                # Check if image has ground truth
                if not image.ground_truth:
                    logger.warning(
                        f"Image {image.image_id} has no ground truth, skipping"
                    )
                    failed_count += 1
                    continue

                s3_url = get_s3_url(image.file_path)
                start_time = time.time()

                vlm_output = infer(
                    runner=runner,
                    image_path=s3_url,
                    prompt=prompt,
                    config=config,
                    local_dataset=False,
                )

                latency_ms = int((time.time() - start_time) * 1000)

                if vlm_output is None or vlm_output.json_data is None:
                    logger.warning(f"No output for {image.file_path}, skipping")

                    # Store failed prediction
                    create_prediction(
                        PredictionCreate(
                            image_id=image.image_id,
                            run_id=run_id,
                            output=None,
                            raw_response=None,
                            latency_ms=latency_ms,
                            success=False,
                            error_message="No output from model",
                        )
                    )

                    failed_count += 1
                    continue

                predicted_table = parse_vlm_output_to_table(
                    vlm_output.json_data, config.output_schema_name
                )

                target_table = image.ground_truth

                image_rms = compute_rms(predicted_table, target_table)
                image_rnss = compute_rnss(predicted_table, target_table)

                total_rms += image_rms
                total_rnss += image_rnss
                processed_count += 1

                prediction = PredictionCreate(
                    image_id=image.image_id,
                    run_id=run_id,
                    output={"predicted_table": predicted_table},
                    raw_response=vlm_output.json_data,
                    latency_ms=latency_ms,
                    input_tokens=getattr(vlm_output, "input_tokens", None),
                    output_tokens=getattr(vlm_output, "output_tokens", None),
                    success=True,
                )

                prediction_id = create_prediction(prediction)

                if prediction_id:
                    create_metric(
                        MetricCreate(
                            prediction_id=prediction_id,
                            metric_name="rms",
                            metric_value=image_rms,
                            meta_data={},
                        )
                    )

                    create_metric(
                        MetricCreate(
                            prediction_id=prediction_id,
                            metric_name="rnss",
                            metric_value=image_rnss,
                            meta_data={},
                        )
                    )

                logger.info(f"RMS: {image_rms:.4f}, RNSS: {image_rnss:.4f}")

                update_run_status(
                    run_id,
                    RunStatus.RUNNING,
                    processed_images=processed_count,
                    failed_images=failed_count,
                )

            except Exception as e:
                logger.error(f"Failed to process image {image.file_path}: {e}")

                create_prediction(
                    PredictionCreate(
                        image_id=image.image_id,
                        run_id=run_id,
                        output=None,
                        raw_response=None,
                        success=False,
                        error_message=str(e),
                    )
                )

                failed_count += 1

                update_run_status(
                    run_id,
                    RunStatus.RUNNING,
                    processed_images=processed_count,
                    failed_images=failed_count,
                )

        if processed_count == 0:
            raise ValueError("No images were successfully processed")

        avg_rnss = total_rnss / processed_count
        avg_rms = total_rms / processed_count

        update_run_status(
            run_id,
            RunStatus.COMPLETED,
            processed_images=processed_count,
            failed_images=failed_count,
        )

        logger.info(f"\n{'='*60}")
        logger.info("EVALUATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Dataset: {dataset_name}")
        logger.info(f"Model: {config.model_name}")
        logger.info(f"Processed: {processed_count}/{len(images)}")
        logger.info(f"Failed: {failed_count}/{len(images)}")
        logger.info(f"Average RMS: {avg_rms:.4f}")
        logger.info(f"Average RNSS: {avg_rnss:.4f}")
        logger.info(f"{'='*60}\n")

        return EvalOutput(
            model_name=config.model_name,
            dataset_name=dataset_name,
            output_schema_name=config.output_schema_name,
            avg_rnss=avg_rnss,
            avg_rms=avg_rms,
        )

    except Exception as e:
        update_run_status(
            run_id,
            RunStatus.FAILED,
            error_message=str(e),
            processed_images=processed_count,
            failed_images=failed_count,
        )
        raise


def parse_vlm_output_to_table(
    json_str: str, schema_name: str
) -> List[List[Union[str, float]]]:
    """
    Convert VLM output (JSON) to 2D table format for metrics.

    Args:
        json_str: JSON string from VLM output
        schema_name: Output schema name

    Returns:
        2D table as List[List[str]]
    """
    if schema_name == "VLMTableOutput":
        data = json.loads(json_str)
        output = VLMTableOutput(**data)
        return vlm_table_output_to_table(output)
    else:
        raise ValueError(f"Unknown schema: {schema_name}")


def vlm_table_output_to_table(output: VLMTableOutput) -> List[List[Union[str, float]]]:
    """
    Convert VLMTableOutput to 2D table format.

    Format:
    [
        ["", "y_label"],
        ["x1", y1],
        ["x2", y2],
        ...
    ]
    """
    y_label = output.y_label or "y"
    table = [["", y_label]]

    for point in output.data:
        table.append([str(point.x), point.y])

    return table


# TODO: This implemenation is might  be deprecated for working wiht local dataset. Either remove or update.
def eval(
    runner: str,
    config: InferenceConfig,
    dataset_name: str,
    local_dataset: bool,
    prompt: str = None,
) -> EvalOutput:
    """
    Legacy eval function for backward compatibility.

    If local_dataset=False, delegates to eval_cloud().
    If local_dataset=True, uses old local dataset logic.
    """
    if not local_dataset:
        return eval_cloud(
            runner=runner,
            config=config,
            dataset_name=dataset_name,
            prompt=prompt,
        )

    from .data import get_dataset, verify_dataset

    dataset = get_dataset(dataset_name, local=local_dataset)
    try:
        verify_dataset(dataset)
    except Exception as e:
        raise ValueError(f"Invalid dataset: {e}")

    if not config.output_schema_name:
        config.output_schema_name = dataset.items[0].output_schema_name
    else:
        logger.warn(
            "output_schema_name forcefully set instead of relying on dataset's schema. "
            "Will produce unwanted results if schemas are not equal."
        )

    if config.output_schema_name != dataset.items[0].output_schema_name:
        raise ValueError(
            "Schema configuration of inference config does not match dataset's schema!"
        )

    rnss = 0.0
    rms = 0.0

    try:
        for item in dataset.items:
            vlm_output = infer(
                runner, item.image_path, prompt, config, local_dataset=local_dataset
            )

            if vlm_output is None or vlm_output.json_data is None:
                logger.warning(f"No output for {item.image_path}, skipping")
                continue

            predicted_table = parse_vlm_output_to_table(
                vlm_output.json_data, config.output_schema_name
            )

            target_table = parse_vlm_output_to_table(
                item.expected, config.output_schema_name
            )

            rms += compute_rms(predicted_table, target_table)
            rnss += compute_rnss(predicted_table, target_table)

    except Exception as e:
        raise ValueError(f"Failed to inference model on dataset: {e}")

    n_items = len(dataset.items)
    avg_rnss = rnss / n_items
    avg_rms = rms / n_items

    return EvalOutput(
        model_name=config.model_name,
        dataset_name=dataset_name,
        output_schema_name=config.output_schema_name,
        avg_rnss=avg_rnss,
        avg_rms=avg_rms,
    )
