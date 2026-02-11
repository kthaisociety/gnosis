# GNOSIS GATEWAY

REST API gateway for VLM inference with routing to Modal or local gRPC server.

## Architecture

**Routing**: Routes inference requests via the `runner` form field:

- `modal` - Modal inference (serverless)
- `local` - gRPC to `vlm_server`

**Components**:

- `src/gateway/routers/process_router.py`: Request validation, queueing, and routing
- `src/gateway/routers/modal_runner.py`: Modal inference runner
- `src/gateway/routers/grpc_runner.py`: gRPC inference runner
- `lib/src/lib/gRPC/protos/vlm.proto`: gRPC protocol definition
- `services/vlm_server/src/vlm_server/inference/`: Model inference

## Setup

```bash
# gateway environment
cd services/gateway
uv venv
uv sync

# generate gRPC stubs
cd ../..
bash scripts/gen_grpc_protos.sh
```

Create `.env` file:

```bash
<<<<<<< HEAD
MODAL_TOKEN_ID=your_token_id
MODAL_TOKEN_SECRET=your_token_secret
SERVER_IP=localhost  # For gRPC

# Optional gateway settings
TITLE="The Gnosis API"
HOST=127.0.0.1
PORT=8000
WORKERS=1
```

## Redis queue (optional)

The gateway can use Redis for request queueing and rate limiting. If disabled,
requests run inline without Redis.

Start Redis (Docker):

```bash
docker run --rm -p 6379:6379 redis:7
```

Enable in `.env`:

```bash
QUEUE_ENABLED=true
REDIS_URL=redis://localhost:6379
RATE_LIMIT_ENABLED=true

# Optional tuning
QUEUE_KEY=jobs
MAX_QUEUE_SIZE=100
JOB_TIMEOUT_S=480
RESULT_TTL_SECONDS=120
RESULT_POLL_INTERVAL_S=0.02
RATE_LIMIT_PER_IP_PER_MIN=10
RATE_LIMIT_GLOBAL_PER_MIN=60
RATE_LIMIT_WINDOW_SECONDS=60
>>>>>>> origin/dev
```

## Run Server

You can run the server directly using uvicorn:

```bash
uv run uvicorn gateway.server:app --host 127.0.0.1 --port 8000
```

Alternatively, you can use the helper script from the project root:

```bash
# From the project root
bash scripts/run_gateway.sh
```

## API Usage

Base URL: `http://127.0.0.1:8000` (override with `HOST` and `PORT` env vars)

### OpenAPI

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

### Health

- HTML dashboard: `GET /health/`
- JSON status: `GET /health/json`

### Inference

`POST /process` (multipart/form-data)

Fields:

- `file` (required): Image file upload
- `runner` (optional): `modal` or `local` (default `modal`)
- `config` (required): JSON string matching `InferenceConfig`
- `prompt` (optional): Custom prompt

`InferenceConfig` (JSON)

Required:

- `model_name`
- `output_schema_name` for Gemini models (supported: `TableOutput`)

Optional:

- `use_gpu`, `dtype`, `max_tokens`, `temperature`, `top_p`, `top_k`
- `api_key` (for API models like Gemini)
- `max_model_len`, `model_class`, `device_map`, `return_tensors`, `padding`, `attn_implementation`

Example (Modal):

```bash
curl -X POST "http://127.0.0.1:8000/process"   -F "file=@image.png"   -F "runner=modal"   -F 'config={"model_name":"gemini-2.5-flash","output_schema_name":"VLMTableOutput"}'
```

Example (local gRPC):

```bash
curl -X POST "http://127.0.0.1:8000/process"   -F "file=@image.png"   -F "runner=local"   -F 'config={"model_name":"gemini-2.5-flash","output_schema_name":"VLMTableOutput"}'
```

### Response Format

```json
{
  "text": "{\"title\":\"...\",\"data\":[{\"x\":1.0,\"y\":2.0}]}",
  "model_name": null,
  "inference_time_ms": 1234.5,
  "tokens_used": null
}
```

The VLM returns a single string (`text`). For structured output (e.g. `VLMTableOutput`), it is JSON-encoded; parse on the client as needed.

## Testing

```bash
uv run tests/test_inference.py
```

## API Structure

- `src/gateway/routers/`: FastAPI routers (process, health)
- `src/gateway/preprocessing/`: Image preprocessing
- `lib/src/lib/gRPC/`: gRPC protocol definitions and generated stubs
- `lib/src/lib/models/`: Pydantic models (VLMResponse, InferenceConfig, etc.)
- `lib/src/lib/utils/`: Helpers (logging, image validation, etc.)
