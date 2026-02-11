#!/bin/bash
# Generate gRPC files from proto

cd "$(dirname "$0")/../lib/src/lib/gRPC"
mkdir -p generated/

PROTOC_ARGS="-I./protos --python_out=./generated --grpc_python_out=./generated ./protos/vlm.proto"
uv run python -m grpc_tools.protoc $PROTOC_ARGS 2>/dev/null || python3 -m grpc_tools.protoc $PROTOC_ARGS

# Create __init__.py
cat > ./generated/__init__.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from . import vlm_pb2
from . import vlm_pb2_grpc
EOF

echo "Done (generated protos)"
