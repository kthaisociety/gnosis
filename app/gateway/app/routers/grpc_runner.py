import os
import time
import grpc
from typing import Optional

from app.gRPC.generated import vlm_pb2, vlm_pb2_grpc
from app.models.vlm_models import VLMResponseFormat, InferenceConfig
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def run_grpc_inference(
    img_bytes: bytes,
    config: InferenceConfig,
    prompt: Optional[str],
    filename: str = "",
) -> VLMResponseFormat:
    try:
        server_ip = os.getenv("SERVER_IP", "localhost")
        grpc_port = os.getenv("GRPC_PORT", "50051")

        channel = grpc.aio.insecure_channel(f"{server_ip}:{grpc_port}")
        stub = vlm_pb2_grpc.VLMServerStub(channel)

        # Serialize config to JSON string for proto
        config_json = config.model_dump_json(exclude_none=True)

        logger.info(
            f"[gRPC] Sending to {server_ip}:{grpc_port}: model={config.model_name}, gpu={config.use_gpu}"
        )

        request = vlm_pb2.InferenceRequest(
            image=img_bytes,
            config_json=config_json,
            prompt=prompt or "",  # Empty string if None
        )

        t0 = time.perf_counter()
        response = await stub.GenerateResponse(request)
        processed_time = (time.perf_counter() - t0) * 1000

        logger.info(f"[gRPC] Done in {processed_time:.1f} ms for {filename}")
        await channel.close()

        return VLMResponseFormat(
            html=response.html or None,
            json_data=response.json or None,
            csv=response.csv or None,
            text=response.text or None,
            markdown=response.markdown or None,
            inference_time_ms=processed_time,
        )

    except Exception as e:
        logger.error(f"[gRPC] Failed for {filename}: {e}")
        raise
