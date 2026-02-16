import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from . import vlm_pb2 as vlm_pb2
from . import vlm_pb2_grpc as vlm_pb2_grpc

__all__ = ["vlm_pb2", "vlm_pb2_grpc"]
