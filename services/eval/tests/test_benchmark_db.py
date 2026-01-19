"""
Test suite for benchmark database operations.

Tests all CRUD operations for the benchmark schema:
- Datasets
- Images
- Evaluation runs
- Predictions
- Metrics
"""

import pytest
from uuid import uuid4

from eval.data.db import (
    create_dataset,
    get_dataset,
    get_dataset_by_name,
    list_datasets,
    create_image,
    get_image,
    update_image_status,
    list_images_by_dataset,
    create_evaluation_run,
    update_run_status,
    get_evaluation_run,
    create_prediction,
    get_predictions_by_run,
    create_metric,
    get_metrics_by_prediction,
    get_run_metrics_summary,
)
from eval.models import (
    DatasetCreate,
    ImageCreate,
    ImageStatus,
    EvaluationRunCreate,
    RunStatus,
    PredictionCreate,
    MetricCreate,
)


class TestDatasetOperations:
    """Test dataset CRUD operations."""

    def test_create_dataset(self):
        """Test creating a new dataset."""
        dataset = DatasetCreate(
            name=f"test_dataset_{uuid4().hex[:8]}",
            description="Test dataset for unit tests",
            version="1.0.0",
        )

        dataset_id = create_dataset(dataset)

        assert dataset_id is not None, "Dataset creation should return an ID"
        assert isinstance(dataset_id, type(uuid4())), "Dataset ID should be a UUID"

    def test_create_duplicate_dataset(self):
        """Test creating a dataset with duplicate name."""
        unique_name = f"test_dataset_{uuid4().hex[:8]}"

        dataset1 = DatasetCreate(name=unique_name, description="First")
        dataset_id1 = create_dataset(dataset1)
        assert dataset_id1 is not None

        # Try to create duplicate
        dataset2 = DatasetCreate(name=unique_name, description="Second")
        dataset_id2 = create_dataset(dataset2)

        # Should return None due to unique constraint
        assert dataset_id2 is None

    def test_get_dataset(self):
        """Test retrieving a dataset by ID."""
        # Create dataset
        dataset = DatasetCreate(
            name=f"test_dataset_{uuid4().hex[:8]}",
            description="Test dataset",
            version="1.0.0",
        )
        dataset_id = create_dataset(dataset)

        # Retrieve dataset
        retrieved = get_dataset(dataset_id)

        assert retrieved is not None
        assert retrieved.dataset_id == dataset_id
        assert retrieved.name == dataset.name
        assert retrieved.description == dataset.description
        assert retrieved.version == dataset.version
        assert retrieved.created_at is not None

    def test_get_dataset_by_name(self):
        """Test retrieving a dataset by name."""
        unique_name = f"test_dataset_{uuid4().hex[:8]}"

        # Create dataset
        dataset = DatasetCreate(
            name=unique_name, description="Test dataset", version="2.0.0"
        )
        dataset_id = create_dataset(dataset)

        # Retrieve by name
        retrieved = get_dataset_by_name(unique_name)

        assert retrieved is not None
        assert retrieved.dataset_id == dataset_id
        assert retrieved.name == unique_name
        assert retrieved.version == "2.0.0"

    def test_list_datasets(self):
        """Test listing all datasets."""
        # Create multiple datasets
        dataset1 = DatasetCreate(name=f"test_dataset_{uuid4().hex[:8]}")
        dataset2 = DatasetCreate(name=f"test_dataset_{uuid4().hex[:8]}")

        create_dataset(dataset1)
        create_dataset(dataset2)

        # List datasets
        datasets = list_datasets()

        assert len(datasets) >= 2
        assert all(hasattr(d, "dataset_id") for d in datasets)
        assert all(hasattr(d, "name") for d in datasets)


