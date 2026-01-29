import time
from typing import Optional

from lib.inference import detect_format
from lib.models.vlm import InferenceConfig
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
from .data.utils import parse_vlm_output_to_table
from .api import infer

logger = get_logger(__name__)


def eval(
    runner: str, # 'modal' or 'local'
    config: InferenceConfig,
    dataset_name: str,
    initiated_by: Optional[str] = None, # optional identifier for who started the eval
) -> EvalOutput:
    """
    1. Fetch dataset and images from Neon DB
    2. Create evaluation run to track progress
    3. For each image:
       - Fetch from S3
       - Run inference
       - Parse output to table format
       - Compute RMS and RNSS metrics
       - Store prediction and metrics in DB
    4. Aggregate metrics and return results
    """

    dataset = get_dataset_by_name(dataset_name)
    if not dataset:
        raise ValueError(f"Dataset '{dataset_name}' not found in database")
    logger.info(f"Evaluating on dataset: {dataset.name} (version: {dataset.version})")

    images = list_images_by_dataset(dataset.dataset_id)
    if not images:
        raise ValueError(f"No images found for dataset '{dataset_name}'")
    logger.info(f"Found {len(images)} images in dataset")

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
                if not image.ground_truth:
                    logger.warning(f"Image {image.image_id} has no ground truth")
                    failed_count += 1
                    continue

                s3_url = get_s3_url(image.file_path)
                start_time = time.time()

                vlm_output = infer(
                    runner=runner,
                    image_path=s3_url,
                    config=config,
                )

                latency_ms = int((time.time() - start_time) * 1000)

                if vlm_output is None or vlm_output.text is None:
                    logger.warning(f"No output for {image.file_path}")
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

                fmt = detect_format(vlm_output.text)
                if fmt != "json":
                    logger.warning(
                        f"VLM output format '{fmt}' for {image.file_path}; expected json"
                    )
                    create_prediction(
                        PredictionCreate(
                            image_id=image.image_id,
                            run_id=run_id,
                            output=None,
                            raw_response=vlm_output.text,
                            latency_ms=latency_ms,
                            success=False,
                            error_message=f"Output format '{fmt}', expected json",
                        )
                    )
                    failed_count += 1
                    continue

                predicted_table = parse_vlm_output_to_table(
                    vlm_output.text, config.output_schema_name
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
                    raw_response=vlm_output.text,
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

