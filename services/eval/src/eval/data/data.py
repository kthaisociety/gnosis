import os

from eval.models import EvalDataset
from .db import get_dataset_items
from .local import csv_to_dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
os.makedirs(DATASET_DIR, exist_ok=True)


def get_dataset(name: str, local: bool) -> EvalDataset:
    if local:
        for filename in os.listdir(DATASET_DIR):
            found_name = os.path.splitext(filename)[0]
            if name == found_name:
                full_path = os.path.join(DATASET_DIR, filename)
                return csv_to_dataset(full_path)
        raise ValueError(f"Cannot find dataset named {name}.")

    else:
        items = get_dataset_items(name)
        return EvalDataset(name=name, items=items)


def verify_dataset(dataset: EvalDataset):
    if len(dataset.items) == 0:
        raise ValueError("Empty dataset")

    output_schema_names = set()
    for item in dataset.items:
        output_schema_names.add(item.output_schema_name)
    if len(output_schema_names) > 1:
        raise ValueError("More than one output_schema_name contained by dataset items")

    # TODO: add check that output_schema_name is valid too
    # currently VLM.get_model_info is local to vlm_server
    # may have to make shared in lib
