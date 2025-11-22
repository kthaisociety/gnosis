import os
import sys
import grpc
import PIL.Image

# make src/ importable so we can reach src/generated
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# protobuf generated code (from src/generated)
from generated import request_pb2, request_pb2_grpc

ip = os.getenv("GRPC_BIND", "0.0.0.0")
port = os.getenv("GRPC_PORT", "50051")
channel = grpc.insecure_channel(f"{ip}:{port}")
stub = request_pb2_grpc.VLMServerStub(channel)

with open("tests/processed_images/7219-8-1-S_2031_0.png", "rb") as f:
    data = f.read()
request = request_pb2.Image(image=data, runner="modal")

response = stub.GenerateResponse(request)
print(response.json)
