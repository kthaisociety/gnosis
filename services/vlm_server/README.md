# Inference Server

gRPC server for local VLM inference.

## Supported Backends

- **Gemini** (`inference/gemini.py`) — Google Gemini API
- **GPT** (`inference/gpt.py`) — OpenAI GPT API
- **Transformer** (`inference/transformer.py`) — Local HuggingFace models (e.g. dots.ocr)

## API

```python
# takes image bytes and json serialized inference config
# returns inference output as str (may be json, html...)
Inference(image: bytes, config_json: InferenceConfig)
```

## Setup

This package is part of the monorepo workspace. From the project root:

```bash
uv sync
```

Or standalone:

```bash
cd services/vlm_server
uv venv
uv sync
```

## Environment

```
GRPC_PORT=50051
GRPC_BIND=0.0.0.0
```

See the root `.env.example` for Modal and other settings.

## Tree

```
.
├── Dockerfile
├── modal_app.py
├── pyproject.toml
├── src
│   └── vlm_server
│       ├── inference
│       │   ├── gemini.py
│       │   ├── gpt.py
│       │   ├── main.py
│       │   └── transformer.py
│       └── server.py
└── tests
    ├── image.png
    └── test_inference.py
```
