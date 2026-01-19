"""
VLM Benchmark Evaluation Module
Tools to evaluate Vision Language Models on benchmark datasets.
"""

from .eval import eval
from .models import EvalOutput

__all__ = [
    "eval",
    "EvalOutput",
]
