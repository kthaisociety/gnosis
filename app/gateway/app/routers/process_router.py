from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from app.services.preprocessing.main import process_and_validate_image_bytes
from app.routers.modal_runner import run_modal_inference
from app.grpc_client import run_grpc_inference
from app.utils.image_validation import verify_image_integrity
from app.utils.logging import get_logger
from app.models.vlm_models import VLMResponseFormat

logger = get_logger(__name__)

router = APIRouter(prefix="/process", tags=["Image Processing"])


@router.post(
    "",
    response_model=VLMResponseFormat,
    summary="Process a given image file",
    description="Upload an image file (.png, .jpg, .jpeg). Use 'runner' query param: 'modal' for Modal inference, 'local' (or any other) for gRPC local inference.",
    responses={
        200: {"description": "Successful image processing."},
        400: {"description": "Bad Request – Invalid or empty image file."},
        413: {
            "description": "Payload Too Large – Image file size exceeds the allowed limit."
        },
        415: {"description": "Unsupported Media Type – File type not allowed."},
        422: {
            "description": "Unprocessable Entity – Image file is corrupted or unreadable."
        },
        500: {"description": "Internal Server Error – Unexpected server failure."},
    },
)
async def process_image_file(
    file: UploadFile = File(..., description="Image file to process"),
    runner: str = Query(
        "modal", description="Inference runner: 'modal' for Modal, 'local' for gRPC"
    ),
) -> VLMResponseFormat:
    filename = file.filename or "unknown"
    try:
        raw_bytes = await file.read()
        logger.info(
            f"Received file for processing: {filename} ({file.content_type}) of size {len(raw_bytes)} bytes"
        )

        # Verify image file integrity
        invalid_image = verify_image_integrity(file, raw_bytes)
        if invalid_image is not None:
            logger.warning(
                f"Image validation failed for {filename}: {invalid_image.error}"
            )
            raise HTTPException(
                status_code=invalid_image.status, detail=invalid_image.message
            )

        # Process image
        try:
            preprocessed_image = process_and_validate_image_bytes(raw_bytes, filename)
        except (ValueError, RuntimeError) as e:
            logger.error(f"Image processing failed for {filename}: {e}")
            raise HTTPException(
                status_code=422, detail=f"Image processing failed: {str(e)}"
            )

        # Query VLM - route based on runner parameter
        try:
            if runner == "modal":
                response = await run_modal_inference(preprocessed_image, filename)
            else:
                response = await run_grpc_inference(
                    preprocessed_image, filename, runner=runner
                )
            return response
        except Exception as e:
            logger.error(f"VLM query failed for {filename}: {e}")
            raise HTTPException(
                status_code=500, detail=f"VLM inference failed: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
