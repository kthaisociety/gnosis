from eval.eval import eval
from lib.models.vlm_models import InferenceConfig


if __name__ == "__main__":
    res = eval(
        runner="modal",
        config=InferenceConfig(
            model_name="gemini-2.5-flash",  # nanonets/Nanonets-OCR-s",  # "Qwen/Qwen3-VL-Embedding-8B",
            use_gpu=True,
            attn_implementation="eager",
        ),
        dataset_name="benchmark_v1",
    )
    print(res.model_dump_json(indent=4))
