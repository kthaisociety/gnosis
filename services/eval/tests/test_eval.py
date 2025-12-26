#
# Requires GEMINI_API_KEY in eval/.env
#

from dotenv import load_dotenv
import os

from eval.eval import eval
from lib.models.vlm_models import InferenceConfig

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No API KEY found in .env")


res = eval(
    runner="local",
    config=InferenceConfig(
        model_name="gemini-2.5-flash",
        api_key=GEMINI_API_KEY,
        output_schema_name="VLMTableOutput"
    ),
    dataset_name="example",
    local_dataset=True,
)


if res:
    print(res.model_dump_json(indent=4))
else:
    print(res)
