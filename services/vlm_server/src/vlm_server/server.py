import os
import json
import grpc
import time
from dotenv import load_dotenv
from concurrent import futures

from lib.utils.log import get_logger
from lib.utils.image import bytes_to_pil
from lib.models.vlm import InferenceConfig
from lib.inference import normalize_output
from lib.gRPC.generated import vlm_pb2, vlm_pb2_grpc

from vlm_server.inference import inference

load_dotenv()
PORT = os.getenv("PORT")
BIND = os.getenv("HOST")

logger = get_logger(__name__)


class VLMServerServicer(vlm_pb2_grpc.VLMServerServicer):
    def Inference(self, request, context):
        t0 = time.perf_counter()

        try:
            config = InferenceConfig(**json.loads(request.config))
            image = bytes_to_pil(bytes(request.image))

            logger.info(f"[ Inference ] model={config.model_name} gpu={config.use_gpu}")

            out = inference(image, config)
            normalized = normalize_output(out)

            logger.info(f"[ Inference ] done in {(time.perf_counter() - t0) * 1000:.f} ms")

            return vlm_pb2.Response(**normalized)

        except Exception as e:
            logger.exception("[ Inference ] FAILED")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return vlm_pb2.Response()


def serve():
    workers = max(1, (os.cpu_count() or 2) - 1)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

    vlm_pb2_grpc.add_VLMServerServicer_to_server(VLMServerServicer(), server)
    server.add_insecure_port(f"{bind}:{port}")

    logger.info(f"VLM gRPC server listening on {bind}:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
