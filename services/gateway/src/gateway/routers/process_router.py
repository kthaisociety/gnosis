import asyncio
import base64
import json
import os
import threading
import time
import uuid
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from redis import Redis

from gateway.preprocessing.main import process_and_validate_image_bytes
from gateway.routers.modal_runner import run_modal_inference
from gateway.routers.grpc_runner import run_grpc_inference
from lib.utils.image import validate_image_bytes
from lib.utils.log import get_logger
from lib.models.vlm_models import VLMResponseFormat, InferenceConfig

# Redis Configuration
QUEUE_KEY = os.getenv("QUEUE_KEY", "jobs")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
RESULT_PREFIX = os.getenv("RESULT_PREFIX", "result_")
JOB_TIMEOUT_S = int(os.getenv("JOB_TIMEOUT_S", "480"))
RESULT_TTL_SECONDS = int(os.getenv("RESULT_TTL_SECONDS", "120"))

# Rate Limiting
RATE_LIMIT_PER_IP_PER_MIN = int(os.getenv("RATE_LIMIT_PER_IP_PER_MIN", "10"))
RATE_LIMIT_GLOBAL_PER_MIN = int(os.getenv("RATE_LIMIT_GLOBAL_PER_MIN", "60"))
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

logger = get_logger(__name__)

redis_connection = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)

# Worker State
_worker_started = False
_worker_lock = threading.Lock()

def process_image(raw_bytes, filename, runner, inference_config, prompt) -> VLMResponseFormat:
    try:
        processed_img = process_and_validate_image_bytes(raw_bytes, filename)
    except Exception as e:
        logger.error(f"Preprocessing failed for {filename}: {e}")
        raise HTTPException(status_code=422, detail="Image preprocessing failed")

    logger.info(f"Running {runner}: model={inference_config.model_name}")

    if runner == "modal":
        return asyncio.run(run_modal_inference(
            processed_img, inference_config, prompt, filename
        ))
    return asyncio.run(run_grpc_inference(
        processed_img, inference_config, prompt, filename
    ))


def worker_loop():
    logger.info("Worker loop started. Waiting for jobs on Redis list '%s'...", QUEUE_KEY)

    while True:
        _, raw = redis_connection.brpop(QUEUE_KEY)

        job = json.loads(raw)

        job_id = job["id"]
        filename = job["filename"]
        runner = job["runner"]
        prompt = job.get("prompt")
        config_dict = job["config"]

        raw_bytes = base64.b64decode(job["image_b64"])
        inference_config = InferenceConfig(**config_dict)
        
        try:
            result_obj = process_image(
                raw_bytes=raw_bytes,
                filename=filename,
                runner=runner,
                inference_config=inference_config,
                prompt=prompt,
            )            
            redis_connection.setex(
                RESULT_PREFIX + job_id,
                RESULT_TTL_SECONDS,
                json.dumps({"ok": True, "result": result_obj.model_dump()}),
            )
        except Exception as e:
            logger.exception("Job %s failed", job_id)
            redis_connection.setex(
                RESULT_PREFIX + job_id,
                RESULT_TTL_SECONDS,
                json.dumps({"ok": False, "error": str(e)}),
            )

# FastAPI Router
router = APIRouter(prefix="/process", tags=["Image Processing"])

def start_worker():
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        t = threading.Thread(target=worker_loop, daemon=True)
        t.start()
        _worker_started = True

# API endpoint: enqueue + wait
@router.post(
    "",
    response_model=VLMResponseFormat,
    responses={
        200: {"description": "Successful image processing."},
        400: {"description": "Bad Request — Invalid or empty image file or config."},
        413: {"description": "Payload Too Large — Image file size exceeds the allowed limit."},
        415: {"description": "Unsupported Media Type — File type not allowed."},
        422: {"description": "Unprocessable Entity — Image file is corrupted or unreadable."},
        500: {"description": "Internal Server Error — Unexpected server failure."},
    },
)
def process_image_file(
    file: UploadFile = File(...),
    runner: Literal["modal", "local"] = Form("modal"),
    config: str = Form(
        ...,
        description='InferenceConfig JSON (e.g., {"model_name": "...", "use_gpu": true})',
    ),
    prompt: Optional[str] = Form(None, description="Custom prompt (optional)"),
) -> VLMResponseFormat:
    filename = file.filename or "unnamed file"

    raw_bytes = file.file.read()
    logger.info("Received %s: %d bytes", filename, len(raw_bytes))

    # Validate image and config
    try:
        validate_image_bytes(raw_bytes)
        inference_config = InferenceConfig(**json.loads(config))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (json.JSONDecodeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid config JSON: {e}")
    
    # Queue size guard
    if redis_connection.llen(QUEUE_KEY) >= MAX_QUEUE_SIZE:
        raise HTTPException(status_code=429, detail="Queue is full. Try again later.")

    # Enqueue job
    job_id = uuid.uuid4().hex
    job_payload = {
        "id": job_id,
        "filename": filename,
        "runner": runner,
        "prompt": prompt,
        "config": inference_config.model_dump(),
        "image_b64": base64.b64encode(raw_bytes).decode("ascii"),
    }
    redis_connection.lpush(QUEUE_KEY, json.dumps(job_payload))

    # Wait for result
    result_key = RESULT_PREFIX + job_id
    deadline = time.time() + JOB_TIMEOUT_S

    while time.time() < deadline:
        raw = redis_connection.get(result_key)
        if raw:
            redis_connection.delete(result_key)
            data = json.loads(raw)

            if data.get("ok"):
                return VLMResponseFormat(**data["result"])

            # worker wrote an error
            raise HTTPException(status_code=500, detail=data.get("error", "Job failed"))

        time.sleep(0.02)

    raise HTTPException(status_code=504, detail="Timed out waiting for result")