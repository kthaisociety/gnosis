import time
import grpc

from gateway.config import config
from lib.gRPC.generated import vlm_pb2, vlm_pb2_grpc
from lib.inference import normalize_vlm_response
from lib.models.vlm import InferenceConfig, VLMResponse
from lib.utils.log import get_logger

logger = get_logger(__name__)


async def run_grpc_inference(
    img_bytes: bytes,
    vlm_config: InferenceConfig,
) -> VLMResponse:
    try:
        server_ip = config.SERVER_IP
        grpc_port = config.GRPC_PORT

        channel = grpc.aio.insecure_channel(f"{server_ip}:{grpc_port}")
        stub = vlm_pb2_grpc.VLMServerStub(channel)

        # Serialize config to JSON string for proto
        config_json = vlm_config.model_dump_json(exclude_none=True)

        logger.info(
            f"[ gRPC ] Sending to {server_ip}:{grpc_port}: model={vlm_config.model_name}, gpu={vlm_config.use_gpu}"
        )

        request = vlm_pb2.InferenceRequest(
            image=img_bytes,
            config_json=config_json,
        )

        t0 = time.perf_counter()
        response = await stub.Inference(request)
        processed_time = (time.perf_counter() - t0) * 1000

        logger.info(f"[ gRPC ] done in {processed_time:.1f} ms")
        await channel.close()

        return normalize_vlm_response(
            response.text, processed_time, model_name=vlm_config.model_name
        )

    except Exception as e:
        logger.error(f"[ gRPC ] failed inference: {e}")
        raise
