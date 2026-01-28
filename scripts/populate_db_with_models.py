import json
import os
import sys
from datetime import datetime


def setup_paths():
    """Add necessary directories to sys.path to allow for package imports."""
    # The script is in /scripts, so we need to go up one level to get to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # The `lib` package source is in /lib/src
    lib_src_path = os.path.join(project_root, "lib", "src")

    if lib_src_path not in sys.path:
        sys.path.insert(0, lib_src_path)


setup_paths()

try:
    from lib.db.client import get_db_pool
    from lib.db.operations.inference_models import create_inference_model
    from lib.models.vlm import Infer
except ImportError as e:
    print(
        "Error: Could not import required modules.",
        "Please ensure that the project structure is correct and you are running this script from the project root.",
        f"Details: {e}",
        sep="\n",
        file=sys.stderr,
    )
    sys.exit(1)


def create_table_if_not_exists():
    """Creates the inference_models table if it doesn't already exist."""
    print("Attempting to create 'inference_models' table if it doesn't exist...")
    try:
        pool = get_db_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS inference_models (
                        id SERIAL PRIMARY KEY,
                        model_name TEXT NOT NULL,
                        inference_type TEXT,
                        inference_class TEXT,
                        requires_gpu BOOLEAN,
                        default_prompt_name TEXT,
                        default_config JSONB,
                        version INTEGER NOT NULL,
                        multimodal BOOLEAN NOT NULL,
                        max_len_tokens INTEGER,
                        avg_latency FLOAT,
                        top_percentile_accuracy FLOAT,
                        latest_eval_accuracy FLOAT,
                        latest_eval_datetime TIMESTAMP WITH TIME ZONE,
                        UNIQUE (model_name, version)
                    );
                """
                )
        print("Table 'inference_models' check/creation complete.")
    except Exception as e:
        print(f"Error during table creation: {e}", file=sys.stderr)
        print("Please check your database connection and permissions.", file=sys.stderr)
        sys.exit(1)


def populate_models():
    """
    Reads model definitions from a JSON file and inserts them into the database.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    models_json_path = os.path.join(
        project_root,
        "services",
        "vlm_server",
        "src",
        "vlm_server",
        "inference",
        "vlm",
        "models.json",
    )

    print(f"Loading models from: {models_json_path}")

    try:
        with open(models_json_path, "r") as f:
            models_data = json.load(f)
    except FileNotFoundError:
        print(
            f"Error: Models JSON file not found at {models_json_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    for model_name, model_details in models_data.items():
        print(f"Processing model: {model_name}")

        try:
            default_config = model_details.get("default_config", {})
            max_len = (
                default_config.get("max_tokens")
                or default_config.get("max_model_len")
                or 8192
            )

            infer_model = Infer(
                model_name=model_name,
                version=1,
                multimodal=True,
                max_len_tokens=max_len,
                avg_latency=0.0,
                top_percentile_accuracy=0.0,
                latest_eval_accuracy=0.0,
                latest_eval_datetime=datetime.now(),
                inference_type=model_details["inference_type"],
                inference_class=model_details["inference_class"],
                requires_gpu=model_details.get("requires_gpu", False),
                default_prompt_name=model_details.get("default_prompt_name", "default"),
                default_config=default_config,
            )

            created_model = create_inference_model(infer_model)

            if created_model:
                print(
                    f"Successfully inserted model: {created_model.model_name} v{created_model.version}"
                )
            else:
                # This could be because the model already exists if there's a unique constraint.
                print(
                    f"Warning: Failed to insert model '{model_name}'. It might already exist or there was a DB error."
                )

        except Exception as e:
            print(f"Error processing model '{model_name}': {e}", file=sys.stderr)
            # Continue to next model
            continue


if __name__ == "__main__":
    print("Starting database population script for inference models...")
    # NOTE: This script will attempt to connect to the database.
    # Ensure that your environment variables for the DB connection are set.
    create_table_if_not_exists()
    populate_models()
    print("Script finished.")
