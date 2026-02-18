import os
from dotenv import load_dotenv

from lib.models.vlm import InferenceConfig

from eval.api import inference
from eval.data import list_images_by_dataset, get_dataset_by_name, get_s3_url

load_dotenv()

TEST_PROMPT = """
Extract all data from this graph.
"""


def get_image_url() -> str:
    dataset = get_dataset_by_name("benchmark_v1")
    assert dataset, "Could not get dataset"

    images = list_images_by_dataset(dataset.dataset_id)
    assert images, "Could not get images"

    url = get_s3_url(images[0].file_path)
    assert url, "Could not get image url"

    return url


def test_inference_local():
    config = InferenceConfig(
        model_name="gemini-2.5-flash",
        output_schema_name="TableOutput",
        api_key=os.getenv("GEMINI_API_KEY"),
        prompt=TEST_PROMPT,
    )

    result = inference(
        runner="local",
        image_path=get_image_url(),
        config=config,
    )

    assert result is not None
    assert result.text is not None


def test_inference_modal():
    config = InferenceConfig(
        model_name="nanonets/Nanonets-OCR-s",
        output_schema_name="TableOutput",
        prompt=TEST_PROMPT,
    )

    result = inference(
        runner="modal",
        image_path=get_image_url(),
        config=config,
    )

    assert result is not None
    assert result.text is not None


if __name__ == "__main__":
    test_inference_local()
    test_inference_modal()
