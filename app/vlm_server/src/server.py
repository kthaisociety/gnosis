import os
import sys
import time
from itertools import count
from concurrent import futures

import grpc
import modal

CURRENT_DIR = os.path.dirname(__file__)
GRPC_DIR = os.path.join(CURRENT_DIR, "gRPC")

if GRPC_DIR not in sys.path:
    sys.path.insert(0, GRPC_DIR)

# Load env from nearest .env (assumes running from project root)
try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore

    _ENV_PATH = find_dotenv()
    _ENV_LOADED = load_dotenv(_ENV_PATH) if _ENV_PATH else False
except Exception:
    _ENV_PATH = ""
    _ENV_LOADED = False

# protobuf generated code
from generated import request_pb2, request_pb2_grpc

# utils
from utils.logging import get_logger
from infer import infer as run_infer
from infer import InferenceConfig
from infer import get_prompt
from utils.image_utils import decode_png_from_bytes

log = get_logger(__name__)

# Minimal log
log.info("dotenv path=%s loaded=%s", _ENV_PATH, _ENV_LOADED)

# Load default system prompt via infer prompts
SYSTEM_PROMPT = get_prompt("default")

# This is fine for now, but we can add more sophisticated system for logging metrics later on.
# Metrics sampling (read RSS every N requests; default every request)
_METRICS_SAMPLE_RATE = max(1, int(os.getenv("METRICS_SAMPLE_RATE", "1")))
_metrics_counter = count(1)


def ensure_modal_auth():
    if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
        # Already set
        return

    load_dotenv()

    modal_token_id = os.getenv("MODAL_TOKEN_ID")
    modal_token_secret = os.getenv("MODAL_TOKEN_SECRET")

    if not (modal_token_id and modal_token_secret):
        raise RuntimeError(
            "Modal credentials not found. Set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env"
        )

    # Explicitly configure Modal client
    modal.configure(token_id=modal_token_id, token_secret=modal_token_secret)
    print("Modal authenticated via .env credentials.")


class VLMServerServicer(request_pb2_grpc.VLMServerServicer):
    def __init__(self) -> None:
        # Build inference config (use Nanonets by default)
        try:
            from infer.vlm import ModelName  # type: ignore

            model_name = getattr(ModelName, "NANONETS", "nanonets/Nanonets-OCR-s")
        except Exception:
            model_name = "nanonets/Nanonets-OCR-s"

        use_gpu = (os.getenv("USE_GPU") or "0") in ("1", "true", "True")
        self._infer_config = InferenceConfig(
            model_name=model_name,
            use_gpu=use_gpu,
        )

    def GenerateResponse(self, request: request_pb2.Image, context):  # type: ignore
        t0 = time.perf_counter()
        response = ""  # Initialize response
        try:
            if request.runner == "modal":
                log.info("GenerateResponse via Modal runner")
                img_bytes_list = [request.image]
                infer_config = self._infer_config
                # Timer: Function loading
                load_start = time.time()

                # setup Modal app with token
                ensure_modal_auth()

                # Look up the deployed OCRInference class using Modal's Cls.from_name API
                OCRInference = modal.Cls.from_name("gnosis-infer-app", "OCRInference")

                result = OCRInference().infer.remote(
                    img_bytes_list, infer_config.model_dump(), SYSTEM_PROMPT
                )

                # Normalize outputs to a string/JSON for the proto
                if isinstance(result, list) and result:
                    first = result[0]
                    if hasattr(first, "model_dump_json"):
                        response = first.model_dump_json(exclude_none=True)
                    else:
                        response = str(first)
                else:
                    response = str(result)

            else:
                peer = context.peer() if hasattr(context, "peer") else "unknown"
                img_size = len(getattr(request, "image", b""))
                log.info("GenerateResponse: peer=%s bytes=%d", peer, img_size)

                # Ensure bytes payload
                image_bytes = request.image
                if isinstance(image_bytes, memoryview):
                    image_bytes = image_bytes.tobytes()
                if not isinstance(image_bytes, (bytes, bytearray)):
                    from io import BytesIO

                    try:
                        from PIL import Image  # type: ignore

                        if isinstance(image_bytes, Image.Image):
                            buf = BytesIO()
                            image_bytes.save(buf, format="PNG")
                            image_bytes = buf.getvalue()
                    except Exception:
                        pass
                if not isinstance(image_bytes, (bytes, bytearray)):
                    raise ValueError("image payload must be bytes")

                # Decode to PNG image and run inference
                image_obj = decode_png_from_bytes(image_bytes)
                outputs = run_infer([image_obj], self._infer_config, SYSTEM_PROMPT)

                # Normalize outputs to a string/JSON for the proto
                if isinstance(outputs, list) and outputs:
                    first = outputs[0]
                    if hasattr(first, "model_dump_json"):
                        response = first.model_dump_json(exclude_none=True)
                    else:
                        response = str(first)
                else:
                    response = str(outputs)
        except Exception as e:
            log.exception("GenerateResponse error")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return request_pb2.Response(json="")

        # Return response
        t1 = time.perf_counter()
        log.info("GenerateResponse done in %.1f ms", (t1 - t0) * 1000.0)
        return request_pb2.Response(json=response)


def serve() -> None:
    workers = max(
        1, (os.cpu_count() or 2) - 1
    )  # Not 100% sure on how much CPU to allocate. Not much concurrency expected.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    request_pb2_grpc.add_VLMServerServicer_to_server(
        VLMServerServicer(), server
    )  # Add the servicer to the server. We could run multiple servicers on the same server if needed.

    bind = os.getenv("GRPC_BIND", "0.0.0.0")
    port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f"{bind}:{port}")
    server.start()

    log.info("gRPC server listening on %s:%s", bind, port)

    server.wait_for_termination()  # Safely exit the server when the client disconnects.


if __name__ == "__main__":
    serve()
