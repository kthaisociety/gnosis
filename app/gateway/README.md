# GNOSIS GATEWAY

REST API gateway for VLM inference with routing to Modal or local gRPC server.

## Architecture

**Routing**: Routes inference requests via `runner` query param:
- `modal` → Modal inference (serverless)
- `local` (or any other) → gRPC to `vlm_server`

**Components**:
- `routers/process_router.py`: Main routing logic
- `routers/modal_runner.py`: Modal inference runner
- `grpc_client.py`: gRPC client for local inference
- `gRPC/protos/vlm.proto`: gRPC protocol definition
- `services/inference/`: Shared inference code (used by both Modal and local)

## Setup

```bash
cd app/gateway
uv venv
uv pip install -r requirements.txt
```

## Generate gRPC Stubs

```bash
uv run python -m grpc_tools.protoc -I app/gRPC/protos --python_out=app/gRPC/generated --grpc_python_out=app/gRPC/generated app/gRPC/protos/vlm.proto
```

After generation, fix the import in `app/gRPC/generated/vlm_pb2_grpc.py`:
```python
from . import vlm_pb2 as vlm__pb2  # Use relative import
```

## Environment

Create `.env` file:
```bash
MODAL_TOKEN_ID=your_token_id
MODAL_TOKEN_SECRET=your_token_secret
SERVER_IP=localhost  # For gRPC
GRPC_PORT=50051      # For gRPC
USE_GPU=false        # For inference config
```

## Run Server

```bash
uv run uvicorn app.server:app --host 127.0.0.1 --port 8000
```

## API Usage

### Process Image

```bash
# Modal inference (default)
curl -X POST "http://127.0.0.1:8000/process?runner=modal" \
  -F "file=@image.png"

# gRPC local inference
curl -X POST "http://127.0.0.1:8000/process?runner=local" \
  -F "file=@image.png"
```

### Response Format

```json
{
  "html": "...",
  "json_data": "{...}",
  "csv": "...",
  "text": "...",
  "markdown": "...",
  "inference_time_ms": 1234.5
}
```

## Testing

```bash
# Test Modal runner
RUNNER=modal uv run python tests/test_inference.py

# Test gRPC runner
RUNNER=local uv run python tests/test_inference.py
```

## API Structure

- `app/routers/`: FastAPI routers (process, health)
- `app/services/inference/`: VLM inference code
- `app/services/preprocessing/`: Image preprocessing
- `app/gRPC/`: gRPC protocol definitions and generated stubs
- `app/models/`: Pydantic models (VLMResponseFormat, InferenceConfig, etc.)
- `app/utils/`: Helpers (logging, image validation, etc.)
