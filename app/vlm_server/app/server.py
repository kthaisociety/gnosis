import os
import sys
import time
import json
from concurrent import futures
import grpc

CURRENT_DIR = os.path.dirname(__file__)
GATEWAY_DIR = os.path.join(CURRENT_DIR, "..", "..", "gateway")
GRPC_DIR = os.path.join(CURRENT_DIR, "gRPC")
if GATEWAY_DIR not in sys.path:
    sys.path.insert(0, GATEWAY_DIR)
if GRPC_DIR not in sys.path:
    sys.path.insert(0, GRPC_DIR)

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception:
    pass

from generated import vlm_pb2, vlm_pb2_grpc
from app.utils.logging import get_logger
from utils.image_utils import decode_png_from_bytes

log = get_logger(__name__)


class VLMServerServicer(vlm_pb2_grpc.VLMServerServicer):
    def GenerateResponse(self, request: vlm_pb2.InferenceRequest, context):
        t0 = time.perf_counter()
        response_fields = {
            "html": "",
            "json": "",
            "csv": "",
            "text": "",
            "markdown": "",
        }

        try:
            # Lazy import
            from app.services.inference.main import infer as run_infer
            from app.models.vlm_models import InferenceConfig

            # Deserialize config from gateway
            config_dict = json.loads(request.config_json)
            config = InferenceConfig(**config_dict)
            prompt = request.prompt

            log.info(
                "GenerateResponse: model=%s gpu=%s", config.model_name, config.use_gpu
            )

            # Decode image
            image_bytes = request.image
            if isinstance(image_bytes, memoryview):
                image_bytes = image_bytes.tobytes()

            image_obj = decode_png_from_bytes(image_bytes)

            # Run inference
            outputs = run_infer([image_obj], config, prompt)

            # Normalize output
            if isinstance(outputs, list) and outputs:
                first = outputs[0]
                if hasattr(first, "model_dump_json"):
                    try:
                        response_fields["json"] = first.model_dump_json(
                            exclude_none=True
                        )
                    except Exception as e:
                        log.warning(f"Failed to serialize as JSON: {e}")
                        response_fields["text"] = str(first)
                elif hasattr(first, "model_dump"):
                    try:
                        response_fields["json"] = json.dumps(
                            first.model_dump(exclude_none=True)
                        )
                    except Exception as e:
                        log.warning(f"Failed to serialize as JSON: {e}")
                        response_fields["text"] = str(first)
                else:
                    response_fields["text"] = str(first)
            else:
                response_fields["text"] = str(outputs)

        except Exception as e:
            log.exception("GenerateResponse error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

        log.info("GenerateResponse done in %.1f ms", (time.perf_counter() - t0) * 1000)
        return vlm_pb2.Response(**response_fields)


def serve():
    workers = max(1, (os.cpu_count() or 2) - 1)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    vlm_pb2_grpc.add_VLMServerServicer_to_server(VLMServerServicer(), server)

    bind = os.getenv("GRPC_BIND", "0.0.0.0")
    port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f"{bind}:{port}")
    server.start()
    log.info("gRPC server listening on %s:%s", bind, port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
