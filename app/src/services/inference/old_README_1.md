# Run a VLLM in inference DOCS





**Info:** The whole purpose of the inference directory and its implementations is to run VLLMs easily with plug and play for differnt models. This avoids boilerplate code and keeps everything nice and simple.

**Be aware that this is an experimental setting. Please report bugs or improvements to Elias or Sebastian.**



## Architecture

  - main.py - Entry point with inference() function
  - vlm.py - Abstract base classes and data models
  - vlm_transformer.py - Transformer-based VLM implementation
  - prompts.py - Predefined prompts for graph extraction

## Instructions

### Get started

```bash
from main import inference

  model_name = ModelName.NANONETS
  results = inference(images, model_name)
```

As of now only the "nanonets/Nanonets-OCR-s" model is supported per default. However you would like to try a different model (given it can be easily loaded with huggingface transformers) you can simply provide it's clear name as model_name. Additional support for GPU acceleration will come to a later point in time.

The inference() function can run single or multiple images. **In any case provide a list of images.**

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


# Modal Deploy

```bash
# this is NEEDED for authenticating with modal (will disappear soon)
uv run python3 -m modal setup

# deploys the two functions infer and download_model
uv run modal deploy src/infer/modalDeploy.py

# runs the download model with parameter model-name 
uv run modal run src/infer/modalDeploy.py::download_model --model-name "nanonets/Nanonets-OCR-s"
```

Then to test it use to run the vlm inference test using the modal `infer` function deployed.
```bash
uv run python tests/vlm_tests.py
```

## Why use attn_implemenation


Effectively this is just used to tell Modal that we want to use a different attention mechanism. There is either "eager" (default), "spda" and "flash_attention_2". 

The attn_implementation parameter lets you choose the speed/compatibility tradeoff based on your deployment environment.