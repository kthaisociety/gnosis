"""
VLM Benchmark Evaluation Module
Tools to evaluate Vision Language Models on benchmark datasets.
"""


def eval(*args, **kwargs):
    from .eval import eval as _eval

    return _eval(*args, **kwargs)


from .models import EvalOutput

__all__ = [
    "eval",
    "EvalOutput",
]
