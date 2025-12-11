#!/bin/bash
# Generate gRPC files from proto

cd "$(dirname "$0")/../app/gateway/app/gRPC"

uv run python -m grpc_tools.protoc \
    -I./protos \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./protos/vlm.proto

mkdir -p ../../../vlm_server/app/gRPC/generated

cp ./generated/vlm_pb2*.py ../../../vlm_server/app/gRPC/generated/

# Create __init__.py in both locations
cat > ./generated/__init__.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from . import vlm_pb2
from . import vlm_pb2_grpc
EOF

cp ./generated/__init__.py ../../../vlm_server/app/gRPC/generated/

echo "Done"
