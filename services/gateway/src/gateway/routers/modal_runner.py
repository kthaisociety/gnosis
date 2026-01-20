import os
import sys
import time
import asyncio
import types
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import modal
from lib.models.vlm_models import (
    VLMResponseFormat,
    DataPoint,
    VLMTableOutput,
    InferenceConfig,
)
from lib.utils.log import get_logger

logger = get_logger(__name__)

# Create stub modules for Modal deserialization
# Modal expects these to exist locally to deserialize the remote objects
_infer_module = types.ModuleType("infer")
_infer_module.vlm = types.ModuleType("infer.vlm")
_infer_module.vlm.vlm = types.ModuleType("infer.vlm.vlm")

# Add models to both namespaces (some versions of the remote app might use different paths)
for mod in [_infer_module.vlm, _infer_module.vlm.vlm]:
    mod.DataPoint = DataPoint
    mod.VLMTableOutput = VLMTableOutput
    mod.VLMOutput = VLMTableOutput # Alias for older/other versions

sys.modules["infer"] = _infer_module
sys.modules["infer.vlm"] = _infer_module.vlm
sys.modules["infer.vlm.vlm"] = _infer_module.vlm.vlm


from gateway.config import config

def ensure_modal_auth():
    """Ensure Modal credentials are available."""
    if not (config.MODAL_TOKEN_ID and config.MODAL_TOKEN_SECRET):
        raise RuntimeError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )
    # Modal reads credentials from environment variables automatically
    logger.info("Modal credentials found.")


async def run_modal_inference(
    img_bytes: bytes,
    config: InferenceConfig,
    prompt: Optional[str],
    filename: str = "",
) -> VLMResponseFormat:
    """Run VLM inference via Modal."""
    try:
        ensure_modal_auth()
        OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

        logger.info(f"[Modal] Starting inference: model={config.model_name}")

        t0 = time.perf_counter()
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: OCRInference().infer.remote(
                    [img_bytes],
                    config.model_dump(exclude_none=True),
                    prompt,
                ),
            )

        processed_time = (time.perf_counter() - t0) * 1000
        logger.info(f"[Modal] Done in {processed_time:.1f} ms for {filename}")

        # Normalize result
        json_data: Optional[str] = None
        text_data: Optional[str] = None

        if hasattr(result, "model_dump_json"):
            json_data = result.model_dump_json(exclude_none=True)
        elif isinstance(result, dict):
            json_data = json.dumps(result)
        elif isinstance(result, str):
            try:
                json.loads(result)
                json_data = result
            except json.JSONDecodeError:
                text_data = result
        else:
            text_data = str(result)

        if json_data:
            return VLMResponseFormat(json_data=json_data, inference_time_ms=processed_time)
        else:
            return VLMResponseFormat(text=text_data, inference_time_ms=processed_time)

    except Exception as e:
        logger.error(f"[Modal] Failed for {filename}: {e}")
        raise
