import json
from typing import List, Union

from lib.models.vlm_models import InferenceConfig, VLMTableOutput
from lib.utils.log import get_logger
from .metrics import compute_rms, compute_rnss
from .models import EvalOutput
from .data import get_dataset, verify_dataset
from .api import infer

logger = get_logger(__name__)


def eval(
    runner: str,
    config: InferenceConfig,
    dataset_name: str,
    local_dataset: bool,
    prompt: str = None,
) -> EvalOutput:
    dataset = get_dataset(dataset_name, local=local_dataset)
    try:
        verify_dataset(dataset)
    except Exception as e:
        raise ValueError(f"Invalid dataset: {e}")

    if not config.output_schema_name:
        config.output_schema_name = dataset.items[0].output_schema_name
    else:
        logger.warn(
            "output_schema_name forcefully set instead of relying on dataset's schema. Will produce unwanted results if schemas are not equal."
        )

    if config.output_schema_name != dataset.items[0].output_schema_name:
        raise ValueError(
            "Schema configuration of inference config does not match dataset's schema!"
        )

    rnss = 0.0
    rms = 0.0

    try:
        for item in dataset.items:
            vlm_output = infer(
                runner, item.image_path, prompt, config, local_dataset=local_dataset
            )

            if vlm_output is None or vlm_output.json_data is None:
                logger.warning(f"No output for {item.image_path}, skipping")
                continue

            predicted_table = parse_json_to_table(
                vlm_output.json_data, config.output_schema_name
            )

            target_table = parse_json_to_table(item.expected, config.output_schema_name)

            rms += compute_rms(predicted_table, target_table)
            rnss += compute_rnss(predicted_table, target_table)

    except Exception as e:
        raise ValueError(f"Failed to inference model on dataset: {e}")

    n_items = len(dataset.items)
    avg_rnss = rnss / n_items
    avg_rms = rms / n_items

    return EvalOutput(
        model_name=config.model_name,
        dataset_name=dataset_name,
        output_schema_name=config.output_schema_name,
        avg_rnss=avg_rnss,
        avg_rms=avg_rms,
    )


def vlm_table_output_to_table(output: VLMTableOutput) -> List[List[Union[str, float]]]:
    """
    helper function for parse_json_to_table
    """
    y_label = output.y_label or "y"
    table = [["", y_label]]
    for point in output.data:
        table.append([str(point.x), point.y])

        return table


def parse_json_to_table(
    json_str: str, schema_name: str
) -> List[List[Union[str, float]]]:
    """
    Convert expected output schema (depending on dataset) to a 2D table format for RMS/RNSS metrics.
    """
    if schema_name == "VLMTableOutput":
        data = json.loads(json_str)
        output = VLMTableOutput(**data)
        return vlm_table_output_to_table(output)
    else:
        raise ValueError(f"Unknown schema: {schema_name}")
