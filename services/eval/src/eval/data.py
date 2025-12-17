import csv
import os

from .eval_models import EvalDataset, EvalDatasetItem  # TODO: Move to lib/ ?


def get_dataset(name: str = None, path: str = None, local: bool = True) -> EvalDataset:
    if local and not path:
        raise ValueError("Cannot get local dataset without path")
    if not local and not name:
        raise ValueError("Cannot get cloud dataset without name")

    if local:
        dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")
        dataset_paths = os.listdir(dataset_dir)
        for path in dataset_paths:
            if name == path:
                return csv_to_dataset(path)

    else:
        raise ValueError("Cannot get cloud dataset. Unsupported.")


def dataset_to_csv(dataset: EvalDataset, dir: str):
    path = os.path.join(dir, f"{dataset.name}.csv")
    fields = ["image_path, image_type, expected"]
    try:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fields=fields)
            writer.writeheader()
            for item in dataset.items:
                writer.writerow(item.model_dump())
    except Exception as e:
        raise ValueError(f"Failed to write dataset to csv at {path}: {e}")


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
