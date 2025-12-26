from lib.models.vlm_models import InferenceConfig
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
        logger.warn("output_schema_name forcefully set instead of relying on dataset's schema. Will produce unwanted results if schemas are not equal.")

    rnss = 0.0
    rms = 0.0

    try:
        for item in dataset.items:
            vlm_output = infer(
                runner, item.image_path, prompt, config, local_dataset=local_dataset
            )

            # TODO
            # rms += compute_rms(vlm_output)
            # rnss += compute_rnss(vlm_output)
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
