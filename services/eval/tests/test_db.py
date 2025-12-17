import os

from lib.db import close_db_pool, create_schema, drop_schema
from eval.db import create_dataset, drop_dataset, upsert_dataset
from eval.models import EvalDataset, EvalDatasetItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Synthesize example dataset
name = "example"
items = []
for filename in os.listdir(IMAGES_DIR):
    full_path = os.path.join(IMAGES_DIR, filename)
    items.append(
        EvalDatasetItem(image_path=full_path, image_type="generic", expected="hihihaha")
    )
dataset = EvalDataset(name=name, items=items)
item = dataset.items[0]
print(item.model_dump())

# Test db
try:
    create_schema("datasets")
    create_dataset("test")
    upsert_dataset("test", item)
    drop_dataset("test")
    drop_schema("datasets")
finally:
    close_db_pool()
