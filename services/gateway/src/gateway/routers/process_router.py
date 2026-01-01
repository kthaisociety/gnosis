import json
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from gateway.preprocessing.main import process_and_validate_image_bytes
from gateway.routers.modal_runner import run_modal_inference
from gateway.routers.grpc_runner import run_grpc_inference

from lib.utils.image import validate_image_bytes
from lib.utils.log import get_logger
from lib.models.vlm_models import VLMResponseFormat, InferenceConfig

logger = get_logger(__name__)
router = APIRouter(prefix="/process", tags=["Image Processing"])


@router.post(
    "",
    response_model=VLMResponseFormat,
    responses={
        200: {"description": "Successful image processing."},
        400: {"description": "Bad Request — Invalid or empty image file or config."},
        413: {
            "description": "Payload Too Large — Image file size exceeds the allowed limit."
        },
        415: {"description": "Unsupported Media Type — File type not allowed."},
        422: {
            "description": "Unprocessable Entity — Image file is corrupted or unreadable."
        },
        500: {"description": "Internal Server Error — Unexpected server failure."},
    },
)
async def process_image_file(
    file: UploadFile = File(...),
    runner: str = Form("modal", pattern="^(modal|local)$"),
    config: str = Form(
        ...,
        description='InferenceConfig JSON (e.g., {"model_name": "gemini-2.5-flash", "output_schema_name": "VLMTableOutput"})',
    ),
    prompt: Optional[str] = Form(None, description="Custom prompt (optional)"),
):
    filename = file.filename or "unknown"

    try:
        # 1. Read & Validate (Delegated to lib)
        raw_bytes = await file.read()
        logger.info(f"Received {filename}: {len(raw_bytes)} bytes")

        try:
            validate_image_bytes(raw_bytes)
        except ValueError as e:
            # Maps validation errors (size, format, empty) to 400 Bad Request
            raise HTTPException(status_code=400, detail=str(e))

        # 2. Parse Config
        try:
            # Pydantic validates the dictionary structure immediately
            inference_config = InferenceConfig(**json.loads(config))
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid config JSON: {e}")

        # 3. Preprocess (Cleaning, Deskewing)
        try:
            processed_img = process_and_validate_image_bytes(
                raw_bytes, filename)
        except Exception as e:
            logger.error(f"Preprocessing failed for {filename}: {e}")
            raise HTTPException(
                status_code=422, detail="Image preprocessing failed")

        # 4. Execution
        logger.info(f"Running {runner}: model={inference_config.model_name}")

        if runner == "modal":
            return await run_modal_inference(
                processed_img, inference_config, prompt, filename
            )
        return await run_grpc_inference(
            processed_img, inference_config, prompt, filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"System error processing {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
