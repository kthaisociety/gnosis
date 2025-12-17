from lib.models.vlm_models import InferenceConfig
from .api import infer
from .eval_models import EvalOutput, EvalDataset  # TODO: Move to lib/ ?
from .data import get_dataset
# from .metrics import ......


def eval(
    runner: str,
    config: InferenceConfig,
    dataset_path: str,
    prompt: str = None,
) -> EvalOutput:
    data: EvalDataset = get_dataset(path=dataset_path, local=True)
    for item in data.items:
        vlm_output = infer(runner, item.image_path, prompt, config, local_imgs=True)

        #
        # TODO: measure accuracy of 'out' using different benchmarks here
        #

        out = EvalOutput()
        return out
