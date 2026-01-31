import json
import sys
from datetime import datetime
from pathlib import Path

# Add lib/src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
lib_src = project_root / "lib" / "src"
sys.path.insert(0, str(lib_src))

from lib.models.vlm import Infer
from lib.db.operations.inference_models import (
    ensure_inference_models_table_exists,
    upsert_inference_model,
)


def main():
    ensure_inference_models_table_exists()

    models_json_path = script_dir / "models.json"
    if not models_json_path.exists():
        print(f"Error: models.json not found at {models_json_path}", file=sys.stderr)
        sys.exit(1)

    with open(models_json_path) as f:
        models_data = json.load(f)

    for model_name, model_details in models_data.items():
        default_config = model_details.get("default_config", {})

        model = Infer(
            model_name=model_name,
            version=1,
            multimodal=True,
            avg_latency=0.0,
            top_percentile_accuracy=0.0,
            latest_eval_accuracy=0.0,
            latest_eval_datetime=datetime.now(),
            inference_type=model_details["inference_type"],
            inference_class=model_details["inference_class"],
            requires_gpu=model_details.get("requires_gpu", False),
            default_config=default_config,
        )

        result = upsert_inference_model(model)
        if result:
            print(f"Upserted: {result.model_name} v{result.version}")


if __name__ == "__main__":
    main()
