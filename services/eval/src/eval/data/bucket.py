from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
import os

from lib.utils.log import get_logger

load_dotenv()
logger = get_logger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "dataset-images"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Requires service key
def _ensure_bucket_exists():
    try:
        supabase.storage.get_bucket(BUCKET_NAME)
    except Exception as e:
        logger.info(f"Could not fetch supabase bucket ({e}). Creating bucket...")
        supabase.storage.create_bucket(BUCKET_NAME, options={"public": True})


def upload_dataset_image(dataset_name: str, local_image_path: str) -> str:
    filename = Path(local_image_path).name
    remote_path = f"{dataset_name}/{filename}"

    with open(local_image_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=remote_path,
            file=f,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )

    return supabase.storage.from_(BUCKET_NAME).get_public_url(remote_path)


def delete_dataset_image(image_url: str):
    path = image_url.split(f"{BUCKET_NAME}/")[-1]
    supabase.storage.from_(BUCKET_NAME).remove([path])


def delete_dataset_images(dataset_name: str):
    files = supabase.storage.from_(BUCKET_NAME).list(dataset_name)
    paths = [f"{dataset_name}/{f['name']}" for f in files]
    if paths:
        supabase.storage.from_(BUCKET_NAME).remove(paths)


def is_local_image(image_path: str) -> bool:
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return False
    return True
