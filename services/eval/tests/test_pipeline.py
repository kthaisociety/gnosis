"""
Test suite for the image upload pipeline.

Tests the complete workflow: Local File → S3 → Database
"""

import os
import tempfile
from uuid import uuid4

import pytest
from lib.db.operations.eval import (
    create_dataset,
    get_image,
)
from lib.storage.s3 import (
    check_image_exists,
    delete_image_from_s3,
)
from PIL import Image

from eval.data.pipeline import (
    bulk_upload_images,
    upload_benchmark_image,
    verify_image_upload,
)
from eval.models import (
    DatasetCreate,
    ImageStatus,
)


class TestImageUploadPipeline:
    """Test complete image upload pipeline."""

    @pytest.fixture
    def test_dataset(self):
        """Create a test dataset."""
        dataset = DatasetCreate(
            name=f"test_pipeline_{uuid4().hex[:8]}",
            description="Dataset for pipeline tests",
            version="1.0",
        )
        dataset_id = create_dataset(dataset)
        return {"id": dataset_id, "name": dataset.name}

    @pytest.fixture
    def temp_image(self):
        """Create a temporary test image."""
        img = Image.new("RGB", (200, 150), color="orange")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_upload_benchmark_image_complete_workflow(self, test_dataset, temp_image):
        """Test complete upload workflow from local file to S3 and DB."""
        # Upload image
        image_id = upload_benchmark_image(
            local_file_path=temp_image,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
            image_type="test_chart",
            ground_truth=[["", "x1", "x2"], ["y", "1", "2"]],
            metadata={"source": "test"},
        )

        # Verify image was uploaded
        assert image_id is not None, "Upload should return image ID"

        # Verify database record
        db_image = get_image(image_id)
        assert db_image is not None
        assert db_image.image_id == image_id
        assert db_image.dataset_id == test_dataset["id"]
        assert db_image.status == ImageStatus.ACTIVE
        assert db_image.image_type == "test_chart"
        assert db_image.width == 200
        assert db_image.height == 150
        assert db_image.format == "png"
        assert db_image.ground_truth is not None
        assert db_image.metadata is not None
        assert db_image.s3_etag is not None

        # Verify S3 upload
        assert check_image_exists(db_image.file_path) is True

        # Cleanup
        delete_image_from_s3(db_image.file_path)

    def test_upload_with_ground_truth(self, test_dataset, temp_image):
        """Test uploading image with ground truth data."""
        ground_truth = [
            ["", "10", "20", "30"],
            ["Series A", "100", "150", "200"],
            ["Series B", "80", "120", "160"],
        ]

        image_id = upload_benchmark_image(
            local_file_path=temp_image,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
            ground_truth=ground_truth,
        )

        # Verify ground truth stored correctly
        db_image = get_image(image_id)
        assert db_image.ground_truth == ground_truth

        # Cleanup
        delete_image_from_s3(db_image.file_path)

    def test_upload_with_metadata(self, test_dataset, temp_image):
        """Test uploading image with custom metadata."""
        metadata = {
            "x_axis": "Time (hours)",
            "y_axis": "Temperature (°C)",
            "units": "celsius",
            "notes": "Test data",
        }

        image_id = upload_benchmark_image(
            local_file_path=temp_image,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
            metadata=metadata,
        )

        # Verify metadata stored correctly
        db_image = get_image(image_id)
        assert "x_axis" in db_image.metadata
        assert db_image.metadata["x_axis"] == "Time (hours)"
        assert "upload_source" in db_image.metadata  # Added by pipeline

        # Cleanup
        delete_image_from_s3(db_image.file_path)

    def test_upload_nonexistent_file(self, test_dataset):
        """Test uploading a file that doesn't exist."""
        image_id = upload_benchmark_image(
            local_file_path="nonexistent_file.png",
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
        )

        # Should return None on failure
        assert image_id is None

    def test_verify_image_upload(self, test_dataset, temp_image):
        """Test verifying a successful upload."""
        # Upload image
        image_id = upload_benchmark_image(
            local_file_path=temp_image,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
        )

        # Verify upload
        is_verified = verify_image_upload(image_id)
        assert is_verified is True

        # Cleanup
        db_image = get_image(image_id)
        delete_image_from_s3(db_image.file_path)