class TestImageOperations:
    """Test image CRUD operations."""

    @pytest.fixture
    def test_dataset(self):
        """Create a test dataset for image tests."""
        dataset = DatasetCreate(
            name=f"test_dataset_{uuid4().hex[:8]}",
            description="Dataset for image tests",
        )
        dataset_id = create_dataset(dataset)
        return dataset_id

    def test_create_image(self, test_dataset):
        """Test creating a new image record."""
        image = ImageCreate(
            dataset_id=test_dataset,
            file_path="datasets/test/image.png",
            s3_etag="abc123",
            width=1024,
            height=768,
            format="png",
            file_size_bytes=50000,
            image_type="line_graph",
            metadata={"source": "test"},
            ground_truth=[["", "x1", "x2"], ["y", "1", "2"]],
        )

        image_id = create_image(image)

        assert image_id is not None
        assert isinstance(image_id, type(uuid4()))

    def test_get_image(self, test_dataset):
        """Test retrieving an image by ID."""
        # Create image
        image = ImageCreate(
            dataset_id=test_dataset,
            file_path="datasets/test/test_image.jpg",
            width=800,
            height=600,
            ground_truth=[["", "col1"], ["row1", "val1"]],
        )
        image_id = create_image(image)

        # Retrieve image
        retrieved = get_image(image_id)

        assert retrieved is not None
        assert retrieved.image_id == image_id
        assert retrieved.dataset_id == test_dataset
        assert retrieved.file_path == "datasets/test/test_image.jpg"
        assert retrieved.width == 800
        assert retrieved.height == 600
        assert retrieved.status == ImageStatus.PENDING_UPLOAD
        assert retrieved.ground_truth is not None

    def test_update_image_status(self, test_dataset):
        """Test updating image status."""
        # Create image
        image = ImageCreate(
            dataset_id=test_dataset, file_path="datasets/test/status_test.png"
        )
        image_id = create_image(image)

        # Update status to active
        result = update_image_status(image_id, ImageStatus.ACTIVE, "etag123")

        assert result is True

        # Verify update
        updated = get_image(image_id)
        assert updated.status == ImageStatus.ACTIVE
        assert updated.s3_etag == "etag123"

    def test_list_images_by_dataset(self, test_dataset):
        """Test listing images for a dataset."""
        # Create multiple images
        for i in range(3):
            image = ImageCreate(
                dataset_id=test_dataset, file_path=f"datasets/test/image_{i}.png"
            )
            create_image(image)

        # List images
        images = list_images_by_dataset(test_dataset)

        assert len(images) >= 3
        assert all(img.dataset_id == test_dataset for img in images)

    def test_list_images_by_status(self, test_dataset):
        """Test filtering images by status."""
        # Create images with different statuses
        image1 = ImageCreate(dataset_id=test_dataset, file_path="img1.png")
        image2 = ImageCreate(dataset_id=test_dataset, file_path="img2.png")

        id1 = create_image(image1)
        create_image(image2)

        # Update one to active
        update_image_status(id1, ImageStatus.ACTIVE)

        # List only active images
        active_images = list_images_by_dataset(test_dataset, ImageStatus.ACTIVE)

        assert len([img for img in active_images if img.image_id == id1]) == 1
        assert all(img.status == ImageStatus.ACTIVE for img in active_images)


class TestEvaluationRunOperations:
    """Test evaluation run operations."""

    @pytest.fixture
    def test_dataset(self):
        """Create a test dataset."""
        dataset = DatasetCreate(name=f"test_dataset_{uuid4().hex[:8]}")
        return create_dataset(dataset)

    def test_create_evaluation_run(self, test_dataset):
        """Test creating an evaluation run."""
        run = EvaluationRunCreate(
            model_name="gemini-2.0",
            model_version="v1",
            dataset_id=test_dataset,
            dataset_version="1.0",
            config={"temperature": 0.7},
            initiated_by="test_suite",
        )

        run_id = create_evaluation_run(run)

        assert run_id is not None
        assert isinstance(run_id, type(uuid4()))

    def test_get_evaluation_run(self, test_dataset):
        """Test retrieving an evaluation run."""
        # Create run
        run = EvaluationRunCreate(
            model_name="test-model", dataset_id=test_dataset, config={"test": "config"}
        )
        run_id = create_evaluation_run(run)

        # Retrieve run
        retrieved = get_evaluation_run(run_id)

        assert retrieved is not None
        assert retrieved.run_id == run_id
        assert retrieved.model_name == "test-model"
        assert retrieved.status == RunStatus.PENDING
        assert retrieved.config == {"test": "config"}

    def test_update_run_status(self, test_dataset):
        """Test updating run status and progress."""
        # Create run
        run = EvaluationRunCreate(model_name="test-model", dataset_id=test_dataset)
        run_id = create_evaluation_run(run)

        # Update to running
        result = update_run_status(
            run_id,
            RunStatus.RUNNING,
            total_images=10,
            processed_images=5,
            failed_images=1,
        )

        assert result is True

        # Verify update
        updated = get_evaluation_run(run_id)
        assert updated.status == RunStatus.RUNNING
        assert updated.total_images == 10
        assert updated.processed_images == 5
        assert updated.failed_images == 1
        assert updated.started_at is not None

    def test_update_run_to_completed(self, test_dataset):
        """Test updating run to completed status."""
        run = EvaluationRunCreate(model_name="test-model", dataset_id=test_dataset)
        run_id = create_evaluation_run(run)

        # Update to completed
        update_run_status(run_id, RunStatus.COMPLETED)

        # Verify
        updated = get_evaluation_run(run_id)
        assert updated.status == RunStatus.COMPLETED
        assert updated.completed_at is not None


