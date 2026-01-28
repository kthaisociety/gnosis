from dotenv import load_dotenv
import os

from eval.api import infer
from lib.models.vlm_models import InferenceConfig

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


res = infer(
    runner="local",
    image_path="tests/images/test_image.png",
    prompt="Extract all data from this graph",
    config=InferenceConfig(
        model_name="gemini-2.5-flash",
        api_key=GEMINI_API_KEY,
        output_schema_name="VLMTableOutput",
        use_gpu=False,
    ),
    local_dataset="example",
)

if res:
    print(res.model_dump_json(indent=4))
else:
    print(res)
