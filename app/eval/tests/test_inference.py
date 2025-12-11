from app.api import infer
from app.tmp_models import InferenceConfig, VLMResponseFormat


res = infer(
    runner="local",
    image_path="tests/test_image.png",
    prompt="Extract all data from this graph",
    config=InferenceConfig(
        model_name="nanonets/Nanonets-OCR-s",
        use_gpu=False,
    ))

if res:
    print(res.model_dump())
else:
    print(res)