class TestPredictionOperations:
    """Test prediction operations."""

    @pytest.fixture
    def test_setup(self):
        """Create test dataset, image, and evaluation run."""
        # Create dataset
        dataset = DatasetCreate(name=f"test_dataset_{uuid4().hex[:8]}")
        dataset_id = create_dataset(dataset)

        # Create image
        image = ImageCreate(dataset_id=dataset_id, file_path="test_image.png")
        image_id = create_image(image)

        # Create evaluation run
        run = EvaluationRunCreate(model_name="test-model", dataset_id=dataset_id)
        run_id = create_evaluation_run(run)

        return {"dataset_id": dataset_id, "image_id": image_id, "run_id": run_id}

    def test_create_prediction(self, test_setup):
        """Test creating a prediction."""
        prediction = PredictionCreate(
            image_id=test_setup["image_id"],
            run_id=test_setup["run_id"],
            output={"table": [["", "x"], ["y", "1"]]},
            raw_response='{"data": "test"}',
            latency_ms=250,
            input_tokens=100,
            output_tokens=50,
            success=True,
        )

        prediction_id = create_prediction(prediction)

        assert prediction_id is not None
        assert isinstance(prediction_id, type(uuid4()))

    def test_get_predictions_by_run(self, test_setup):
        """Test retrieving all predictions for a run."""
        # Create multiple predictions with different images (unique constraint on image_id, run_id)
        for i in range(3):
            image = ImageCreate(
                dataset_id=test_setup["dataset_id"],
                file_path=f"test_pred_image_{i}.png"
            )
            image_id = create_image(image)
            prediction = PredictionCreate(
                image_id=image_id,
                run_id=test_setup["run_id"],
                output={"value": i},
                success=True,
            )
            create_prediction(prediction)

        # Retrieve predictions
        predictions = get_predictions_by_run(test_setup["run_id"])

        assert len(predictions) >= 3
        assert all(p.run_id == test_setup["run_id"] for p in predictions)


class TestMetricOperations:
    """Test metric operations."""

    @pytest.fixture
    def test_prediction(self):
        """Create a test prediction."""
        # Create dataset
        dataset = DatasetCreate(name=f"test_dataset_{uuid4().hex[:8]}")
        dataset_id = create_dataset(dataset)

        # Create image
        image = ImageCreate(dataset_id=dataset_id, file_path="test.png")
        image_id = create_image(image)

        # Create run
        run = EvaluationRunCreate(model_name="test-model", dataset_id=dataset_id)
        run_id = create_evaluation_run(run)

        # Create prediction
        prediction = PredictionCreate(image_id=image_id, run_id=run_id, success=True)
        prediction_id = create_prediction(prediction)

        return {"prediction_id": prediction_id, "run_id": run_id}

    def test_create_metric(self, test_prediction):
        """Test creating a metric."""
        metric = MetricCreate(
            prediction_id=test_prediction["prediction_id"],
            metric_name="rms",
            metric_value=0.85,
            meta_data={"note": "test"},
        )

        metric_id = create_metric(metric)

        assert metric_id is not None
        assert isinstance(metric_id, type(uuid4()))

    def test_get_metrics_by_prediction(self, test_prediction):
        """Test retrieving metrics for a prediction."""
        # Create metrics
        create_metric(
            MetricCreate(
                prediction_id=test_prediction["prediction_id"],
                metric_name="rms",
                metric_value=0.75,
            )
        )
        create_metric(
            MetricCreate(
                prediction_id=test_prediction["prediction_id"],
                metric_name="rnss",
                metric_value=0.90,
            )
        )

        # Retrieve metrics
        metrics = get_metrics_by_prediction(test_prediction["prediction_id"])

        assert len(metrics) >= 2
        metric_names = [m.metric_name for m in metrics]
        assert "rms" in metric_names
        assert "rnss" in metric_names

    def test_get_run_metrics_summary(self, test_prediction):
        """Test getting aggregated metrics for a run."""
        # Create multiple predictions with metrics
        for i in range(3):
            # Create image
            dataset = DatasetCreate(name=f"temp_{uuid4().hex[:4]}")
            dataset_id = create_dataset(dataset)

            image = ImageCreate(dataset_id=dataset_id, file_path=f"img_{i}.png")
            image_id = create_image(image)

            # Create prediction for the run
            prediction = PredictionCreate(
                image_id=image_id, run_id=test_prediction["run_id"], success=True
            )
            pred_id = create_prediction(prediction)

            # Add metrics
            create_metric(
                MetricCreate(
                    prediction_id=pred_id,
                    metric_name="rms",
                    metric_value=0.8 + (i * 0.05),
                )
            )

        # Get summary
        summary = get_run_metrics_summary(test_prediction["run_id"])

        assert "rms" in summary
        assert "avg_value" in summary["rms"]
        assert "min_value" in summary["rms"]
        assert "max_value" in summary["rms"]
        assert "count" in summary["rms"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
