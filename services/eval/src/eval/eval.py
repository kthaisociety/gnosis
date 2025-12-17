from lib.models.vlm_models import InferenceConfig
from .models import EvalOutput
from .data import get_dataset
from .api import infer


def eval(
    runner: str,
    config: InferenceConfig,
    dataset_name: str,
    local_dataset: bool,
    prompt: str = None,
) -> EvalOutput:
    dataset = get_dataset(dataset_name, local=local_dataset)
    for item in dataset.items:
        vlm_output = infer(
            runner, item.image_path, prompt, config, local_dataset=local_dataset
        )
        if vlm_output:
            print(vlm_output.model_dump_json(indent=4))
        else:
            print("infer returned none")

        #
        # TODO: measure accuracy of 'out' using different benchmarks here
        #

        out = EvalOutput()
        return out
