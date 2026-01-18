"""
VLM Benchmark Evaluation Module

This module provides tools for evaluating Vision Language Models on benchmark datasets.
Supports both cloud-based (S3 + Neon DB) and legacy local datasets.
"""

from .eval import eval, eval_cloud
from .models import EvalOutput

__all__ = [
    "eval",
    "eval_cloud",
    "EvalOutput",
]
