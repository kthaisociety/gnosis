from eval.api import infer
from lib.models.vlm_models import InferenceConfig


res = infer(
    runner="local",
    image_path="tests/images/test_image.png",
    prompt="Extract all data from this graph",
    config=InferenceConfig(
        model_name="nanonets/Nanonets-OCR-s",
        use_gpu=False,
    ),
)

if res:
    print(res.model_dump_json(indent=4))
else:
    print(res)
