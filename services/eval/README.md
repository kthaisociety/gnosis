# Evaluation Service

This directory contains the evaluation service for benchmarking VLM performance.

All environment variables are documented and configured in the root `README.md`.

## S3 Bucket Setup

To create the S3 bucket (or verify it exists), run:

uv run scripts/setup_s3_bucket.py

## Tree

```
.
├── src/
│   └── eval/
│       ├── data/           # Database, S3, and pipeline logic
│       ├── metrics/        # Scoring algorithms (RMS, RNSS)
│       ├── eval.py         # Main evaluation runner
│       └── models.py       # Pydantic schemas
└── tests/                  # Integration and unit tests
```
