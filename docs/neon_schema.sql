-- VLM Benchmark Database Schema
-- PostgreSQL (Neon)

-- ============================================
-- SCHEMA SETUP
-- ============================================
CREATE SCHEMA IF NOT EXISTS benchmark;
SET search_path TO benchmark;

-- ============================================
-- DATASETS
-- Groups images into named benchmark sets
-- ============================================
CREATE TABLE datasets (
    dataset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- IMAGES
-- Tracks images stored in S3
-- ============================================
CREATE TYPE image_status AS ENUM ('pending_upload', 'active', 'upload_failed', 'deleted');

CREATE TABLE images (
    image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID REFERENCES datasets(dataset_id) ON DELETE SET NULL,

    -- S3 reference
    file_path VARCHAR(512) NOT NULL,          -- S3 key, e.g., "{uuid}.png"
    s3_etag VARCHAR(64),                       -- For verification
    status image_status NOT NULL DEFAULT 'pending_upload',

    -- Image properties (useful for analysis)
    width INTEGER,
    height INTEGER,
    format VARCHAR(20),                        -- png, jpg, etc.
    file_size_bytes BIGINT,

    -- Classification
    image_type VARCHAR(100),                   -- e.g., 'bar_chart', 'line_graph', 'technical_drawing'

    -- Flexible metadata and ground truth
    metadata JSONB DEFAULT '{}',
    ground_truth JSONB,                        -- The expected extraction result

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_images_dataset ON images(dataset_id);
CREATE INDEX idx_images_status ON images(status);
CREATE INDEX idx_images_type ON images(image_type);

-- ============================================
-- EVALUATION RUNS
-- A single benchmark execution of a model
-- ============================================
CREATE TYPE run_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');

CREATE TABLE evaluation_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Model identification
    model_name VARCHAR(255) NOT NULL,          -- e.g., 'gpt-4o', 'claude-3-opus'
    model_version VARCHAR(100),                -- e.g., '2024-01-01'

    -- Dataset reference
    dataset_id UUID REFERENCES datasets(dataset_id) ON DELETE SET NULL,
    dataset_version VARCHAR(50),               -- Snapshot version at time of run

    -- Run configuration
    config JSONB DEFAULT '{}',                 -- Prompt template, temperature, etc.

    -- Status tracking
    status run_status NOT NULL DEFAULT 'pending',
    error_message TEXT,

    -- Progress
    total_images INTEGER DEFAULT 0,
    processed_images INTEGER DEFAULT 0,
    failed_images INTEGER DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Optional: user/system that initiated the run
    initiated_by VARCHAR(255)
);

CREATE INDEX idx_runs_model ON evaluation_runs(model_name, model_version);
CREATE INDEX idx_runs_dataset ON evaluation_runs(dataset_id);
CREATE INDEX idx_runs_status ON evaluation_runs(status);

-- ============================================
-- PREDICTIONS
-- Individual model outputs per image
-- ============================================
CREATE TABLE predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID NOT NULL REFERENCES images(image_id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES evaluation_runs(run_id) ON DELETE CASCADE,

    -- Model output
    output JSONB,                              -- The extracted data
    raw_response TEXT,                         -- Full API response (optional)

    -- Performance metadata
    latency_ms INTEGER,                        -- Response time
    input_tokens INTEGER,
    output_tokens INTEGER,

    -- Error handling
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure one prediction per image per run
    UNIQUE(image_id, run_id)
);

CREATE INDEX idx_predictions_image ON predictions(image_id);
CREATE INDEX idx_predictions_run ON predictions(run_id);
CREATE INDEX idx_predictions_success ON predictions(success);

-- ============================================
-- METRICS
-- Evaluation metrics per prediction
-- ============================================
CREATE TABLE metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES predictions(prediction_id) ON DELETE CASCADE,

    metric_name VARCHAR(100) NOT NULL,         -- e.g., 'rnss', 'rms', 'exact_match'
    metric_value DOUBLE PRECISION NOT NULL,

    -- Additional context for the metric
    meta_data JSONB DEFAULT '{}',              -- e.g., matching details, breakdown

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- One metric type per prediction
    UNIQUE(prediction_id, metric_name)
);

CREATE INDEX idx_metrics_prediction ON metrics(prediction_id);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
CREATE INDEX idx_metrics_value ON metrics(metric_value);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_datasets_updated_at
    BEFORE UPDATE ON datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_images_updated_at
    BEFORE UPDATE ON images
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- USEFUL VIEWS
-- ============================================

-- Quick overview of run performance
CREATE VIEW run_summary AS
SELECT
    er.run_id,
    er.model_name,
    er.model_version,
    d.name AS dataset_name,
    er.status,
    er.processed_images,
    er.failed_images,
    er.started_at,
    er.completed_at,
    EXTRACT(EPOCH FROM (er.completed_at - er.started_at)) AS duration_seconds
FROM evaluation_runs er
LEFT JOIN datasets d ON er.dataset_id = d.dataset_id;

-- Detailed prediction results with metrics
CREATE VIEW prediction_details AS
SELECT
    p.prediction_id,
    i.image_id,
    i.file_path,
    i.image_type,
    er.model_name,
    er.model_version,
    p.success,
    p.latency_ms,
    m.metric_name,
    m.metric_value
FROM predictions p
JOIN images i ON p.image_id = i.image_id
JOIN evaluation_runs er ON p.run_id = er.run_id
LEFT JOIN metrics m ON p.prediction_id = m.prediction_id;
