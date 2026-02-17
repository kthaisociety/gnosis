"""
Test suite for S3/Cloudflare R2 operations.

Tests all S3 bucket operations including:
- Bucket existence checks
- File uploads
- File downloads
- File deletion
- Metadata extraction
- UUID generation
"""

import os
import tempfile
from uuid import UUID

import pytest
from lib.storage.s3 import (
    S3_BUCKET_NAME,
    check_image_exists,
    delete_image_from_s3,
    ensure_s3_bucket_exists,
    generate_s3_key,
    get_image_metadata,
    get_s3_url,
    upload_image_to_s3,
)
from PIL import Image


class TestS3BucketOperations:
    """Test basic S3 bucket operations."""

    def test_bucket_exists(self):
        """Test that the S3 bucket exists or can be created."""
        result = ensure_s3_bucket_exists()
        assert result is True, "S3 bucket should exist or be created"

    def test_bucket_name_configured(self):
        """Test that bucket name is configured in environment."""
        assert S3_BUCKET_NAME is not None, "BUCKET_NAME must be set in .env"
        assert len(S3_BUCKET_NAME) > 0, "BUCKET_NAME cannot be empty"


class TestS3KeyGeneration:
    """Test S3 key generation with UUIDs."""

    def test_generate_s3_key_new_uuid(self):
        """Test generating a new UUID-based S3 key."""
        dataset_name = "test_dataset"
        file_extension = "png"

        image_uuid, s3_key = generate_s3_key(dataset_name, file_extension)

        # Verify UUID is valid
        assert isinstance(image_uuid, UUID)

        # Verify S3 key format
        expected_format = f"datasets/{dataset_name}/{image_uuid}.{file_extension}"
        assert s3_key == expected_format

    def test_generate_s3_key_with_existing_uuid(self):
        """Test generating S3 key with a provided UUID."""
        dataset_name = "test_dataset"
        file_extension = "jpg"
        existing_uuid = UUID("12345678-1234-5678-1234-567812345678")

        image_uuid, s3_key = generate_s3_key(
            dataset_name, file_extension, existing_uuid
        )

        # Verify UUID matches
        assert image_uuid == existing_uuid

        # Verify S3 key format
        expected_format = f"datasets/{dataset_name}/{existing_uuid}.{file_extension}"
        assert s3_key == expected_format

    def test_generate_s3_key_strips_leading_dot(self):
        """Test that leading dot is stripped from file extension."""
        dataset_name = "test_dataset"
        file_extension = ".png"  # With leading dot

        _, s3_key = generate_s3_key(dataset_name, file_extension)

        # Should not have double dot
        assert ".." not in s3_key
        assert s3_key.endswith(".png")


class TestImageMetadata:
    """Test image metadata extraction."""

    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image."""
        # Create a simple test image
        img = Image.new("RGB", (100, 200), color="red")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_get_image_metadata(self, temp_image):
        """Test extracting metadata from an image file."""
        metadata = get_image_metadata(temp_image)

        # Verify all fields are present
        assert "width" in metadata
        assert "height" in metadata
        assert "format" in metadata
        assert "file_size_bytes" in metadata

        # Verify values
        assert metadata["width"] == 100
        assert metadata["height"] == 200
        assert metadata["format"] == "png"
        assert metadata["file_size_bytes"] > 0

    def test_get_image_metadata_invalid_file(self):
        """Test metadata extraction with invalid file."""
        metadata = get_image_metadata("nonexistent_file.png")

        # Should return None for all fields
        assert metadata["width"] is None
        assert metadata["height"] is None
        assert metadata["format"] is None
        assert metadata["file_size_bytes"] is None


class TestS3Upload:
    """Test S3 file upload operations."""

    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image."""
        img = Image.new("RGB", (50, 50), color="blue")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_upload_image_to_s3(self, temp_image):
        """Test uploading an image to S3."""
        # Generate S3 key
        dataset_name = "test_dataset"
        file_extension = "png"
        _, s3_key = generate_s3_key(dataset_name, file_extension)

        # Upload image
        etag = upload_image_to_s3(temp_image, s3_key)

        # Verify upload succeeded
        assert etag is not None, "Upload should return an ETag"
        assert isinstance(etag, str), "ETag should be a string"
        assert len(etag) > 0, "ETag should not be empty"

        # Verify file exists in S3
        exists = check_image_exists(s3_key)
        assert exists is True, "Uploaded file should exist in S3"

        # Cleanup: delete the uploaded file
        delete_image_from_s3(s3_key)

    def test_upload_image_with_custom_content_type(self, temp_image):
        """Test uploading with custom content type."""
        dataset_name = "test_dataset"
        _, s3_key = generate_s3_key(dataset_name, "png")

        etag = upload_image_to_s3(temp_image, s3_key, content_type="image/png")

        assert etag is not None
        assert check_image_exists(s3_key)

        # Cleanup
        delete_image_from_s3(s3_key)

    def test_upload_nonexistent_file(self):
        """Test uploading a file that doesn't exist."""
        _, s3_key = generate_s3_key("test_dataset", "png")

        etag = upload_image_to_s3("nonexistent_file.png", s3_key)

        # Should return None on failure
        assert etag is None


