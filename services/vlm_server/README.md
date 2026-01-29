# Inference server
gRPC server for local inference.
Supports transformers and gemini.

### API
```python
# takes image bytes and json serialized inference config
# returns inference output as str (may be json, html...)
Inference(image: bytes, config_json: InferenceConfig)
```

### Environment
```
GRPC_PORT=
GRPC_BIND=
```
