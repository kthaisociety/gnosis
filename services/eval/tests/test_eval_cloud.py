from eval.eval import eval_cloud
from lib.models.vlm_models import InferenceConfig


if __name__ == "__main__":
    res = eval_cloud(
        runner="modal",
        config=InferenceConfig(
            model_name="Qwen/Qwen3-VL-Embedding-8B",
            use_gpu=False,
        ),
        dataset_name="benchmark_v1",
    )
