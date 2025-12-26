from eval.models import EvalDatasetItem
import ast


def parse_eval_dataset_row(row: dict) -> EvalDatasetItem:
    if 'eval_type' in row and isinstance(row['eval_type'], str):
        row['eval_type'] = ast.literal_eval(row['eval_type'])
    return EvalDatasetItem(**row)
