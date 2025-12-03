import os
import time
import grpc
from app.gRPC.generated import vlm_pb2, vlm_pb2_grpc
from app.models.vlm_models import VLMResponseFormat
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def run_grpc_inference(
    img_bytes: bytes, filename: str = "", runner: str = "local"
) -> VLMResponseFormat:
    """Run VLM inference via gRPC to vlm_server."""
    try:
        server_ip = os.getenv("SERVER_IP", "localhost")
        grpc_port = os.getenv("GRPC_PORT", "50051")
        channel = grpc.aio.insecure_channel(f"{server_ip}:{grpc_port}")
        stub = vlm_pb2_grpc.VLMServerStub(channel)

        request = vlm_pb2.Image(image=img_bytes, runner=runner)

        t0 = time.perf_counter()
        response = await stub.GenerateResponse(request)
        t1 = time.perf_counter()
        processed_time = (t1 - t0) * 1000

        logger.info(
            f"[gRPC] Inference finished in {processed_time:.1f} ms for {filename}"
        )

        await channel.close()

        return VLMResponseFormat(
            html=response.html if response.html else None,
            json_data=response.json if response.json else None,
            csv=response.csv if response.csv else None,
            text=response.text if response.text else None,
            markdown=response.markdown if response.markdown else None,
            inference_time_ms=processed_time,
        )
    except Exception as e:
        logger.error(f"[gRPC] Failed to query VLM for {filename}: {e}")
        raise
