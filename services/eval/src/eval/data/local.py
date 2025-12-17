import csv
import os

from eval.models import EvalDataset, EvalDatasetItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
os.makedirs(DATASET_DIR, exist_ok=True)


def csv_to_dataset(path: str) -> EvalDataset:
    name = os.path.splitext(os.path.basename(path))[0]
    items = []
    try:
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(EvalDatasetItem(**row))
        return EvalDataset(name=name, items=items)
    except Exception as e:
        raise ValueError(f"Failed to read dataset from csv at {path}: {e}")


def dataset_to_csv(dataset: EvalDataset):
    path = os.path.join(DATASET_DIR, f"{dataset.name}.csv")
    fields = ["image_path", "image_type", "expected"]

    try:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for item in dataset.items:
                writer.writerow(item.model_dump())
    except Exception as e:
        raise ValueError(f"Failed to write dataset to csv at {path}: {e}")
