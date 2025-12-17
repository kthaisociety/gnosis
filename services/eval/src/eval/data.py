from .eval_models import EvalDataset  # TODO: Move to lib/ ?


def get_dataset(name: str = None, path: str = None, local: bool = True) -> EvalDataset:
    if local and not path:
        raise ValueError("Cannot get local dataset without path")
    if not local and not name:
        raise ValueError("Cannot get cloud dataset without name")
    return EvalDataset()
