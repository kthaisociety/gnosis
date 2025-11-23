# Inference

Contains the inference service for the OCR model, both VLM server and modal compute.

## Compute

### VLM Server
...TODO

### Modal Deployment

#### Prerequisites
- Modal token credentials (MODAL_TOKEN_ID + MODAL_TOKEN_SECRET)
- GPU access (L4 or higher)

#### Deployment
1. Build the Modal app:
```bash
modal build gnosis/app/src/services/inference/compute/modal/deploy.py
```

2. Deploy the app:
```bash
modal deploy gnosis/app/src/services/inference/compute/modal/deploy.py
```

#### Download Model
```bash
modal run gnosis/app/src/services/inference/compute/modal/deploy.py::download_model --model-name "nanonets/Nanonets-OCR-s"
```