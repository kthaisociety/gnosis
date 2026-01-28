import os
import json
import time
import grpc
from concurrent import futures

from lib.utils.log import get_logger
from lib.utils.image import bytes_to_pil
from lib.models.vlm import InferenceConfig
from lib.gRPC.generated import vlm_pb2, vlm_pb2_grpc

from vlm_server.inference.main import infer

logger = get_logger(__name__)


class VLMServerServicer(vlm_pb2_grpc.VLMServerServicer):
    def GenerateResponse(self, request, context):
        t0 = time.perf_counter()

        try:
            # 1. Prepare Inputs
            config = InferenceConfig(**json.loads(request.config_json))
            # Handle bytes or memoryview automatically
            image = bytes_to_pil(bytes(request.image))

            logger.info(f"Infer: model={config.model_name} gpu={config.use_gpu}")

            # 2. Run Inference
            output = infer([image], config, request.prompt)

            # 3. Format & Return
            response_data = self._normalize_output(output)

            logger.info(f"Done: {(time.perf_counter() - t0) * 1000:.1f} ms")
            return vlm_pb2.Response(**response_data)

        except Exception as e:
            logger.exception("RPC Failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return vlm_pb2.Response()

    def _normalize_output(self, result) -> dict:
        """Unwraps list and serializes Pydantic models to JSON."""
        data = {k: "" for k in ["json", "text", "html", "csv", "markdown"]}

        # Unwrap list if necessary
        if isinstance(result, list):
            if not result:
                return data
            result = result[0]

        # Attempt JSON serialization (Pydantic)
        try:
            if hasattr(result, "model_dump_json"):
                data["json"] = result.model_dump_json(exclude_none=True)
                return data
            if hasattr(result, "model_dump"):
                data["json"] = json.dumps(result.model_dump(exclude_none=True))
                return data
        except Exception:
            pass  # Fallback to text representation

        data["text"] = str(result)
        return data


def serve():
    port = os.getenv("GRPC_PORT", "50051")
    bind = os.getenv("GRPC_BIND", "0.0.0.0")

    # Auto-scale workers to CPU count
    workers = max(1, (os.cpu_count() or 2) - 1)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

    vlm_pb2_grpc.add_VLMServerServicer_to_server(VLMServerServicer(), server)
    server.add_insecure_port(f"{bind}:{port}")

    logger.info(f"VLM gRPC Server listening on {bind}:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
