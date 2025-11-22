from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import json

from app.services.preprocessing.main import process_and_validate_image_bytes
from app.routers.modal_runner import run_modal_inference
from app.routers.grpc_runner import run_grpc_inference
from app.utils.image_validation import verify_image_integrity
from app.utils.logging import get_logger
from app.models.vlm_models import VLMResponseFormat, InferenceConfig

logger = get_logger(__name__)

router = APIRouter(prefix="/process", tags=["Image Processing"])


@router.post(
    "",
    response_model=VLMResponseFormat,
    summary="Process a given image file",
    description="Upload an image file and provide config as JSON.",
    responses={
        200: {"description": "Successful image processing."},
        400: {"description": "Bad Request — Invalid or empty image file or config."},
        413: {"description": "Payload Too Large — Image file size exceeds the allowed limit."},
        415: {"description": "Unsupported Media Type — File type not allowed."},
        422: {"description": "Unprocessable Entity — Image file is corrupted or unreadable."},
        500: {"description": "Internal Server Error — Unexpected server failure."},
    },
)
async def process_image_file(
    file: UploadFile = File(..., description="Image file to process"),
    runner: str = Form("modal", description="'modal' or 'local'"),
    config: str = Form(..., description="InferenceConfig JSON (e.g., {\"model_name\": \"...\", \"use_gpu\": true})"),
    prompt: Optional[str] = Form(None, description="Custom prompt (optional)"),
) -> VLMResponseFormat:
    filename = file.filename or "unknown"
    try:
        raw_bytes = await file.read()
        logger.info(f"Received: {filename} ({len(raw_bytes)} bytes)")

        # Verify image integrity
        invalid_image = verify_image_integrity(file, raw_bytes)
        if invalid_image is not None:
            logger.warning(f"Validation failed for {filename}: {invalid_image.error}")
            raise HTTPException(status_code=invalid_image.status, detail=invalid_image.message)

        # Preprocess
        try:
            preprocessed_image = process_and_validate_image_bytes(raw_bytes, filename)
        except (ValueError, RuntimeError) as e:
            logger.error(f"Preprocessing failed for {filename}: {e}")
            raise HTTPException(status_code=422, detail=f"Image processing failed: {e}")

        # Parse config JSON
        try:
            config_dict = json.loads(config)
            inference_config = InferenceConfig(**config_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid config JSON: {e}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid config: {e}")

        logger.info(f"Running {runner}: model={inference_config.model_name}, gpu={inference_config.use_gpu}")

        # Route to runner
        try:
            if runner == "modal":
                response = await run_modal_inference(preprocessed_image, inference_config, prompt, filename)
            else:
                response = await run_grpc_inference(preprocessed_image, inference_config, prompt, filename)
            return response
        except Exception as e:
            logger.error(f"VLM query failed for {filename}: {e}")
            raise HTTPException(status_code=500, detail=f"VLM inference failed: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
