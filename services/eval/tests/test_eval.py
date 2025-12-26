#
# Requires GEMINI_API_KEY in eval/.env
#

from dotenv import load_dotenv
import os

from lib.models.vlm_models import InferenceConfig
from lib.db import close_db_pool
from eval.eval import eval
from eval.data.db import upsert_eval_table

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No API KEY found in .env")


res = eval(
    runner="local",
    config=InferenceConfig(
        model_name="gemini-2.5-flash",
        api_key=GEMINI_API_KEY,
        #output_schema_name="VLMTableOutput",
        use_gpu=False,
    ),
    dataset_name="test",
    local_dataset=False,
)

upsert_eval_table(res)


if res:
    print(res.model_dump_json(indent=4))
else:
    print(res)

close_db_pool()
