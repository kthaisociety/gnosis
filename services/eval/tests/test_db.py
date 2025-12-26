import os

from lib.db import close_db_pool, create_schema, drop_schema
from eval.data.db import (
    create_dataset,
    get_dataset_items,
    drop_dataset,
    upsert_dataset,
    create_eval_table,
    get_eval_items,
    upsert_eval_table,
    drop_eval_table,
)
from eval.models import EvalDataset, EvalDatasetItem, EvalOutput
from eval.data import get_dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Synthesize example dataset
name = "example"
items = []
for filename in os.listdir(IMAGES_DIR):
    full_path = os.path.join(IMAGES_DIR, filename)
    items.append(
        EvalDatasetItem(image_path=full_path,
                        output_schema_name="VLMTableOutput", expected="hihihaha")
    )
dataset = EvalDataset(name=name, items=items)
item = dataset.items[0]
print(item.model_dump())

# Synthesize example eval output
eval_output = EvalOutput(
    model_name="model-2.5-flash",
    dataset_name="example",
    output_schema_name="generic",
    avg_rnss=0.1,
    avg_rms=1,
)

# Test db
try:
    # Test datasets
    create_schema("datasets")
    create_dataset("test")
    upsert_dataset("test", item)

    dataset_items = get_dataset_items("test")
    print(dataset_items)

    dataset = get_dataset("test", local=False)
    print(dataset.model_dump())

    #drop_dataset("test")
    #drop_schema("datasets")

    # Test eval output
    create_eval_table()
    upsert_eval_table(eval_output)

    eval_items = get_eval_items()
    print(eval_items)

    #drop_eval_table()
finally:
    close_db_pool()
