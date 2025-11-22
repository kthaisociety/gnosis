# GNOSIS VLM SERVER

gRPC server for VLM inference. Supports both Modal and local inference via `runner` parameter.

- **Goal**: Run inference on multiple VLMs through one gRPC endpoint
- **Status**: WIP
- **Todo**: Implement VLM class hierarchy from `gateway/app/services/inference/vlm/` for consistency

## Environment

```bash
# Use uv
uv venv
uv pip install -r requirements.txt
```

```bash
# Install pre-commit hook (formats with Ruff on commit)
pre-commit install
```

## Commits and Formatting

```bash
pre-commit run --all-files
```

## Run Server

```bash
uv run python src/server.py
```

Server listens on `GRPC_BIND:GRPC_PORT` (default: `0.0.0.0:50051`).

## gRPC Protocol

The server implements `VLMServer.GenerateResponse`:
- Request: `Image` message with `image` (bytes) and `runner` (string)
- Response: `Response` message with `html`, `json`, `csv`, `text`, `markdown` fields

### Generate Protos

```bash
cd app/vlm_server
uv run python -m grpc_tools.protoc -I src/protos --python_out=src/generated --grpc_python_out=src/generated src/protos/request.proto
```

## Runner Modes

- `runner="modal"`: Routes to Modal inference (requires `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`)
- `runner="local"` (or any other): Routes to local inference using `services/inference/`

## Modal Setup

```bash
uv run modal setup
```

Create proxy token:
```bash
uv run modal token new --profile gnosis-infer
```

Add to `.env`:
```bash
MODAL_TOKEN_ID=your_token_id
MODAL_TOKEN_SECRET=your_token_secret
```

## Testing

```bash
uv run python tests/vlm_test.py
```