# GNOSIS VLM SERVER

gRPC server for VLM inference.

## Setup
```bash
uv venv
uv pip install -r requirements.txt
```

## Run
```bash
uv run app/server.py
```

Server listens on `GRPC_BIND:GRPC_PORT` (default: `0.0.0.0:50051`).

## Commits and Formatting

```bash
pre-commit install
pre-commit run --all-files
```

## gRPC Protocol

The server implements `VLMServer.GenerateResponse`:
- Request: `Image` message with `image` (bytes) and `runner` (string)
- Response: `Response` message with `html`, `json`, `csv`, `text`, `markdown` fields

### Generate Protos

```bash
cd ../..
bash scripts/gen_grpc_protos.sh
```

## Testing

```bash
uv run tests/test_grpc_inference.py
```
