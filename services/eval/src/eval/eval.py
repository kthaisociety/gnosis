from lib.models.vlm_models import InferenceConfig
from .metrics import compute_rms, compute_rnss
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

    rnss = 0.0
    rms = 0.0
    for item in dataset.items:

        vlm_output = infer(
            runner, item.image_path, prompt, config, local_dataset=local_dataset
        )
        if vlm_output:
            print(vlm_output.model_dump_json(indent=4))
        else:
            print("infer returned none")

        rms += compute_rms(vlm_output)
        rnss += compute_rnss(vlm_output)

        #
        # TODO: measure accuracy of 'out' using different benchmarks here
        #

    out = EvalOutput()
    return out
