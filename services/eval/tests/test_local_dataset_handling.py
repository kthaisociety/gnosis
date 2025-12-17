import os

from eval.data import get_dataset
from eval.data.local import dataset_to_csv
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

# Save the dataset as csv
dataset = EvalDataset(name=name, items=items)
print(dataset.model_dump_json(indent=4))
dataset_to_csv(dataset)


# Try to retrieve the example dataset
res = get_dataset(name, local=True)
print(res.model_dump_json(indent=4))