class TestS3Delete:
    """Test S3 file deletion operations."""

    @pytest.fixture
    def uploaded_image(self):
        """Upload a test image and return its S3 key."""
        # Create temporary image
        img = Image.new("RGB", (10, 10), color="green")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        # Generate S3 key and upload
        _, s3_key = generate_s3_key("test_dataset", "png")
        upload_image_to_s3(temp_path, s3_key)

        # Cleanup local file
        os.remove(temp_path)

        yield s3_key

        # Ensure cleanup (in case test fails)
        try:
            delete_image_from_s3(s3_key)
        except Exception:
            pass

    def test_delete_image_from_s3(self, uploaded_image):
        """Test deleting an image from S3."""
        s3_key = uploaded_image

        # Verify file exists before deletion
        assert check_image_exists(s3_key) is True

        # Delete the file
        result = delete_image_from_s3(s3_key)

        # Verify deletion succeeded
        assert result is True

        # Verify file no longer exists
        assert check_image_exists(s3_key) is False

    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist."""
        s3_key = "datasets/test/nonexistent-file.png"

        # Should still return True (S3 delete is idempotent)
        result = delete_image_from_s3(s3_key)
        assert result is True


class TestS3URLGeneration:
    """Test S3 URL generation."""

    def test_get_s3_url(self):
        """Test generating S3 URL for an object."""
        s3_key = "datasets/test_dataset/test-image.png"

        url = get_s3_url(s3_key)

        # Verify URL format
        assert url is not None
        assert isinstance(url, str)
        assert s3_key in url
        assert S3_BUCKET_NAME in url


class TestS3CheckExists:
    """Test S3 file existence checks."""

    @pytest.fixture
    def uploaded_image(self):
        """Upload a test image and return its S3 key."""
        img = Image.new("RGB", (10, 10), color="yellow")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        _, s3_key = generate_s3_key("test_dataset", "png")
        upload_image_to_s3(temp_path, s3_key)
        os.remove(temp_path)

        yield s3_key

        delete_image_from_s3(s3_key)

    def test_check_image_exists_true(self, uploaded_image):
        """Test checking existence of an uploaded file."""
        result = check_image_exists(uploaded_image)
        assert result is True

    def test_check_image_exists_false(self):
        """Test checking existence of a non-existent file."""
        s3_key = "datasets/test/does-not-exist.png"
        result = check_image_exists(s3_key)
        assert result is False


class TestS3Integration:
    """Integration tests for complete S3 workflows."""

    def test_complete_upload_workflow(self):
        """Test complete workflow: generate key, upload, verify, delete."""
        # 1. Create test image
        img = Image.new("RGB", (150, 100), color="purple")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img.save(f, format="JPEG")
            temp_path = f.name

        try:
            # 2. Extract metadata
            metadata = get_image_metadata(temp_path)
            assert metadata["width"] == 150
            assert metadata["height"] == 100
            assert metadata["format"] == "jpeg"

            # 3. Generate S3 key
            dataset_name = "integration_test"
            image_uuid, s3_key = generate_s3_key(dataset_name, "jpg")
            assert isinstance(image_uuid, UUID)
            assert "integration_test" in s3_key

            # 4. Upload to S3
            etag = upload_image_to_s3(temp_path, s3_key)
            assert etag is not None

            # 5. Verify exists
            assert check_image_exists(s3_key) is True

            # 6. Get URL
            url = get_s3_url(s3_key)
            assert url is not None
            assert s3_key in url

            # 7. Delete from S3
            delete_result = delete_image_from_s3(s3_key)
            assert delete_result is True

            # 8. Verify deleted
            assert check_image_exists(s3_key) is False

        finally:
            # Cleanup local file
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
