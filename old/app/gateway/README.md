# GNOSIS GATEWAY

REST API gateway for VLM inference with routing to Modal or local gRPC server.

## Architecture

**Routing**: Routes inference requests via `runner` query param:
- `modal` → Modal inference (serverless)
- `local` → gRPC to `vlm_server`

**Components**:
- `routers/process_router.py`: Main routing logic
- `routers/modal_runner.py`: Modal inference runner
- `routers/grpc_runner.py`: gRPC inference runner
- `gRPC/protos/vlm.proto`: gRPC protocol definition
- `services/inference/`: Shared inference code (used by both Modal and local)

## Setup

```bash
# gateway environment
cd app/gateway
uv venv
uv sync

# generate gRPC stubs
cd ../..
bash scripts/gen_grpc_protos.sh
```

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
uv run tests/test_inference.py
```

## API Structure

- `app/routers/`: FastAPI routers (process, health)
- `app/services/inference/`: VLM inference code
- `app/services/preprocessing/`: Image preprocessing
- `app/gRPC/`: gRPC protocol definitions and generated stubs
- `app/models/`: Pydantic models (VLMResponseFormat, InferenceConfig, etc.)
- `app/utils/`: Helpers (logging, image validation, etc.)
