import os
import sys
import time

from grpc import aio
from models.vlm_models import VLMResponseFormat
from utils.logging import get_logger

CURRENT_DIR = os.path.dirname(__file__)
GRPC_DIR = os.path.join(CURRENT_DIR, "gRPC")

if GRPC_DIR not in sys.path:
    sys.path.insert(0, GRPC_DIR)

logger = get_logger(__name__)

async def query_vlm(img_bytes: bytes, filename: str = "") -> VLMResponseFormat:
    from generated import request_pb2, request_pb2_grpc

    GRPC_PORT = os.getenv("GRPC_PORT", "50051")
    IP = os.getenv("SERVER_IP", "localhost")
    ADDRESS = f"{IP}:{GRPC_PORT}"

    try:
        async with aio.insecure_channel(ADDRESS) as channel:
            stub = request_pb2_grpc.PreProcessingStub(channel)
            req = request_pb2.RawImage(image=img_bytes, filename=filename)

            t0 = time.perf_counter()
            resp = await stub.Process(req)
            t1 = time.perf_counter()
        processed_time = (t1 - t0) * 1000

        logger.info(f"[gRPC] Exchange finished in {processed_time:.1f} ms for {filename}")
        return VLMResponseFormat(
            html=getattr(resp, "html", None),
            json=getattr(resp, "json", None),
            csv=getattr(resp, "csv", None),
            text=getattr(resp, "text", None),
            markdown=getattr(resp, "markdown", None),
            inference_time_ms=processed_time
        )
    except Exception as e:
        logger.error(f"[gRPC] Failed to query VLM for {filename}: {e}")
        raise

if __name__ == "__main__":
    logger.info("gRPC client module loaded")
