import sys
from pathlib import Path

# Add lib/src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
lib_src = project_root / "lib" / "src"
sys.path.insert(0, str(lib_src))


def main():
    from lib.storage.s3 import S3_BUCKET_NAME, ensure_s3_bucket_exists

    if not S3_BUCKET_NAME:
        print("Error: BUCKET_NAME environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Checking S3 bucket '{S3_BUCKET_NAME}'...")
    success = ensure_s3_bucket_exists()

    if success:
        print(f"S3 bucket '{S3_BUCKET_NAME}' is ready.")
    else:
        print(
            f"Error: Failed to ensure S3 bucket '{S3_BUCKET_NAME}' exists.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
