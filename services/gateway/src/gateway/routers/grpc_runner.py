import time
import grpc
from typing import Optional
from gateway.config import config
from lib.gRPC.generated import vlm_pb2, vlm_pb2_grpc
from lib.models.vlm_models import VLMResponseFormat, InferenceConfig
from lib.utils.log import get_logger

logger = get_logger(__name__)


async def run_grpc_inference(
    img_bytes: bytes,
    vlm_config: InferenceConfig,
    prompt: Optional[str],
    filename: str = "",
) -> VLMResponseFormat:
    try:
        server_ip = config.SERVER_IP
        grpc_port = config.GRPC_PORT

        channel = grpc.aio.insecure_channel(f"{server_ip}:{grpc_port}")
        stub = vlm_pb2_grpc.VLMServerStub(channel)

        # Serialize config to JSON string for proto
        config_json = vlm_config.model_dump_json(exclude_none=True)

        logger.info(
            f"[gRPC] Sending to {server_ip}:{grpc_port}: model={vlm_config.model_name}, gpu={vlm_config.use_gpu}"
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
