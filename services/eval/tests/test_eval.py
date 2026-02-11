import os
from dotenv import load_dotenv

from lib.models.vlm import InferenceConfig
from eval.eval import eval

load_dotenv()

TEST_PROMPT = """
Extract all data from this graph.

Respond in exactly this JSON format:
{
  "title": "string",
  "x_label": "string",
  "y_label": "string",
  "legend": ["string"],
  "data": [
    {"x": ..., "y": ...},
    ...
  ]
}
"""


def test_eval_local():
    config = InferenceConfig(
        model_name="gemini-3-flash-preview",
        output_schema_name="TableOutput",
        api_key=os.getenv("GEMINI_API_KEY"),
        prompt=TEST_PROMPT
    )

    result = eval(
        runner="local",
        config=config,
        dataset_name="benchmark_v1",
        initiated_by="test",
    )

    assert result is not None
    assert result.model_name == "gemini-3-flash-preview"
    assert result.dataset_name == "benchmark_v1"
    assert result.avg_rms >= 0
    assert result.avg_rnss >= 0


def test_eval_modal():
    config = InferenceConfig(
        model_name="nanonets/Nanonets-OCR-s",
        output_schema_name="TableOutput",
        prompt=TEST_PROMPT
    )

    result = eval(
        runner="modal",
        config=config,
        dataset_name="benchmark_v1",
        initiated_by="test",
    )

    assert result is not None
    assert result.model_name == "gemini-2.5-flash"
    assert result.dataset_name == "benchmark_v1"
    assert result.avg_rms >= 0
    assert result.avg_rnss >= 0


if __name__ == "__main__":
    test_eval_local()
    #test_eval_modal()
