# Gateway: Modal/gRPC routing and inference runners

## Architecture

**Routing**: `process_router.py` routes via `runner` query param (`modal` → Modal, else → gRPC).

**Runners**:
- `modal_runner.py`: Modal inference via `OCRInference().infer.remote()`, stub modules for Pydantic deserialization EVERYTHING WORKS
- `grpc_client.py`: gRPC client to `vlm_server`, extracts all response fields (html, json_data, csv, text, markdown)

**gRPC**: Added `vlm.proto` with `Image`/`Response` messages. Generated stubs with fixed relative imports.

## Changes

- `routers/process_router.py`: Added `runner` param routing (`run_modal_inference` vs `run_grpc_inference`)
- `routers/modal_runner.py`: New Modal runner with deserialization stubs
- `grpc_client.py`: New gRPC client
- `gRPC/protos/vlm.proto`: New proto definition
- `gRPC/generated/vlm_pb2_grpc.py`: Fixed relative import
- `models/vlm_models.py`: `json` → `json_data` (fixes Pydantic shadow warning)
- `tests/test_inference.py`: Added modal runner tests, `runner` param, 600s timeout
- `pyproject.toml`: Package structure updates

## TODO

- `vlm_server` should implement VLM class hierarchy from `gateway/app/services/inference/vlm/` for consistency.
