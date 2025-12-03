# Run a VLLM in inference DOCS





**Info:** The whole purpose of the inference directory and its implementations is to run VLLMs easily with plug and play for differnt models. This avoids boilerplate code and keeps everything nice and simple.

**Be aware that this is an experimental setting. Please report bugs or improvements to Elias or Sebastian.**



## Architecture

- `main.py`: Entry point with `infer()` function
- `vlm/vlm.py`: Abstract base classes and data models
- `vlm/transformer.py`: Transformer-based VLM implementation
- `vlm/gemini.py`: Gemini API VLM implementation
- `prompts/`: Predefined prompts for graph extraction

## Instructions

### Get Started

```python
from infer.main import infer
from infer.vlm import InferenceConfig

config = InferenceConfig(
    model_name="nanonets/Nanonets-OCR-s",
    use_gpu=True
)
results = infer(images, config, prompt="default")
```

The `infer()` function accepts a list of PIL Images, `InferenceConfig`, and optional prompt string. Returns `VLMOutput` objects.

### Access structured output

```bash
{
    "title": str or null,
    "x_label": str or null,
    "y_label": str or null,
    "legend": ["serie1", "serie2"] or null,
    "data": [[x1, y1], [x2, y2], [x3, y3], ...]
}
```
A basic prompt is used (can be found in prompts.py) to get the structured output as can be seen above. You can also provide inference() with your own prompt and adapt the output format to your needs.


## Modal Deploy

```bash
# Authenticate with Modal
uv run modal setup

# Deploy inference functions
uv run python scripts/modal_deploy.py

# Pre-download model (optional)
uv run modal run scripts/modal_deploy.py::download_model --model-name "nanonets/Nanonets-OCR-s"
```

Test Modal inference:
```bash
uv run python tests/vlm_test.py
```

## Why use attn_implemenation


Effectively this is just used to tell Modal that we want to use a different attention mechanism. There is either "eager" (default), "spda" and "flash_attention_2". 

The attn_implementation parameter lets you choose the speed/compatibility tradeoff based on your deployment environment.