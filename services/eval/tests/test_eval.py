from eval.eval import eval
from lib.models.vlm import InferenceConfig

prompt = """Extract frm this graph:
1. Title
2. X-axis label
3. Y-axis label
4. Legend (if present)
5. ALL data values
Required JSON format:
{
    "title": str or null,
    "x_label": str or null,
    "y_label": str or null,
    "legend": ["serie1", "serie2"] or null,
    "data": [{"x": x1, "y": y1}, {"x": x2, "y": y2}, {"x": x3, "y": y3}, ...]
}
Return ONLY the JSON object, nothing else.

Respond with only 3 data points to not reach the token limit.
"""

if __name__ == "__main__":
    res = eval(
        prompt=prompt,
        runner="local",
        config=InferenceConfig(
            model_name="gemini-2.5-flash",  # nanonets/Nanonets-OCR-s",  # "Qwen/Qwen3-VL-Embedding-8B",
            use_gpu=True,
            attn_implementation="eager",
            output_schema_name="TableOutput",
            api_key="",
        ),
        dataset_name="benchmark_v1",
    )
    print(res.model_dump_json(indent=4))