class TestBulkUpload:
    """Test bulk image upload operations."""

    @pytest.fixture
    def test_dataset(self):
        """Create a test dataset."""
        dataset = DatasetCreate(
            name=f"test_bulk_{uuid4().hex[:8]}",
            description="Dataset for bulk upload tests",
        )
        dataset_id = create_dataset(dataset)
        return {"id": dataset_id, "name": dataset.name}

    @pytest.fixture
    def temp_images(self):
        """Create multiple temporary test images."""
        images = []

        for i in range(3):
            img = Image.new("RGB", (100, 100), color=["red", "green", "blue"][i])

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                img.save(f, format="PNG")
                images.append(f.name)

        yield images

        # Cleanup
        for img_path in images:
            if os.path.exists(img_path):
                os.remove(img_path)

    def test_bulk_upload_images(self, test_dataset, temp_images):
        """Test uploading multiple images at once."""
        results = bulk_upload_images(
            image_files=temp_images,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
            image_type="test_bulk",
        )

        # Verify results
        assert "successful" in results
        assert "failed" in results
        assert len(results["successful"]) == 3
        assert len(results["failed"]) == 0

        # Cleanup uploaded images
        for image_id in results["successful"]:
            db_image = get_image(image_id)
            if db_image:
                delete_image_from_s3(db_image.file_path)

    def test_bulk_upload_with_failures(self, test_dataset, temp_images):
        """Test bulk upload with some failures."""
        # Add a nonexistent file
        image_files = temp_images + ["nonexistent.png"]

        results = bulk_upload_images(
            image_files=image_files,
            dataset_id=test_dataset["id"],
            dataset_name=test_dataset["name"],
        )

        # Should have 3 successful and 1 failed
        assert len(results["successful"]) == 3
        assert len(results["failed"]) == 1

        # Cleanup
        for image_id in results["successful"]:
            db_image = get_image(image_id)
            if db_image:
                delete_image_from_s3(db_image.file_path)


class TestPipelineEdgeCases:
    """Test edge cases and error handling in pipeline."""

    @pytest.fixture
    def test_dataset(self):
        """Create a test dataset."""
        dataset = DatasetCreate(name=f"test_edge_{uuid4().hex[:8]}")
        dataset_id = create_dataset(dataset)
        return {"id": dataset_id, "name": dataset.name}

    def test_upload_large_image(self, test_dataset):
        """Test uploading a large image."""
        # Create large image (2000x2000)
        img = Image.new("RGB", (2000, 2000), color="blue")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, format="PNG")
            temp_path = f.name

        try:
            image_id = upload_benchmark_image(
                local_file_path=temp_path,
                dataset_id=test_dataset["id"],
                dataset_name=test_dataset["name"],
            )

            assert image_id is not None

            # Verify dimensions
            db_image = get_image(image_id)
            assert db_image.width == 2000
            assert db_image.height == 2000

            # Cleanup
            delete_image_from_s3(db_image.file_path)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_different_formats(self, test_dataset):
        """Test uploading images in different formats."""
        formats = [
            ("PNG", "png"),
            ("JPEG", "jpg"),
        ]

        for format_name, extension in formats:
            img = Image.new("RGB", (50, 50), color="green")

            with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as f:
                img.save(f, format=format_name)
                temp_path = f.name

            try:
                image_id = upload_benchmark_image(
                    local_file_path=temp_path,
                    dataset_id=test_dataset["id"],
                    dataset_name=test_dataset["name"],
                )

                assert image_id is not None

                # Verify format
                db_image = get_image(image_id)
                assert db_image.format in [extension, format_name.lower()]

                # Cleanup
                delete_image_from_s3(db_image.file_path)

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
